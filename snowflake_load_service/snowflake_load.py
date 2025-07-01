import os
import glob
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from config import TRANSFORMED_DIR
from dotenv import load_dotenv

load_dotenv()

# Step 1: Locate most recent CSV in transformed_data/
snowflake.connector.pandas_tools.pandas = pd  # Ensures snowflake sees pandas

csv_files = glob.glob(str(TRANSFORMED_DIR / "*.csv"))
latest_file = max(csv_files, key=os.path.getctime)

print(f"📂 Loading file: {latest_file}")
df = pd.read_csv(latest_file)

# Normalize column names to match Snowflake schema
df = df.rename(columns={
    'subba-name': 'subba_name',
    'parent-name': 'parent_name',
    'value-units': 'value_units'
})

# Step 2: Split into dimension and fact tables
regions_dim = df[['sub_region_code', 'subba_name', 'parent', 'parent_name', 'timezone']].drop_duplicates()
power_usage_fact = df[['timestamp', 'demand_mwh', 'value_units', 'sub_region_code']].copy()
power_usage_fact.insert(0, 'usage_id', range(1, len(power_usage_fact) + 1))

# 🔧 Normalize DataFrame index and column names
regions_dim = regions_dim.reset_index(drop=True)
power_usage_fact = power_usage_fact.reset_index(drop=True)

regions_dim.columns = [col.upper() for col in regions_dim.columns]
power_usage_fact.columns = [col.upper() for col in power_usage_fact.columns]

# Step 3: Connect to Snowflake using env vars
conn = snowflake.connector.connect(
    user=os.getenv('SNOWFLAKE_USER'),
    password=os.getenv('SNOWFLAKE_PASSWORD'),
    account=os.getenv('SNOWFLAKE_ACCOUNT'),
    warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
    database=os.getenv('SNOWFLAKE_DATABASE'),
    schema=os.getenv('SNOWFLAKE_SCHEMA')
)

# # Optional: Create tables if they don't exist
# with conn.cursor() as cur:
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS REGIONS_DIM (
#             SUB_REGION_CODE STRING,
#             SUBBA_NAME STRING,
#             PARENT STRING,
#             PARENT_NAME STRING,
#             TIMEZONE STRING
#         )
#     """)
#     cur.execute("""
#         CREATE TABLE IF NOT EXISTS POWER_USAGE_FACT (
#             USAGE_ID INT,
#             TIMESTAMP TIMESTAMP_NTZ,
#             DEMAND_MWH FLOAT,
#             VALUE_UNITS STRING,
#             SUB_REGION_CODE STRING
#         )
#     """)
#     print("📌 Ensured REGIONS_DIM and POWER_USAGE_FACT tables exist")

# Step 4: Upload to Snowflake tables
success_1, _, nrows_1, _ = write_pandas(conn, regions_dim, 'REGIONS_DIM', overwrite=True)
success_2, _, nrows_2, _ = write_pandas(conn, power_usage_fact, 'POWER_USAGE_FACT', overwrite=True)

print("✅ REGIONS_DIM uploaded:", success_1, f"{nrows_1} rows")
print("✅ POWER_USAGE_FACT uploaded:", success_2, f"{nrows_2} rows")

conn.close()
