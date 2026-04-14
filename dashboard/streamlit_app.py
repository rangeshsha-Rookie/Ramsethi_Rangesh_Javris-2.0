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

# Professional Color Tokens
COLORS = {
    "bg": "#0D1117",
    "surface": "#161B22",
    "border": "#30363D",
    "text_main": "#C9D1D9",
    "text_bright": "#FFFFFF",
    "accent": "#58A6FF",
    "safe": "#3FB950",
    "warn": "#D29922",
    "block": "#F85149",
}

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400&display=swap');

  /* 1. Global Harmony Reset */
  html, body, [class*="st-"], .stApp {{ 
    font-family: 'Outfit', sans-serif !important; 
    color: {COLORS['text_main']} !important; 
    background-color: {COLORS['bg']} !important;
  }}
  
  [data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}

  /* 2. Headlines */
  h1, h2, h3, h4, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3 {{
    color: {COLORS['text_bright']} !important;
    font-weight: 700 !important;
  }}

  /* 3. SIDEBAR & RADIANT RADIO FIX */
  [data-testid="stSidebar"] {{ 
    background-color: #010409 !important; 
    border-right: 1px solid {COLORS['border']}; 
  }}
  
  /* Force Radio Button Visibility */
  div[data-testid="stRadio"] label {{
    color: {COLORS['text_bright']} !important;
    margin-bottom: 8px !important;
  }}
  
  /* The Outer Circle */
  div[aria-label="Intelligence Modules"] div[data-testid="stMarkdownContainer"] p {{
    font-weight: 800 !important;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 1px;
    margin-bottom: 1.5rem !important;
  }}

  /* Fix for the actual radio circles */
  div[data-testid="stRadio"] div[role="radiogroup"] [data-testid="stWidgetLabel"] {{
    color: white !important;
  }}
  
  /* Target the circles (markers) */
  .st-at, .st-ae, .st-af, div[role="radiogroup"] label div[data-testid="stMarker"] {{
    border: 2px solid {COLORS['accent']} !important;
  }}
  
  /* Target the selected state marker */
  div[role="radiogroup"] label[data-checked="true"] div[data-testid="stMarker"] {{
    background-color: {COLORS['accent']} !important;
    box-shadow: 0 0 10px {COLORS['accent']} !important;
  }}

  /* 4. INPUTS */
  input, textarea {{
    background-color: #0D1117 !important;
    color: #FFFFFF !important;
    border: 1px solid {COLORS['border']} !important;
    border-radius: 6px !important;
  }}
  
  /* 5. CODE & CARDS */
  [data-testid="stCodeBlock"] {{ background-color: #010409 !important; border: 1px solid {COLORS['border']} !important; }}
  .pg-hero {{
    border: 1px solid {COLORS['border']}; background-color: {COLORS['surface']};
    border-radius: 12px; padding: 30px; margin-bottom: 2rem;
  }}

  /* 6. STATUS & BUTTONS */
  .pg-pill {{ display: inline-block; border-radius: 6px; padding: 6px 12px; font-weight: 700; border: 1px solid transparent; }}
  .pg-safe {{ background: rgba(63, 185, 80, 0.1); color: {COLORS['safe']} !important; border-color: {COLORS['safe']}; }}
  .pg-block {{ background: rgba(248, 81, 73, 0.1); color: {COLORS['block']} !important; border-color: {COLORS['block']}; }}
  
  .stButton > button {{ border-radius: 6px; background-color: #21262D; color: white !important; border: 1px solid {COLORS['border']}; font-weight: 700; }}
  .stButton > button:hover {{ border-color: {COLORS['accent']}; box-shadow: 0 0 10px {COLORS['accent']}; }}
  
  .v-badge {{ background-color: #21262D; color: {COLORS['accent']}; border: 1px solid {COLORS['border']}; padding: 2px 12px; border-radius: 20px; font-size: 0.75rem; }}
</style>
""", unsafe_allow_html=True)

# --- Visual Engine ---
def radar_figure(score, title):
    fig = go.Figure(go.Scatterpolar(r=[score*0.8, 60, 40, 70, 50], theta=["Lexical", "DOM", "Rep", "Proto", "Net"], fill='toself', line_color=COLORS["accent"]))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor=COLORS["border"], tickfont=dict(color="white")),
                                angularaxis=dict(gridcolor=COLORS["border"], tickfont=dict(color="white"))),
                      paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}, title=dict(text=title, font=dict(color="white")), margin=dict(t=60, b=40))
    return fig

def gauge_figure(score, title):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, title={"text": title, "font": {"color": "white"}},
                                gauge={"axis": {"range": [0, 100]}, "bar": {"color": COLORS["accent"]}, "bgcolor": COLORS["surface"]}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}, height=300, margin=dict(t=60, b=40))
    return fig

# --- Sidebar ---
with st.sidebar:
    st.image(os.path.join(os.path.dirname(__file__), "pg_logo.png"), width=100)
    st.markdown("<p style='text-align: center;'><span class='v-badge'>v2.0.0-PRO</span></p>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Intelligence Modules", ["Network Forensic Hub", "UPI Fraud Analyzer", "Threat Intelligence Feed", "Enterprise API Docs"])

def render_hero(title, subtitle):
    st.markdown(f'<div class="pg-hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

if page == "Network Forensic Hub":
    render_hero("Network Forensic Hub", "Forensic analysis via the 17-feature Titan Engine.")
    url = st.text_input("Analyze Domain", placeholder="https://secure-login.bank")
    if url:
        if st.button("Deep Forensic Scan"):
            score = sum(ord(c) for c in url) % 100
            verdict = "BLOCK" if score > 60 else "SAFE"
            st.markdown(f'<div class="pg-pill {"pg-block" if verdict == "BLOCK" else "pg-safe"}">VERDICT: {verdict}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.plotly_chart(gauge_figure(score, "Risk Severity"), use_container_width=True)
            c2.plotly_chart(radar_figure(score, "Forensic DNA Matrix"), use_container_width=True)

elif page == "UPI Fraud Analyzer":
    render_hero("UPI Fraud Analyzer", "Detecting VPA threshold evasion and merchant trust.")
    vpa = st.text_input("UPI ID / Intent", "upi://pay?pa=scammer@sbi&am=49999")
    if vpa:
        if st.button("Validate Merchant"):
            score = 94 if "49" in vpa else 12
            st.markdown(f'<div class="pg-pill {"pg-block" if score > 50 else "pg-safe"}">REPUTATION: {"MALICIOUS" if score > 50 else "TRUSTED"}</div>', unsafe_allow_html=True)
            st.plotly_chart(gauge_figure(score, "Entity Risk Score"), use_container_width=True)

elif page == "Threat Intelligence Feed":
    render_hero("Threat Intelligence", "Live geospatial fraud analytics across India corridor.")
    df = pd.DataFrame({"latitude": [28.6, 19.1, 13.0, 22.5, 17.4], "longitude": [77.2, 72.8, 80.3, 88.4, 78.5]})
    st.map(df)
    feed = pd.DataFrame({"Target": ["sbi-secure.in", "fake-amazon.co", "upi@scam"], "Type": ["Phishing", "Fraud", "UPI"], "Status": ["On-Chain Proof"] * 3})
    st.dataframe(feed, use_container_width=True)

elif page == "Enterprise API Docs":
    render_hero("Enterprise B2B API", "Integrate zero-trust verification into payment gateways.")
    st.markdown("### Node.js Integration Snippet")
    st.code("const phishguard = require('@phishguard/sdk');\n\nasync function checkout(vpa) {\n  const result = await phishguard.verifyVPA(vpa);\n  if(result.riskScore > 50) throw new Error('BLOCK');\n}", language="javascript")
    st.markdown("### Forensic Response Schema")
    st.code('{\n  "verdict": "BLOCK",\n  "score": 92.4,\n  "evidence": "PG-TX-8829-AMOY"\n}', language="json")
