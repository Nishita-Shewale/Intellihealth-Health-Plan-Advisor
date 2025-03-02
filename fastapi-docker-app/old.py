



@app.get("/insurance-plans/", response_model=List[InsurancePlan])
def read_insurance_plans(skip: int = 0, limit: int = 10):
    conn = get_snowflake_connection()
    cursor = conn.cursor()

    # Construct the query for Snowflake
    query = f"""
    SELECT * 
    FROM PLAN_SCHEMA.INSURANCE_PLANS
    LIMIT {limit} OFFSET {skip}
    """

    cursor.execute(query)
    db_plans = cursor.fetchall()

    # Get the column names
    columns = [column[0] for column in cursor.description]
    
    cursor.close()
    conn.close()

    # Map the fetched rows to the Pydantic schema
    plans = []
    for plan in db_plans:
        # Map each row to a dictionary
        plan_dict = dict(zip(columns, plan))
        
        # Create an InsurancePlan Pydantic model instance
        try:
            insurance_plan = InsurancePlan(**plan_dict)
            plans.append(insurance_plan)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error mapping data: {e}")

    return plans


def filter_plans(patient_data: dict) -> List[InsurancePlan]:
    """
    Filters insurance plans based on patient data from Snowflake.
    """

    # Connect to Snowflake
    conn = get_snowflake_connection()
    cursor = conn.cursor()

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

    # Add medical conditions filter dynamically
    for condition in patient_data["medical_conditions"]:
        query += f" AND DiseaseManagementProgramsOffered LIKE '%{condition}%'"

    cursor.execute(query)
    db_plans = cursor.fetchall()

    # Get the column names
    columns = [column[0] for column in cursor.description]

    cursor.close()
    conn.close()

    # Map the fetched data to a list of InsurancePlan models
    plans = []
    for plan in db_plans:
        plan_dict = dict(zip(columns, plan))
        try:
            insurance_plan = InsurancePlan(**plan_dict)  # Pydantic model
            plans.append(insurance_plan)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error mapping data: {e}")

    return {"total_count": len(plans), "plans": plans}





@app.get("/insurance-plans/", response_model=List[schemas.InsurancePlan])
def read_insurance_plans(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Query the database for insurance plans with pagination
    db_plans = db.query(models.InsurancePlan).offset(skip).limit(limit).all()
    # Replace NaN and other invalid values
    def clean_data(plan):
        for key, value in plan.__dict__.items():
            if isinstance(value, float) and (value != value or value in [float('inf'), float('-inf')]):
                setattr(plan, key, None)  # Replace invalid floats with None
        return plan

    cleaned_plans = [clean_data(plan) for plan in db_plans]
    return cleaned_plans


def filter_plans(db: Session, patient_data: dict) -> List[models.InsurancePlan]:  # Use models.InsurancePlan
    query = db.query(models.InsurancePlan).filter(  # Explicitly use the SQLAlchemy model here
        models.InsurancePlan.StateCode == patient_data["state"],
        models.InsurancePlan.MetalLevel == patient_data["budget_category"],
        models.InsurancePlan.OutOfCountryCoverage == ('Yes' if patient_data["travel_coverage_needed"] else 'No')
    )
    
    # Filter for family coverage
    if patient_data["family_coverage"]:
        query = query.filter(models.InsurancePlan.ChildOnlyOffering.ilike('%Adult%'))
    
    # Filter for offspring coverage
    if patient_data.get("has_offspring", False):
        query = query.filter(models.InsurancePlan.ChildOnlyOffering.ilike('%Child%'))

    # Add medical conditions filter dynamically
    for condition in patient_data["medical_conditions"]:
        query = query.filter(models.InsurancePlan.DiseaseManagementProgramsOffered.ilike(f'%{condition}%'))
    
    total_count = query.count()
    db_plans = query.all()

    # Clean the data
    def clean_data(plan):
        for key, value in plan.__dict__.items():
            if isinstance(value, float) and (value != value or value in [float('inf'), float('-inf')]):  # Check for NaN, Infinity
                setattr(plan, key, None)  # Replace invalid floats with None
        return plan

    cleaned_plans = [clean_data(plan) for plan in db_plans]
    return cleaned_plans, total_count
