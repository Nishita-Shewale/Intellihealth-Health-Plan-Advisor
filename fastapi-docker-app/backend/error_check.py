from sqlalchemy import inspect
from generated_model import InsurancePlan
from schemas import DynamicInsurancePlan
import json

# Inspecting the database model
model_columns = [column.name for column in InsurancePlan.__table__.columns]
model_column_types = [str(column.type) for column in InsurancePlan.__table__.columns]

# Retrieving schema details
schema_json = DynamicInsurancePlan.schema_json()
schema_details = json.loads(schema_json)

# Displaying results
print("Database Model Columns and Types:")
for column, column_type in zip(model_columns, model_column_types):
    print(f"Column: {column}, Type: {column_type}")

print("\nDynamicInsurancePlan Pydantic Schema Fields:")
for field_name, field_info in schema_details["properties"].items():
    print(f"Field: {field_name}, Type: {field_info.get('type')}")

# Save the outputs to a file for detailed comparison (optional)
with open("model_schema_comparison.txt", "w") as file:
    file.write("Database Model Columns and Types:\n")
    for column, column_type in zip(model_columns, model_column_types):
        file.write(f"Column: {column}, Type: {column_type}\n")

    file.write("\nDynamicInsurancePlan Pydantic Schema Fields:\n")
    for field_name, field_info in schema_details["properties"].items():
        file.write(f"Field: {field_name}, Type: {field_info.get('type')}\n")
