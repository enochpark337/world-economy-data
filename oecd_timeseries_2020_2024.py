import time
import requests
import pandas as pd

from country_code_convert import get_oecd_countries_iso3

BASE_URL = "https://api.worldbank.org/v2"

START_YEAR = 2020
END_YEAR = 2024

# ✅ Phase 2에서 사용할 6개 지표
INDICATORS = {
    "gdp_per_capita_usd": "NY.GDP.PCAP.CD",
    "gdp_growth_pct": "NY.GDP.MKTP.KD.ZG",
    "unemployment_pct": "SL.UEM.TOTL.ZS",
    "inflation_cpi_pct": "FP.CPI.TOTL.ZG",
    "gov_debt_pct_gdp": "GC.DOD.TOTL.GD.ZS",
    "current_account_pct_gdp": "BN.CAB.XOKA.GD.ZS",
}


def fetch_timeseries_rows(session, iso3, indicator_code, start_year, end_year, timeout_sec=20):
    """
    World Bank에서 한 국가(iso3) + 한 지표(indicator_code)의
    start_year:end_year 범위 데이터를 받아 rows(list of dict)로 반환.
    """
    url = BASE_URL + "/country/" + iso3 + "/indicator/" + indicator_code

    params = {}
    params["format"] = "json"
    params["date"] = str(start_year) + ":" + str(end_year)
    params["per_page"] = 200
    params["page"] = 1

    resp = session.get(url, params=params, timeout=timeout_sec)
    resp.raise_for_status()

    data = resp.json()

    # 구조 검증: [meta, rows]
    if type(data) != list:
        return []
    if len(data) < 2:
        return []
    if data[1] is None:
        return []

    return data[1]


def build_long_rows(country_name, iso3, indicator_name, indicator_code, rows, start_year, end_year):
    """
    World Bank rows를 우리가 원하는 long format으로 변환:
    country, iso3, year, indicator, value
    """
    output = []

    for row in rows:
        year_str = row.get("date")
        value = row.get("value")

        # year가 없으면 skip
        if year_str is None:
            continue

        # 숫자 변환 가능한지 확인
        try:
            year = int(year_str)
        except ValueError:
            continue

        # 범위 밖이면 skip
        if year < start_year or year > end_year:
            continue

        # value가 None이면 그대로 None (결측치)
        if value is not None:
            value = float(value)

        output.append({
            "country": country_name,
            "iso3": iso3,
            "year": year,
            "indicator": indicator_name,       # 우리가 정한 컬럼명
            "indicator_code": indicator_code,  # World Bank 코드 (추적용)
            "value": value
        })

    return output


def fetch_oecd_timeseries_long(start_year=START_YEAR, end_year=END_YEAR, sleep_sec=0.12):
    """
    OECD 전체 국가에 대해 6개 지표의 2020–2024 데이터를 수집하여
    long format DataFrame을 반환.
    """
    oecd_countries = get_oecd_countries_iso3()
    session = requests.Session()

    all_rows = []

    for c in oecd_countries:
        country_name = c["name"]
        iso3 = c["iso3"]

        for indicator_name in INDICATORS:
            indicator_code = INDICATORS[indicator_name]

            try:
                rows = fetch_timeseries_rows(session, iso3, indicator_code, start_year, end_year)
                long_rows = build_long_rows(country_name, iso3, indicator_name, indicator_code, rows, start_year, end_year)
                all_rows.extend(long_rows)

            except Exception as e:
                # 실패 로그도 long format으로 남기면 나중에 디버깅이 쉬움
                all_rows.append({
                    "country": country_name,
                    "iso3": iso3,
                    "year": None,
                    "indicator": indicator_name,
                    "indicator_code": indicator_code,
                    "value": None,
                    "error": str(e)
                })

            time.sleep(sleep_sec)

    df = pd.DataFrame(all_rows)

    # 정렬(보기/검증용)
    df = df.sort_values(by=["country", "indicator", "year"], ascending=[True, True, True]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df_long = fetch_oecd_timeseries_long(START_YEAR, END_YEAR, sleep_sec=0.10)

    print("Rows:", len(df_long))
    print(df_long.head(20).to_string(index=False))

    # 결측치 개수(지표별)
    print("\n[Missing counts by indicator]")
    for ind in INDICATORS:
        missing = df_long[(df_long["indicator"] == ind) & (df_long["value"].isna())].shape[0]
        print(ind, "missing =", missing)

    df_long.to_csv("oecd_6_indicators_2020_2024_long.csv", index=False)
    print("\nSaved: oecd_6_indicators_2020_2024_long.csv")