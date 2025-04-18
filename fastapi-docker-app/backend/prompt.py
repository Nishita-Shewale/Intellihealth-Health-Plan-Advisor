import json
from snowflake_utils import get_snowflake_connection
from datetime import date
import traceback
import textwrap


def execute_cortex_query(patient_data: dict, plan_ids, model_name: str):
    plans = fetch_selected_insurance_plans(plan_ids)
    if not plans:
        return {"error": "No plans retrieved from Snowflake"}

    prompt_payload = build_llm_prompt(patient_data, plans)

    try:
        #prompt_json = json.dumps(prompt_payload)
        prompt_json = json.dumps(prompt_payload, ensure_ascii=False).replace("'", "''")
        print("🧾 Prompt JSON being sent:")
        print(prompt_json)

        sql_query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{model_name}',
                PARSE_JSON('{prompt_json}')
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


def build_llm_prompt(patient_data: dict, plans: list) -> dict:
    """
    Constructs a structured JSON prompt for Snowflake Cortex LLM.
    """

    if not patient_data or not plans:
        raise ValueError("Patient data and plans cannot be empty.")

    prompt = {
        "messages": [
            {
                "role": "system",
                "content": "You are an advanced insurance expert with strong analytical and symbolic reasoning capabilities. Your job is to evaluate and rank insurance plans based on a patient's detailed profile. Dynamically assess each attribute's relevance to the patient, assign scores, and explain how the scores were determined."
            },
            {
                "role": "user",
                "content": "Here are the details of the patient seeking an insurance plan. Consider their occupation, medical conditions, lifestyle, and any special requirements they may have."
            },
            {
                "role": "user",
                "content": f"Patient Details: {patient_data}"
            },
            {
                "role": "user",
                "content":
                    "Each insurance plan contains attributes such as PlanId, PlanMarketingName, IssuerMarketPlaceMarketingName, MetalLevel, OutOfCountryCoverage, OutOfServiceAreaCoverage, WellnessProgramOffered, DiseaseManagementProgramsOffered, IsReferralRequiredForSpecialist, IsHSAEligible, SBCHavingSimplefractureDeductible, SBCHavingSimplefractureCoinsurance, TEHBDedInnTier1Individual (used as Deductible), TEHBInnTier1IndividualMOOP (used as MaxOutOfPocket), and more."
            },
            {
                "role": "user",
                "content":
                    "Scoring Logic: For each attribute, determine how relevant it is to the patient's context. Assign scores based on relevance: high relevance gets 2 to 3 points, moderate relevance gets 1 to 2 points, low relevance gets 0 to 1 point, and none gets 0. Do not penalize plans for missing attributes."
            },
            {
                "role": "user",
                "content":
                    "Scoring Examples: If the patient frequently travels, OutOfCountryCoverage is highly relevant. If the patient works in a high-risk job like Construction or Race Car Driving, injury-related attributes like SBCHavingSimplefractureDeductible should be prioritized. If the patient has chronic medical conditions like Diabetes or Heart Disease, DiseaseManagementProgramsOffered should be rated highly. Cost-related attributes like Deductible, MaxOutOfPocket, and HSA eligibility are relevant if the patient has a low budget or affordability concerns. Sedentary patients should value wellness or weight-loss support. Active patients should value injury or sports-related coverage."
            },
            {
                "role": "user",
                "content":
                    "Final Output: Rank the top 3 plans based on total score. Each plan must include: Rank (1 to 3), PlanId, PlanMarketingName, IssuerName (from IssuerMarketPlaceMarketingName), MetalLevel, Deductible (from TEHBDedInnTier1Individual), MaxOutOfPocket (from TEHBInnTier1IndividualMOOP), TotalScore, ScoreExplanation (explain the scores with reasons), Justification (why the plan was ranked this way)."
            },
            {
                "role": "user",
                "content":
                    "At the end, include a comparison paragraph explaining why the top-ranked plan outperformed the others. Highlight which attributes made the difference. Use plain structured format with no special characters or extra commentary."
            },
            {
                "role": "user",
                "content": "Here are the available insurance plans. Please assess these options carefully based on the patient's profile."
            },
            {
                "role": "user",
                "content": f"Plans: {plans}"
            }
        ],
        "max_tokens": 4000,
        "temperature": 0.5,
        "top_p": 0.9,
        "response_format": {
            "type": "json",
            "schema": {
                "type": "object",
                "properties": {
                    "recommended_plans": {
                        "type": "array",
                        "items": {"type": "object"}
                    }
                },
                "required": ["recommended_plans"]
            }
        }
    }

    return prompt


def fetch_selected_insurance_plans(plan_ids: list) -> list:
    """
    Fetches only the selected insurance plans from Snowflake based on plan_ids.
    """
    if not plan_ids:
        return []

    conn = get_snowflake_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("USE DATABASE HEALTHCARE_INSURANCE_DB;")
        cursor.execute("USE SCHEMA PLAN_SCHEMA;")

        plan_ids_str = ", ".join([f"'{plan_id}'" for plan_id in plan_ids])

        # ✅ Print Plan IDs before query execution
        print(f"🔍 Plan IDs to query: {plan_ids_str}")  

        sql_query = f"""
        SELECT * FROM PLAN_SCHEMA.INSURANCE_PLANS
        WHERE PLANID IN ({plan_ids_str});
        """

        # ✅ Print SQL Query before execution
        print(f"📌 Executing SQL query: {sql_query}")

        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]  # Get column names
        raw_plans = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert to list of dicts

        # ✅ Convert date fields to strings
        for plan in raw_plans:
            for key, value in plan.items():
                if isinstance(value, date):  # Convert date to string
                    plan[key] = value.strftime("%Y-%m-%d")  # Convert to "YYYY-MM-DD" format

        return raw_plans

    except Exception as e:
        print(f"⚠️ Error fetching plans: {str(e)}")
        print(traceback.format_exc())  # ✅ Print full traceback to debug

        return []
    
    finally:
        cursor.close()
        conn.close()
