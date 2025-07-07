import os
import requests
import pandas as pd
from datetime import datetime, timedelta

# === CONFIG ===
API_URL = "https://bconomy.net/api/data"
API_KEY = os.getenv("bconomyapikey")
EXCEL_FILENAME = "bconomy.xlsx"

def to_utc_iso(timestamp_ms=None):
    """Return current or given timestamp in ISO format (UTC+0)."""
    if timestamp_ms:
        dt = datetime.utcfromtimestamp(timestamp_ms / 1000)
    else:
        dt = datetime.utcnow()
    return dt.isoformat(timespec='minutes')

def fetch_data():
    """Fetch data from API."""
    if not API_KEY:
        raise ValueError("API key not found in environment variables (expected key: 'apikey')")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
    }
    payload = {"type": "marketPreview"}

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def update_excel(api_data, timestamp):
    """Append new timestamped column using FlatId match."""
    # Load existing Excel file
    if not os.path.exists(EXCEL_FILENAME):
        raise FileNotFoundError(f"{EXCEL_FILENAME} not found. Please create it with a 'FlatId' column first.")

    df = pd.read_excel(EXCEL_FILENAME)

    if "FlatId" not in df.columns:
        raise ValueError("'FlatId' column not found in the Excel file.")

    # Create a Series mapping FlatId -> value
    api_series = pd.Series(api_data)

    # Create a new column by matching FlatId to API values
    df[timestamp] = df["FlatId"].map(api_series)

    # Save updated file
    df.to_excel(EXCEL_FILENAME, index=False)
    print(f"✅ Updated Excel with timestamp column: {timestamp}")

def main():
    try:
        parsed = fetch_data()
        if "data" not in parsed or not isinstance(parsed["data"], dict):
            raise ValueError("Unexpected or missing 'data' field in response.")

        data = parsed["data"]
        timestamp = to_utc_iso(parsed.get("lastUpdated"))
        update_excel(data, timestamp)

    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()