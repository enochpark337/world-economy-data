import time
import requests
import pandas as pd

from country_code_convert import get_oecd_countries_iso3

BASE_URL = "https://api.worldbank.org/v2"
YEAR = 2024

# ✅ 6개 지표: "CSV 컬럼명" -> "World Bank indicator code"
INDICATORS = {
    "gdp_per_capita_usd": "NY.GDP.PCAP.CD",
    "gdp_growth_pct": "NY.GDP.MKTP.KD.ZG",
    "unemployment_pct": "SL.UEM.TOTL.ZS",
    "inflation_cpi_pct": "FP.CPI.TOTL.ZG",
    "gov_debt_pct_gdp": "GC.DOD.TOTL.GD.ZS",
    "current_account_pct_gdp": "BN.CAB.XOKA.GD.ZS",
}

def fetch_value_for_country_year(session, iso3, indicator_code, year, timeout_sec=20):
    """
    한 국가(iso3), 한 지표(indicator_code), 한 연도(year)의 값(value)을 가져온다.
    반환:
      - float (값이 있으면)
      - None (값이 없으면)
    """
    url = BASE_URL + "/country/" + iso3 + "/indicator/" + indicator_code

    params = {}
    params["format"] = "json"
    params["date"] = str(year) + ":" + str(year)  # 2024:2024
    params["per_page"] = 100
    params["page"] = 1

    resp = session.get(url, params=params, timeout=timeout_sec)
    resp.raise_for_status()

    data = resp.json()

    # World Bank 응답 기본 구조: [meta, rows]
    if type(data) != list:
        return None
    if len(data) < 2:
        return None
    if data[1] is None:
        return None
    if len(data[1]) == 0:
        return None

    rows = data[1]

    # 해당 연도 row 찾기
    for row in rows:
        if str(row.get("date")) == str(year):
            value = row.get("value")
            if value is None:
                return None
            return float(value)

    return None


def fetch_oecd_6_indicators(year=YEAR, sleep_sec=0.15):
    """
    OECD 국가 전체에 대해 6개 지표를 한 번에 수집해서 DataFrame으로 반환.
    결과는 wide 형태:
      country, iso3, year, (6 indicators...)
    """
    oecd_countries = get_oecd_countries_iso3()
    session = requests.Session()

    results = []

    for country in oecd_countries:
        name = country["name"]
        iso3 = country["iso3"]

        # ✅ 한 국가(row) 만들기
        row = {}
        row["country"] = name
        row["iso3"] = iso3
        row["year"] = year

        # ✅ 지표 6개를 돌면서 값 채우기
        for col_name in INDICATORS:
            indicator_code = INDICATORS[col_name]

            try:
                value = fetch_value_for_country_year(
                    session=session,
                    iso3=iso3,
                    indicator_code=indicator_code,
                    year=year,
                )
                row[col_name] = value
            except Exception as e:
                # 실패해도 전체 파이프라인이 멈추지 않도록 처리
                row[col_name] = None
                row[col_name + "_error"] = str(e)

            time.sleep(sleep_sec)

        results.append(row)

    df = pd.DataFrame(results)
    return df


def save_csv(df, filename):
    df.to_csv(filename, index=False)
    print("Saved:", filename)


if __name__ == "__main__":
    df = fetch_oecd_6_indicators(year=2024, sleep_sec=0.12)

    # 간단 검증: 결측치 개수 확인
    print("\n[Missing counts]")
    for col in INDICATORS:
        print(col, "missing =", df[col].isna().sum())

    save_csv(df, "oecd_6_indicators_2024.csv")

    # 상위 5개 미리 보기 (gdp_per_capita 기준)
    df_sorted = df.sort_values(by="gdp_per_capita_usd", ascending=False, na_position="last")
    print("\n[Top 5 by GDP per capita]")
    print(df_sorted[["country", "iso3", "gdp_per_capita_usd"]].head(5).to_string(index=False))