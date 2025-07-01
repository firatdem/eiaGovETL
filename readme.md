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
 ├── config.py                  # Central config (e.g., data path)
 ├── eia_ingestion_service.py  # Ingestion script
 ├── .env                      # Stores your EIA_API_KEY (not committed)
 └── data/                     # Where the raw EIA JSON gets saved
```

---

## Setup Instructions

1. **Install dependencies** (in a virtual environment):

```
pip install requests python-dotenv
```

2. **Create `.env` file**:

```
EIA_API_KEY=your_real_key_here
```

3. **Run the ingestion service**:

```
python eia_ingestion_service.py
```

---

## Example Output

```
✅ Data saved to data/20250701_133219_eia_hourly_data.json
```
