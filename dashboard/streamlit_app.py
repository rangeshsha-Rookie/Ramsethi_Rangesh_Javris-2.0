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
            "risk_score": 0,
            "flags": [],
            "recommendation": "SAFE",
            "parsed": {},
            "explanation": "UPI analyzer module not found."
        }

st.set_page_config(
    layout="wide",
    page_title="PhishGuard India Dashboard",
    page_icon="PG",
    initial_sidebar_state="expanded"
)

THEME = {
    "bg": "#0A0F1D",
    "surface": "#131B33",
    "surface_soft": "#1A2542",
    "border": "#2D3E61",
    "text": "#F3F4F6",
    "muted": "#9CA3AF",
    "safe": "#10B981",
    "warn": "#F59E0B",
    "block": "#EF4444",
    "accent": "#3B82F6",
}

EXPECTED_MODEL_FEATURES = [
    "url_length",
    "is_shortened",
    "has_at_symbol",
    "double_slash_redirect",
    "prefix_suffix",
    "subdomain_depth",
    "has_https",
    "domain_reg_length",
    "has_ip",
    "external_anchors_ratio",
    "suspicious_form",
    "right_click_disabled",
    "has_iframe",
    "dns_record",
    "google_index",
    "phishtank_reported",
    "domain_age",
]

st.markdown(
    f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

  :root {{
    --pg-bg: {THEME['bg']};
    --pg-surface: rgba(19, 27, 51, 0.5);
    --pg-surface-soft: rgba(26, 38, 77, 0.4);
    --pg-border: rgba(69, 89, 142, 0.3);
    --pg-text: {THEME['text']};
    --pg-muted: {THEME['muted']};
    --pg-safe: {THEME['safe']};
    --pg-warn: {THEME['warn']};
    --pg-block: {THEME['block']};
    --pg-accent: {THEME['accent']};
  }}

  /* Apply global font */
  html, body, [class*="st-"], .stApp {{
    font-family: 'Outfit', sans-serif !important;
  }}

  /* Override generic text colors to ensure visibility on dark background */
  h1, h2, h3, h4, p, span, div, label {{
    color: var(--pg-text);
  }}

  .stApp {{
    background:
      radial-gradient(ellipse at top, rgba(29, 78, 216, 0.15), transparent 60%),
      radial-gradient(ellipse at bottom right, rgba(16, 185, 129, 0.1), transparent 50%),
      linear-gradient(to bottom right, #0A0F1D, #050811);
  }}

  [data-testid="stHeader"] {{
    background: rgba(0, 0, 0, 0);
  }}

  .block-container {{
    max-width: 1220px;
    padding-top: 2rem;
    padding-bottom: 2rem;
  }}

  /* Masterfully styled Sidebar */
  [data-testid="stSidebar"] {{
    background: rgba(11, 15, 27, 0.85);
    backdrop-filter: blur(16px);
    border-right: 1px solid var(--pg-border);
  }}

  [data-testid="stSidebar"] hr {{
    border-color: rgba(255, 255, 255, 0.08);
  }}

  [data-testid="stSidebar"] [role="radiogroup"] {{
    background: rgba(19, 27, 51, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid var(--pg-border);
    border-radius: 16px;
    padding: 12px 10px;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2);
  }}

  /* Hero Section */
  .pg-hero {{
    border: 1px solid rgba(59, 130, 246, 0.3);
    background: linear-gradient(135deg, rgba(29, 78, 216, 0.2) 0%, rgba(10, 15, 29, 0.5) 100%);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 24px 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
  }}

  .pg-hero::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), transparent);
  }}

  .pg-title {{
    font-size: 36px !important;
    font-weight: 800 !important;
    line-height: 1.2 !important;
    margin: 0 !important;
    background: linear-gradient(90deg, #FFFFFF, #93C5FD);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .pg-subtitle {{
    margin: 10px 0 0 !important;
    color: #CBD5E1 !important;
    font-size: 15px !important;
    font-weight: 300 !important;
  }}

  .pg-identity {{
    margin-top: 14px;
    color: #60A5FA;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
  }}

  .pg-status-pill {{
    display: inline-block;
    border-radius: 999px;
    padding: 6px 14px;
    font-weight: 700;
    font-size: 14px;
    letter-spacing: 0.5px;
    margin: 10px 0 14px;
    border: 1px solid transparent;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }}

  .pg-safe {{
    background: rgba(16, 185, 129, 0.15);
    color: #6EE7B7;
    border-color: rgba(16, 185, 129, 0.4);
  }}

  .pg-warn {{
    background: rgba(245, 158, 11, 0.15);
    color: #FCD34D;
    border-color: rgba(245, 158, 11, 0.4);
  }}

  .pg-block {{
    background: rgba(239, 68, 68, 0.15);
    color: #FCA5A5;
    border-color: rgba(239, 68, 68, 0.4);
  }}

  /* General Cards */
  .pg-card {{
    border: 1px solid var(--pg-border);
    background: rgba(19, 27, 51, 0.6);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  }}

  .pg-chip {{
    display: inline-block;
    margin: 4px 6px 4px 0;
    border-radius: 8px;
    border: 1px solid rgba(96, 165, 250, 0.4);
    background: rgba(30, 58, 138, 0.4);
    color: #DBEAFE;
    font-size: 12px;
    padding: 6px 12px;
    font-weight: 500;
    transition: all 0.2s ease;
  }}
  .pg-chip:hover {{
    background: rgba(30, 58, 138, 0.7);
    border-color: rgba(96, 165, 250, 0.8);
  }}

  /* Inputs and Textareas */
  div[data-baseweb="input"] > div,
  div[data-baseweb="textarea"] > div,
  [data-testid="stFileUploaderDropzone"] {{
    border-radius: 14px !important;
    border: 1px solid var(--pg-border) !important;
    background: rgba(11, 15, 27, 0.6) !important;
    transition: all 0.2s ease;
  }}
  div[data-baseweb="input"] > div:focus-within,
  div[data-baseweb="textarea"] > div:focus-within {{
    border-color: var(--pg-accent) !important;
    box-shadow: 0 0 0 1px var(--pg-accent) !important;
    background: rgba(15, 23, 42, 0.8) !important;
  }}

  /* Make inputs text white */
  input, textarea {{
    color: #FFFFFF !important;
  }}
  input::placeholder, textarea::placeholder {{
    color: #64748B !important;
  }}

  /* Buttons */
  .stButton > button {{
    border-radius: 12px;
    border: 1px solid rgba(59, 130, 246, 0.6);
    background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
    color: #FFFFFF !important;
    font-weight: 600;
    padding: 0.5rem 1.25rem;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }}
  .stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
    border-color: #60A5FA;
    background: linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%);
  }}
  .stButton > button * {{
    color: #FFFFFF !important;
  }}

  /* Metrics */
  [data-testid="stMetric"] {{
    border: 1px solid var(--pg-border);
    background: rgba(19, 27, 51, 0.5);
    backdrop-filter: blur(8px);
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }}

  [data-testid="stMetricLabel"] {{
    color: #9CA3AF !important;
    font-weight: 500 !important;
  }}
  [data-testid="stMetricValue"] {{
    color: #F8FAFC !important;
    font-weight: 700 !important;
  }}

  .pg-source {{
    color: #94A3B8;
    font-size: 13px;
    margin-top: -8px;
    margin-bottom: 12px;
    font-weight: 400;
  }}
</style>
""",
    unsafe_allow_html=True,
)


def safe_get_secret(name, default=None):
    try:
        secrets = st.secrets
    except Exception:
        return default
    try:
        return secrets.get(name, default)
    except Exception:
        return default


def verdict_from_score(score):
    if score > 70:
        return "BLOCK"
    if score >= 40:
        return "WARN"
    return "SAFE"


def verdict_class(verdict):
    return {
        "SAFE": "pg-safe",
        "WARN": "pg-warn",
        "BLOCK": "pg-block",
    }.get(verdict, "pg-safe")


def verdict_color(verdict):
    return {
        "SAFE": THEME["safe"],
        "WARN": THEME["warn"],
        "BLOCK": THEME["block"],
    }.get(verdict, THEME["safe"])


def render_hero(title, subtitle):
    st.markdown(
        f"""
        <div class="pg-hero">
          <h1 class="pg-title">{title}</h1>
          <p class="pg-subtitle">{subtitle}</p>
          <div class="pg-identity">JAVRIS 2.0 | Team Ramsethi | Team ID S23</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, delta=None):
    st.metric(label=label, value=value, delta=delta)


def parse_host(url):
    candidate = url.strip()
    if not candidate:
        return ""
    if "//" not in candidate:
        candidate = f"https://{candidate}"
    parsed = urlparse(candidate)
    host = (parsed.netloc or "").split(":")[0].strip().lower()
    return host


def extract_fast_url_features(url):
    host = parse_host(url)
    subdomain_depth = max(host.count(".") - 1, 0) if host else 0
    is_shortened = 1 if any(s in host for s in ["bit.ly", "tinyurl", "t.co", "goo.gl"]) else 0
    has_https = 1 if url.strip().lower().startswith("https://") else 0
    has_at_symbol = 1 if "@" in url else 0
    double_slash_redirect = 1 if url.find("//", 8) != -1 else 0
    prefix_suffix = 1 if "-" in host else 0
    try:
        ipaddress.ip_address(host)
        has_ip = 1
    except ValueError:
        has_ip = 0

    return {
        "url_length": len(url),
        "is_shortened": is_shortened,
        "has_at_symbol": has_at_symbol,
        "double_slash_redirect": double_slash_redirect,
        "prefix_suffix": prefix_suffix,
        "subdomain_depth": subdomain_depth,
        "has_https": has_https,
        "domain_reg_length": 0,
        "has_ip": has_ip,
        "external_anchors_ratio": 0,
        "suspicious_form": 0,
        "right_click_disabled": 0,
        "has_iframe": 0,
        "dns_record": 0,
        "google_index": 1,
        "phishtank_reported": 0,
        "domain_age": 0,
    }


@st.cache_resource
def load_xgb_model():
    model_path = os.path.join(ML_ENGINE_PATH, "phishnet_xgboost.pkl")
    if not os.path.exists(model_path):
        return None
    import joblib

    return joblib.load(model_path)


def heuristic_score(features):
    score = 8
    score += min(features["url_length"] / 3, 24)
    score += 20 if features["is_shortened"] else 0
    score += 16 if features["has_at_symbol"] else 0
    score += 12 if features["double_slash_redirect"] else 0
    score += 10 if features["prefix_suffix"] else 0
    score += min(features["subdomain_depth"] * 8, 20)
    score += 14 if features["has_ip"] else 0
    score -= 10 if features["has_https"] else 0
    jitter = random.uniform(-4, 4)
    return max(0, min(int(round(score + jitter)), 100))


def check_url(url):
    features = extract_fast_url_features(url)
    row = [features.get(col, 0) for col in EXPECTED_MODEL_FEATURES]
    frame = pd.DataFrame([row], columns=EXPECTED_MODEL_FEATURES)

    model = load_xgb_model()
    if model is None:
        score = heuristic_score(features)
        return {
            "risk_score": score,
            "verdict": verdict_from_score(score),
            "features": features,
            "source": "simulated (model not found)",
        }

    try:
        probability = float(model.predict_proba(frame)[0][1])
        score = int(round(probability * 100))
        return {
            "risk_score": score,
            "verdict": verdict_from_score(score),
            "features": features,
            "source": "xgboost model",
        }
    except Exception:
        score = heuristic_score(features)
        return {
            "risk_score": score,
            "verdict": verdict_from_score(score),
            "features": features,
            "source": "simulated (model fallback)",
        }


def gauge_figure(score, verdict, title):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": title},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#9fb6e8"},
                "bar": {"color": verdict_color(verdict)},
                "steps": [
                    {"range": [0, 39], "color": "rgba(34, 197, 94, 0.18)"},
                    {"range": [40, 70], "color": "rgba(245, 158, 11, 0.18)"},
                    {"range": [71, 100], "color": "rgba(239, 68, 68, 0.18)"},
                ],
                "threshold": {
                    "line": {"color": "#cdd9fa", "width": 2},
                    "thickness": 0.75,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": THEME["text"], "size": 14},
    )
    return fig


def render_flag_chips(flags):
    if not flags:
        st.write("No fraud flags detected.")
        return
    chip_html = "".join([f'<span class="pg-chip">{flag}</span>' for flag in flags])
    st.markdown(chip_html, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_sample_data():
    csv_path = os.path.join(os.path.dirname(__file__), "sample_data.csv")
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    return pd.read_csv(csv_path)


def load_analytics_data():
    mongo_uri = safe_get_secret("MONGODB_URI")
    if mongo_uri:
        try:
            import pymongo

            client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=2500)
            records = list(client.phishguard.fraud_reports.find())
            if records:
                return pd.DataFrame(records), "mongodb", None
        except Exception as exc:
            return load_sample_data(), "sample_data", f"MongoDB unavailable: {exc}"

    return load_sample_data(), "sample_data", None


def normalize_analytics(df):
    if df.empty:
        return df

    clean = df.copy()
    if "timestamp" in clean.columns:
        clean["timestamp"] = pd.to_datetime(clean["timestamp"], errors="coerce")
        clean = clean.dropna(subset=["timestamp"])

    if "verdict" not in clean.columns:
        clean["verdict"] = "SAFE"
    clean["verdict"] = clean["verdict"].astype(str).str.upper()

    if "flags" not in clean.columns:
        clean["flags"] = "none"
    clean["flags"] = clean["flags"].fillna("none")

    if "risk_score" in clean.columns:
        clean["risk_score"] = pd.to_numeric(clean["risk_score"], errors="coerce").fillna(0).astype(int)

    if "type" not in clean.columns:
        clean["type"] = "unknown"

    return clean


with st.sidebar:
    st.image("pg_logo.png", width=80)
    st.markdown("## PhishGuard India")
    st.caption("Real-time phishing and UPI fraud analytics")
    page = st.radio(
        "Navigation",
        ["URL Scanner", "UPI QR Analyzer", "Analytics Dashboard"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.caption("Team Ramsethi | S23")
    st.caption("Members: Rangesh Gupta, Ansh Jasiwal")


if page == "URL Scanner":
    render_hero("URL Scanner", "Analyze suspicious links with model-backed risk scoring.")

    st.markdown('<div class="pg-card">', unsafe_allow_html=True)
    url = st.text_input("Enter URL", placeholder="https://secure-bank-verification.example")
    scan_clicked = st.button("Scan URL", use_container_width=False)
    st.markdown("</div>", unsafe_allow_html=True)

    if scan_clicked:
        if not url.strip():
            st.warning("Please enter a URL before scanning.")
        else:
            st.session_state["url_result"] = check_url(url.strip())

    result = st.session_state.get("url_result")
    if result:
        risk_score = int(result["risk_score"])
        verdict = result["verdict"]
        source = result["source"]

        st.markdown(
            f'<div class="pg-status-pill {verdict_class(verdict)}">Verdict: {verdict} | Risk: {risk_score}/100</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="pg-source">Model source: {source}</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.plotly_chart(gauge_figure(risk_score, verdict, "Phishing Risk"), use_container_width=True)
        with col2:
            feature_df = pd.DataFrame(
                list(result["features"].items()), columns=["Feature", "Value"]
            ).sort_values("Value", ascending=True)
            feature_fig = px.bar(
                feature_df,
                x="Value",
                y="Feature",
                orientation="h",
                title="Extracted Feature Snapshot",
                color="Value",
                color_continuous_scale=["#35589d", "#62a1ff"],
            )
            feature_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"color": THEME["text"]},
                margin=dict(l=10, r=10, t=40, b=10),
                coloraxis_showscale=False,
            )
            st.plotly_chart(feature_fig, use_container_width=True)

elif page == "UPI QR Analyzer":
    render_hero("UPI QR Analyzer", "Validate UPI deeplinks and uploaded QR payloads before payment.")

    st.markdown('<div class="pg-card">', unsafe_allow_html=True)
    upi_input = st.text_area(
        "Paste UPI String",
        placeholder="upi://pay?pa=merchant@ybl&pn=Display Name&am=49999&cu=INR",
        height=120,
    )
    upload = st.file_uploader("Or upload QR image", type=["png", "jpg", "jpeg"])
    st.markdown("</div>", unsafe_allow_html=True)

    decoded_payload = ""
    if upload is not None:
        if decode is None:
            st.info("QR image decode is unavailable because pyzbar/zbar is not installed on this system.")
        else:
            image = Image.open(upload)
            decoded = decode(image)
            if decoded:
                decoded_payload = decoded[0].data.decode("utf-8", errors="ignore")
                st.success("QR decoded successfully.")
                st.code(decoded_payload)
            else:
                st.warning("No readable QR content was found in the uploaded image.")

    analyze_clicked = st.button("Analyze UPI", use_container_width=False)
    if analyze_clicked:
        candidate = (decoded_payload or upi_input or "").strip()
        if not candidate.startswith("upi://pay"):
            st.error("Invalid UPI input. Start with upi://pay")
        else:
            st.session_state["upi_result"] = analyze_upi_qr(candidate)

    result = st.session_state.get("upi_result")
    if result:
        score = int(result.get("risk_score", 0))
        recommendation = str(result.get("recommendation", "SAFE")).upper()
        flags = result.get("flags", [])
        explanation = result.get("explanation", "")
        parsed = result.get("parsed", {})

        st.markdown(
            f'<div class="pg-status-pill {verdict_class(recommendation)}">Recommendation: {recommendation} | Risk: {score}/100</div>',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card("Risk Score", score)
        with col2:
            metric_card("Detected Flags", len(flags))
        with col3:
            metric_card("Decision", recommendation)

        st.plotly_chart(gauge_figure(score, recommendation, "UPI Fraud Risk"), use_container_width=True)

        st.markdown("### Flags")
        render_flag_chips(flags)

        st.markdown("### Explanation")
        st.info(explanation or "No explanation available.")

        st.markdown("### Parsed Fields")
        if parsed:
            parsed_df = pd.DataFrame(parsed.items(), columns=["Field", "Value"])
            st.dataframe(parsed_df, use_container_width=True, hide_index=True)
        else:
            st.write("No parsed fields available.")

else:
    render_hero("Analytics Dashboard", "Track scan trends, threat distribution, and operational metrics.")

    analytics_df, source, error_message = load_analytics_data()
    if error_message:
        st.warning(error_message)

    if source == "sample_data":
        st.info("Running in sample-data mode. Add MONGODB_URI in Streamlit secrets to use live reports.")

    analytics_df = normalize_analytics(analytics_df)
    if analytics_df.empty:
        st.warning("No analytics data found. Add sample_data.csv or connect MongoDB.")
    else:
        total_scans = len(analytics_df)
        blocked = int((analytics_df["verdict"] == "BLOCK").sum())
        warned = int((analytics_df["verdict"] == "WARN").sum())
        safe = int((analytics_df["verdict"] == "SAFE").sum())

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Total Scans", total_scans)
        with c2:
            metric_card("Threats Blocked", blocked)
        with c3:
            metric_card("Warnings", warned)
        with c4:
            metric_card("Safe", safe)

        daily = (
            analytics_df.groupby([analytics_df["timestamp"].dt.date, "verdict"]).size().reset_index(name="count")
        )
        daily.columns = ["date", "verdict", "count"]

        line_fig = px.line(
            daily,
            x="date",
            y="count",
            color="verdict",
            title="Daily Scan Volume",
            markers=True,
            color_discrete_map={
                "SAFE": THEME["safe"],
                "WARN": THEME["warn"],
                "BLOCK": THEME["block"],
            },
        )
        line_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": THEME["text"]},
            margin=dict(l=10, r=10, t=40, b=10),
            legend_title_text="Verdict",
            xaxis_title="Date",
            yaxis_title="Scans",
        )

        flag_series = (
            analytics_df["flags"]
            .astype(str)
            .str.split(",")
            .explode()
            .str.strip()
        )
        flag_series = flag_series[(flag_series != "") & (flag_series.str.lower() != "none")]

        col_left, col_right = st.columns([1.35, 1])
        with col_left:
            st.plotly_chart(line_fig, use_container_width=True)
        with col_right:
            if not flag_series.empty:
                flag_counts = flag_series.value_counts().reset_index()
                flag_counts.columns = ["flag", "count"]
                pie_fig = px.pie(
                    flag_counts,
                    values="count",
                    names="flag",
                    hole=0.45,
                    title="Flag Distribution",
                    color_discrete_sequence=["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#94a3b8"],
                )
                pie_fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font={"color": THEME["text"]},
                    margin=dict(l=10, r=10, t=40, b=10),
                    legend_title_text="Flag",
                )
                st.plotly_chart(pie_fig, use_container_width=True)
            else:
                st.markdown('<div class="pg-card">No flagged records available yet.</div>', unsafe_allow_html=True)

        st.markdown("### Recent Reports")
        show_columns = [col for col in ["timestamp", "type", "identifier", "risk_score", "verdict", "flags"] if col in analytics_df.columns]
        recent = analytics_df.sort_values("timestamp", ascending=False).head(20)[show_columns]
        st.dataframe(recent, use_container_width=True, hide_index=True)
