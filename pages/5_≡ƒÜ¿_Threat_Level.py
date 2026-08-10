import streamlit as st
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

from utils.data_loader import load_data
from utils.theme import apply_theme, section_header, kpi_card

st.set_page_config(page_title="Threat Level Prediction", page_icon="🚨", layout="wide")
apply_theme()

st.markdown("<h1 style='color:#00F0FF;'>🚨 AI Threat Level Prediction — What-If Simulator</h1>", unsafe_allow_html=True)
st.caption("Move the sliders — the prediction updates live, no button needed.")


@st.cache_resource(show_spinner="Training threat-level model...")
def train_model():
    df = load_data()
    df = df[["country_txt", "region_txt", "attacktype1_txt", "weaptype1_txt",
              "targtype1_txt", "nkill", "nwound"]].dropna()

    df["impact"] = df["nkill"] + df["nwound"]

    def classify(x):
        if x <= 2:
            return "LOW"
        elif x <= 10:
            return "MEDIUM"
        return "HIGH"

    df["threat_level"] = df["impact"].apply(classify)

    encoders = {}
    for col in ["country_txt", "region_txt", "attacktype1_txt", "weaptype1_txt", "targtype1_txt"]:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    target_encoder = LabelEncoder()
    df["threat_level"] = target_encoder.fit_transform(df["threat_level"])

    X = df.drop(columns=["threat_level", "impact"])
    y = df["threat_level"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    return model, encoders, target_encoder, df


model, encoders, target_encoder, ref_df = train_model()

# ----------------------------------------------------------------
# Sidebar what-if controls
# ----------------------------------------------------------------
st.sidebar.header("What-If Parameters")

country_options = list(encoders["country_txt"].classes_)
region_options = list(encoders["region_txt"].classes_)
attack_options = list(encoders["attacktype1_txt"].classes_)
weapon_options = list(encoders["weaptype1_txt"].classes_)
target_options = list(encoders["targtype1_txt"].classes_)

country = st.sidebar.selectbox("Country", country_options)
region = st.sidebar.selectbox("Region", region_options)
attack = st.sidebar.selectbox("Attack Type", attack_options)
weapon = st.sidebar.selectbox("Weapon Type", weapon_options)
target = st.sidebar.selectbox("Target Type", target_options)

nkill = st.sidebar.slider("Number Killed (scenario)", 0, 200, 0)
nwound = st.sidebar.slider("Number Wounded (scenario)", 0, 200, 0)

# ----------------------------------------------------------------
# Live prediction — runs on every widget change automatically
# ----------------------------------------------------------------
input_data = np.array([[
    encoders["country_txt"].transform([country])[0],
    encoders["region_txt"].transform([region])[0],
    encoders["attacktype1_txt"].transform([attack])[0],
    encoders["weaptype1_txt"].transform([weapon])[0],
    encoders["targtype1_txt"].transform([target])[0],
    nkill,
    nwound,
]])

prediction = model.predict(input_data)
probability = model.predict_proba(input_data)
result = target_encoder.inverse_transform(prediction)[0]
confidence = float(np.max(probability) * 100)

section_header("🔍", "Live Prediction")

c1, c2 = st.columns([1, 2])
with c1:
    color = {"LOW": "emerald", "MEDIUM": "amber", "HIGH": "crimson"}.get(result, "cyan")
    kpi_card("Predicted Threat Level", result, color=color)
    kpi_card("Confidence", f"{confidence:.1f}%", color="cyan")

with c2:
    prob_df = pd.DataFrame({
        "Threat Level": target_encoder.classes_,
        "Probability": probability[0],
    })
    st.bar_chart(prob_df.set_index("Threat Level"))

st.caption(
    "This model is retrained once per session from the loaded dataset (cached). "
    "Adjust any control on the left to re-run the scenario instantly."
)
