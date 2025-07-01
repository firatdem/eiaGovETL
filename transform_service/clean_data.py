# transform/clean_data.py

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from config import DATA_DIR, TRANSFORMED_DIR


def load_raw_json(file_path: Path) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def transform_eia_data(payload: dict) -> pd.DataFrame:
    """
    Flatten the nested EIA structure and extract relevant columns
    """
    records = payload.get("response", {}).get("data", [])
    if not records:
        raise ValueError("No data found in payload")

    df = pd.DataFrame(records)

    # Rename columns for clarity
    df.rename(columns={
        'period': 'timestamp',
        'value': 'demand_mwh',
        'region': 'region_code',
        'subba': 'sub_region_code'
    }, inplace=True)

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Drop any rows with missing demand values
    df.dropna(subset=['demand_mwh'], inplace=True)

    return df


def save_transformed_data(df: pd.DataFrame, original_file: Path) -> Path:
    """Save cleaned dataframe to CSV in transformed directory."""
    TRANSFORMED_DIR.mkdir(parents=True, exist_ok=True)
    name_part = original_file.stem.replace("eia_hourly_data", "transformed")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{name_part}.csv"
    path = TRANSFORMED_DIR / filename
    df.to_csv(path, index=False)
    return path


def transform_latest_json() -> Path:
    """Wrapper to run full transformation pipeline on the latest raw JSON."""
    try:
        latest_file = sorted(DATA_DIR.glob("*_eia_hourly_data.json"))[-1]
        raw = load_raw_json(latest_file)
        df = transform_eia_data(raw)
        path = save_transformed_data(df, latest_file)
        print(f"✅ Transformed data saved to {path}")
        return path
    except Exception as e:
        print(f"❌ Transformation failed: {e}")
        return None


if __name__ == "__main__":
    latest_file = sorted(DATA_DIR.glob("*_eia_hourly_data.json"))[-1]
    raw = load_raw_json(latest_file)
    df = transform_eia_data(raw)
    path = save_transformed_data(df, latest_file)
    print(f"✅ Transformed data saved to {path}")
