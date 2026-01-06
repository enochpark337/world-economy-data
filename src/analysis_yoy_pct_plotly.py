import pandas as pd
import plotly.express as px

INPUT_CSV = "data/oecd_6_indicators_2020_2024_wide.csv"

# 바꾸면 다른 지표도 동일하게 분석 가능
METRIC = "gdp_per_capita_usd"   # 예: "gov_debt_pct_gdp", "inflation_cpi_pct"
COUNTRY_ISO3 = "KOR"            # 보고 싶은 나라 (예: "USA", "JPN", "AUS")

START_YEAR = 2020
END_YEAR = 2024


def main():
    # -------------------------
    # Step 1) Load
    # -------------------------
    df = pd.read_csv(INPUT_CSV)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    needed = {"country", "iso3", "year", METRIC}
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in wide CSV: {missing}")

    df = df[["country", "iso3", "year", METRIC]].dropna()
    df = df[(df["year"] >= START_YEAR) & (df["year"] <= END_YEAR)]
    df = df.sort_values(["iso3", "year"]).reset_index(drop=True)

    # -------------------------
    # Step 2) YoY % change per country
    # pct_change() = (current - previous) / previous
    # -------------------------
    df["yoy_pct"] = df.groupby("iso3")[METRIC].pct_change() * 100

    # -------------------------
    # Chart A) Single country line (YoY %)
    # -------------------------
    df_country = df[df["iso3"] == COUNTRY_ISO3].copy()

    if df_country.empty:
        raise ValueError(f"No data found for iso3={COUNTRY_ISO3}")

    country_name = df_country["country"].iloc[0]

    # 첫 해(2020)는 비교 대상이 없어서 yoy_pct가 NaN인 게 정상
    df_country_plot = df_country.dropna(subset=["yoy_pct"]).copy()

    fig1 = px.line(
        df_country_plot,
        x="year",
        y="yoy_pct",
        markers=True,
        title=f"{country_name} ({COUNTRY_ISO3}) — YoY % Change of {METRIC} ({START_YEAR}–{END_YEAR})",
        labels={"year": "Year", "yoy_pct": "YoY % change"},
    )
    fig1.update_xaxes(tickmode="linear", tick0=START_YEAR + 1, dtick=1)
    fig1.show()

    # -------------------------
    # Chart B) Top 10 movers in latest year (e.g., 2024 YoY %)
    # -------------------------
    latest_year = END_YEAR
    df_latest = df[df["year"] == latest_year].dropna(subset=["yoy_pct"]).copy()

    # TOP 10 (YoY % 증가율이 가장 큰 나라)
    df_top = df_latest.sort_values("yoy_pct", ascending=False).head(10).sort_values("yoy_pct", ascending=True)

    fig2 = px.bar(
        df_top,
        x="yoy_pct",
        y="country",
        orientation="h",
        title=f"Top 10 OECD Countries — YoY % Change of {METRIC} in {latest_year}",
        labels={"yoy_pct": "YoY % change", "country": "Country"},
        text="yoy_pct",
        hover_data=["iso3", "year"],
    )
    fig2.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig2.update_layout(margin=dict(l=140, r=40, t=60, b=40))
    fig2.show()


if __name__ == "__main__":
    main()