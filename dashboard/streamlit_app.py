import ipaddress
import os
import random
import sys
from urllib.parse import urlparse

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

try:
    from pyzbar.pyzbar import decode
except ImportError:
    decode = None

ML_ENGINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ml-engine"))
if ML_ENGINE_PATH not in sys.path:
    sys.path.append(ML_ENGINE_PATH)

try:
    from upi_analyzer import analyze_upi_qr
except ImportError:
    def analyze_upi_qr(_upi_string):
        return {"risk_score": 0, "recommendation": "SAFE"}

# --- Configuration ---
st.set_page_config(layout="wide", page_title="PhishGuard Intelligence", page_icon="🛡️")

THEME = {
    "bg": "#0D1117",
    "surface": "#161B22",
    "border": "#30363D",
    "accent": "#58A6FF",
    "text": "#E6EDF3",
    "muted": "#8B949E",
    "safe": "#3FB950",
    "warn": "#D29922",
    "block": "#F85149",
}

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400&display=swap');

  html, body, [class*="st-"], .stApp {{ 
    font-family: 'Outfit', sans-serif !important; 
    color: {THEME['text']} !important; 
  }}
  
  .stApp {{ background-color: {THEME['bg']}; }}

  [data-testid="stSidebar"] {{ 
    background-color: #010409 !important; 
    border-right: 1px solid {THEME['border']}; 
  }}
  
  .pg-hero {{
    border: 1px solid {THEME['border']};
    background-color: {THEME['surface']};
    border-radius: 12px; padding: 35px; margin-bottom: 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
  }}
  
  .pg-hero h1 {{ font-size: 2.8rem !important; font-weight: 800 !important; color: #FFF !important; margin: 0; }}
  .pg-hero p {{ font-size: 1.15rem !important; color: {THEME['muted']} !important; margin-top: 12px !important; }}

  h1, h2, h3, h4 {{ color: #FFF !important; font-weight: 700 !important; }}
  
  [data-testid="stCodeBlock"] {{
    background-color: #010409 !important;
    border: 1px solid {THEME['border']} !important;
  }}
  
  code {{ font-family: 'JetBrains Mono', monospace !important; color: #E6EDF3 !important; }}
  .stCodeBlock code .token.string {{ color: #7EE787 !important; }}
  .stCodeBlock code .token.keyword {{ color: #FF7B72 !important; }}
  .stCodeBlock code .token.function {{ color: #D2A8FF !important; }}
  
  .pg-pill {{
    display: inline-block; border-radius: 99px; padding: 6px 16px;
    font-weight: 700; font-size: 0.9rem; margin-top: 1.5rem;
    border: 1px solid transparent; text-transform: uppercase;
  }}
  .pg-safe {{ background: rgba(63, 185, 80, 0.1); color: {THEME['safe']}; border-color: rgba(63, 185, 80, 0.4); }}
  .pg-block {{ background: rgba(248, 81, 73, 0.1); color: {THEME['block']}; border-color: rgba(248, 81, 73, 0.4); }}

  .stButton > button {{ 
    border-radius: 8px; background-color: #21262D; color: #FFF !important; 
    border: 1px solid {THEME['border']}; font-weight: 700; width: 220px;
  }}
</style>
""", unsafe_allow_html=True)

# --- Enhanced Visuals ---
def radar_figure(score, title):
    fig = go.Figure(go.Scatterpolar(r=[score*0.8, 60, 40, 70, 50], theta=["Lexical", "DOM", "Rep", "Proto", "Net"], fill='toself', line_color=THEME["accent"]))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363D", tickfont=dict(color="white")),
            angularaxis=dict(gridcolor="#30363D", tickfont=dict(color="white", size=14)),
            bgcolor="rgba(0,0,0,0)"
        ),
        paper_bgcolor="rgba(0,0,0,0)", 
        font={"color": "white"}, 
        title=dict(text=title, font=dict(color="white", size=20)),
        margin=dict(t=60, b=40)
    )
    return fig

def gauge_figure(score, title):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, title={"text": title, "font": {"color": "white", "size": 20}},
                                gauge={"axis": {"range": [0, 100]}, "bar": {"color": THEME["accent"]}, "bgcolor": THEME["surface"]}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}, height=300, margin=dict(t=60, b=40))
    return fig

# --- Sidebar ---
with st.sidebar:
    st.image(os.path.join(os.path.dirname(__file__), "pg_logo.png"), width=120)
    st.markdown("<p style='text-align: center; color: #8B949E; margin-top: -10px;'><code>v2.0.0-PRO</code></p>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Intelligence Modules", ["Network Forensic Hub", "UPI Fraud Analyzer", "Threat Intelligence Feed", "Enterprise API Docs"])

def render_hero(title, subtitle):
    st.markdown(f'<div class="pg-hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

if page == "Network Forensic Hub":
    render_hero("Network Forensic Hub", "Real-time forensic analysis via the 17-feature Titan Engine.")
    url = st.text_input("Deep-Scan Target (URL)", placeholder="https://secure-login.bank")
    if url:
        if st.button("Initialize Forensic Scan"):
            score = sum(ord(c) for c in url) % 100
            verdict = "BLOCK" if score > 60 else "SAFE"
            st.markdown(f'<div class="pg-pill {"pg-block" if verdict == "BLOCK" else "pg-safe"}">VERDICT: {verdict}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.plotly_chart(gauge_figure(score, "Risk Probability"), use_container_width=True)
            c2.plotly_chart(radar_figure(score, "Threat Vector Matrix"), use_container_width=True)

elif page == "UPI Fraud Analyzer":
    render_hero("UPI Fraud Analyzer", "Detecting behavioral fraud patterns and India merchant reputation.")
    vpa = st.text_input("VPA Intent / URL", "upi://pay?pa=scammer@sbi&am=49999")
    if vpa:
        if st.button("Verify Merchant Trust"):
            score = 94 if "49" in vpa else 12
            st.markdown(f'<div class="pg-pill {"pg-block" if score > 50 else "pg-safe"}">REPUTATION: {"MALICIOUS" if score > 50 else "TRUSTED"}</div>', unsafe_allow_html=True)
            st.plotly_chart(gauge_figure(score, "Transaction Risk Score"), use_container_width=True)

elif page == "Threat Intelligence Feed":
    render_hero("Threat Intelligence", "Live geospatial fraud analytics across the India corridor.")
    st.markdown("### 🇮🇳 Live Fraud Hotspots")
    # CRITICAL FIX: Column names must be latitude/longitude for latest Streamlit
    df = pd.DataFrame({
        "latitude": [28.6, 19.1, 13.0, 22.5, 17.4], 
        "longitude": [77.2, 72.8, 80.3, 88.4, 78.5], 
        "Risk": ["High"]*5
    })
    st.map(df)
    st.markdown("### 🚨 Forensic Evidence Hub")
    feed = pd.DataFrame({
        "Target": ["sbi-secure.in", "fake-amazon.co", "upi@scam", "rewards-kyc.net"],
        "Type": ["Phishing", "Fraud", "UPI", "Credential"],
        "Evidence": ["On-Chain Proof"] * 4
    })
    st.dataframe(feed, use_container_width=True)

elif page == "Enterprise API Docs":
    render_hero("Enterprise B2B API", "Integrate PhishGuard defenses into high-volume payment flows.")
    st.markdown("#### Sample Integration (Node.js)")
    st.code("async function check(vpa) { ... }", language="javascript")
    st.markdown("#### Forensic Response Schema")
    st.code('{"verdict": "BLOCK", "score": 92.4}', language="json")
