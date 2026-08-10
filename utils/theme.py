"""
Shared tactical dark theme for the AI Military Intelligence Dashboard.

Import and call `apply_theme()` at the top of every page, right after
`st.set_page_config(...)`. Then use `kpi_card()` / `section_header()`
instead of `st.metric()` / `st.subheader()` for the tactical look.
"""

import streamlit as st

# ----------------------------------------------------------------
# Palette (matches the mentor brief)
# ----------------------------------------------------------------
BG = "#090D16"
SURFACE = "#111827"
CYAN = "#00F0FF"
AMBER = "#FFB800"
CRIMSON = "#FF0055"
EMERALD = "#00FF66"
TEXT_MUTED = "#8A93A6"

COLOR_MAP = {
    "cyan": CYAN,
    "amber": AMBER,
    "crimson": CRIMSON,
    "emerald": EMERALD,
}


def apply_theme():
    """Inject the dark tactical CSS. Call once per page."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top left, #0d1420 0%, {BG} 60%);
            color: #E6EDF7;
        }}

        section[data-testid="stSidebar"] {{
            background: #0B101B;
            border-right: 1px solid rgba(0, 240, 255, 0.15);
        }}

        /* Glassmorphism panel used by kpi_card / chart wrappers */
        .tac-card {{
            background: rgba(17, 24, 39, 0.65);
            border: 1px solid rgba(0, 240, 255, 0.18);
            border-radius: 14px;
            padding: 16px 18px;
            backdrop-filter: blur(6px);
            box-shadow: 0 0 24px rgba(0, 240, 255, 0.05);
            transition: box-shadow 0.2s ease;
        }}
        .tac-card:hover {{
            box-shadow: 0 0 28px rgba(0, 240, 255, 0.18);
        }}

        .tac-label {{
            font-size: 12px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {TEXT_MUTED};
            margin-bottom: 4px;
        }}

        .tac-value {{
            font-size: 30px;
            font-weight: 700;
            line-height: 1.1;
        }}

        .tac-delta {{
            font-size: 12px;
            margin-top: 4px;
            opacity: 0.85;
        }}

        .tac-section-title {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 18px;
            font-weight: 600;
            color: #E6EDF7;
            border-left: 3px solid {CYAN};
            padding-left: 10px;
            margin: 18px 0 10px 0;
        }}

        /* Plotly chart containers get the same glass treatment */
        div[data-testid="stPlotlyChart"] {{
            background: rgba(17, 24, 39, 0.5);
            border: 1px solid rgba(0, 240, 255, 0.12);
            border-radius: 14px;
            padding: 6px;
        }}

        .stButton>button {{
            background: rgba(0, 240, 255, 0.08);
            border: 1px solid {CYAN};
            color: {CYAN};
            border-radius: 8px;
        }}
        .stButton>button:hover {{
            background: rgba(0, 240, 255, 0.2);
            color: white;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, color: str = "cyan", delta: str | None = None):
    """Render one glassmorphism KPI card. `color` in cyan/amber/crimson/emerald."""
    hex_color = COLOR_MAP.get(color, CYAN)
    delta_html = f'<div class="tac-delta" style="color:{hex_color}">{delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="tac-card">
            <div class="tac-label">{label}</div>
            <div class="tac-value" style="color:{hex_color}">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(icon: str, title: str):
    st.markdown(
        f'<div class="tac-section-title">{icon} {title}</div>',
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------
# A shared plotly dark layout so every chart matches the theme
# ----------------------------------------------------------------
def dark_layout(fig, height=None):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E6EDF7"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=40, b=10),
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)")
    return fig
