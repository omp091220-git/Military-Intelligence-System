import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

from utils.data_loader import load_data
from utils.theme import apply_theme, section_header, kpi_card, dark_layout

st.set_page_config(page_title="Forecasting", page_icon="📈", layout="wide")
apply_theme()

st.markdown("<h1 style='color:#00F0FF;'>📈 Terrorism Attack Forecasting</h1>", unsafe_allow_html=True)
st.caption("Forecast future attack counts per country using historical GTD data.")

df = load_data()

st.sidebar.header("Forecast Settings")
countries = sorted(df["country_txt"].dropna().unique())
country = st.sidebar.selectbox("Select Country", countries)
forecast_years = st.sidebar.slider("Forecast Years", 1, 10, 5)

country_df = df[df["country_txt"] == country]
yearly = country_df.groupby("iyear").size().reset_index(name="Attacks").sort_values("iyear")

if len(yearly) < 5:
    st.warning("Not enough historical data for this country to forecast.")
    st.stop()

X = yearly[["iyear"]]
y = yearly["Attacks"]
model = LinearRegression().fit(X, y)

last_year = yearly["iyear"].max()
future_years = np.arange(last_year + 1, last_year + forecast_years + 1)
predictions = np.maximum(model.predict(pd.DataFrame({"iyear": future_years})), 0)

forecast = pd.DataFrame({"Year": future_years, "Forecasted Attacks": predictions.astype(int)})

section_header("📊", "Historical + Forecast")

fig = go.Figure()
fig.add_trace(go.Scatter(x=yearly["iyear"], y=yearly["Attacks"], mode="lines+markers",
                          name="Historical", line=dict(color="#00F0FF")))
fig.add_trace(go.Scatter(x=forecast["Year"], y=forecast["Forecasted Attacks"], mode="lines+markers",
                          name="Forecast", line=dict(color="#FF0055", dash="dash")))
st.plotly_chart(dark_layout(fig, height=500), use_container_width=True)

section_header("📋", "Forecast Table")
st.dataframe(forecast, use_container_width=True)

historical_last = yearly.iloc[-1]["Attacks"]
forecast_last = forecast.iloc[-1]["Forecasted Attacks"]
growth = ((forecast_last - historical_last) / max(historical_last, 1)) * 100

section_header("📐", "Growth Analysis")
c1, c2, c3 = st.columns(3)
with c1:
    kpi_card("Current Attacks", f"{int(historical_last)}", color="cyan")
with c2:
    kpi_card(f"Forecast ({forecast_years}y)", f"{int(forecast_last)}", color="amber")
with c3:
    kpi_card("Growth %", f"{growth:.1f}%", color="crimson" if growth >= 15 else "emerald")

section_header("⚠️", "Risk Assessment")
if growth < 0:
    st.success("🟢 Threat Trend: Decreasing")
elif growth < 15:
    st.warning("🟡 Threat Trend: Stable")
else:
    st.error("🔴 Threat Trend: Increasing")

csv = forecast.to_csv(index=False)
st.download_button("📥 Download Forecast CSV", csv, file_name=f"{country}_forecast.csv", mime="text/csv")
