from fastapi import FastAPI, Query
from snowflake.connector import connect
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/regions")
def get_regions():
    try:
        conn = connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            role=os.getenv("SNOWFLAKE_ROLE"),
        )
        cur = conn.cursor()
        cur.execute("USE DATABASE EIA_POWER_USAGE")
        cur.execute("USE SCHEMA TRANSFORMED_DATA")
        cur.execute("SELECT DISTINCT SUBBA_NAME FROM REGIONS_DIM")
        results = cur.fetchall()
        return [r[0] for r in results if r[0] is not None]
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


@app.get("/api/data")
def get_data(region: str = Query(None)):
    try:
        conn = connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            role=os.getenv("SNOWFLAKE_ROLE"),
        )
        cur = conn.cursor()
        cur.execute("USE DATABASE EIA_POWER_USAGE")
        cur.execute("USE SCHEMA TRANSFORMED_DATA")

        # Base query with optional WHERE clause
        query = '''
            SELECT r.SUBBA_NAME, u.TIMESTAMP, u.DEMAND_MWH
            FROM RAW_HOURLY_USAGE u
            JOIN REGIONS_DIM r ON u.SUB_REGION_CODE = r.SUB_REGION_CODE
        '''
        if region:
            query += f" WHERE r.SUBBA_NAME = %s"
            cur.execute(query + " ORDER BY u.TIMESTAMP DESC LIMIT 100", (region,))
        else:
            query += " ORDER BY u.TIMESTAMP DESC LIMIT 100"
            cur.execute(query)

        results = cur.fetchall()
        return [
            {"region": r[0], "datetime": r[1], "usage_mw": r[2]}
            for r in results
        ]
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass