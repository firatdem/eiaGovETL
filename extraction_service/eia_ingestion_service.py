# eia_ingestion_service.py

import requests
import os
import json
from datetime import datetime
from pathlib import Path
from config import DATA_DIR
from dotenv import load_dotenv
load_dotenv()

# EIA API config
EIA_API_KEY = os.getenv("EIA_API_KEY") or "your_api_key_here"
EIA_ENDPOINT = "https://api.eia.gov/v2/electricity/rto/daily-region-sub-ba-data/data/"

# Optional: customize these params per your use case
EIA_PARAMS = {
    "api_key": EIA_API_KEY,
    "frequency": "daily",
    "data[0]": "value",
    "sort[0][column]": "period",
    "sort[0][direction]": "desc",
    "offset": 0,
    "length": 5000
}

def sanitize_filename(name: str) -> str:
    """Sanitize and timestamp filenames."""
    base = name.replace(" ", "_").replace("/", "-")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{timestamp}_{base}.json"

def save_json(data: dict, filename: str) -> str:
    """Save a JSON payload to file with sanitized name."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return str(filepath)

def fetch_eia_data():
    """Pull data from EIA API and save locally."""
    try:
        print("Fetching EIA data...")
        response = requests.get(EIA_ENDPOINT, params=EIA_PARAMS)
        response.raise_for_status()
        payload = response.json()

        # Save locally
        filename = sanitize_filename("eia_hourly_data")
        path = save_json(payload, filename)

        print(f"✅ Data saved to {path}")
        return path

    except Exception as e:
        print(f"❌ Failed to fetch EIA data: {e}")
        return None

if __name__ == "__main__":
    fetch_eia_data()
