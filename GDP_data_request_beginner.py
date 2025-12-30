import time
import requests
import pandas as pd

from country_code_convert import get_oecd_countries_iso3


# -----------------------------
# Step 0) Basic settings
# -----------------------------
BASE_URL = "https://api.worldbank.org/v2"

# GDP per capita (current US$)
INDICATOR = "NY.GDP.PCAP.CD"

YEAR = 2024


# ---------------------------------------------------------
# Step 1) Fetch data for ONE country (very explicit version)
# ---------------------------------------------------------
def fetch_indicator_for_country_year_basic(session, iso3, indicator, year):
    """
    Fetch ONE indicator value for ONE country for ONE year.
    Returns:
      - float number if found
      - None if missing
    """

    # 1) Build the URL (no f-string)
    url = BASE_URL + "/country/" + iso3 + "/indicator/" + indicator

    # 2) Build the query parameters (no dict literal shortcut)
    params = {}
    params["format"] = "json"
    params["date"] = str(year) + ":" + str(year)   # only one year
    params["per_page"] = 100
    params["page"] = 1

    # 3) Send request
    response = session.get(url, params=params, timeout=20)

    # 4) If request failed (404, 500, etc.), raise an error
    response.raise_for_status()

    # 5) Convert JSON response into Python data
    data = response.json()

    # 6) Validate response structure carefully (expanded checks)
    if type(data) != list:
        return None

    if len(data) < 2:
        return None

    # data[1] should be the rows list
    if data[1] is None:
        return None

    if len(data[1]) == 0:
        return None

    rows = data[1]

    # 7) Find the row where the year matches
    for row in rows:
        row_year = row.get("date")

        # World Bank year comes as a string, so compare as strings
        if row_year == str(year):
            value = row.get("value")

            # 8) value might be None
            if value is None:
                return None
            else:
                return float(value)

    # 9) If we didn't find a matching year row
    return None


# --------------------------------------------------------------------
# Step 2) Loop OECD countries and collect 2024 data (beginner version)
# --------------------------------------------------------------------
def fetch_oecd_indicator_2024_basic(oecd_countries):
    """
    Loop over OECD countries, request indicator value for YEAR,
    and return a DataFrame.
    """

    # 1) Create a session once (more efficient than requests.get repeatedly)
    session = requests.Session()

    # 2) We'll store results in a normal Python list
    results = []

    for country in oecd_countries:
        name = country["name"]
        iso3 = country["iso3"]

        # We'll build one result row as a dictionary
        result_row = {}
        result_row["country"] = name
        result_row["iso3"] = iso3
        result_row["year"] = YEAR

        try:
            value = fetch_indicator_for_country_year_basic(session, iso3, INDICATOR, YEAR)

            result_row["value"] = value

            if value is None:
                result_row["status"] = "missing_value"
            else:
                result_row["status"] = "ok"

        except requests.HTTPError as e:
            result_row["value"] = None
            result_row["status"] = "http_error: " + str(e)

        except requests.RequestException as e:
            result_row["value"] = None
            result_row["status"] = "request_error: " + str(e)

        except Exception as e:
            result_row["value"] = None
            result_row["status"] = "unexpected_error: " + str(e)

        # Add row to results list
        results.append(result_row)

        # Polite delay
        time.sleep(0.15)

    # Convert list of dictionaries into a DataFrame
    df = pd.DataFrame(results)
    return df


# --------------------------------------------------------------------
# Step 3) Sort + print summary + save CSV (beginner version)
# --------------------------------------------------------------------
def finalize_and_save_basic(df, filename):
    """
    Sort by value (descending), print summary, save to CSV.
    """

    # Sort (missing values go to bottom)
    df_sorted = df.sort_values(by="value", ascending=False, na_position="last")
    df_sorted = df_sorted.reset_index(drop=True)

    # Print top 10
    print("\n--- Top 10 (by value) ---")
    print(df_sorted.head(10).to_string(index=False))

    # Print missing/errors
    print("\n--- Missing / Errors ---")
    df_errors = df_sorted[df_sorted["status"] != "ok"]
    print(df_errors[["country", "iso3", "status"]].to_string(index=False))

    # Save to CSV
    df_sorted.to_csv(filename, index=False)
    print("\nSaved CSV:", filename)


# -----------------------------
# Main program entry point
# -----------------------------
if __name__ == "__main__":
    # 1) Load OECD countries from your conversion module
    oecd_countries = get_oecd_countries_iso3()

    # 2) Print sanity checks
    print("OECD countries loaded:", len(oecd_countries))
    print("Sample:", oecd_countries[0:3])

    # 3) Fetch data
    df = fetch_oecd_indicator_2024_basic(oecd_countries)

    # 4) Save results
    finalize_and_save_basic(df, "oecd_gdp_per_capita_2024.csv")