import snowflake.connector
import os
import re
from datetime import date
from pydantic import BaseModel
from typing import List, Dict

def get_snowflake_connection():
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE") 
    )
    return conn


def convert_to_pydantic_case(snake_str: str) -> str:
    """
    Converts UPPERCASE_SNAKE_CASE to PascalCase for Pydantic field matching.
    """
    components = re.split('_', snake_str.lower())
    return ''.join(x.title() for x in components)

def normalize_snowflake_data(
    raw_data: List[tuple], 
    columns: List[str], 
    pydantic_model: BaseModel,
    date_fields: List[str] = None
) -> List[BaseModel]:
    """
    Normalizes data fetched from Snowflake to match Pydantic models.

    Args:
    - raw_data: List of tuples fetched from Snowflake.
    - columns: List of column names from Snowflake.
    - pydantic_model: The Pydantic model to map data to.
    - date_fields: List of fields that need to be converted from date to ISO string.

    Returns:
    - List of Pydantic model instances.
    """

    # Step 1: Convert column names to match Pydantic fields
    normalized_columns = [convert_to_pydantic_case(col) for col in columns]
    pydantic_fields = pydantic_model.model_fields.keys()

    # Step 2: Map columns dynamically
    field_mapping = {
        col: next((field for field in pydantic_fields if field.lower() == norm_col.lower()), col)
        for col, norm_col in zip(columns, normalized_columns)
    }

    # Step 3: Process rows
    processed_data = []
    for row in raw_data:
        plan_dict = {field_mapping.get(col, col): value for col, value in zip(columns, row)}

        # Convert date fields to ISO format if necessary
        if date_fields:
            for date_field in date_fields:
                if date_field in plan_dict and isinstance(plan_dict[date_field], date):
                    plan_dict[date_field] = plan_dict[date_field].isoformat()

        # Step 4: Map to Pydantic
        try:
            processed_data.append(pydantic_model(**plan_dict))
        except Exception as e:
            print("Data Causing Error:", plan_dict)
            raise Exception(f"Error mapping data to Pydantic model: {e}")

    return processed_data
