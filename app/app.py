# app/app.py
# OECD Crisis & Recovery Dashboard (2020–2024)
# - Country dropdown shows full country names (uses ISO3 internally)
# - Indicator dropdown shows friendly names
# - Includes an Indicator Guide section (definitions + interpretation)
# - Uses Long CSV for trend chart and Wide CSV for 2024 scatter
#
# Expected files:
#   data/oecd_6_indicators_2020_2024_long.csv
#   data/oecd_6_indicators_2020_2024_wide.csv

import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="OECD Crisis & Recovery Dashboard", layout="wide")


# -------------------------
# Indicator definitions (portfolio-friendly)
# -------------------------
INDICATOR_INFO = {
    "gdp_per_capita_usd": {
        "label": "GDP per Capita (current US$)",
        "unit": "USD",
        "means": (
            "Average economic output per person in current US dollars (not inflation-adjusted). "
            "Often used as a rough proxy for living standards."
        ),
        "interpretation": (
            "Higher values usually suggest higher average income/production per person, but it does not "
            "capture inequality or differences in cost of living."
        ),
    },
    "gdp_growth_pct": {
        "label": "GDP Growth (annual %)",
        "unit": "%",
        "means": "Annual percent growth rate of real GDP compared to the previous year.",
        "interpretation": (
            "Positive indicates expansion; negative indicates contraction. "
            "Comparing 2020–2024 highlights shock → rebound → slowdown patterns."
        ),
    },
    "unemployment_pct": {
        "label": "Unemployment Rate (% of labor force)",
        "unit": "%",
        "means": "Share of the labor force without work but available and actively seeking employment.",
        "interpretation": (
            "Lower is generally better. Unemployment often lags economic slowdowns and can be slower to recover."
        ),
    },
    "inflation_cpi_pct": {
        "label": "Inflation (CPI, annual %)",
        "unit": "%",
        "means": "Annual percent change in consumer prices (CPI).",
        "interpretation": (
            "High inflation can signal overheating or supply shocks; very low/negative inflation can indicate weak demand. "
            "Context matters across countries and years."
        ),
    },
    "gov_debt_pct_gdp": {
        "label": "Government Debt (% of GDP)",
        "unit": "% of GDP",
        "means": "Government debt burden relative to the size of the economy (GDP).",
        "interpretation": (
            "Higher debt can reduce fiscal flexibility, especially when interest rates rise. Sustainability depends on "
            "growth, rates, and debt structure (e.g., maturity and who holds the debt)."
        ),
    },
    "current_account_pct_gdp": {
        "label": "Current Account Balance (% of GDP)",
        "unit": "% of GDP",
        "means": (
            "Net flow of goods/services, income, and transfers with the rest of the world (as a share of GDP)."
        ),
        "interpretation": (
            "Positive suggests a net external surplus; negative suggests net borrowing from abroad. Persistent deficits "
            "can increase external vulnerability, especially during global stress."
        ),
    },
}


# -------------------------
# Data loading (cached)
# -------------------------
@st.cache_data
def load_long() -> pd.DataFrame:
    df = pd.read_csv("data/oecd_6_indicators_2020_2024_long.csv")
    # Basic cleanup / safety
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


@st.cache_data
def load_wide() -> pd.DataFrame:
    df = pd.read_csv("data/oecd_6_indicators_2020_2024_wide.csv")
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


df_long = load_long()
df_wide = load_wide()


# -------------------------
# Build country mapping (country name -> iso3)
# -------------------------
country_df = (
    df_long[["country", "iso3"]]
    .dropna()
    .drop_duplicates()
    .sort_values("country")
    .reset_index(drop=True)
)

country_names = country_df["country"].tolist()

# Reasonable default if present
default_country = "Korea, Rep." if "Korea, Rep." in country_names else country_names[0]


# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.title("Controls")

selected_country = st.sidebar.selectbox(
    "Select a country",
    country_names,
    index=country_names.index(default_country),
)

selected_iso3 = country_df.loc[country_df["country"] == selected_country, "iso3"].iloc[0]

indicator_keys = list(INDICATOR_INFO.keys())
indicator_labels = [INDICATOR_INFO[k]["label"] for k in indicator_keys]

default_indicator_key = "gdp_growth_pct" if "gdp_growth_pct" in indicator_keys else indicator_keys[0]
default_indicator_idx = indicator_keys.index(default_indicator_key)

selected_indicator_label = st.sidebar.selectbox(
    "Select an indicator",
    indicator_labels,
    index=default_indicator_idx,
)

selected_indicator = indicator_keys[indicator_labels.index(selected_indicator_label)]


# -------------------------
# Header
# -------------------------
st.title("OECD Crisis & Recovery Dashboard (2020–2024)")
st.caption("Data source: World Bank Open Data (Indicators).")

st.write(
    f"**Selected:** {selected_country} (**{selected_iso3}**)  \n"
    f"**Indicator:** {INDICATOR_INFO[selected_indicator]['label']}"
)


# -------------------------
# Indicator Guide
# -------------------------
st.subheader("Indicator Guide")

with st.expander("What do these indicators mean? (definitions + interpretation)", expanded=False):
    for key, info in INDICATOR_INFO.items():
        st.markdown(
            f"**{info['label']}**  \n"
            f"- **Unit:** {info['unit']}  \n"
            f"- **What it measures:** {info['means']}  \n"
            f"- **How to interpret:** {info['interpretation']}"
        )


# -------------------------
# Section 1: Trend chart (Long format)
# -------------------------
st.subheader("1) Country Trend (2020–2024)")

st.caption(
    f"**{INDICATOR_INFO[selected_indicator]['label']}** — Unit: **{INDICATOR_INFO[selected_indicator]['unit']}**. "
    f"{INDICATOR_INFO[selected_indicator]['interpretation']}"
)

df_sel = df_long[
    (df_long["iso3"] == selected_iso3) & (df_long["indicator"] == selected_indicator)
].copy()

df_sel = df_sel.dropna(subset=["year"]).sort_values("year")

fig1 = px.line(
    df_sel,
    x="year",
    y="value",
    markers=True,
    title=f"{selected_country}: {INDICATOR_INFO[selected_indicator]['label']} (2020–2024)",
    labels={"year": "Year", "value": INDICATOR_INFO[selected_indicator]["unit"]},
)

# Force year ticks to be integers (removes 2023.5-like ticks)
fig1.update_xaxes(tickmode="linear", tick0=2020, dtick=1)

st.plotly_chart(fig1, use_container_width=True)


# -------------------------
# Section 2: Snapshot scatter (Wide format) — 2024
# -------------------------
st.subheader("2) Fiscal vs External Balance Snapshot (2024)")

st.caption(
    "X = Government Debt (% of GDP), Y = Current Account Balance (% of GDP). "
    "This view helps compare fiscal burden vs external balance across countries."
)

df_2024 = df_wide[df_wide["year"] == 2024].copy()

# Guard: if wide file is missing required columns, show message instead of crashing
required_cols = {"gov_debt_pct_gdp", "current_account_pct_gdp", "country", "iso3"}
missing_cols = [c for c in required_cols if c not in df_2024.columns]

if missing_cols:
    st.warning(
        "Wide CSV is missing required columns for the scatter plot: "
        + ", ".join(missing_cols)
        + ".\n\nMake sure you generated `data/oecd_6_indicators_2020_2024_wide.csv` from the long file."
    )
else:
    fig2 = px.scatter(
        df_2024,
        x="gov_debt_pct_gdp",
        y="current_account_pct_gdp",
        hover_name="country",
        hover_data=["iso3", "gdp_per_capita_usd"] if "gdp_per_capita_usd" in df_2024.columns else ["iso3"],
        title="OECD 2024: Government Debt vs Current Account Balance",
        labels={
            "gov_debt_pct_gdp": "Government Debt (% of GDP)",
            "current_account_pct_gdp": "Current Account Balance (% of GDP)",
        },
    )
    st.plotly_chart(fig2, use_container_width=True)


# -------------------------
# Optional: show raw data
# -------------------------
with st.expander("Show filtered raw data (selected country + selected indicator)"):
    st.dataframe(df_sel, use_container_width=True)