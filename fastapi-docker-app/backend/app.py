# app.py
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import models
from models import InsurancePlan
import schemas
from schemas import InsurancePlan, PatientID
from database import Base, engine, SessionLocal
from typing import List
import pandas as pd
from neo4j_utils import neo4j_driver
from rules import apply_selected_rules, clean_value, get_plan_distribution,get_plans_by_type_from_neo4j, get_plan_ids_from_neo4j
from snowflake_utils import get_snowflake_connection, normalize_snowflake_data
from prompt import execute_cortex_query
import re
from datetime import date
import json
from openai_prompts import call_chatgpt_structured
from cleanup import clean_value, ATTRIBUTE_CLEANUP_CONFIG
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Patient Endpoints
@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient



@app.get("/insurance-plans/", response_model=List[InsurancePlan])
def read_insurance_plans(skip: int = 0, limit: int = 10):
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        # Set context
        cursor.execute("USE DATABASE HEALTHCARE_INSURANCE_DB")
        cursor.execute("USE SCHEMA PLAN_SCHEMA")
        cursor.execute("USE ROLE BISON_ROLE")

        # Fetch data
        query = f"""
        SELECT * 
        FROM INSURANCE_PLANS
        LIMIT {limit} OFFSET {skip}
        """
        cursor.execute(query)
        db_plans = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        # Use common normalization function
        plans = normalize_snowflake_data(
            raw_data=db_plans,
            columns=columns,
            pydantic_model=InsurancePlan,
            date_fields=["PlanEffectiveDate", "PlanExpirationDate"]
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error mapping data: {e}")
    
    finally:
        cursor.close()
        conn.close()

    return plans


def filter_plans(patient_data: dict) -> dict:
    """
    Filters insurance plans based on patient data from Snowflake.
    Returns a dictionary with total count and list of InsurancePlan objects.
    """

    # Connect to Snowflake
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        # Build the SQL query using patient data
        query = f"""
        SELECT * 
        FROM PLAN_SCHEMA.INSURANCE_PLANS
        WHERE 
            StateCode = '{patient_data["state"]}' AND
            MetalLevel = '{patient_data["budget_category"]}' AND
            OutOfCountryCoverage = '{'Yes' if patient_data["travel_coverage_needed"] else 'No'}'
        """

        # Add additional filters for family coverage and offspring coverage
        if patient_data["family_coverage"]:
            query += " AND ChildOnlyOffering LIKE '%Adult%'"

        if patient_data.get("has_offspring", False):
            query += " AND ChildOnlyOffering LIKE '%Child%'"

        # Only add disease filter if patient has selected any diseases
        if patient_data["medical_conditions"]:
            for condition in patient_data["medical_conditions"]:
                query += f" AND DiseaseManagementProgramsOffered LIKE '%{condition}%'"


        cursor.execute(query)
        db_plans = cursor.fetchall()

        # Get the column names
        columns = [column[0] for column in cursor.description]

        # Use the common normalization function
        plans = normalize_snowflake_data(
            raw_data=db_plans,
            columns=columns,
            pydantic_model=InsurancePlan,
            date_fields=["PlanEffectiveDate", "PlanExpirationDate"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering plans: {e}")

    finally:
        cursor.close()
        conn.close()

    return {"total_count": len(plans), "plans": plans}



@app.post("/filter-plans/")
def filter_plans_endpoint(patient_id: PatientID, db: Session = Depends(get_db)):
    if isinstance(patient_id, PatientID):  # Check if it's wrapped in a custom type
        patient_id = patient_id.patient_id
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    print(f"Received patient_id: {patient_id}, Type: {type(patient_id)}")

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Convert patient object to a dictionary
    patient_data = {
        "state": patient.state,
        "budget_category": patient.budget_category,
        "travel_coverage_needed": patient.travel_coverage_needed,
        "family_coverage": patient.family_coverage,
        "has_offspring": patient.has_offspring,
        "smoking_status": patient.smoking_status,
        "medical_conditions": patient.medical_conditions,
        "physical_activity_level": patient.physical_activity_level,
    }
    print(f"Patient Data: {patient_data}")
    filtered_data = filter_plans(patient_data)
    total_count = filtered_data["total_count"]
    plans = filtered_data["plans"]
    plan_ids = [plan.PlanId for plan in plans]

    # Print the list of Plan IDs
    print("Filtered Plan IDs:", plan_ids)

    if not plans:
        raise HTTPException(status_code=404, detail="No plans found for the given criteria")
    return {
        "total_count": total_count,
        "plans": plans[:10],
    }

@app.post("/process-plans/")
def process_plans(patient_id: PatientID, db: Session = Depends(get_db)):
    if isinstance(patient_id, PatientID):
        patient_id = patient_id.patient_id

    # Fetch patient data
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Convert patient object to dictionary
    patient_data = {
        "id": patient.id, 
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "state": patient.state,
        "occupation": patient.occupation,
        "smoking_status": patient.smoking_status,
        "physical_activity_level": patient.physical_activity_level,
        "medical_conditions": patient.medical_conditions,
        "travel_coverage_needed": patient.travel_coverage_needed,
        "family_coverage": patient.family_coverage,
        "budget_category": patient.budget_category,
        "has_offspring": patient.has_offspring,
        "is_married": patient.is_married,
    }

    # Filter plans using SQL
    plans = filter_plans(patient_data)["plans"]

    if not plans:
        raise HTTPException(status_code=404, detail="No plans found for the given criteria")

    # Insert patient and filtered plans into Neo4j
    with neo4j_driver.session() as session:
        session.run(
            """
            MERGE (p:Patient {id: $id})
            SET p.name = $name,
                p.age = $age,
                p.gender = $gender,
                p.state = $state,
                p.occupation = $occupation,
                p.smoking_status = $smoking_status,
                p.physical_activity_level = $physical_activity_level,
                p.medical_conditions = $medical_conditions,
                p.travel_coverage_needed = $travel_coverage_needed,
                p.family_coverage = $family_coverage,
                p.budget_category = $budget_category,
                p.has_offspring = $has_offspring,
                p.is_married = $is_married
            """,
            id=patient_data["id"],
            name=patient_data["name"],
            age=patient_data["age"],
            gender=patient_data["gender"],
            state=patient_data["state"],
            occupation=patient_data["occupation"],
            smoking_status=patient_data["smoking_status"],
            physical_activity_level=patient_data["physical_activity_level"],
            medical_conditions=patient_data["medical_conditions"],
            travel_coverage_needed=patient_data["travel_coverage_needed"],
            family_coverage=patient_data["family_coverage"],
            budget_category=patient_data["budget_category"],
            has_offspring=patient_data["has_offspring"],
            is_married=patient_data["is_married"],
        )

        print("\n🔍 Plans Received in process_plans:")

        for plan in plans:
            try:
                if isinstance(plan, InsurancePlan):
                    plan_data = {
                        key: clean_value(getattr(plan, key, None), ATTRIBUTE_CLEANUP_CONFIG.get(key, str))
                        if key.lower() != "planid" else str(getattr(plan, key, None)) 
                        for key in plan.__dict__
                        if not key.startswith("_")
                    }
                elif isinstance(plan, dict):
                    plan_data = {
                        key: clean_value(plan.get(key, None), ATTRIBUTE_CLEANUP_CONFIG.get(key, str))
                        if key.lower() != "planid" else str(plan.get(key, None))
                        for key in plan.keys()
                    }
                else:
                    raise Exception("Unexpected data type in plans")

                # Insert into Neo4j
                session.run(
                    """
                    MERGE (plan:Plan {PlanId: $id})
                    SET plan += $plan_data
                    MERGE (p:Patient {id: $patient_id})
                    MERGE (p)-[:CONSIDERS]->(plan)
                    """,
                    id=getattr(plan, 'PlanId', None) if isinstance(plan, InsurancePlan) else plan.get('PlanId'),
                    plan_data=plan_data,
                    patient_id=patient_id
                )

            except Exception as e:

                raise HTTPException(status_code=500, detail=f"Error processing plan: {str(e)}")
            
    preferred_plans = apply_selected_rules(neo4j_driver, patient_data)

    if not preferred_plans:
        raise HTTPException(status_code=404, detail="No preferred plans found for the patient in Neo4j")

    # Extract patient info (same across all rule results)
    first_rule = next(iter(preferred_plans.values()))
    patient_info = first_rule["patient"]

    # ✅ Deduplicate plans and count rule matches
    from collections import defaultdict
    plan_id_to_data = defaultdict(lambda: {"plan": None, "rule_count": 0})

    for rule_data in preferred_plans.values():
        for plan in rule_data["plans"]:
            plan_id = plan["PlanId"]
            plan_id_to_data[plan_id]["plan"] = plan
            plan_id_to_data[plan_id]["rule_count"] += 1

    # Sort by rule match count (optional)
    sorted_plans = sorted(
        plan_id_to_data.values(), 
        key=lambda x: x["rule_count"], 
        reverse=True
    )

    top_plans = [entry["plan"] for entry in sorted_plans[:10]]
    preferred_plans_count = len(plan_id_to_data)

    print(f"Total unique plans selected: {preferred_plans_count}")

    return {
        "patient_id": patient_info,
        "preferred_plans_count": preferred_plans_count,
        "preferred_plans": top_plans
    }

@app.get("/plan-distribution/")
def plan_distribution(patient_id: int, db: Session = Depends(get_db)):
    """
    This endpoint returns the distribution of plans for a specific patient based on the number of rules they satisfy.
    """
    try:
        # Fetch the patient data first
        patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Fetch the plan distribution from Neo4j for the given patient
        plan_distribution, plan_type_distribution, highest_rule_count = get_plan_distribution(neo4j_driver, patient_id)

        print(f"Highest Rule Count Identified: {highest_rule_count}")
        # Add context about plan type distribution
        plan_type_note = f"Plan types listed in 'plan_type_distribution' correspond to the plans that satisfy {highest_rule_count} rules."

        # Return both distributions along with the patient ID
        return {
            "patient_id": patient_id,
            "plan_distribution": plan_distribution,
            "plan_type_distribution": plan_type_distribution,
            "note": plan_type_note
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plan distribution: {str(e)}")

@app.get("/get-plans-by-type/{patient_id}/{plan_type}")
def get_plans_by_type(patient_id: int, plan_type: str, db: Session = Depends(get_db)):
    """
    This endpoint filters and returns all plans of a specific type for a given patient based on their selected plan type,
    but only considering the plans that satisfy the most rules.
    """
    try:
        # Fetch the patient data first
        patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        _, _, highest_rule_count = get_plan_distribution(neo4j_driver, patient_id)


        # Fetch the plans that satisfy the highest number of rules
        selected_plans = get_plans_by_type_from_neo4j(neo4j_driver, patient_id, plan_type, highest_rule_count)

        if not selected_plans:
            raise HTTPException(status_code=404, detail=f"No plans found for the selected type '{plan_type}' with the highest rule satisfaction.")

        # Return the filtered plans and patient info
        return {
            "patient_id": patient_id,
            "selected_plan_type": plan_type,
            "plans": selected_plans
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plans by type: {str(e)}")

@app.post("/recommend-insurance/")
def recommend_insurance(patient_id: int, plan_type: str, model_name: str, db: Session = Depends(get_db)) -> dict:
    """
    Fetches patient data and recommends insurance plans using Snowflake Cortex.
    """
    # Fetch patient details
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    _, _, highest_rule_count = get_plan_distribution(neo4j_driver, patient_id)

    plan_ids = get_plan_ids_from_neo4j(neo4j_driver, patient_id, plan_type, highest_rule_count)

    if not plan_ids:
        raise HTTPException(status_code=404, detail="No plans found for the given type")
    
    patient_data = {column.name: getattr(patient, column.name) for column in models.Patient.__table__.columns}
    plans=get_plans_by_type_from_neo4j(neo4j_driver, patient_id, plan_type, highest_rule_count)

    if model_name.lower() in ["gpt-4o", "gpt-4o-mini", "o1-mini-2024-09-12","o3-mini-2025-01-31"]:
        response = call_chatgpt_structured(patient_data, plans, model_name)
    else:
        response = execute_cortex_query(patient_data, plan_ids, model_name)
    print(f"🔹 Raw LLM Output: {response}")
    return {"recommendations": response}

