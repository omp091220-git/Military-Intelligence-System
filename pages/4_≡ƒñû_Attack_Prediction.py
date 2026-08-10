import streamlit as st
import joblib
import pandas as pd
import numpy as np
import os

from utils.data_loader import load_data
from utils.theme import apply_theme, section_header, kpi_card

st.set_page_config(page_title="Attack Prediction", page_icon="🤖", layout="wide")
apply_theme()

st.markdown("<h1 style='color:#00F0FF;'>🤖 Attack Type Prediction</h1>", unsafe_allow_html=True)
st.caption("Enter scenario details — prediction updates live as you change any field.")

MODEL_PATH = "models/attack_prediction_model.pkl"

if not os.path.exists(MODEL_PATH):
    st.error(
        "Model files not found. Run `python train_attack_model.py` once from your project "
        "folder first, then reload this page."
    )
    st.stop()

model = joblib.load(MODEL_PATH)
encoders = joblib.load("models/feature_encoders.pkl")
target_encoder = joblib.load("models/target_encoder.pkl")

df = load_data()

# ----------------------------------------------------------------
# Inputs (live — no submit button, prediction updates on any change)
# ----------------------------------------------------------------
section_header("🎛", "Scenario Inputs")

col1, col2 = st.columns(2)

with col1:
    country = st.selectbox("🌍 Country", list(encoders["country_txt"].classes_))
    region = st.selectbox("🌎 Region", list(encoders["region_txt"].classes_))
    weapon = st.selectbox("🔫 Weapon Type", list(encoders["weaptype1_txt"].classes_))
    target = st.selectbox("🎯 Target Type", list(encoders["targtype1_txt"].classes_))

with col2:
    group = st.selectbox("👥 Terrorist Group", list(encoders["gname"].classes_))
    success = st.selectbox("✅ Attack Successful?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    suicide = st.selectbox("💣 Suicide Attack?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    nkill = st.number_input("☠ Number of Fatalities", min_value=0, value=0, step=1)
    nwound = st.number_input("🏥 Number of Injured", min_value=0, value=0, step=1)

# ----------------------------------------------------------------
# Live prediction
# ----------------------------------------------------------------
input_df = pd.DataFrame({
    "country_txt": [encoders["country_txt"].transform([country])[0]],
    "region_txt": [encoders["region_txt"].transform([region])[0]],
    "weaptype1_txt": [encoders["weaptype1_txt"].transform([weapon])[0]],
    "targtype1_txt": [encoders["targtype1_txt"].transform([target])[0]],
    "gname": [encoders["gname"].transform([group])[0]],
    "success": [success],
    "suicide": [suicide],
    "nkill": [nkill],
    "nwound": [nwound],
})

prediction = model.predict(input_df)
attack_type = target_encoder.inverse_transform(prediction)[0]
probabilities = model.predict_proba(input_df)
confidence = probabilities.max() * 100

st.divider()
section_header("🔍", "Live Prediction")

c1, c2 = st.columns([1, 2])
with c1:
    kpi_card("Predicted Attack Type", attack_type, color="crimson")
    kpi_card("Confidence", f"{confidence:.1f}%", color="cyan")

with c2:
    prob_df = pd.DataFrame({
        "Attack Type": target_encoder.classes_,
        "Probability": probabilities[0],
    }).sort_values("Probability", ascending=False).head(8)
    st.bar_chart(prob_df.set_index("Attack Type"))
