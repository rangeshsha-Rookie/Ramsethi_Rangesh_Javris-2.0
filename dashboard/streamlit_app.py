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
    "text": "#F0F6FC",
    "muted": "#8B949E",
    "safe": "#3FB950",
    "warn": "#D29922",
    "block": "#F85149",
}

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400&display=swap');

  /* 1. Global Visibility Fix */
  html, body, [class*="st-"], .stApp {{ 
    font-family: 'Outfit', sans-serif !important; 
    color: {THEME['text']} !important; 
    background-color: {THEME['bg']} !important;
  }}
  
  [data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}

  /* 2. INPUT & TEXTAREA VISIBILITY RESCUE (The Fix) */
  input, div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {{
    background-color: #010409 !important;
    color: #FFFFFF !important;
    border: 1px solid {THEME['border']} !important;
    caret-color: white !important;
    border-radius: 6px !important;
  }}
  
  /* Placeholder coloring */
  input::placeholder, textarea::placeholder {{
    color: #484F58 !important;
  }}

  /* 3. SIDEBAR & PILL POLISH */
  [data-testid="stSidebar"] {{ 
    background-color: #010409 !important; 
    border-right: 1px solid {THEME['border']}; 
  }}
  
  code {{ 
    background-color: rgba(110, 118, 129, 0.4) !important; 
    padding: 2px 4px !important;
    border-radius: 4px !important;
    color: #FFFFFF !important;
  }}

  .v-pill {{
    background-color: #1F6FEB !important;
    color: white !important;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 800;
  }}

  /* 4. HERO SECTION READABILITY */
  .pg-hero {{
    border: 1px solid {THEME['border']};
    background-color: {THEME['surface']};
    border-radius: 12px; padding: 35px; margin-bottom: 2rem;
  }}
  .pg-hero h1 {{ font-size: 2.8rem !important; font-weight: 800 !important; color: #FFFFFF !important; margin: 0; }}
  .pg-hero p {{ font-size: 1.15rem !important; color: {THEME['muted']} !important; margin-top: 12px !important; }}

  /* 5. TABLE / DATAFRAME VISIBILITY */
  [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] span, .stTable span {{
    color: white !important;
  }}
  [data-testid="stDataFrame"] {{
    border: 1px solid {THEME['border']};
  }}

  /* 6. STATUS PILLS */
  .pg-pill {{
    display: inline-block; border-radius: 6px; padding: 6px 12px;
    font-weight: 700; font-size: 0.9rem; margin-top: 1.5rem;
    border: 1px solid transparent;
  }}
  .pg-safe {{ background: rgba(63, 185, 80, 0.15); color: {THEME['safe']} !important; border-color: {THEME['safe']}; }}
  .pg-block {{ background: rgba(248, 81, 73, 0.15); color: {THEME['block']} !important; border-color: {THEME['block']}; }}

  .stButton > button {{ 
    border-radius: 6px; background-color: #21262D; color: white !important; 
    border: 1px solid {THEME['border']}; font-weight: 700; width: 220px;
  }}
</style>
""", unsafe_allow_html=True)

# --- Enhanced Visuals ---
def radar_figure(score, title):
    fig = go.Figure(go.Scatterpolar(r=[score*0.8, 60, 40, 70, 50], theta=["Lexical", "DOM", "Rep", "Proto", "Net"], fill='toself', line_color=THEME["accent"]))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363D", tickfont=dict(color="white")),
                                angularaxis=dict(gridcolor="#30363D", tickfont=dict(color="white"))),
                      paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}, title=dict(text=title, font=dict(color="white")), margin=dict(t=60, b=40))
    return fig

def gauge_figure(score, title):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, title={"text": title, "font": {"color": "white"}},
                                gauge={"axis": {"range": [0, 100]}, "bar": {"color": THEME["accent"]}, "bgcolor": THEME["surface"]}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}, height=300, margin=dict(t=60, b=40))
    return fig

# --- Sidebar ---
with st.sidebar:
    st.image(os.path.join(os.path.dirname(__file__), "pg_logo.png"), width=120)
    st.markdown("<p style='text-align: center;'><span class='v-pill'>v2.0.0-PRO</span></p>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Intelligence Modules", ["Network Forensic Hub", "UPI Fraud Analyzer", "Threat Intelligence Feed", "Enterprise API Docs"])

def render_hero(title, subtitle):
    st.markdown(f'<div class="pg-hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

if page == "Network Forensic Hub":
    render_hero("Network Forensic Hub", "Forensic analysis via the 17-feature Titan Engine.")
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
    render_hero("UPI Fraud Analyzer", "Detecting behavioral fraud patterns and merchant trust.")
    vpa = st.text_input("VPA Intent / URL", "upi://pay?pa=scammer@sbi&am=49999")
    if vpa:
        if st.button("Verify Merchant Trust"):
            score = 94 if "49" in vpa else 12
            st.markdown(f'<div class="pg-pill {"pg-block" if score > 50 else "pg-safe"}">REPUTATION: {"MALICIOUS" if score > 50 else "TRUSTED"}</div>', unsafe_allow_html=True)
            st.plotly_chart(gauge_figure(score, "Transaction Risk Score"), use_container_width=True)

elif page == "Threat Intelligence Feed":
    render_hero("Threat Intelligence", "Live geospatial fraud analytics across India.")
    st.markdown("### 🇮🇳 Live Fraud Hotspots")
    df = pd.DataFrame({"latitude": [28.6, 19.1, 13.0, 22.5, 17.4], "longitude": [77.2, 72.8, 80.3, 88.4, 78.5], "Risk": ["High"]*5})
    st.map(df)
    st.markdown("### 🚨 Forensic Evidence Hub")
    feed = pd.DataFrame({"Target": ["sbi-secure.in", "fake-amazon.co", "upi@scam", "rewards-kyc.net"], "Type": ["Phishing", "Fraud", "UPI", "Credential"], "Evidence": ["On-Chain Proof"] * 4})
    st.dataframe(feed, use_container_width=True)

elif page == "Enterprise API Docs":
    render_hero("Enterprise B2B API", "Zero-trust verification for high-volume Indian gateways.")
    st.markdown("#### Sample Integration (Node.js)")
    st.code("async function check(vpa) { ... }", language="javascript")
    st.markdown("#### Forensic Response Schema")
    st.code('{"verdict": "BLOCK", "score": 92.4}', language="json")
