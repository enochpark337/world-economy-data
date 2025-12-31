import pandas as pd

INPUT_PATH = "data/oecd_6_indicators_2020_2024_long.csv"
OUTPUT_PATH = "data/oecd_6_indicators_2020_2024_wide.csv"

def main():
    df_long = pd.read_csv(INPUT_PATH)

    # Long → Wide
    df_wide = (
        df_long
        .pivot(
            index=["country", "iso3", "year"],
            columns="indicator",
            values="value"
        )
        .reset_index()
    )

    # 컬럼 정렬 (가독성 + 일관성)
    ordered_columns = [
        "country",
        "iso3",
        "year",
        "gdp_per_capita_usd",
        "gdp_growth_pct",
        "unemployment_pct",
        "inflation_cpi_pct",
        "gov_debt_pct_gdp",
        "current_account_pct_gdp",
    ]

    # 존재하는 컬럼만 유지 (지표 누락 대비)
    ordered_columns = [c for c in ordered_columns if c in df_wide.columns]
    df_wide = df_wide[ordered_columns]

    df_wide.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Wide CSV generated: {OUTPUT_PATH}")
    print(f"Rows: {len(df_wide)}")

if __name__ == "__main__":
    main()
