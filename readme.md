# Step 1: Data Ingestion

This pipeline begins by pulling **hourly electricity demand data** from the [U.S. Energy Information Administration (EIA)](https://www.eia.gov/opendata/) using their open API.

## Source

We use the endpoint:

```
https://api.eia.gov/v2/electricity/rto/daily-region-sub-ba-data/data/
```

This endpoint provides **regional electricity demand** across the U.S., organized by **RTO/ISO (region)** and **balancing sub-region (subba)**.

---

## How It Works

1. **Authentication**
   Your EIA API key is stored securely in a `.env` file and loaded via Python.

2. **Dynamic Parameters**
   The ingestion service constructs API requests with options like:

   * Frequency (`daily`)
   * Data type (`value`)
   * Sorting (`descending by period`)
   * Pagination (`offset`, `length`)

3. **Request & Save**

   * The script sends a request to EIA's API
   * Parses the JSON payload
   * Saves it to `data/` directory with a timestamped filename

---

## Project Structure

```
eiaGovPipeline/
├── extraction_service/
│   ├── config.py                  # Ingestion config
│   └── eia_ingestion_service.py  # Ingestion script
├── data/                         # Where raw JSON gets saved
├── .env                          # Stores your EIA_API_KEY (not committed)
```

---

## Setup Instructions

1. **Install dependencies**:

```
pip install requests python-dotenv
```

2. **Create `.env` file**:

```
EIA_API_KEY=your_real_key_here
```

3. **Run the ingestion service**:

```
python extraction_service/eia_ingestion_service.py
```

---

## Example Output

```
✅ Data saved to data/20250701_133219_eia_hourly_data.json
```

---

# Step 2: Data Transformation

Once the raw JSON data is saved, we process it into a clean format for analytics or loading into a database.

## Goal

Transform hourly electricity demand readings into a structured table that maps:

- **Datetime**
- **Region code** (e.g., `ERCO`, `NYIS`)
- **Subregion** (if applicable)
- **Electricity demand value**

---

## How It Works

1. **Load JSON File**
   * The transform script reads the latest file in the `data/` directory

2. **Normalize Structure**
   * Uses `pandas.json_normalize` to flatten nested JSON
   * Extracts only the relevant columns: `period`, `region`, `subregion`, `value`

3. **Clean Data**
   * Converts timestamp strings to proper datetime format
   * Fills missing subregions with 'N/A'
   * Filters out rows with missing or null demand values

4. **Export to CSV**
   * Cleaned data is saved to `data/` with a new timestamped name

---

## File Structure

```
eiaGovPipeline/
├── transform_service/
│   ├── config_transform.py     # Paths for transform step
│   └── clean_data.py           # Main transformation logic
```

---

## Example Output

```
✅ Cleaned data saved to data/20250701_135037_transformed.csv
```

---

# Step 3: Load to Snowflake

The final step in the pipeline uploads the transformed electricity demand data into **Snowflake**, split into two normalized tables:

- `REGIONS_DIM`: stores region/subregion metadata
- `POWER_USAGE_FACT`: stores time-series demand values

---

## How It Works

1. **Environment Setup**

   The script reads Snowflake credentials from a `.env` file using `python-dotenv`. Required keys:

   ```
   SNOWFLAKE_USER=
   SNOWFLAKE_PASSWORD=
   SNOWFLAKE_ACCOUNT=
   SNOWFLAKE_WAREHOUSE=
   SNOWFLAKE_DATABASE=
   SNOWFLAKE_SCHEMA=
   ```

2. **Data Preparation**

   * Automatically locates the latest transformed CSV in `transformed_data/`
   * Renames columns for Snowflake compatibility
   * Splits data into:
     - `regions_dim` (dimension table)
     - `power_usage_fact` (fact table with `usage_id`)

3. **Normalization**

   * Resets index and uppercases all column names to match Snowflake naming conventions
   * Ensures `write_pandas()` can process the DataFrame

4. **Snowflake Upload**

   * Establishes connection via `snowflake.connector`
   * Uploads each table using `write_pandas()`
   * Tables are overwritten each run (`overwrite=True`)
   * (Optional) Table creation SQL is available in the script as commented-out code

---

## Dependencies

```bash
pip install pandas snowflake-connector-python "pyarrow<19.0.0" python-dotenv
```

> ⚠️ Make sure `pyarrow` is below version 19 to avoid compatibility issues with Snowflake’s pandas integration.

---

## File Structure

```
eiaGovPipeline/
├── snowflake_load_service/
│   └── snowflake_load.py       # Handles data upload to Snowflake
├── transformed_data/           # Contains cleaned CSVs ready for loading
```

---

## Example Output

```
📂 Loading file: transformed_data/20250701_135037_transformed.csv
✅ REGIONS_DIM uploaded: True 415 rows
✅ POWER_USAGE_FACT uploaded: True 5000 rows
```

---
