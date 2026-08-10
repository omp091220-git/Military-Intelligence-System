import streamlit as st
import pydeck as pdk
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import apply_theme, section_header, kpi_card, dark_layout

st.set_page_config(page_title="Global Threat Map", page_icon="🌍", layout="wide")
apply_theme()

st.markdown("<h1 style='color:#00F0FF;'>🌍 Global Threat Map</h1>", unsafe_allow_html=True)

df = load_data()

# ----------------------------------------------------------------
# Filters
# ----------------------------------------------------------------
st.sidebar.header("Filters")

year = st.sidebar.selectbox("Year", ["All"] + sorted(df["iyear"].unique().tolist()))
view_mode = st.sidebar.radio("Map Mode", ["3D Tactical (pydeck)", "Flat Geo (plotly)"])

filtered = df if year == "All" else df[df["iyear"] == year]
filtered = filtered.dropna(subset=["latitude", "longitude"])

c1, c2, c3 = st.columns(3)
with c1:
    kpi_card("Incidents shown", f"{len(filtered):,}", color="cyan")
with c2:
    kpi_card("Fatalities", f"{int(filtered['nkill'].sum()):,}", color="crimson")
with c3:
    kpi_card("Countries", f"{filtered['country_txt'].nunique()}", color="emerald")

st.divider()

if view_mode == "3D Tactical (pydeck)":
    section_header("🛰", "3D Threat Density (rotate: drag + right-click / two-finger)")

    hex_layer = pdk.Layer(
        "HexagonLayer",
        data=filtered,
        get_position=["longitude", "latitude"],
        radius=45000,
        elevation_scale=4000,
        elevation_range=[0, 3000],
        extruded=True,
        pickable=True,
        colorRange=[
            [0, 240, 255, 60],
            [0, 240, 255, 140],
            [255, 184, 0, 180],
            [255, 0, 85, 220],
        ],
    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        get_position=["longitude", "latitude"],
        get_fill_color=[255, 0, 85, 140],
        get_radius=15000,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=filtered["latitude"].mean() if len(filtered) else 20,
        longitude=filtered["longitude"].mean() if len(filtered) else 20,
        zoom=1.4,
        pitch=45,
        bearing=0,
    )

    deck = pdk.Deck(
        layers=[hex_layer, scatter_layer],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "Incidents in this zone: {elevationValue}"},
    )

    st.pydeck_chart(deck, use_container_width=True)
    st.caption(
        "Column height/color = incident density in that zone. "
        "Drag to pan, scroll to zoom, hold right-click (or two-finger drag) to tilt/rotate."
    )

else:
    section_header("🗺", "Flat Geographic View")
    fig = px.scatter_geo(
        filtered,
        lat="latitude",
        lon="longitude",
        color="attacktype1_txt",
        hover_name="country_txt",
        hover_data=["city", "gname", "nkill"],
        projection="orthographic",
    )
    fig.update_geos(
        showland=True, landcolor="#111827",
        showocean=True, oceancolor="#090D16",
        showcountries=True, countrycolor="rgba(0,240,255,0.25)",
        bgcolor="rgba(0,0,0,0)",
    )
    fig = dark_layout(fig, height=650)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Orthographic projection — drag to rotate the globe.")

st.info("👈 Change filters or map mode from the sidebar.")
