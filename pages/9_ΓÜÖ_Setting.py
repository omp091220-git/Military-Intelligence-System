import streamlit as st
import pandas as pd

from utils.theme import apply_theme, section_header, kpi_card
from utils.data_loader import DATA_PATH

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
apply_theme()

st.markdown("<h1 style='color:#00F0FF;'>⚙️ Dashboard Settings</h1>", unsafe_allow_html=True)
st.caption("Configure your AI-Based Military Intelligence Dashboard.")

section_header("🎨", "Appearance")
theme = st.selectbox("Dashboard Theme", ["Dark (Tactical)", "Light"])
layout = st.selectbox("Dashboard Layout", ["Wide", "Centered"])

section_header("🌍", "Default Dashboard")
country = st.text_input("Default Country", "India")
forecast_years = st.slider("Default Forecast Years", 1, 10, 5)
confidence = st.slider("Minimum Prediction Confidence (%)", 50, 100, 80)

section_header("🗺️", "Global Threat Map")
map_style = st.selectbox("Map Mode", ["3D Tactical (pydeck)", "Flat Geo (plotly)"])
show_cluster = st.checkbox("Enable Marker Clustering", value=True)

section_header("🤖", "Machine Learning")
ml_model = st.selectbox("Prediction Model", ["Random Forest", "Decision Tree", "Gradient Boosting"])
probability = st.checkbox("Show Prediction Probability", value=True)

section_header("🔔", "Notifications")
attack_alert = st.checkbox("Enable Attack Alerts", value=True)
forecast_alert = st.checkbox("Enable Forecast Alerts", value=True)

st.divider()
section_header("📊", "Dataset Information")

try:
    df = pd.read_csv(DATA_PATH, encoding="latin1", low_memory=False)
    st.success("Dataset loaded successfully")
    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Rows", f"{df.shape[0]:,}", color="cyan")
    with c2:
        kpi_card("Columns", f"{df.shape[1]}", color="emerald")
    with c3:
        kpi_card("Countries", f"{df['country_txt'].nunique()}", color="amber")
except Exception:
    st.error(f"Dataset not found at `{DATA_PATH}`. Place your CSV there first.")

st.divider()
if st.button("💾 Save Settings"):
    st.success("Settings saved successfully!")
    st.balloons()

if st.button("🔄 Reset Settings"):
    st.warning("Settings reset to default values.")
