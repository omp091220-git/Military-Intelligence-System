import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

from utils.data_loader import load_data
from utils.theme import apply_theme, section_header, kpi_card, dark_layout

st.set_page_config(page_title="AI Intelligence Report", page_icon="🧠", layout="wide")
apply_theme()

st.markdown("<h1 style='color:#00F0FF;'>🧠 AI Intelligence Report</h1>", unsafe_allow_html=True)
st.caption("AI-assisted intelligence summary and anomaly detection from the Global Terrorism Database.")

df = load_data()

st.sidebar.header("Report Filters")
years = sorted(df["iyear"].unique())
selected_year = st.sidebar.selectbox("Select Year", ["All"] + list(years))
if selected_year != "All":
    df = df[df["iyear"] == selected_year]

# ----------------------------------------------------------------
# Key stats (original)
# ----------------------------------------------------------------
total_incidents = len(df)
total_killed = int(df["nkill"].fillna(0).sum())
total_wounded = int(df["nwound"].fillna(0).sum())
countries = df["country_txt"].nunique()

top_countries = df["country_txt"].value_counts().head(10)
top_groups = df["gname"].value_counts().head(10)
attack_types = df["attacktype1_txt"].value_counts()
weapon_types = df["weaptype1_txt"].value_counts()

avg_killed = df["nkill"].fillna(0).mean()
if avg_killed < 2:
    threat = "LOW 🟢"
elif avg_killed < 5:
    threat = "MEDIUM 🟡"
else:
    threat = "HIGH 🔴"

section_header("📊", "Key Intelligence Indicators")
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Incidents", f"{total_incidents:,}", color="cyan")
with c2:
    kpi_card("Fatalities", f"{total_killed:,}", color="crimson")
with c3:
    kpi_card("Injuries", f"{total_wounded:,}", color="amber")
with c4:
    kpi_card("Threat Level", threat, color="emerald")

st.divider()

# ----------------------------------------------------------------
# NEW: Real anomaly detection (IsolationForest), not rule-based
# ----------------------------------------------------------------
section_header("🚨", "Anomaly Detection Engine")

anomaly_cols = ["nkill", "nwound", "iyear"]
work = df.dropna(subset=anomaly_cols).copy()

# encode categorical context so unusual combinations (not just casualty
# spikes) can also be flagged
cat_cols = ["country_txt", "attacktype1_txt", "weaptype1_txt", "targtype1_txt"]
encoded = work[anomaly_cols].copy()
for col in cat_cols:
    if col in work.columns:
        le = LabelEncoder()
        encoded[col] = le.fit_transform(work[col].astype(str))

if len(encoded) >= 20:
    iso = IsolationForest(
        n_estimators=200,
        contamination=0.02,   # flag roughly the top 2% most unusual incidents
        random_state=42,
    )
    work["anomaly_score"] = iso.fit_predict(encoded)
    work["anomaly_score_raw"] = iso.decision_function(encoded)

    anomalies = (
        work[work["anomaly_score"] == -1]
        .sort_values("anomaly_score_raw")
        .head(15)
    )

    kpi_card("Anomalies flagged", f"{len(work[work['anomaly_score'] == -1]):,}", color="crimson")

    st.dataframe(
        anomalies[["iyear", "country_txt", "city", "attacktype1_txt", "weaptype1_txt",
                   "gname", "nkill", "nwound"]],
        use_container_width=True,
    )
    st.caption(
        "Flagged using IsolationForest across casualty counts, year, country, attack/weapon/target "
        "type — these are incidents that deviate most from the overall pattern, not simply the "
        "highest-casualty rows."
    )
else:
    st.caption("Not enough rows in this filter to run anomaly detection (need at least 20).")

st.divider()

# ----------------------------------------------------------------
# Executive Summary (original, still rule-based — this part is meant
# to be a fast factual recap, so keep it deterministic)
# ----------------------------------------------------------------
section_header("📝", "Executive Summary")

summary = f"""
During the selected period, {total_incidents:,} terrorist incidents were recorded across
{countries} countries, resulting in {total_killed:,} fatalities and {total_wounded:,} injuries.

Overall threat level is assessed as **{threat}**.

Most affected country: **{top_countries.index[0] if len(top_countries) else 'N/A'}**.
Most active organization: **{top_groups.index[0] if len(top_groups) else 'N/A'}**.
Most common attack type: **{attack_types.index[0] if len(attack_types) else 'N/A'}**.
Most frequently used weapon: **{weapon_types.index[0] if len(weapon_types) else 'N/A'}**.
"""
st.info(summary)

st.divider()

section_header("🌍", "Top 10 High-Risk Countries")
fig = px.bar(top_countries, x=top_countries.values, y=top_countries.index, orientation="h",
             labels={"x": "Incidents", "y": "Country"},
             color=top_countries.values, color_continuous_scale=["#0B101B", "#00F0FF"])
st.plotly_chart(dark_layout(fig, height=400), use_container_width=True)

section_header("👥", "Most Active Terrorist Groups")
fig2 = px.bar(top_groups, x=top_groups.values, y=top_groups.index, orientation="h",
              labels={"x": "Attacks", "y": "Group"},
              color=top_groups.values, color_continuous_scale=["#0B101B", "#FF0055"])
st.plotly_chart(dark_layout(fig2, height=400), use_container_width=True)

st.divider()

# ----------------------------------------------------------------
# Download (original, extended with anomaly count)
# ----------------------------------------------------------------
report = f"""
==============================
AI INTELLIGENCE REPORT
==============================
Total Incidents : {total_incidents}
Fatalities : {total_killed}
Injuries : {total_wounded}
Threat Level : {threat}
Top Country : {top_countries.index[0] if len(top_countries) else 'N/A'}
Top Group : {top_groups.index[0] if len(top_groups) else 'N/A'}
Most Common Attack : {attack_types.index[0] if len(attack_types) else 'N/A'}
Most Common Weapon : {weapon_types.index[0] if len(weapon_types) else 'N/A'}
Anomalies Flagged : {int((work['anomaly_score'] == -1).sum()) if 'anomaly_score' in work else 'N/A'}
"""

st.download_button("📄 Download Intelligence Report", report, file_name="AI_Intelligence_Report.txt")
