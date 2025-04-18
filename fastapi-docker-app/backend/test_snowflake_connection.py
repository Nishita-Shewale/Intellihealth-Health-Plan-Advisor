import snowflake.connector

# Explicitly define the Snowflake credentials here
conn = snowflake.connector.connect(
    user='BISON',
    password='Snowflakepassword123',
    account='pdb57018',  # Correct Snowflake account identifier
    warehouse='HEALTHCARE',
    database='HEALTHCARE_INSURANCE_DB',
    schema='PLAN_SCHEMA',
    role='TRAINING_ROLE',  # If you want to specify a role explicitly
)

# Test the connection by executing a simple query
try:
    cursor = conn.cursor()
    cursor.execute("SELECT CURRENT_VERSION()")
    version = cursor.fetchone()
    print(f"Successfully connected to Snowflake. Version: {version[0]}")
except Exception as e:
    print(f"Failed to connect to Snowflake: {e}")
finally:
    cursor.close()
    conn.close()
