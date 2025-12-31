import pandas as pd
import plotly.express as px

df = pd.read_csv("oecd_6_indicators_2020_2024_long.csv")

df_sel = df[
    (df["iso3"] == "AUS") &
    (df["indicator"] == "gdp_growth_pct")
]

fig = px.line(
    df_sel,
    x="year",
    y="value",
    markers=True,
    title="Australia: GDP Growth (2020–2024)",
    labels={
        "year": "Year",
        "value": "GDP Growth (%)"
    }
)

# ✅ x축을 연도 단위로 고정
fig.update_xaxes(
    tickmode="linear",
    tick0=2020,
    dtick=1
)

fig.show()