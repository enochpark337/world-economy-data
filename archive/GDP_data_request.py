import time
from typing import Optional, Dict, List

import requests
import pandas as pd

# ✅ This must match your filename and exported function name
# Example expected output:
# [{"name": "Lithuania", "iso3": "LTU"}, {"name": "United States", "iso3": "USA"}, ...]
from country_code_convert import get_oecd_countries_iso3

# -----------------------------
# Step 0) Constants (Base setup)
# -----------------------------
BASE_URL = "https://api.worldbank.org/v2"

# ✅ GDP per capita (current US$) — best for cross-country comparison
INDICATOR = "NY.GDP.PCAP.CD"

# If you want total GDP instead, use:
# INDICATOR = "NY.GDP.MKTP.CD"

YEAR = 2024  # ✅ Only fetch 2024


# ---------------------------------------------------------
# Step 1) Basic: build a URL + call the API for ONE country
# ---------------------------------------------------------
def fetch_indicator_for_country_year(
    session: requests.Session,
    iso3: str,
    indicator: str,
    year: int,
    timeout_sec: int = 20,
) -> Optional[float]:
    """
    Fetch a single indicator value for a single country for a single year (e.g., 2024).

    Returns:
      - float value if available
      - None if missing/empty
    """
    url = f"{BASE_URL}/country/{iso3}/indicator/{indicator}"
    params = {
        "format": "json",
        "date": f"{year}:{year}",   # ✅ only one year
        "per_page": 100,
        "page": 1
    }

    resp = session.get(url, params=params, timeout=timeout_sec)
    resp.raise_for_status()
    data = resp.json()

    # World Bank response is usually: [meta, rows]
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        return None

    rows = data[1]

    # Find the row for that year (should be one row, but we guard anyway)
    for row in rows:
        if str(row.get("date")) == str(year):
            value = row.get("value")  # can be None
            return float(value) if value is not None else None

    return None


# --------------------------------------------------------------------
# Step 2) Intermediate: loop OECD countries and collect 2024 values
# --------------------------------------------------------------------
def fetch_oecd_indicator_2024(oecd_countries: List[Dict[str, str]]) -> pd.DataFrame:
    """
    For each OECD country (name, iso3), fetch indicator for 2024 only.
    Returns a DataFrame.
    """
    session = requests.Session()
    results = []

    for c in oecd_countries:
        name = c["name"]
        iso3 = c["iso3"]

        try:
            value = fetch_indicator_for_country_year(
                session=session,
                iso3=iso3,
                indicator=INDICATOR,
                year=YEAR,
            )

            results.append({
                "country": name,
                "iso3": iso3,
                "year": YEAR,
                "value": value,
                "status": "ok" if value is not None else "missing_value"
            })

        except requests.HTTPError as e:
            results.append({
                "country": name,
                "iso3": iso3,
                "year": YEAR,
                "value": None,
                "status": f"http_error: {e}"
            })
        except requests.RequestException as e:
            results.append({
                "country": name,
                "iso3": iso3,
                "year": YEAR,
                "value": None,
                "status": f"request_error: {e}"
            })
        except Exception as e:
            results.append({
                "country": name,
                "iso3": iso3,
                "year": YEAR,
                "value": None,
                "status": f"unexpected_error: {e}"
            })

        # polite sleep helps avoid transient throttling issues
        time.sleep(0.15)

    df = pd.DataFrame(results)
    return df


# --------------------------------------------------------------------
# Step 3) More complete: sort + save + show summary
# --------------------------------------------------------------------
def finalize_and_save(df: pd.DataFrame, filename: str = "oecd_indicator_2024.csv") -> None:
    """
    - Sort descending by value
    - Print quick summary
    - Save to CSV
    """
    # Sort with missing values at bottom
    df_sorted = df.sort_values(by="value", ascending=False, na_position="last").reset_index(drop=True)

    print("\n--- Top 10 (by value) ---")
    print(df_sorted.head(10).to_string(index=False))

    print("\n--- Missing / Errors ---")
    print(df_sorted[df_sorted["status"] != "ok"][["country", "iso3", "status"]].to_string(index=False))

    df_sorted.to_csv(filename, index=False)
    print(f"\nSaved CSV: {filename}")


# -----------------------------
# Main: run the pipeline
# -----------------------------
if __name__ == "__main__":
    # ✅ Step A: Import OECD country codes from your conversion module
    oecd_countries = get_oecd_countries_iso3()

    # Quick sanity check
    print(f"OECD countries loaded: {len(oecd_countries)}")
    print("Sample:", oecd_countries[:3])

    # ✅ Step B: Fetch OECD indicator values for 2024 only
    df = fetch_oecd_indicator_2024(oecd_countries)

    # ✅ Step C: Finalize (sort/print/save)
    finalize_and_save(df, filename="oecd_gdp_per_capita_2024.csv")