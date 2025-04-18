import streamlit as st
import requests
import json
# FastAPI Backend URL
BACKEND_URL = "http://fastapi:8000"

# Available states (from Snowflake data)
states = [
    "AK", "AL", "AR", "AZ", "DE", "FL", "GA", "HI", "IA", "IL", "IN", "KS", "LA", "MI", "MO", "MS",
    "MT", "NC", "ND", "NE", "NH", "OH", "OK", "OR", "SC", "SD", "TN", "TX", "UT", "WI", "WV", "WY"
]

# List of disease management programs with "None" as an option
disease_options = ["None", "Asthma", "Heart Disease", "Diabetes", "Depression", 
                   "High Blood Pressure & High Cholesterol", "Low Back Pain", 
                   "Pain Management", "Pregnancy", "Weight Loss Programs"]

# LLM Model options
llm_models = ["claude-3-5-sonnet", "llama3.1-405b", "mistral-large2", "gpt-4o-mini", "o3-mini-2025-01-31"]
openai_models = ["gpt-4o-mini", "o3-mini-2025-01-31"]

# Session defaults
st.session_state.setdefault("patient_id", None)
st.session_state.setdefault("show_distribution", False)
st.session_state.setdefault("selected_plan_type", None)
st.session_state.setdefault("selected_llm_model", llm_models[0])

# Title
st.title("🏥 Health Plan Optimization System")
st.markdown("**Find the best insurance plan based on your needs.**")

# **SECTION 1: Patient Input**
st.subheader("👤 Enter Patient Details")
with st.form("patient_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        state = st.selectbox("Select State", states)
        occupation = st.text_input("Occupation")

    with col2:
        smoking_status = st.selectbox("Do you smoke?", ["Yes", "No"])
        physical_activity_level = st.selectbox("Physical Activity Level", ["sedentary", "moderate", "active"])
        medical_conditions = st.multiselect("Medical Conditions", disease_options, default=["None"])
        travel_coverage_needed = st.selectbox("Need Travel Coverage?", ["Yes", "No"])
        family_coverage = st.selectbox("Need Family Coverage?", ["Yes", "No"])
    
    budget_category = st.selectbox("Budget Category", ["Bronze", "Silver", "Gold", "Platinum"])
    has_offspring = st.selectbox("Do you have children?", ["Yes", "No"])
    is_married = st.selectbox("Are you married?", ["Yes", "No"])

    # Remove "None" if other diseases are selected
    if "None" in medical_conditions and len(medical_conditions) > 1:
        medical_conditions.remove("None")
    elif "None" in medical_conditions:
        medical_conditions = []

    submitted = st.form_submit_button("✅ Submit Patient Info")
    
    if submitted:
        patient_data = {
            "name": name,
            "age": age,
            "gender": gender,
            "state": state,
            "occupation": occupation,
            "smoking_status": smoking_status,
            "physical_activity_level": physical_activity_level,
            "medical_conditions": medical_conditions,
            "travel_coverage_needed": travel_coverage_needed == "Yes",
            "family_coverage": family_coverage == "Yes",
            "budget_category": budget_category,
            "has_offspring": has_offspring == "Yes",
            "is_married": is_married == "Yes",
        }

        with st.spinner("Creating patient..."):
            response = requests.post(f"{BACKEND_URL}/patients/", json=patient_data)

        if response.status_code == 200:
            st.success("✅ Patient created successfully!")
            patient_id = response.json().get("id")
            st.session_state.patient_id = patient_id

            # ⏩ CALL /process-plans/ to populate Neo4j before plan distribution
            with st.spinner("Processing plans..."):
                process_response = requests.post(
                    f"{BACKEND_URL}/process-plans/", json={"patient_id": patient_id}
                )

            if process_response.status_code == 200:
                st.success("✅ Plans processed successfully.")
                st.session_state.show_distribution = True
            else:
                st.error(f"❌ Failed to process plans: {process_response.text}")
        else:
            st.error(f"❌ Error creating patient: {response.text}")


# **SECTION 2: Plan Distribution**
if st.session_state.get("show_distribution", False):
    patient_id = st.session_state.patient_id
    st.subheader(f"📊 Plan Distribution for Patient ID: {patient_id}")

    response = requests.get(f"{BACKEND_URL}/plan-distribution/?patient_id={patient_id}")
    if response.status_code == 200:
        distribution_data = response.json()
        st.write("📦 Plan Type Distribution Raw:", distribution_data)

        # 🧩 Enhanced rule satisfaction breakdown
        raw_distribution = distribution_data.get("plan_distribution", {})
        plan_distribution = {
            int(k): v for k, v in raw_distribution.items()
            if int(k) > 0
        }

        st.markdown("### 🧠 Plans That Match Rules")
        if not plan_distribution:
            st.warning("No plans matched any filtering rules.")
        else:
            for rule_count in sorted(plan_distribution.keys(), reverse=True):
                group = plan_distribution[rule_count]
                with st.expander(f"✅ {group['count']} plan{'s' if group['count'] > 1 else ''} matched {rule_count} rule{'s' if rule_count > 1 else ''}"):
                    for entry in group.get("rule_sets_summary", []):
                        rules = entry["rules"]
                        if rules:
                            readable = " + ".join(rule.replace("_", " ").title() for rule in rules)
                        else:
                            readable = "❌ *No rules matched*"

                        st.markdown(
                            f"<div style='padding:6px 0;'>"
                            f"<span style='font-weight:bold;'>{readable}</span> → "
                            f"{entry['count']} plan{'s' if entry['count'] > 1 else ''}"
                            f"</div>",
                            unsafe_allow_html=True
                        )


        # Plan type distribution logic remains the same
        plan_type_distribution = distribution_data.get("plan_type_distribution", {})
        if plan_type_distribution:
            plan_options = ", ".join([f"{ptype} ({count} plans)" for ptype, count in plan_type_distribution.items()])
            st.info(f"Based on your details, you qualify for the following plan types: **{plan_options}**. Please select one to proceed.")

            st.selectbox("🔍 Select a Plan Type", list(plan_type_distribution.keys()), key="selected_plan_type")
            st.selectbox("🤖 Select LLM Model", llm_models, key="selected_llm_model")

            if st.button("📄 Get Plans for Selected Type"):
                with st.spinner("Fetching plans..."):
                    response = requests.get(f"{BACKEND_URL}/get-plans-by-type/{patient_id}/{st.session_state.selected_plan_type}")

                if response.status_code == 200:
                    st.session_state.plans = response.json()["plans"]
                    st.success(f"✅ Found {len(st.session_state.plans)} plans for {st.session_state.selected_plan_type}.")
                else:
                    st.error("❌ Error retrieving plans")


# **SECTION 3: LLM Recommendation**
if "plans" in st.session_state and st.session_state.plans:
    st.subheader("🧠 AI-Powered Plan Recommendation")

    if "llm_recommendation" not in st.session_state:
        st.session_state.llm_recommendation = None

    debug_container = st.empty()

    if st.button("🤖 Get AI Recommendation"):
        with st.spinner("Calling AI model..."):
            response = requests.post(f"{BACKEND_URL}/recommend-insurance/", params={
                "patient_id": st.session_state.patient_id,
                "plan_type": st.session_state.selected_plan_type.strip(),
                "model_name": st.session_state.selected_llm_model.strip(),
            })

        st.session_state.raw_response = response.text

        if response.status_code == 200:
            try:
                st.session_state.llm_recommendation = response.json()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to parse JSON response: {str(e)}")
                st.code(response.text, language="json")
        else:
            st.error(f"❌ Error retrieving AI recommendation: {response.status_code}")
            st.code(response.text)

    show_raw = st.checkbox("Show raw response")
    if show_raw and hasattr(st.session_state, "raw_response"):
        debug_container.code(st.session_state.raw_response, language="json")

    if st.session_state.llm_recommendation is not None:
        recommendation = st.session_state.llm_recommendation
        model = st.session_state.selected_llm_model.strip()

        recommended_plans = None

        # 🔀 Handle OpenAI-style output (nested JSON string sometimes)
        if model in openai_models:
            content = recommendation.get("recommendations", recommendation)

            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except Exception:
                    st.markdown("### Raw AI Response")
                    st.markdown(content)
                    content = None

            if content:
                if "summary" in content:
                    st.markdown("### Summary")
                    st.markdown(content["summary"])

                recommended_plans = content.get("recommended_plans", [])

        # 🔀 Handle non-OpenAI output (Cortex-style or consistent JSON dicts)
        else:
            raw = recommendation.get("recommendations", {}).get("raw_output", "")
            json_start = raw.find("{")
            json_end = raw.rfind("}") + 1

            try:
                json_part = raw[json_start:json_end]
                parsed = json.loads(json_part)
                recommended_plans = parsed.get("recommended_plans", [])
            except Exception as e:
                st.error(f"❌ Cortex parsing failed: {str(e)}")
                st.code(raw)

        # ✅ Display recommended plans
        if recommended_plans and len(recommended_plans) > 0:
            st.success(f"✅ Found {len(recommended_plans)} AI-recommended plans!")

            for idx, plan in enumerate(recommended_plans, start=1):
                plan_name = (
                    plan.get('PlanMarketingName') or
                    plan.get('plan_marketing_name') or
                    f'Plan {idx}'
                )
                rank = plan.get('rank', idx)

                with st.expander(f"🏥 **Rank {rank}: {plan_name}**"):
                    key_attributes = ["IssuerName", "MetalLevel", "Deductible", "MaxOutOfPocket"]
                    existing_keys = [k for k in key_attributes if k in plan]
                    if existing_keys:
                        cols = st.columns(len(existing_keys))
                        for i, key in enumerate(existing_keys):
                            with cols[i]:
                                st.markdown(f"**{key.replace('_', ' ').title()}:**  \n{plan[key]}")

                    if "Justification" in plan:
                        st.markdown("### Justification")
                        st.markdown(plan["Justification"])

                    if "ScoreBreakdown" in plan:
                        st.markdown("### Score Breakdown")
                        for attr, breakdown in plan["ScoreBreakdown"].items():
                            st.markdown(f"**{attr}**")
                            st.markdown(f"- Score: {breakdown.get('score')}")
                            st.markdown(f"- Relevance: {breakdown.get('relevance')}")
                            st.markdown(f"- Explanation: {breakdown.get('explanation')}")

                    st.markdown("### All Plan Details")
                    for key, value in plan.items():
                        if key in ["Justification", "ScoreBreakdown"]:
                            continue
                        formatted_key = key.replace('_', ' ').title()
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

            if "recommendations" in recommendation:
                st.write("Keys in 'recommendations':", list(recommendation["recommendations"].keys()) if isinstance(recommendation["recommendations"], dict) else "Not a dictionary")
