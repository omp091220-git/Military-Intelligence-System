import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, kpi_card, section_header, dark_layout

st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")
apply_theme()

st.markdown(
    "<h1 style='color:#00F0FF;'>🛡 Command Overview</h1>",
    unsafe_allow_html=True,
)

df = load_data()

section_header("📊", "Dashboard Summary")

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Incidents", f"{len(df):,}", color="cyan")
with c2:
    kpi_card("Fatalities", f"{int(df['nkill'].sum()):,}", color="crimson")
with c3:
    kpi_card("Injured", f"{int(df['nwound'].sum()):,}", color="amber")
with c4:
    kpi_card("Countries", f"{df['country_txt'].nunique()}", color="emerald")

st.divider()

section_header("📈", "Attacks Over Years")

yearly = df.groupby("iyear").size().reset_index(name="Attacks")

fig = px.area(
    yearly,
    x="iyear",
    y="Attacks",
    markers=True,
    color_discrete_sequence=["#00F0FF"],
)
fig.update_traces(fill="tozeroy", fillcolor="rgba(0,240,255,0.12)")
fig = dark_layout(fig, height=380)
st.plotly_chart(fig, use_container_width=True)

st.divider()

section_header("🌐", "Regional Share")

regional = df.groupby("region_txt").size().reset_index(name="Attacks")
fig2 = px.pie(
    regional,
    names="region_txt",
    values="Attacks",
    hole=0.55,
    color_discrete_sequence=["#00F0FF", "#FFB800", "#FF0055", "#00FF66", "#5B8CFF", "#B18CFF"],
)
fig2 = dark_layout(fig2, height=380)
st.plotly_chart(fig2, use_container_width=True)

st.success("👉 Open **Global Threat Map** from the sidebar to explore incidents geographically.")
