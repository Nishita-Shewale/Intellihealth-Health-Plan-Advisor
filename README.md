# 🧠 Intelligent Health Plan Advisor (IntelliHealth)

**Last Updated**: April 2025

---

## 📝 Project Overview

**IntelliHealth** is an intelligent backend system designed to recommend U.S. health insurance plans based on patient demographics, healthcare needs, and financial constraints. The system integrates three powerful data layers — **PostgreSQL**, **Snowflake**, and **Neo4j** — along with **Large Language Models (LLMs)** to make advanced, explainable plan recommendations.

---

## 🎯 Key Features

### 🔐 Patient Profile Management
- Create, retrieve, and manage patient data (stored in **PostgreSQL**)
- Demographics include medical history, lifestyle, occupation, budget, family status

### 📊 Insurance Plan Retrieval & Filtering
- Query large-scale plan data from **Snowflake**
- Apply initial filtering based on patient state, budget tier, medical needs, and travel preferences
- Data normalization ensures compatibility with internal models

### ⚖️ Rule-Based Plan Scoring (Neo4j)
- Apply **customized rules** to further filter plans dynamically based on:
  - Chronic conditions (e.g. **Diabetes Rule**)
  - Age group (**Older Adults Rule**)
  - Gender and age (**Maternity Rule**)
  - Family needs (**Family Coverage Rule**)
- Rule logic uses **per-plan-type median thresholds** for fairness

### 🤖 LLM-Based Dynamic Scoring
- Plans passing Neo4j rules are ranked using **Chain-of-Thought (CoT)** prompting
- LLMs evaluate each plan attribute’s relevance to the patient context
- Scoring is **dynamic**, **explainable**, and personalized


### 🔄 Multi-Model LLM Support
- Supports both **Snowflake Cortex (Claude)** and **OpenAI models (GPT-4o, o3)**
- Flexible backend toggle allows switching models at runtime
- Normalized output structure ensures consistent frontend rendering

### 📈 Plan Distribution & Rule Metrics
- Visual breakdown of how many rules each plan satisfies
- PlanType summaries (e.g., HMO vs PPO match count) assist downstream decisions

---

## 🧰 Tech Stack

| Layer            | Tool                          |
|------------------|-------------------------------|
| **Backend**      | FastAPI (Python)              |
| **Databases**    | PostgreSQL, Snowflake, Neo4j  |
| **LLMs**         | OpenAI GPT-4o, GPT-o3, Claude via Cortex |
| **Libraries**    | SQLAlchemy, Pydantic, Pandas, Neo4j Driver, Snowflake Connector |
| **DevOps**       | Docker Compose, .env support  |
| **Frontend**     | Streamlit (in progress)       |

---

## ⚙️ Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-repo-org>/intellihealth.git
   cd intellihealth

2. **Set Up Environment**:
   Copy .env.example to .env and populate with credentials:
   
   DATABASE_URL=postgresql://user:password@localhost:5432/intellihealth_db
   SNOWFLAKE_USER=<your-user>
   SNOWFLAKE_PASSWORD=<your-password>
   SNOWFLAKE_ACCOUNT=<your-account>
   SNOWFLAKE_WAREHOUSE=HEALTHCARE
   SNOWFLAKE_DATABASE=HEALTHCARE_INSURANCE_DB
   SNOWFLAKE_SCHEMA=PLAN_SCHEMA
   SNOWFLAKE_ROLE=<your-role>
   NEO4J_URI=bolt://neo4j:7687
   NEO4J_AUTH=neo4j/neo4jpassword


## 📬 API Highlights

- `POST /patients/` → Add patient
- `GET /insurance-plans/` → View all plans
- `POST /filter-plans/` → SQL-level filtering via Snowflake
- `POST /process-plans/` → Apply Neo4j rules and match plans
- `GET /plan-distribution/` → See how many rules each plan satisfies
- `POST /recommend-insurance/` → LLM-based scoring (select model dynamically)

---

## 🧠 What Makes It Smart?

- Uses **summary statistics** to dynamically adjust rule thresholds  
  _(e.g., medians for different PlanTypes)_
- Leverages **LLMs** to mimic expert reasoning for plan recommendation
- Capable of adapting to **multiple models** and **changing attributes** without rewriting code

 Time to configure the magic behind the scenes! We’ve provided a handy .env.example file as a template. Duplicate it to .env, then fill in your database and service credentials. 
 Think of this as giving IntelliHealth the keys to connect to PostgreSQL, Snowflake, and Neo4j. Replace placeholders like <your-user> with your actual Snowflake details—don’t 
 worry, we won’t peek!
