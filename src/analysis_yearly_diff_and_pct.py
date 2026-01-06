import pandas as pd

# -------------------------
# Config
# -------------------------
INPUT_CSV = "data/oecd_6_indicators_2020_2024_wide.csv"
OUTPUT_CSV = "data/oecd_yearly_diff_pct.csv"

METRIC = "gdp_per_capita_usd"   # 다른 지표로 바꿔도 됨
START_YEAR = 2020
END_YEAR = 2024


def main():
    # -------------------------
    # Step 1) Load data
    # -------------------------
    df = pd.read_csv(INPUT_CSV)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # 필요한 컬럼만
    df = df[["country", "iso3", "year", METRIC]].dropna()

    # -------------------------
    # Step 2) Sort properly
    # -------------------------
    df = df.sort_values(["country", "year"]).reset_index(drop=True)

    # -------------------------
    # Step 3) Compute yearly difference
    # -------------------------
    # diff(): 이전 행과의 차이
    df["yearly_diff"] = df.groupby("iso3")[METRIC].diff()

    # -------------------------
    # Step 4) Compute yearly % increase
    # pct_change(): (현재-이전)/이전
    df["yearly_pct_change"] = df.groupby("iso3")[METRIC].pct_change() * 100

    # -------------------------
    # Step 5) Keep analysis range
    # -------------------------
    df = df[(df["year"] >= START_YEAR) & (df["year"] <= END_YEAR)]

    # -------------------------
    # Step 6) Round for readability
    # -------------------------
    df["yearly_diff"] = df["yearly_diff"].round(2)
    df["yearly_pct_change"] = df["yearly_pct_change"].round(2)

    # -------------------------
    # Step 7) Save result
    # -------------------------
    df.to_csv(OUTPUT_CSV, index=False)

    print("✅ Yearly difference & percentage change calculated")
    print(f"Saved: {OUTPUT_CSV}")

    # -------------------------
    # Step 8) Show example (Korea if exists)
    # -------------------------
    example = df[df["iso3"] == "KOR"]
    if not example.empty:
        print("\nExample: Korea (GDP per Capita)")
        print(example.to_string(index=False))


if __name__ == "__main__":
    main()