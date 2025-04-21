import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

st.set_page_config(layout="wide")
st.title("Today's Insurance Problems")

@st.cache_data
def load_data():
    return pd.read_csv("./cleaned_plans_data.csv")

df = load_data()
st.success("Loaded insurance data with {} plans.".format(len(df)))

# 1. Too Many Options
st.header("📌 Too Many Options")
st.markdown("Too many choices make plan selection overwhelming. Here's how many options patients face by state and plan type.")

col1, col2 = st.columns(2)
with col1:
    plan_by_state = df['StateCode'].value_counts().sort_values(ascending=False)
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    plan_by_state.plot(kind='bar', color="#84b6f4", ax=ax1)
    ax1.set_title("Number of Plans per State")
    ax1.set_ylabel("Plans")
    st.pyplot(fig1)

with col2:
    plan_type_dist = df['PlanType'].value_counts()
    fig2, ax2 = plt.subplots()
    plan_type_dist.plot(kind='bar', color="#77dd77", ax=ax2)
    ax2.set_title("Plan Type Distribution")
    ax2.set_ylabel("Count")
    st.pyplot(fig2)

# 1.5 Plan Type Explanation in Layman Terms
st.markdown("### 🧾 What Do These Plan Types Actually Mean?")

# ✅ Use relative paths (make sure files are in ./images/)
try:
    plan_types_img = Image.open("./images/image.png")
    cost_vs_flex_img = Image.open("./images/output_image.png")

    col3, col4 = st.columns(2)
    with col3:
        st.image(plan_types_img, caption="Visual Summary of Plan Types", use_container_width=True)

    with col4:
        st.image(cost_vs_flex_img, caption="Cost vs. Flexibility of Plan Types", use_container_width=True)
except FileNotFoundError as e:
    st.error(f"🔴 Could not load image: {e.filename}. Make sure it exists in the './images/' folder.")

# 2. High Out-of-Pocket Costs
st.header("📌 High Out-of-Pocket Costs")
st.markdown("Even insured patients face high deductibles, especially for chronic or emergency needs.")

cost_cols = ['SBCHavingDiabetesDeductible', 'SBCHavingSimplefractureDeductible']
df_cost_filtered = df[cost_cols].replace(["Not Applicable", "per person not applicable", "per group not applicable", "$0"], pd.NA)

# Clean numeric
for col in cost_cols:
    df_cost_filtered[col] = df_cost_filtered[col].astype(str).str.replace(r'[$,]', '', regex=True)
    df_cost_filtered[col] = pd.to_numeric(df_cost_filtered[col], errors='coerce')

df_cost_filtered = df_cost_filtered.dropna(how='all')

fig, axs = plt.subplots(1, 2, figsize=(12, 5))

df_cost_filtered.boxplot(column=['SBCHavingDiabetesDeductible'], ax=axs[0])
axs[0].set_title("Diabetes Deductibles")
axs[0].set_ylabel("Cost ($)")

df_cost_filtered.boxplot(column=['SBCHavingSimplefractureDeductible'], ax=axs[1])
axs[1].set_title("Fracture Deductibles")
axs[1].set_ylabel("Cost ($)")

st.pyplot(fig)

# 3. Lack of Financial Planning Options (HSA)
st.header("📌 Lack of Financial Planning Options")
st.markdown("Many plans don’t support Health Savings Accounts or don’t disclose contributions.")

hsa_cols = ['IsHSAEligible', 'HSAOrHRAEmployerContribution', 'HSAOrHRAEmployerContributionAmount']
hsa_missing = df[hsa_cols].isnull().mean() * 100

fig5, ax5 = plt.subplots(figsize=(7, 3))
hsa_missing.plot(kind='barh', color="#cbaacb", ax=ax5)

ax5.set_title("Missing Financial Planning Fields (%)", fontsize=12)
ax5.set_xlabel("% Missing", fontsize=10)
ax5.tick_params(axis='x', labelsize=8)
ax5.tick_params(axis='y', labelsize=8)
plt.tight_layout()

st.pyplot(fig5)

# Wrap Up
st.markdown("---")
st.info("These visualizations highlight why IntelliHealth is essential: to simplify, explain, and optimize plan selection for real people.")
