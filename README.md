# Intelligent Health Plan Advisor (IntelliHealth)

**Date**: April 09, 2025

## Project Details

### Description
**Intelligent Health Plan Advisor (IntelliHealth)** is a FastAPI-based application designed to simplify the complex process of selecting health insurance plans in the U.S. healthcare ecosystem. By integrating patient demographic and health data (stored in PostgreSQL) with a comprehensive dataset of insurance plans (sourced from Snowflake) and applying a rule-based recommendation engine (powered by Neo4j), IntelliHealth delivers personalized plan recommendations. The system exposes a RESTful API for managing patient profiles, retrieving plans, filtering based on individual needs, and analyzing plan suitability through rule satisfaction metrics.

This project aims to reduce financial strain and unnecessary spending by helping individuals choose plans that align with their unique health and economic needs. It leverages advanced data processing and graph-based reasoning to cut through the noise of insurance options, addressing a critical pain point in the U.S. healthcare economy.

### Features
- **Patient Management**: Create, retrieve, and manage patient profiles via API endpoints.
- **Plan Retrieval**: Fetch and normalize insurance plans from Snowflake with pagination support.
- **Plan Filtering**: Match plans to patient criteria such as state, budget category, and medical conditions.
- **Rule-Based Recommendations**: Apply dynamic rules in Neo4j (e.g., Diabetes, Maternity) for tailored plan suggestions.
- **Plan Distribution Analysis**: Evaluate how many plans satisfy varying numbers of rules per patient.
- **Data Normalization**: Clean and standardize data from CSV files and database sources for consistency.
- **Research Integration**: Experiment with Chain-of-Thought (CoT) reasoning using advanced LLMs to enhance decision-making logic.

### Tech Stack
- **Backend**: FastAPI (Python)
- **Databases**:
  - PostgreSQL (patient data storage)
  - Snowflake (insurance plans data warehouse)
  - Neo4j (graph-based rule engine)
- **Libraries**: SQLAlchemy, Pydantic, Pandas, Neo4j Driver, Snowflake Connector
- **Deployment**: Docker Compose
- **Frontend (In Progress)**: Streamlit (UI testing phase)
- **Research Tools**: OpenAI o1, Deepseek R1, GPT-4o (for CoT experimentation)

### Installation
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

Time to configure the magic behind the scenes! We’ve provided a handy .env.example file as a template. Duplicate it to .env, then fill in your database and service credentials. Think of this as giving IntelliHealth the keys to connect to PostgreSQL, Snowflake, and Neo4j. Replace placeholders like <your-user> with your actual Snowflake details—don’t worry, we won’t peek!
