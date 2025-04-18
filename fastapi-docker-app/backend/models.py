# models.py
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Enum, ARRAY
from database import Base
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import os
import enum

Base = declarative_base()


# Enums for controlled values
class PhysicalActivityLevel(str, enum.Enum):
    sedentary = "sedentary"
    moderate = "moderate"
    active = "active"

class BudgetCategory(str, enum.Enum):
    bronze = "Bronze"
    silver = "Silver"
    gold = "Gold"
    platinum = "Platinum"

# Patient Model
class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    state = Column(String, nullable=False)
    occupation = Column(String, nullable=True)
    smoking_status = Column(Boolean, default=False)  # Boolean field for Yes/No
    physical_activity_level = Column(Enum(PhysicalActivityLevel), nullable=False)  # Enum for controlled options
    medical_conditions = Column(ARRAY(String), nullable=True)  # List of conditions
    travel_coverage_needed = Column(Boolean, default=False)  # Boolean field for Yes/No
    family_coverage = Column(Boolean, default=False)  # Boolean field for Yes/No
    budget_category = Column(Enum(BudgetCategory), nullable=True)  # Enum for budget categories
    has_offspring = Column(Boolean)  # New Field
    is_married = Column(Boolean) 

csv_path = os.path.join(os.path.dirname(__file__), "cleaned_plans_data.csv")

if not os.path.exists("generated_model.py"):
    def generate_columns(dataframe):
        column_map = {
            "int64": Integer,
            "float64": Float,
            "bool": Boolean,
            "datetime64[ns]": Date,
            "object": String,
        }

        columns = {
            "__tablename__": "insurance_plans",
            "id": Column(Integer, primary_key=True, index=True)
        }

        for column_name, dtype in zip(dataframe.columns, dataframe.dtypes):
            if column_name.lower() != "id":  # Skip ID column if it exists
                sqlalchemy_type = column_map.get(str(dtype), String)
                columns[column_name] = Column(sqlalchemy_type)

        return type("InsurancePlan", (Base,), columns)

    # Load the cleaned DataFrame
    df = pd.read_csv(csv_path)  # Path to your dataset
    InsurancePlan = generate_columns(df)

    # Save the generated model to a file
    with open("generated_model.py", "w") as f:
        f.write(f"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from database import Base

class InsurancePlan(Base):
    __tablename__ = "insurance_plans"
    id = Column(Integer, primary_key=True, index=True)
""")
        for column_name, dtype in zip(df.columns, df.dtypes):
            if column_name.lower() != "id":
                column_type = {
                    "int64": "Integer",
                    "float64": "Float",
                    "bool": "Boolean",
                    "datetime64[ns]": "Date",
                    "object": "String",
                }.get(str(dtype), "String")
                f.write(f"    {column_name} = Column({column_type})\n")

# Import the generated model
from generated_model import InsurancePlan