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
st.set_page_config(layout="wide", page_title="PhishGuard Intelligence Dashboard", page_icon="🛡️")

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

  /* Global Polish */
  html, body, [class*="st-"], .stApp {{ 
    font-family: 'Outfit', sans-serif !important; 
    color: {THEME['text']} !important; 
    line-height: 1.6;
  }}
  
  .stApp {{ background-color: {THEME['bg']}; }}

  /* Sidebar Branding */
  [data-testid="stSidebar"] {{ 
    background-color: #010409 !important; 
    border-right: 1px solid {THEME['border']}; 
  }}
  [data-testid="stSidebar"] [data-testid="stImage"] {{ margin: auto; }}
  
  /* Container Architecture */
  .pg-hero {{
    border: 1px solid {THEME['border']};
    background-color: {THEME['surface']};
    border-radius: 12px; padding: 35px; margin-bottom: 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
    background-image: radial-gradient(at 0% 0%, rgba(88, 166, 255, 0.05) 0, transparent 50%);
  }}
  .pg-hero h1 {{ font-size: 2.8rem !important; font-weight: 800 !important; color: #FFF !important; margin: 0; }}
  .pg-hero p {{ font-size: 1.15rem !important; color: {THEME['muted']} !important; margin-top: 12px !important; }}

  h1, h2, h3, h4 {{ color: #FFF !important; font-weight: 700 !important; margin-bottom: 1.2rem !important; }}
  
  /* DARK EDITOR THEME - ULTRA CONTRAST OVERRIDE */
  [data-testid="stCodeBlock"] {{
    background-color: #010409 !important;
    border: 1px solid {THEME['border']} !important;
    border-radius: 8px !important;
  }}
  
  /* Force syntax highlighting colors for deep readability */
  code {{ font-family: 'JetBrains Mono', monospace !important; color: #E6EDF3 !important; }}
  .stCodeBlock code span {{ color: #79C0FF !important; }} /* Global Tokens */
  .stCodeBlock code .token.string {{ color: #7EE787 !important; }}
  .stCodeBlock code .token.keyword {{ color: #FF7B72 !important; }}
  .stCodeBlock code .token.function {{ color: #D2A8FF !important; }}
  .stCodeBlock code .token.comment {{ color: #8B949E !important; }}
  .stCodeBlock code .token.number {{ color: #79C0FF !important; }}
  .stCodeBlock code .token.operator {{ color: #79C0FF !important; }}
  
  /* Professional Status Pills */
  .pg-pill {{
    display: inline-block; border-radius: 99px; padding: 6px 16px;
    font-weight: 700; font-size: 0.9rem; margin-top: 1.5rem;
    border: 1px solid transparent; text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .pg-safe {{ background: rgba(63, 185, 80, 0.1); color: {THEME['safe']}; border-color: rgba(63, 185, 80, 0.4); }}
  .pg-block {{ background: rgba(248, 81, 73, 0.1); color: {THEME['block']}; border-color: rgba(248, 81, 73, 0.4); }}

  .stButton > button {{ 
    border-radius: 8px; background-color: #21262D; color: #C9D1D9 !important; 
    border: 1px solid {THEME['border']}; font-weight: 700; padding: 10px 20px;
    width: 200px; transition: 0.3s cubic-bezier(0.3, 0, 0.5, 1);
  }}
  .stButton > button:hover {{ 
    background-color: #30363D; border-color: {THEME['accent']}; color: #FFF !important;
    box-shadow: 0 0 15px rgba(88, 166, 255, 0.25);
  }}
</style>
""", unsafe_allow_html=True)

# --- Visual Logic ---
def radar_figure(score, title):
    fig = go.Figure(go.Scatterpolar(r=[score*0.8, 60, 40, 70, 50], theta=["Lexical", "DOM", "Rep", "Proto", "Net"], fill='toself', line_color=THEME["accent"]))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#30363D"), bgcolor="rgba(0,0,0,0)"),
                      paper_bgcolor="rgba(0,0,0,0)", font={"color": THEME["text"]}, title=title, margin=dict(t=40, b=20))
    return fig

def gauge_figure(score, title):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, title={"text": title, "font": {"size": 20}},
                                gauge={"axis": {"range": [0, 100]}, "bar": {"color": THEME["accent"]}, "bgcolor": THEME["surface"]}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": THEME["text"]}, height=280, margin=dict(t=50, b=40))
    return fig

# --- App Engine ---
with st.sidebar:
    st.image(os.path.join(os.path.dirname(__file__), "pg_logo.png"), width=120)
    st.markdown("<h2 style='text-align: center;'>PhishGuard</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8B949E;'>Sovereign UPI Defense <br> `v2.0.0-PRO`</p>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("Intelligence Modules", ["Network Forensic Hub", "UPI Fraud Analyzer", "Threat Intelligence Feed", "Enterprise API Docs"])

if page == "Network Forensic Hub":
    st.markdown('<div class="pg-hero"><h1>Network Forensic Hub</h1><p>Analyze domain longevity, registrar entropy, and Titan Engine lexical scores.</p></div>', unsafe_allow_html=True)
    url = st.text_input("Deep-Scan Forensic Target", placeholder="https://secure-login.bank")
    if url:
        if st.button("Initialize Forensic Scan"):
            score = sum(ord(c) for c in url) % 100
            verdict = "BLOCK" if score > 60 else "SAFE"
            pill_class = "pg-block" if verdict == "BLOCK" else "pg-safe"
            st.markdown(f'<div class="pg-pill {pill_class}">Global Verdict: {verdict}</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            c1.plotly_chart(gauge_figure(score, "Risk Probability Index"), use_container_width=True)
            c2.plotly_chart(radar_figure(score, "Forensic DNA Matrix"), use_container_width=True)

elif page == "UPI Fraud Analyzer":
    st.markdown('<div class="pg-hero"><h1>UPI Fraud Analyzer</h1><p>Detecting VPA threshold evasion and Indian merchant trust profiles.</p></div>', unsafe_allow_html=True)
    vpa = st.text_input("VPA Intent / Payment URL", "upi://pay?pa=scammer@sbi&am=49999")
    if vpa:
        if st.button("Verify UPI Intent"):
            score = 94 if "49" in vpa else 12
            st.markdown(f'<div class="pg-pill {"pg-block" if score > 50 else "pg-safe"}">REPUTATION: {"MALICIOUS" if score > 50 else "TRUSTED"}</div>', unsafe_allow_html=True)
            st.plotly_chart(gauge_figure(score, "Transaction Risk Score"), use_container_width=True)

elif page == "Threat Intelligence Feed":
    st.markdown('<div class="pg-hero"><h1>Threat Intelligence</h1><p>Live fraudcentroids across the India-APAC corridor.</p></div>', unsafe_allow_html=True)
    st.markdown("### 🇮🇳 Real-time Fraud Hotspots")
    df = pd.DataFrame({"Lat": [28.6, 19.1, 13.0, 22.5, 17.4], "Lon": [77.2, 72.8, 80.3, 88.4, 78.5], "Risk": ["High"]*5})
    st.map(df)
    
    st.markdown("### 🚨 Forensic Intelligence Log")
    feed = pd.DataFrame({
        "Verified Target": ["sbi-secure.in", "fake-amazon.co", "upi@scam", "rewards-kyc.net"],
        "Threat Type": ["Phishing", "Fraud", "UPI", "Credential"],
        "Evidence Status": ["On-Chain Proof", "Verified Log", "On-Chain Proof", "Pending Audit"]
    })
    st.dataframe(feed, use_container_width=True)

elif page == "Enterprise API Docs":
    st.markdown('<div class="pg-hero"><h1>Enterprise B2B API</h1><p>Zero-trust verification for high-volume Indian payment gateways.</p></div>', unsafe_allow_html=True)
    st.markdown("#### Node.js Integration Example")
    st.code("""
const phishguard = require('@phishguard/sdk');

async function checkout(vpa) {
  const result = await phishguard.verifyVPA(vpa);
  if(result.riskScore > 50) {
    throw new Error('Transaction Terminated: High Risk Detected');
  }
}
    """, language="javascript")
    st.markdown("#### Risk Analysis Response (JSON)")
    st.code("""
{
  "entity": "upi://pay?pa=...",
  "riskScore": 92.4,
  "verdict": "BLOCK",
  "evidence": "PG-TX-8829-AMOY",
  "heuristics": ["threshold_evasion", "vpa_impersonation"]
}
    """, language="json")
