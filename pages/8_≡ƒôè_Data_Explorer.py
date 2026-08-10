import streamlit as st
import pandas as pd
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, section_header, kpi_card, dark_layout

st.set_page_config(page_title="Data Explorer", page_icon="📊", layout="wide")
apply_theme()

st.markdown("<h1 style='color:#00F0FF;'>📊 Global Terrorism Data Explorer</h1>", unsafe_allow_html=True)
st.caption("Explore, filter, visualize and download the GTD dataset.")

df = load_data()

st.sidebar.header("Filter Dataset")

years = sorted(df["iyear"].dropna().unique())
selected_year = st.sidebar.multiselect("Year", years, default=[])

countries = sorted(df["country_txt"].dropna().unique())
selected_country = st.sidebar.multiselect("Country", countries, default=[])

regions = sorted(df["region_txt"].dropna().unique())
selected_region = st.sidebar.multiselect("Region", regions, default=[])

attack_types = sorted(df["attacktype1_txt"].dropna().unique())
selected_attack = st.sidebar.multiselect("Attack Type", attack_types, default=[])

weapons = sorted(df["weaptype1_txt"].dropna().unique())
selected_weapon = st.sidebar.multiselect("Weapon Type", weapons, default=[])

groups = sorted(df["gname"].dropna().unique())
selected_group = st.sidebar.multiselect("Terrorist Group", groups, default=[])

filtered_df = df.copy()
if selected_year:
    filtered_df = filtered_df[filtered_df["iyear"].isin(selected_year)]
if selected_country:
    filtered_df = filtered_df[filtered_df["country_txt"].isin(selected_country)]
if selected_region:
    filtered_df = filtered_df[filtered_df["region_txt"].isin(selected_region)]
if selected_attack:
    filtered_df = filtered_df[filtered_df["attacktype1_txt"].isin(selected_attack)]
if selected_weapon:
    filtered_df = filtered_df[filtered_df["weaptype1_txt"].isin(selected_weapon)]
if selected_group:
    filtered_df = filtered_df[filtered_df["gname"].isin(selected_group)]

search = st.text_input("🔍 Search by City or Country")
if search:
    filtered_df = filtered_df[
        filtered_df["city"].fillna("").str.contains(search, case=False)
        | filtered_df["country_txt"].fillna("").str.contains(search, case=False)
    ]

section_header("📊", "Dataset Summary")
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Incidents", f"{len(filtered_df):,}", color="cyan")
with c2:
    kpi_card("Countries", f"{filtered_df['country_txt'].nunique()}", color="emerald")
with c3:
    kpi_card("Fatalities", f"{int(filtered_df['nkill'].fillna(0).sum()):,}", color="crimson")
with c4:
    kpi_card("Injuries", f"{int(filtered_df['nwound'].fillna(0).sum()):,}", color="amber")

st.divider()
section_header("📋", "Filtered Dataset")
st.dataframe(filtered_df, use_container_width=True, height=500)

csv = filtered_df.to_csv(index=False)
st.download_button("📥 Download Filtered Data", csv, file_name="Filtered_GTD_Data.csv", mime="text/csv")

st.divider()
section_header("📈", "Visual Analytics")
tab1, tab2, tab3 = st.tabs(["Country", "Attack Type", "Weapon Type"])

with tab1:
    country_chart = filtered_df["country_txt"].value_counts().head(10).reset_index()
    country_chart.columns = ["Country", "Incidents"]
    fig = px.bar(country_chart, x="Country", y="Incidents", color="Incidents",
                 color_continuous_scale=["#0B101B", "#00F0FF"])
    st.plotly_chart(dark_layout(fig, height=380), use_container_width=True)

with tab2:
    attack_chart = filtered_df["attacktype1_txt"].value_counts().reset_index()
    attack_chart.columns = ["Attack Type", "Count"]
    fig = px.pie(attack_chart, names="Attack Type", values="Count", hole=0.5,
                 color_discrete_sequence=["#00F0FF", "#FFB800", "#FF0055", "#00FF66", "#5B8CFF"])
    st.plotly_chart(dark_layout(fig, height=380), use_container_width=True)

with tab3:
    weapon_chart = filtered_df["weaptype1_txt"].value_counts().reset_index()
    weapon_chart.columns = ["Weapon", "Count"]
    fig = px.bar(weapon_chart, x="Weapon", y="Count", color="Count",
                 color_continuous_scale=["#0B101B", "#FF0055"])
    st.plotly_chart(dark_layout(fig, height=380), use_container_width=True)

st.divider()
section_header("🧩", "Missing Values")
missing = filtered_df.isnull().sum().sort_values(ascending=False).reset_index()
missing.columns = ["Column", "Missing Values"]
st.dataframe(missing, use_container_width=True)

section_header("ℹ️", "Dataset Information")
st.write("Rows:", filtered_df.shape[0])
st.write("Columns:", filtered_df.shape[1])
st.write("Memory Usage (MB):", round(filtered_df.memory_usage(deep=True).sum() / 1024**2, 2))
st.write("Column Names")
st.write(filtered_df.columns.tolist())
