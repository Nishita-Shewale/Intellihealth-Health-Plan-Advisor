import streamlit as st
import base64

# Function to encode local image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Path to your local image
image_path = "./10554240.jpg"

# Convert image to base64
base64_img = get_base64_image(image_path)

# Set background image and remove top padding/margin to fix grey line
page_bg_img = f'''
<style>
.stApp {{
    background: url("data:image/jpg;base64,{base64_img}") no-repeat center center fixed;
    background-size: cover;
}}

.block-container {{ padding-top: 0px; }}

.container {{
    background: rgba(0, 0, 0, 0.7);  /* Semi-transparent black */
    padding: 20px;
    border-radius: 10px;
    color: white;
    max-width: 800px;
    margin: auto;
    margin-top: -30px; /* Adjusts for unwanted spacing */
}}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# Initialize session state if not set
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "plan_type" not in st.session_state:
    st.session_state["plan_type"] = None
if "patient_data" not in st.session_state:
    st.session_state["patient_data"] = {}

# Wrap content in a div with class "container"
st.markdown('<div class="container">', unsafe_allow_html=True)

# Streamlit UI
st.title(" IntelliHealth : 🩺 Health Plan Advisor ")

# Option to select AI model
model_option = st.selectbox("🤖 **Select AI Model**", ["Model A", "Model B", "Model C"])

st.header("📝 **Enter Patient Data**")
if not st.session_state["submitted"] or st.button("✏️ **Edit Patient Data**"):
    with st.form(key='patient_form'):
        st.session_state["patient_data"] = {
            "name": st.text_input("👤 **Name**", st.session_state["patient_data"].get("name", "")),
            "age": st.number_input("🎂 **Age**", min_value=0, max_value=120, step=1, value=st.session_state["patient_data"].get("age", 0)),
            "gender": st.selectbox("⚤ **Gender**", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state["patient_data"].get("gender", "Male"))),
            "state": st.text_input("🌍 **State**", st.session_state["patient_data"].get("state", "")),
            "occupation": st.text_input("💼 **Occupation**", st.session_state["patient_data"].get("occupation", "")),
            "smoking_status": st.checkbox("🚬 **Smoker?**", st.session_state["patient_data"].get("smoking_status", False)),
            "physical_activity_level": st.selectbox("🏃 **Physical Activity Level**", ["Sedentary", "Moderate", "Active"], index=["Sedentary", "Moderate", "Active"].index(st.session_state["patient_data"].get("physical_activity_level", "Sedentary"))),
            "medical_conditions": st.text_area("🏥 **Medical Conditions (comma separated)**", st.session_state["patient_data"].get("medical_conditions", "")),
            "travel_coverage_needed": st.checkbox("✈️ **Need Travel Coverage?**", st.session_state["patient_data"].get("travel_coverage_needed", False)),
            "family_coverage": st.checkbox("👨‍👩‍👦 **Family Coverage?**", st.session_state["patient_data"].get("family_coverage", False)),
            "budget_category": st.selectbox("💰 **Budget Category**", ["Bronze", "Silver", "Gold", "Platinum"], index=["Bronze", "Silver", "Gold", "Platinum"].index(st.session_state["patient_data"].get("budget_category", "Bronze"))),
            "has_offspring": st.checkbox("👶 **Has Offspring?**", st.session_state["patient_data"].get("has_offspring", False)),
            "is_married": st.checkbox("💍 **Married?**", st.session_state["patient_data"].get("is_married", False))
        }
        submit_button = st.form_submit_button(label='🚀 **Submit Data**')

    if submit_button:
        st.session_state["submitted"] = True
        st.success("✅ **Patient data submitted successfully!**")

# Show plan selection only if form is submitted
if st.session_state["submitted"]:
    st.subheader("📜 **Select Plan Type**")
    st.session_state["plan_type"] = st.selectbox("📜 **Select Plan Type**", ["Basic", "Standard", "Premium"], key="plan_select")

# Show top recommended plans based on selected plan type
if st.session_state["plan_type"]:
    st.subheader("🏆 **Top Recommended Plans**")
    if st.session_state["plan_type"] == "Basic":
        st.write("1️⃣ **Basic Plan A**")
        st.write("2️⃣ **Basic Plan B**")
        st.write("3️⃣ **Basic Plan C**")
    elif st.session_state["plan_type"] == "Standard":
        st.write("1️⃣ **Standard Plan X**")
        st.write("2️⃣ **Standard Plan Y**")
        st.write("3️⃣ **Standard Plan Z**")
    elif st.session_state["plan_type"] == "Premium":
        st.write("1️⃣ **Premium Plan 1**")
        st.write("2️⃣ **Premium Plan 2**")
        st.write("3️⃣ **Premium Plan 3**")

# Close the container div
st.markdown('</div>', unsafe_allow_html=True)
