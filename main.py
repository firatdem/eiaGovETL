from extraction_service.eia_ingestion_service import fetch_eia_data
from transform_service.clean_data import transform_latest_json
from snowflake_load_service.snowflake_load import upload_to_snowflake


def run_pipeline():
    if not fetch_eia_data():
        print("❌ Extraction failed")
        return
    if not transform_latest_json():
        print("❌ Transformation failed")
        return
    if not upload_to_snowflake():
        print("❌ Load to Snowflake failed")
        return
    print("✅ Pipeline completed successfully!")


if __name__ == "__main__":
    run_pipeline()
