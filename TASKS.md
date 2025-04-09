# IntelliHealth WorkLogs

Below are the tasks and subtasks assigned to **AnoushkaBansal** and **Nishita-Shewale**,reflecting the current state of the project as of April 09, 2025. Tasks are prioritized to align with ongoing work and goals for April 2025.

## 1. Project Setup
- [x] Initialize Git repository - *Completed*
- [x] Set up FastAPI structure - *Completed*
- [x] Configure Docker Compose - *Completed*

## 2. Database Setup
- **PostgreSQL**
  - [x] Define `Patient` model - *Completed*
  - [ ] Add Alembic migrations
    - **AnoushkaBansal**: Install Alembic, create initial migration for `patients` table, test rollback functionality.
- **Snowflake**
  - [x] Implement connection and normalization - *Completed*
  - [ ] Populate with `cleaned_plans_data.csv`
    - **Nishita-Shewale**: Develop `load_to_snowflake.py` to upload CSV using batch inserts for efficiency.
    - **Nishita-Shewale**: Validate data integrity (e.g., `SELECT COUNT(*)` matches CSV rows, check numeric fields).
  - [ ] Align schema with `InsurancePlan`
    - **AnoushkaBansal**: Update `generated_model.py` to enforce `FLOAT` for monetary fields (e.g., `SpecialtyDrugMaximumCoinsurance`), sync with Snowflake schema.
- **Neo4j**
  - [x] Set up driver - *Completed*
  - [ ] Document schema
    - **Nishita-Shewale**: Create `neo4j_schema.md` detailing nodes (`Patient`, `Plan`) and relationships (e.g., `CONSIDERS`, rule-specific edges).

## 3. Data Processing
- [x] Clean CSV data - *Completed*
- [ ] Upload to Snowflake
  - **Nishita-Shewale**: (See Snowflake population task above)
- [ ] Enhance normalization
  - **AnoushkaBansal**: Extend `normalize_snowflake_data` to handle edge cases (e.g., malformed dates, null values in critical fields).

## 4. API Development
- **Patient Endpoints**
  - [ ] `PUT /patients/{patient_id}`
    - **AnoushkaBansal**: Implement update logic with Pydantic validation for partial updates, test with sample data.
  - [ ] `DELETE /patients/{patient_id}`
    - **AnoushkaBansal**: Add delete endpoint, ensure cascading removal of Neo4j relationships, test edge cases.
  - [ ] Enhance `POST /patients/`
    - **Nishita-Shewale**: Add duplicate check (e.g., name + age combo) to prevent redundant entries, return 409 conflict if duplicate found.
- **Insurance Plan Endpoints**
  - [ ] Ensure pagination consistency
    - **Nishita-Shewale**: Standardize `skip` and `limit` parameters across all GET endpoints, test with large datasets (e.g., 1000+ plans).
- **Error Handling**
  - [ ] Add logging
    - **Nishita-Shewale**: Integrate Python `logging` module, configure to write errors to `intellihealth.log`, test with simulated failures.

## 5. Rule Engine
- [ ] Expand rule set
  - **AnoushkaBansal**: Add rules for `smoking_status` (e.g., prioritize plans with wellness programs) and `physical_activity_level` (e.g., filter for preventive care benefits).
  - **Nishita-Shewale**: Create 5 diverse patient profiles to test new rules, document results in `rule_tests.md`.
- [ ] Optimize Neo4j queries
  - **AnoushkaBansal**: Add indexes (`CREATE INDEX ON :Patient(id)`, `CREATE INDEX ON :Plan(plan_type)`), measure query speed before/after.
- [ ] Integrate CoT reasoning
  - **Nishita-Shewale**: Experiment with OpenAI o1 for rule prioritization (e.g., explain why a plan is recommended), log findings in `cot_research.md`.

## 6. Testing
- [ ] Unit Tests
  - **Nishita-Shewale**: Write `test_patient_endpoints.py` covering CRUD operations, use `pytest` with mock data.
  - **AnoushkaBansal**: Write `test_plan_processing.py` for plan retrieval and normalization, test edge cases (e.g., missing fields).
- [ ] Integration Tests
  - **Nishita-Shewale**: Develop `test_end_to_end.py` for patient creation → plan recommendation flow, validate output structure.
- [ ] LLM Validation
  - **AnoushkaBansal**: Compare CoT LLM outputs (o1, Deepseek R1) against baseline rules, quantify accuracy improvements in `cot_research.md`.

## 7. Documentation
- [x] Draft README - *Completed*
- [ ] Enhance Setup Instructions
  - **Nishita-Shewale**: Add `.env` example and troubleshooting tips (e.g., common Docker errors) to README.
- [ ] API Examples
  - **AnoushkaBansal**: Document 3-5 sample payloads (e.g., `POST /process-plans/`, `GET /plan-distribution/`) in README.
- [ ] Research Paper Support
  - **Nishita-Shewale**: Draft initial `cot_research.md` with CoT experiment setup, hypotheses, and early results.

## 8. UI Development
- [ ] Streamlit UI
  - **Nishita-Shewale**: Finalize Streamlit app in Docker, implement patient input form with validation.
  - **AnoushkaBansal**: Connect Streamlit to FastAPI endpoints (e.g., `POST /patients/`), ensure UI reflects API responses, test responsiveness.

## 9. Deployment
- [ ] Production Server
  - **Nishita-Shewale**: Configure Gunicorn + Uvicorn in `docker-compose.prod.yml`, test with 10 concurrent requests.
- [ ] CI/CD
  - **AnoushkaBansal**: Set up GitHub Actions workflow (lint, test, deploy), ensure all tests pass before deployment.

## 10. Enhancements
- [ ] Authentication
  - **AnoushkaBansal**: Implement JWT-based authentication for API endpoints, secure `POST /patients/` and `/process-plans/`.
- [ ] Scalability
  - **Nishita-Shewale**: Add Redis caching for frequent plan queries (e.g., `GET /insurance-plans/`), measure performance gains.
