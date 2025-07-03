from fastapi import FastAPI
from snowflake.connector import connect
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/data")
def get_data():
    conn = connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )
    cur = conn.cursor()
    cur.execute("SELECT region, datetime, usage_mw FROM energy_usage ORDER BY datetime DESC LIMIT 100")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return [{"region": r[0], "datetime": r[1], "usage_mw": r[2]} for r in results]
