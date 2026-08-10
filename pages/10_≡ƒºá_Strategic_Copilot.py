import os
import json
import requests
import streamlit as st

from utils.data_loader import load_data
from utils.theme import apply_theme, section_header, kpi_card

st.set_page_config(page_title="Strategic Copilot", page_icon="🧠", layout="wide")
apply_theme()

st.markdown("<h1 style='color:#00F0FF;'>🧠 Strategic Copilot</h1>", unsafe_allow_html=True)
st.caption("Ask natural-language questions about the currently loaded dataset.")

def get_api_key():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("ANTHROPIC_API_KEY", None)
    except Exception:
        # Raised when no secrets.toml exists at all — treat as "not set"
        return None


API_KEY = get_api_key()

if not API_KEY:
    st.error(
        "No Anthropic API key found. Set the `ANTHROPIC_API_KEY` environment variable, "
        "or add `ANTHROPIC_API_KEY = \"sk-ant-...\"` to `.streamlit/secrets.toml`, then reload this page."
    )
    st.stop()

df = load_data()

# ----------------------------------------------------------------
# Build a compact, token-cheap context summary from the real data
# (never send the raw dataframe — summarize it instead)
# ----------------------------------------------------------------
def build_context(frame) -> str:
    top_countries = frame["country_txt"].value_counts().head(10).to_dict()
    top_groups = frame["gname"].value_counts().head(10).to_dict()
    by_year = frame.groupby("iyear").size().to_dict()
    attack_types = frame["attacktype1_txt"].value_counts().to_dict()
    weapon_types = frame["weaptype1_txt"].value_counts().to_dict()

    return json.dumps({
        "total_incidents": int(len(frame)),
        "total_fatalities": int(frame["nkill"].sum()),
        "total_wounded": int(frame["nwound"].sum()),
        "top_countries_by_incidents": top_countries,
        "top_groups_by_incidents": top_groups,
        "incidents_by_year": by_year,
        "attack_type_breakdown": attack_types,
        "weapon_type_breakdown": weapon_types,
    }, default=str)


SYSTEM_PROMPT = """You are a Strategic Intelligence Copilot embedded in a threat-analysis
dashboard. You answer questions ONLY using the JSON data summary provided in each message.
Be concise, cite specific numbers from the data, and never invent facts not present in the
summary. If the data doesn't contain what's needed to answer, say so plainly."""


def ask_copilot(question: str, context_json: str) -> str:
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 600,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": f"DATA SUMMARY:\n{context_json}\n\nQUESTION: {question}",
                }
            ],
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return "".join(block.get("text", "") for block in data.get("content", []) if block.get("type") == "text")


# ----------------------------------------------------------------
# KPIs so the copilot's numbers are visibly grounded
# ----------------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    kpi_card("Incidents in context", f"{len(df):,}", color="cyan")
with c2:
    kpi_card("Countries", f"{df['country_txt'].nunique()}", color="emerald")
with c3:
    kpi_card("Years covered", f"{df['iyear'].nunique()}", color="amber")

st.divider()
section_header("💬", "Ask the Copilot")

if "copilot_history" not in st.session_state:
    st.session_state.copilot_history = []

for role, msg in st.session_state.copilot_history:
    with st.chat_message(role):
        st.write(msg)

suggestion_cols = st.columns(3)
suggestions = [
    "What are the top 3 high-risk countries right now?",
    "Which group shows the sharpest rise in activity?",
    "Summarize the overall threat trend in 3 sentences.",
]
clicked = None
for col, s in zip(suggestion_cols, suggestions):
    if col.button(s, use_container_width=True):
        clicked = s

question = st.chat_input("Ask about the current dataset...") or clicked

if question:
    st.session_state.copilot_history.append(("user", question))
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing dataset..."):
            try:
                context = build_context(df)
                answer = ask_copilot(question, context)
            except requests.HTTPError as e:
                answer = f"API error: {e.response.status_code} — {e.response.text[:300]}"
            except Exception as e:
                answer = f"Error reaching the copilot: {e}"
        st.write(answer)

    st.session_state.copilot_history.append(("assistant", answer))
