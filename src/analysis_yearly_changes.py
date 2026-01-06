import pandas as pd

INPUT_CSV = "data/oecd_6_indicators_2020_2024_wide.csv"
OUTPUT_CSV = "data/oecd_changes_2020_to_2024.csv"

START_YEAR = 2020
END_YEAR = 2024

# 분석할 지표 목록 (너의 6개 지표)
METRICS = [
    "gdp_per_capita_usd",
    "gdp_growth_pct",
    "unemployment_pct",
    "inflation_cpi_pct",
    "gov_debt_pct_gdp",
    "current_account_pct_gdp",
]


def main():
    # -------------------------
    # Step 1) Load data
    # -------------------------
    df = pd.read_csv(INPUT_CSV)

    # 안전장치: year가 숫자가 아닐 수 있으니 숫자로 변환
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # -------------------------
    # Step 2) Split into start and end year
    # -------------------------
    df_start = df[df["year"] == START_YEAR].copy()
    df_end = df[df["year"] == END_YEAR].copy()

    # -------------------------
    # Step 3) Merge (join) by country + iso3
    # -------------------------
    # suffixes로 컬럼 이름에 _2020, _2024 를 붙여서 구분
    df_merged = pd.merge(
        df_start,
        df_end,
        on=["country", "iso3"],
        how="inner",
        suffixes=(f"_{START_YEAR}", f"_{END_YEAR}")
    )

    # -------------------------
    # Step 4) Compute changes (delta = 2024 - 2020)
    # -------------------------
    for m in METRICS:
        start_col = f"{m}_{START_YEAR}"
        end_col = f"{m}_{END_YEAR}"

        # 두 컬럼이 존재할 때만 계산
        if start_col in df_merged.columns and end_col in df_merged.columns:
            df_merged[f"{m}_change"] = df_merged[end_col] - df_merged[start_col]

    # -------------------------
    # Step 5) Keep only useful columns (clean output)
    # -------------------------
    keep_cols = ["country", "iso3"]
    for m in METRICS:
        keep_cols.append(f"{m}_{START_YEAR}")
        keep_cols.append(f"{m}_{END_YEAR}")
        keep_cols.append(f"{m}_change")

    # 존재하는 컬럼만 유지 (혹시 결측/누락 대비)
    keep_cols = [c for c in keep_cols if c in df_merged.columns]
    out = df_merged[keep_cols].copy()

    # -------------------------
    # Step 6) Quick rankings (print top/bottom)
    # -------------------------
    print("\n==============================")
    print(f"Changes from {START_YEAR} to {END_YEAR} (delta = {END_YEAR} - {START_YEAR})")
    print("==============================\n")

    def show_ranking(change_col, title, top_n=10):
        if change_col not in out.columns:
            print(f"[SKIP] Missing column: {change_col}")
            return

        tmp = out[["country", "iso3", change_col]].dropna()

        print(f"\n--- {title}: TOP {top_n} ---")
        print(tmp.sort_values(change_col, ascending=False).head(top_n).to_string(index=False))

        print(f"\n--- {title}: BOTTOM {top_n} ---")
        print(tmp.sort_values(change_col, ascending=True).head(top_n).to_string(index=False))

    # “좋아짐/나빠짐” 해석이 직관적인 항목부터 보여주기
    show_ranking("gdp_per_capita_usd_change", "GDP per Capita change (USD)")
    show_ranking("gdp_growth_pct_change", "GDP Growth change (percentage points)")
    show_ranking("unemployment_pct_change", "Unemployment change (percentage points)")
    show_ranking("gov_debt_pct_gdp_change", "Gov Debt change (% of GDP points)")
    show_ranking("current_account_pct_gdp_change", "Current Account change (% of GDP points)")
    show_ranking("inflation_cpi_pct_change", "Inflation change (percentage points)")

    # -------------------------
    # Step 7) Save results
    # -------------------------
    out.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Saved: {OUTPUT_CSV}")
    print(f"Rows: {len(out)}")


if __name__ == "__main__":
    main()