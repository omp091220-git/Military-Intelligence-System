import streamlit as st
from utils.theme import apply_theme, kpi_card, section_header
from utils.data_loader import load_data

st.set_page_config(
    page_title="AI Military Intelligence Dashboard",
    page_icon="🛡",
    layout="wide",
)
apply_theme()

st.markdown(
    "<h1 style='color:#00F0FF;'>🛡 AI-Based Military Intelligence Dashboard</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    Real-time-style threat analysis over the Global Terrorism Database (GTD),
    with AI-driven prediction, forecasting, anomaly detection, and a
    conversational Strategic Copilot.

    👈 Select a page from the sidebar to begin.
    """
)

df = load_data()

section_header("📊", "Live Snapshot")
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Incidents", f"{len(df):,}", color="cyan")
with c2:
    kpi_card("Fatalities", f"{int(df['nkill'].sum()):,}", color="crimson")
with c3:
    kpi_card("Countries", f"{df['country_txt'].nunique()}", color="emerald")
with c4:
    kpi_card("Active Groups", f"{df['gname'].nunique()}", color="amber")

st.divider()

section_header("🧭", "Available Modules")
st.markdown(
    """
    - 🏠 **Home** — summary KPIs and trend
    - 🌍 **Global Threat Map** — 3D tactical map + flat geo view
    - 🌎 **Country Analysis** — deep-dive per country (sunburst, radar, map)
    - 🤖 **Attack Prediction** — live what-if attack-type prediction
    - 🚨 **Threat Level** — live what-if threat-severity prediction
    - 📈 **Forecasting** — attack trend forecasting per country
    - 🧠 **AI Intelligence** — executive summary + real anomaly detection
    - 🧠 **Strategic Copilot** — chat with your data (needs API key)
    - 📊 **Data Explorer** — full filter/search/download
    - ⚙ **Settings** — preferences
    """
)
