import pandas as pd
import plotly.express as px

# -------------------------
# Config
# -------------------------
INPUT_CSV = "data/oecd_changes_2020_to_2024.csv"

# 보고 싶은 변화량 지표 선택
# 예시:
# "gdp_per_capita_usd_change"
# "gdp_growth_pct_change"
# "unemployment_pct_change"
# "gov_debt_pct_gdp_change"
# "current_account_pct_gdp_change"
METRIC = "gdp_per_capita_usd_change"

TOP_N = 10


def main():
    # -------------------------
    # Step 1) Load change data
    # -------------------------
    df = pd.read_csv(INPUT_CSV)

    # 변화량 컬럼이 없으면 중단
    if METRIC not in df.columns:
        raise ValueError(f"Column not found: {METRIC}")

    # -------------------------
    # Step 2) Clean + sort
    # -------------------------
    df_sel = df[["country", "iso3", METRIC]].dropna()

    # TOP N (가장 많이 증가한 국가)
    df_top = df_sel.sort_values(METRIC, ascending=False).head(TOP_N)

    # 보기 좋게 정렬 (아래 → 위로 증가)
    df_top = df_top.sort_values(METRIC, ascending=True)

    # -------------------------
    # Step 3) Build bar chart
    # -------------------------
    fig = px.bar(
        df_top,
        x=METRIC,
        y="country",
        orientation="h",
        title="Top 10 OECD Countries by Change (2020 → 2024)",
        labels={
            METRIC: "Change (2024 − 2020)",
            "country": "Country"
        },
        text=METRIC
    )

    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")

    fig.update_layout(
        yaxis=dict(title=""),
        xaxis=dict(zeroline=True),
        margin=dict(l=120, r=40, t=60, b=40)
    )

    fig.show()


if __name__ == "__main__":
    main()