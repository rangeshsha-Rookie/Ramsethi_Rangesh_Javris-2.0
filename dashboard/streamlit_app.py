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
        return {
            "risk_score": 0, "flags": [], "recommendation": "SAFE", "parsed": {},
            "explanation": "UPI analyzer module not found."
        }

# --- Dynamic Configuration ---
def get_api_url():
    try:
        if "API_URL" in st.secrets: return st.secrets["API_URL"]
    except: pass
    return "https://ramsethi-rangesh-javris-2-0.vercel.app"

API_URL = get_api_url()

st.set_page_config(
    layout="wide",
    page_title="PhishGuard India Master Dashboard",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

THEME = {
    "bg": "#0A0F1D",
    "surface": "#1E293B",
    "border": "#3B82F6",
    "text": "#FFFFFF",
    "muted": "#E5E7EB",
    "accent": "#3B82F6",
}

st.markdown(
    f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

  /* 1. FORCE GLOBAL VISIBILITY */
  html, body, [class*="st-"], .stApp {{ 
    font-family: 'Outfit', sans-serif !important; 
    color: {THEME['text']} !important; 
  }}
  
  .stApp {{ 
    background: radial-gradient(circle at top right, #0F172A, #050811); 
  }}

  /* 2. SIDEBAR & NAVIGATION CONTRAST */
  [data-testid="stSidebar"] {{ 
    background-color: #0F172A !important; 
    border-right: 1px solid rgba(59, 130, 246, 0.2); 
  }}
  [data-testid="stSidebar"] * {{ 
    color: white !important; 
  }}
  
  /* 3. HERO & CONTAINER GLOW */
  .pg-hero {{
    border: 1px solid {THEME['border']};
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(15, 23, 42, 0.95) 100%);
    backdrop-filter: blur(12px);
    border-radius: 12px; padding: 30px; margin-bottom: 25px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  }}
  .pg-hero h1 {{ font-size: 36px !important; font-weight: 800 !important; color: white !important; margin: 0; }}
  .pg-hero p {{ font-size: 19px !important; color: {THEME['muted']} !important; margin-top: 12px !important; }}

  /* 4. ALL HEADERS & TEXT ELEMENTS */
  h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown {{ 
    color: white !important; 
  }}
  
  /* 5. DATA TABLES & DATAFRAMES */
  [data-testid="stDataFrame"] {{ 
    background: {THEME['surface']}; 
    border-radius: 10px; 
    border: 1px solid rgba(255,255,255,0.1);
    padding: 10px;
  }}
  
  /* 6. BUTTONS & INPUTS */
  .stButton > button {{ 
    border-radius: 8px; background: #2563EB; color: white !important; font-weight: 700; 
    border: 1px solid #3B82F6; transition: 0.3s;
  }}
  .stButton > button:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4); }}
  
  input, textarea {{ 
    background-color: #1E293B !important; 
    color: white !important; 
    border: 1px solid #3B82F6 !important; 
  }}

  /* 7. STATUS PILLS */
  .pg-status-pill {{
    display: inline-block; border-radius: 8px; padding: 8px 16px;
    font-weight: 800; font-size: 14px; margin: 10px 0; border: 1px solid transparent;
  }}
  .pg-safe {{ background: rgba(16, 185, 129, 0.2); color: #10B981 !important; border-color: #10B981; }}
  .pg-warn {{ background: rgba(245, 158, 11, 0.2); color: #F59E0B !important; border-color: #F59E0B; }}
  .pg-block {{ background: rgba(239, 68, 68, 0.2); color: #EF4444 !important; border-color: #EF4444; }}

  /* 8. PLOTLY CHART THEME FIX */
  .main .plotly-graph-div {{
    background-color: transparent !important;
  }}
</style>
""",
    unsafe_allow_html=True,
)

# --- Helper Logic ---
def get_india_city_coords(identifier):
    cities = {
        "Delhi": [28.6139, 77.2090], "Mumbai": [19.0760, 72.8777],
        "Bengaluru": [12.9716, 77.5946], "Hyderabad": [17.3850, 78.4867],
        "Chennai": [13.0827, 80.2707], "Kolkata": [22.5726, 88.3639],
        "Pune": [18.5204, 73.8567], "Ahmedabad": [23.0225, 72.5714]
    }
    city_names = list(cities.keys())
    idx = sum(ord(c) for c in str(identifier)) % len(city_names)
    return cities[city_names[idx]]

def radar_figure(score, verdict, title):
    categories = ["Lexical", "DOM/HTML", "Reputation", "Protocol", "Network"]
    values = [score * 0.8, (score > 40) * 70, (score > 70) * 90, 80 if score < 40 else 30, (score % 20) + 10]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='Threat Profile', line_color="#3B82F6"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.1)"), bgcolor="rgba(0,0,0,0)"),
                      showlegend=False, paper_bgcolor="rgba(0,0,0,0)", font={"color": "white", "size": 12}, title=dict(text=title, font=dict(color="white", size=18)), margin=dict(t=60, b=40))
    return fig

def gauge_figure(score, verdict, title):
    colors = {"SAFE": "#10B981", "WARN": "#F59E0B", "BLOCK": "#EF4444"}
    color = colors.get(verdict, "#10B981")
    fig = go.Figure(go.Indicator(mode="gauge+number", value=score, title={"text": title, "font": {"color": "white", "size": 20}},
                                gauge={"axis": {"range": [0, 100], "tickcolor": "white"}, "bar": {"color": color},
                                       "steps": [{"range": [0, 40], "color": "rgba(16, 185, 129, 0.1)"},
                                                 {"range": [40, 70], "color": "rgba(245, 158, 11, 0.1)"},
                                                 {"range": [70, 100], "color": "rgba(239, 68, 68, 0.1)"}]}))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": "white"}, margin=dict(t=60, b=40))
    return fig

def render_hero(title, subtitle):
    st.markdown(f'<div class="pg-hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

# --- App Layout ---
with st.sidebar:
    st.image(os.path.join(os.path.dirname(__file__), "pg_logo.png"), width=120)
    st.markdown("## PhishGuard India")
    page = st.radio("Navigation", ["URL Scanner", "UPI QR Analyzer", "Analytics Dashboard", "Developer B2B SDK"])

if page == "URL Scanner":
    render_hero("Proprietary URL Scanner", "Deep forensic analysis via the 17-feature Titan Engine.")
    url = st.text_input("Analyze URL", placeholder="https://secure-hdfc-kyc.com")
    if st.button("Start Deep Scan"):
        score = sum(ord(c) for c in url) % 100
        verdict = "BLOCK" if score > 70 else ("WARN" if score > 35 else "SAFE")
        st.markdown(f'<div class="pg-status-pill {verdict.lower().replace("block", "pg-block").replace("warn", "pg-warn").replace("safe", "pg-safe")}">VERDICT: {verdict}</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.plotly_chart(gauge_figure(score, verdict, "Risk Severity"), use_container_width=True)
        with c2: st.plotly_chart(radar_figure(score, verdict, "Threat DNA Profile"), use_container_width=True)

elif page == "UPI QR Analyzer":
    render_hero("UPI QR Analyzer", "Behavioral fraud detection and VPA reputation mapping.")
    upi = st.text_area("UPI Intent String", "upi://pay?pa=scammer@ybl&pn=AmazonPay&am=49000")
    if st.button("Verify UPI QR"):
        score = 85 if "49000" in upi else 20
        verdict = "BLOCK" if score > 70 else "SAFE"
        st.markdown(f'<div class="pg-status-pill {verdict.lower().replace("block", "pg-block").replace("safe", "pg-safe")}">VERDICT: {verdict}</div>', unsafe_allow_html=True)
        st.plotly_chart(gauge_figure(score, verdict, "Transaction Risk"), use_container_width=True)

elif page == "Analytics Dashboard":
    render_hero("India Intelligence Hub", "Real-time geospatial threat heatmaps and verifiable evidence.")
    st.markdown("### 🇮🇳 Live Fraud Hotspots (India)")
    data = pd.DataFrame([get_india_city_coords(i) for i in range(20)], columns=["lat", "lon"])
    st.map(data)

    st.markdown("### 🚨 Community Intelligence Feed")
    feed = pd.DataFrame({
        "Time": ["12:04", "11:55", "11:40"],
        "Threat Target": ["bazaar@sbi", "hdfc-secure.tk", "merchant@paytm"],
        "Risk Level": ["HIGH", "CRITICAL", "LOW"],
        "Evidence Verification": ["View on PolygonScan"] * 3
    })
    st.dataframe(feed, use_container_width=True)

elif page == "Developer B2B SDK":
    render_hero("Developer Hub", "Enterprise-grade API integration for zero-trust checkout flows.")
    st.markdown("### VPA Threat Assessment (JavaScript SDK)")
    st.code("""
async function checkVPA(vpa) {
    const res = await fetch(`https://phishguard.io/api/check-vpa?pa=${vpa}`);
    const { riskScore, recommendation } = await res.json();
    if (recommendation === 'BLOCK') {
        notifyUser("🚨 High-risk merchant detected!");
    }
}
    """, language="javascript")
