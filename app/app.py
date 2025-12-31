import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="OECD Crisis & Recovery Dashboard", layout="wide")

# -------------------------
# Load data (cached)
# -------------------------
@st.cache_data
def load_long():
    return pd.read_csv("data/oecd_6_indicators_2020_2024_long.csv")

@st.cache_data
def load_wide():
    return pd.read_csv("data/oecd_6_indicators_2020_2024_wide.csv")


df_long = load_long()
df_wide = load_wide()

# -------------------------
# Sidebar controls
# -------------------------
st.sidebar.title("Controls")

# 국가 선택 (ISO3)
iso3_list = sorted(df_long["iso3"].dropna().unique())
default_iso3 = "KOR" if "KOR" in iso3_list else iso3_list[0]
selected_iso3 = st.sidebar.selectbox("Select a country (ISO3)", iso3_list, index=iso3_list.index(default_iso3))

# 지표 선택 (Long format indicator)
indicator_list = sorted(df_long["indicator"].dropna().unique())
default_indicator = "gdp_growth_pct" if "gdp_growth_pct" in indicator_list else indicator_list[0]
selected_indicator = st.sidebar.selectbox("Select an indicator", indicator_list, index=indicator_list.index(default_indicator))

# -------------------------
# Header
# -------------------------
st.title("OECD Crisis & Recovery Dashboard (2020–2024)")
st.caption("Data source: World Bank Open Data API (Indicators).")

# -------------------------
# Section 1: Trend chart
# -------------------------
st.subheader("1) Country Trend (2020–2024)")

df_sel = df_long[(df_long["iso3"] == selected_iso3) & (df_long["indicator"] == selected_indicator)].copy()
df_sel = df_sel.sort_values("year")

# y축 라벨 자동화 (단위 힌트)
unit_hint = ""
if selected_indicator.endswith("_pct") or selected_indicator.endswith("_pct_gdp"):
    unit_hint = " (%)"
elif "usd" in selected_indicator:
    unit_hint = " (USD)"

fig1 = px.line(
    df_sel,
    x="year",
    y="value",
    markers=True,
    title=f"{selected_iso3}: {selected_indicator}{unit_hint} (2020–2024)",
    labels={"year": "Year", "value": f"Value{unit_hint}"}
)

# ✅ x축 연도 눈금 정수로 고정
fig1.update_xaxes(tickmode="linear", tick0=2020, dtick=1)

st.plotly_chart(fig1, use_container_width=True)

# -------------------------
# Section 2: Snapshot scatter (2024)
# -------------------------
st.subheader("2) Fiscal vs External Balance Snapshot (2024)")
st.caption("X = Government Debt (% of GDP), Y = Current Account Balance (% of GDP)")

df_2024 = df_wide[df_wide["year"] == 2024].copy()

# 산점도: 부채 vs 경상수지
fig2 = px.scatter(
    df_2024,
    x="gov_debt_pct_gdp",
    y="current_account_pct_gdp",
    hover_name="country",
    hover_data=["iso3", "gdp_per_capita_usd"],
    title="OECD 2024: Debt vs Current Account",
    labels={
        "gov_debt_pct_gdp": "Government Debt (% of GDP)",
        "current_account_pct_gdp": "Current Account Balance (% of GDP)",
    }
)

st.plotly_chart(fig2, use_container_width=True)

# -------------------------
# Optional: Show raw data table
# -------------------------
with st.expander("Show filtered raw data"):
    st.write(df_sel)