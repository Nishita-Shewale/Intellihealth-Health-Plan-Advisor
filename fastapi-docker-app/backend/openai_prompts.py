import os
import json
from openai import OpenAI

#load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def build_chatgpt_prompt(patient_data: dict, plans: list) -> list:
    messages = [
        {
            "role": "user",
            "content": (
                "You are an advanced insurance expert with strong analytical and symbolic reasoning capabilities. "
                "Your task is to evaluate and rank insurance plans based specifically on a patient's detailed profile, dynamically assigning importance and scores to plan attributes. "
                "You must provide clear, detailed explanations for each scoring decision, highlighting why each attribute matters in the context of the patient."
            )
        },
        {
            "role": "user",
            "content": (
                "Below is the detailed profile of a patient seeking insurance coverage. "
                "Carefully consider the patient's occupation, medical conditions, lifestyle, age, specific risks, and any explicitly mentioned requirements when evaluating the plans."
            )
        },
        {
            "role": "user",
            "content": f"Patient Details: {patient_data}"
        },
        {
            "role": "user",
            "content": (
                "Evaluate the provided insurance plans dynamically, explicitly considering each attribute's relevance to the patient. "
                "Do NOT rely solely on fixed symbolic scoring; instead, determine scores based on the specific relevance and importance of each attribute to this particular patient's profile."
                "\n\nFor each plan attribute, follow these steps:"
                "\n1. Decide relevance (high, moderate, low, none) of the attribute for the patient's context (e.g., occupation risks, medical needs, lifestyle)."
                "\n2. Assign a dynamic score based on this relevance: high relevance (2-3 points), moderate relevance (1-2 points), low relevance (0-1 point), none (0 points)."
                "\n3. Explicitly state and justify each scoring decision in the score explanation."
                "\n\nSome examples:"
                "\n- If the patient travels frequently, 'OutOfCountryCoverage' should be highly relevant."
                "\n- For a patient in a risky profession (race car driver, construction worker), injury-related attributes (like 'SBCHavingSimplefractureDeductible') should carry higher weight."
                "\n- If the patient has chronic medical conditions, 'DiseaseManagementProgramsOffered' relevance is high."
                "\n- Cost attributes (Deductible, MaxOutOfPocket, HSA eligibility) should be weighted based on patient's stated financial needs or implied affordability concerns."
            )
        },
        {
            "role": "user",
            "content": (
                "Output a JSON object strictly following this schema:"
                "\n{"
                "\n  'recommended_plans': [{"
                "\n    'rank': integer (1-3),"
                "\n    'PlanId': string (e.g. plan.PlanId),"
                "\n    'PlanMarketingName': string (e.g. plan.PlanMarketingName),"
                "\n    'IssuerName': string (e.g. plan.IssuerMarketPlaceMarketingName),"
                "\n    'MetalLevel': string,"
                "\n    'Deductible': string (use plan.TEHBDedInnTier1Individual),"
                "\n    'MaxOutOfPocket': string (use plan.TEHBInnTier1IndividualMOOP),"
                "\n    'TotalScore': integer — sum of individual scores,"
                "\n    'ScoreExplanation': string — explain which attributes were used and why,"
                "\n    'Justification': string — summarize why this plan was ranked this way"
                "\n  }]"
                "\n}\n\n"
                "Only return top 3 plans. Finally, include a brief comparative paragraph at the end explaining why the top-ranked plan outperformed the others, highlighting specific attributes that made the difference. "
                "Do not omit any plan provided; if attributes are missing, explicitly note them but do not penalize. Respond strictly in JSON with no additional text or disclaimers. Only return unique plan IDS and unique plan marketing names for comparison in your top 3."
            )
        },
        {
            "role": "user",
            "content": f"Plans: {json.dumps(plans, default=str)}"
        }
    ]
    return messages

def call_chatgpt_structured(patient_data, plans, model="gpt-4"):
    messages = build_chatgpt_prompt(patient_data, plans)
    is_o1_mini = model in ["o1-mini-2024-09-12"]

    # Define the enforced JSON Schema
    schema = {
        "type": "object",
        "properties": {
            "recommended_plans": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "rank": {"type": "integer"},
                        "PlanId": {"type": "string"},
                        "PlanMarketingName": {"type": "string"},
                        "IssuerName": {"type": "string"},
                        "MetalLevel": {"type": "string"},
                        "Deductible": {"type": "string"},
                        "MaxOutOfPocket": {"type": "string"},
                        "TotalScore": {"type": "integer"},
                        "ScoreExplanation": {"type": "string"},
                        "Justification": {"type": "string"}
                    },
                    "required": [
                        "rank", "PlanId", "PlanMarketingName", "IssuerName", "MetalLevel",
                        "Deductible", "MaxOutOfPocket", "TotalScore","ScoreExplanation" ,"Justification"
                    ],
                    "additionalProperties": False
                }
            },
            "summary": {"type": "string"}
        },
        "required": ["recommended_plans", "summary"],
        "additionalProperties": False
    }
    print(model)

    try:
        client= OpenAI()
        if is_o1_mini:
            # No temperature, no response_format, no system
            print("o1 block")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=3000
            )
            print(" o3 Response:", response)
        else:
            # Full features enabled for GPT-4 / 4o
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                #temperature=0.5,
                max_completion_tokens=8000,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "insurance_recommendation",
                        "schema": schema,
                        "strict": True
                    }
                }
            )
            print(" o3 Response:", response)
        return response.choices[0].message.content

    except Exception as e:
        return {
            "error": str(e),
            "raw_prompt": messages
        }