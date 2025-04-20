



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


def execute_cortex_query(patient_data: dict, plan_ids, model_name: str = "llama3.1-405b"):
    plans = fetch_selected_insurance_plans(plan_ids)
    if not plans:
        return {"error": "No plans retrieved from Snowflake"}

    prompt_payload = build_llm_prompt(patient_data, plans)

    try:
        #prompt_json = json.dumps(prompt_payload)
        prompt_json = json.dumps(prompt_payload, ensure_ascii=False).replace("'", "''")
        print("🧾 Prompt JSON being sent:")
        print(prompt_json)

        # Build the SQL query with all values directly interpolated (no parameter binding)
        parameters={
            "temperature": 0.5,
            "max_tokens": 4000,
            "top_p": 0.9,
            "response_format": {
                "type": "json",
                "schema": {
                "type": "object",
                "properties": {
                    "recommended_plans": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                        "rank": { "type": "integer" },
                        "PlanId": { "type": "string" },
                        "PlanMarketingName": { "type": "string" },
                        "IssuerName": { "type": "string" },
                        "MetalLevel": { "type": "string" },
                        "Deductible": { "type": "number" },
                        "MaxOutOfPocket": { "type": "number" },
                        "TotalScore": { "type": "integer" },
                        "Justification": { "type": "string" },
                        "OutOfCountryCoverage": { "type": "string" },
                        "OutOfServiceAreaCoverage": { "type": "string" },
                        "WellnessProgramOffered": { "type": "string" },
                        "DiseaseManagementProgramsOffered": { "type": "string" },
                        "IsReferralRequiredForSpecialist": { "type": "string" },
                        "IsHSAEligible": { "type": "string" },
                        "SBCHavingSimplefractureDeductible": { "type": "string" },
                        "SBCHavingSimplefractureCoinsurance": { "type": "string" },
                        "ChildOnlyOffering": { "type": "string" },
                        "StateCode": { "type": "string" },
                        "PlanEffectiveDate": { "type": "string" },
                        "PlanExpirationDate": { "type": "string" }
                        },
                        "required": [
                        "rank",
                        "PlanId",
                        "PlanMarketingName",
                        "IssuerName",
                        "MetalLevel",
                        "Deductible",
                        "MaxOutOfPocket",
                        "TotalScore",
                        "Justification"
                        ]
                    }
                    }
                }
                }
            }
            }
        parameters_json_sql = json.dumps(parameters).replace("'", "''")
        sql_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{model_name}',
                PARSE_JSON('{prompt_json}'),
                PARSE_JSON('{parameters_json_sql}')
            ) AS recommendations;
        """
        
        conn = get_snowflake_connection()
        cursor = conn.cursor()
        print("🧠 Executing Cortex SQL...")
        print(textwrap.indent(sql_query, "  "))  # Indent the SQL query for better readability
        cursor.execute(sql_query)  # No parameter binding
        

        result = cursor.fetchone()
        if not result:
            return {"error": "No response from Cortex"}

        raw_output = result[0]
        print(f"🔹 Raw LLM Output: {raw_output}")

        try:
            return json.loads(raw_output)
        except json.JSONDecodeError as e:
            return {
                "error": f"JSON parsing failed: {str(e)}",
                "raw_output": raw_output
            }

    except Exception as e:
        return {"error": f"Error executing Cortex: {str(e)}"}
    
    finally:
        cursor.close()
        conn.close()



# **SECTION 3: LLM Recommendation**
if "plans" in st.session_state and st.session_state.plans:
    st.subheader("🧠 AI-Powered Plan Recommendation")

    # Store recommendation in session state to persist across reruns
    if "llm_recommendation" not in st.session_state:
        st.session_state.llm_recommendation = None
    
    # Debug container that stays visible
    debug_container = st.empty()
    
    if st.button("🤖 Get AI Recommendation"):
        with st.spinner("Calling AI model..."):
            response = requests.post(f"{BACKEND_URL}/recommend-insurance/", params={
                "patient_id": st.session_state.patient_id,
                "plan_type": st.session_state.selected_plan_type.strip(),
                "model_name": st.session_state.selected_llm_model.strip(),
            })
            
        # Always store the raw text response in session state
        st.session_state.raw_response = response.text
            
        if response.status_code == 200:
            try:
                # Store the parsed response
                st.session_state.llm_recommendation = response.json()
                st.rerun() # Rerun to ensure UI updates correctly
            except Exception as e:
                st.error(f"❌ Failed to parse JSON response: {str(e)}")
                st.code(response.text, language="json")
        else:
            st.error(f"❌ Error retrieving AI recommendation: {response.status_code}")
            st.code(response.text)
    
    # Show debug toggle (outside the button click handler)
    show_raw = st.checkbox("Show raw response")
    if show_raw and hasattr(st.session_state, "raw_response"):
        debug_container.code(st.session_state.raw_response, language="json")
    
    # Display recommendation (outside the button click handler)
    if st.session_state.llm_recommendation is not None:
        recommendation = st.session_state.llm_recommendation
        
        # Handle the extra nesting level - check for recommendations.recommended_plans
        recommended_plans = None
        if "recommendations" in recommendation and "recommended_plans" in recommendation["recommendations"]:
            recommended_plans = recommendation["recommendations"]["recommended_plans"]
        elif "recommended_plans" in recommendation:
            recommended_plans = recommendation["recommended_plans"]
        
        # Check if we found plans in any structure
        if recommended_plans and len(recommended_plans) > 0:
            st.success(f"✅ Found {len(recommended_plans)} AI-recommended plans!")
            
            # Display plans
            for idx, plan in enumerate(recommended_plans, start=1):
                # Get plan name with fallback
                plan_name = plan.get('plan_marketing_name', f'Plan {idx}')
                rank = plan.get('rank', idx)
                
                with st.expander(f"🏥 **Rank {rank}: {plan_name}**"):
                    # First display key attributes if they exist
                    key_attributes = ["issuer_name", "metal_level", "deductible", "max_out_of_pocket"]
                    
                    # Create columns for key attributes that exist
                    existing_keys = [k for k in key_attributes if k in plan]
                    if existing_keys:
                        cols = st.columns(len(existing_keys))
                        for i, key in enumerate(existing_keys):
                            with cols[i]:
                                st.markdown(f"**{key.replace('_', ' ').title()}:**  \n{plan[key]}")
                    
                    # Special handling for justification
                    if "justification" in plan:
                        st.markdown("### Justification")
                        st.markdown(plan["justification"])
                    
                    # Display all other attributes
                    st.markdown("### All Plan Details")
                    for key, value in plan.items():
                        if key == "justification":
                            continue
                        formatted_key = key.replace('_', ' ').title()
                        
                        # Handle different value types
                        if isinstance(value, dict):
                            st.markdown(f"**{formatted_key}:**")
                            st.json(value)
                        elif isinstance(value, list):
                            st.markdown(f"**{formatted_key}:**")
                            for item in value:
                                st.markdown(f"- {item}")
                        else:
                            st.markdown(f"**{formatted_key}:** {value}")
        else:
            st.warning("⚠️ No recommended plans found in the response.")
            st.write("Available keys in response:", list(recommendation.keys()) if isinstance(recommendation, dict) else "Not a dictionary")
            
            # If we have a recommendations key but no plans, show its structure
            if "recommendations" in recommendation:
                st.write("Keys in 'recommendations':", list(recommendation["recommendations"].keys()) if isinstance(recommendation["recommendations"], dict) else "Not a dictionary")