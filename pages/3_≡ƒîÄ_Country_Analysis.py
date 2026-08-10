import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils.data_loader import load_data
from utils.theme import apply_theme, kpi_card, section_header, dark_layout

st.set_page_config(page_title="Country Analysis", page_icon="🌎", layout="wide")
apply_theme()

st.markdown("<h1 style='color:#00F0FF;'>🌎 Country Analysis</h1>", unsafe_allow_html=True)

df = load_data()

countries = sorted(df["country_txt"].dropna().unique())
country = st.sidebar.selectbox("Select Country", countries)

country_df = df[df["country_txt"] == country]

st.header(f"Intelligence Report : {country}")

# ----------------------------------------------------------------
# KPIs
# ----------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Incidents", f"{len(country_df):,}", color="cyan")
with c2:
    kpi_card("Fatalities", f"{int(country_df['nkill'].sum()):,}", color="crimson")
with c3:
    kpi_card("Injured", f"{int(country_df['nwound'].sum()):,}", color="amber")
with c4:
    kpi_card("Groups", f"{country_df['gname'].nunique()}", color="emerald")

st.divider()

# ----------------------------------------------------------------
# Attacks over time / attack type split
# ----------------------------------------------------------------
left, right = st.columns(2)

with left:
    section_header("📈", "Attacks Over Years")
    yearly = country_df.groupby("iyear").size().reset_index(name="Attacks")
    fig = px.line(yearly, x="iyear", y="Attacks", markers=True,
                  color_discrete_sequence=["#00F0FF"])
    st.plotly_chart(dark_layout(fig, height=340), use_container_width=True)

with right:
    section_header("🥧", "Attack Types")
    attack = country_df.groupby("attacktype1_txt").size().reset_index(name="Count")
    fig = px.pie(attack, names="attacktype1_txt", values="Count", hole=0.5,
                 color_discrete_sequence=["#00F0FF", "#FFB800", "#FF0055", "#00FF66", "#5B8CFF"])
    st.plotly_chart(dark_layout(fig, height=340), use_container_width=True)

st.divider()

# ----------------------------------------------------------------
# NEW: Sunburst — group -> weapon -> attack type chain
# ----------------------------------------------------------------
section_header("🌪", "Intelligence Data Flow (Group → Weapon → Attack Type)")

sun_df = (
    country_df
    .groupby(["gname", "weaptype1_txt", "attacktype1_txt"])
    .size()
    .reset_index(name="Count")
)
# Keep it readable: top groups only
top_gnames = country_df["gname"].value_counts().head(8).index
sun_df = sun_df[sun_df["gname"].isin(top_gnames)]

if len(sun_df):
    fig_sun = px.sunburst(
        sun_df,
        path=["gname", "weaptype1_txt", "attacktype1_txt"],
        values="Count",
        color="Count",
        color_continuous_scale=["#0B101B", "#00F0FF", "#FF0055"],
    )
    fig_sun = dark_layout(fig_sun, height=550)
    st.plotly_chart(fig_sun, use_container_width=True)
else:
    st.caption("Not enough grouped data to render the sunburst for this country.")

st.divider()

# ----------------------------------------------------------------
# NEW: Radar — this country's attack-type profile vs global average
# ----------------------------------------------------------------
section_header("🕸", "Attack Profile vs Global Average")

categories = sorted(df["attacktype1_txt"].dropna().unique())

def pct_profile(frame):
    counts = frame["attacktype1_txt"].value_counts(normalize=True) * 100
    return [counts.get(cat, 0) for cat in categories]

country_profile = pct_profile(country_df)
global_profile = pct_profile(df)

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=country_profile, theta=categories, fill="toself",
    name=country, line_color="#FF0055",
))
fig_radar.add_trace(go.Scatterpolar(
    r=global_profile, theta=categories, fill="toself",
    name="Global Average", line_color="#00F0FF", opacity=0.6,
))
fig_radar.update_layout(
    polar=dict(
        bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(visible=True, gridcolor="rgba(255,255,255,0.1)"),
        angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
    ),
    showlegend=True,
)
st.plotly_chart(dark_layout(fig_radar, height=480), use_container_width=True)

st.divider()

# ----------------------------------------------------------------
# Organizations & weapons (original)
# ----------------------------------------------------------------
left, right = st.columns(2)

with left:
    section_header("👥", "Top Terrorist Organizations")
    groups = (country_df.groupby("gname").size().reset_index(name="Attacks")
              .sort_values("Attacks", ascending=False).head(10))
    fig = px.bar(groups, x="Attacks", y="gname", orientation="h",
                 color="Attacks", color_continuous_scale=["#0B101B", "#00F0FF"])
    st.plotly_chart(dark_layout(fig, height=380), use_container_width=True)

with right:
    section_header("🔫", "Weapon Types")
    weapon = (country_df.groupby("weaptype1_txt").size().reset_index(name="Count")
              .sort_values("Count", ascending=False))
    fig = px.bar(weapon, x="weaptype1_txt", y="Count",
                 color="Count", color_continuous_scale=["#0B101B", "#FF0055"])
    st.plotly_chart(dark_layout(fig, height=380), use_container_width=True)

st.divider()

# ----------------------------------------------------------------
# Map
# ----------------------------------------------------------------
section_header("📍", "Incident Locations")

map_df = country_df.dropna(subset=["latitude", "longitude"])
fig = px.scatter_geo(
    map_df, lat="latitude", lon="longitude", hover_name="city",
    hover_data={"country_txt": True, "iyear": True, "attacktype1_txt": True,
                "gname": True, "nkill": True, "latitude": False, "longitude": False},
    color="attacktype1_txt", projection="natural earth", height=600,
)
fig.update_geos(showland=True, landcolor="#111827", showocean=True,
                 oceancolor="#090D16", bgcolor="rgba(0,0,0,0)")
st.plotly_chart(dark_layout(fig), use_container_width=True)

st.divider()

# ----------------------------------------------------------------
# Table + Download (original)
# ----------------------------------------------------------------
section_header("📋", "Incident Details")

cols = ["iyear", "city", "attacktype1_txt", "targtype1_txt", "weaptype1_txt", "gname", "nkill", "nwound"]
st.dataframe(country_df[cols], use_container_width=True)

csv = country_df.to_csv(index=False).encode()
st.download_button("Download Country Data", csv, file_name=f"{country}.csv", mime="text/csv")
