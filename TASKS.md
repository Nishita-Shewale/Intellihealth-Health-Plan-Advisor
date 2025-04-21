# IntelliHealth WorkLogs

Below are the tasks and subtasks assigned to **AnoushkaBansal** and **Nishita-Shewale**,reflecting the current state of the project as of April 09, 2025. Tasks are prioritized to align with ongoing work and goals for April 2025.

## 1. Project Setup
- [x] Initialize Git repository - *Completed*
- [x] Set up FastAPI structure - *Completed*
- [x] Configure Docker Compose - *Completed*

## 2. Database Setup
- **PostgreSQL**
  - [x] Define `Patient` model - *Completed*
  - [x] Add Alembic migrations - *Completed*
    - **AnoushkaBansal**: Install Alembic, create initial migration for `patients` table, test rollback functionality.
- **Snowflake**
  - [x] Implement connection and normalization - *Completed*
  - [x] Populate with `cleaned_plans_data.csv` - *Completed*
    - **Nishita-Shewale**: Develop `load_to_snowflake.py` to upload CSV using batch inserts for efficiency.
    - **Nishita-Shewale**: Validate data integrity (e.g., `SELECT COUNT(*)` matches CSV rows, check numeric fields).
  - [x] Align schema with `InsurancePlan` - *Completed*
    - **AnoushkaBansal**: Update `generated_model.py` to enforce `FLOAT` for monetary fields (e.g., `SpecialtyDrugMaximumCoinsurance`), sync with Snowflake schema.
- **Neo4j**
  - [x] Set up driver - *Completed*
  - [x] Document schema - *Completed*
    - **Nishita-Shewale**: Create `neo4j_schema.md` detailing nodes (`Patient`, `Plan`) and relationships (e.g., `CONSIDERS`, rule-specific edges).

## 3. Data Processing
- [x] Clean CSV data - *Completed*
- [x] Upload to Snowflake - *Completed*
  - **Nishita-Shewale**: (See Snowflake population task above)
- [x]  Enhance normalization - *Completed*
  - **AnoushkaBansal**: Extend `normalize_snowflake_data` to handle edge cases (e.g., malformed dates, null values in critical fields).

## 4. API Development
- **Patient Endpoints**
  - [x] `PUT /patients/{patient_id}` - *Completed*
    - **AnoushkaBansal**: Implement update logic with Pydantic validation for partial updates, test with sample data.
  - [x] `DELETE /patients/{patient_id}` - *Completed*
    - **AnoushkaBansal**: Add delete endpoint, ensure cascading removal of Neo4j relationships, test edge cases.
  - [x] Enhance `POST /patients/` - *Completed*
    - **Nishita-Shewale**: Add duplicate check (e.g., name + age combo) to prevent redundant entries, return 409 conflict if duplicate found.
- **Insurance Plan Endpoints**
  - [x] Ensure pagination consistency - *Completed*
    - **Nishita-Shewale**: Standardize `skip` and `limit` parameters across all GET endpoints, test with large datasets (e.g., 1000+ plans).
- **Error Handling**
  - [x] Add logging - *Completed*
    - **Nishita-Shewale**: Integrate Python `logging` module, configure to write errors to `intellihealth.log`, test with simulated failures.

## 5. Rule Engine
- [x] Expand rule set - *Completed*
  - **AnoushkaBansal**: Add rules for `smoking_status` (e.g., prioritize plans with wellness programs) and `physical_activity_level` (e.g., filter for preventive care benefits).
  - **Nishita-Shewale**: Create 5 diverse patient profiles to test new rules, document results in `rule_tests.md`.
- [x] Optimize Neo4j queries - *Completed*
  - **AnoushkaBansal**: Add indexes (`CREATE INDEX ON :Patient(id)`, `CREATE INDEX ON :Plan(plan_type)`), measure query speed before/after.
- [x] Integrate CoT reasoning - *Completed*
  - **Nishita-Shewale**: Experiment with OpenAI o1 for rule prioritization (e.g., explain why a plan is recommended), log findings in `cot_research.md`.

## 6. Testing
- [x] Unit Tests - *Completed*
  - **Nishita-Shewale**: Write `test_patient_endpoints.py` covering CRUD operations, use `pytest` with mock data.
  - **AnoushkaBansal**: Write `test_plan_processing.py` for plan retrieval and normalization, test edge cases (e.g., missing fields).
- [x] Integration Tests - *Completed*
  - **Nishita-Shewale**: Develop `test_end_to_end.py` for patient creation → plan recommendation flow, validate output structure.
- [x] LLM Validation - *Completed*
  - **AnoushkaBansal**: Compare CoT LLM outputs (o1, Deepseek R1) against baseline rules, quantify accuracy improvements in `cot_research.md`.

## 7. Documentation
- [x] Draft README - *Completed*
- [x] Enhance Setup Instructions - *Completed*
  - **Nishita-Shewale**: Add `.env` example and troubleshooting tips (e.g., common Docker errors) to README.
- [x] API Examples - *Completed*
  - **AnoushkaBansal**: Document 3-5 sample payloads (e.g., `POST /process-plans/`, `GET /plan-distribution/`) in README.
- [x] Research Paper Support - *Completed*
  - **Nishita-Shewale**: Draft initial `cot_research.md` with CoT experiment setup, hypotheses, and early results.

## 8. UI Development
- [x] Streamlit UI - *Completed*
  - **Nishita-Shewale**: Finalize Streamlit app in Docker, implement patient input form with validation.
  - **AnoushkaBansal**: Connect Streamlit to FastAPI endpoints (e.g., `POST /patients/`), ensure UI reflects API responses, test responsiveness.

## 9. Deployment
- [x] Production Server - *Completed*
  - **Nishita-Shewale**: Configure Gunicorn + Uvicorn in `docker-compose.prod.yml`, test with 10 concurrent requests.
- [x] CI/CD - *Completed*
  - **AnoushkaBansal**: Set up GitHub Actions workflow (lint, test, deploy), ensure all tests pass before deployment.

## 10. Enhancements
- [x] Authentication - *Completed*
  - **AnoushkaBansal**: Implement JWT-based authentication for API endpoints, secure `POST /patients/` and `/process-plans/`.
- [x] Scalability - *Completed*
  - **Nishita-Shewale**: Add Redis caching for frequent plan queries (e.g., `GET /insurance-plans/`), measure performance gains.
