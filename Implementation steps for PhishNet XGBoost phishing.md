<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Implementation steps for PhishNet XGBoost phishing detector

Dataset sources for training UPI QR scam models
How to deploy Streamlit dashboard for fraud visualization

Here is the complete, implementation-ready guide for all three components — PhishNet XGBoost, UPI QR dataset sourcing, and Streamlit dashboard deployment.

***

# Implementation Guide: Track 2 Phishing + UPI Fraud Detector


***

## Part 1: PhishNet XGBoost Phishing Detector

XGBoost consistently outperforms all other classifiers for phishing URL detection across research benchmarks — 98–99.74% accuracy on URL + HTML hybrid features, with the best accuracy-to-latency tradeoff for real-time use.[^1][^2]

### Step 1 — Install Dependencies

```python
pip install xgboost scikit-learn pandas numpy \
            requests tldextract whois beautifulsoup4 \
            joblib flask
```


### Step 2 — Feature Engineering (The Core Logic)

This is the most critical part. XGBoost needs structured numerical features, not raw text. Extract **three categories** of features from any URL:[^3][^4]

**Category A — Address Bar Features (9 features)**

```python
import re
import tldextract
import whois
from urllib.parse import urlparse
from datetime import datetime

def extract_url_features(url):
    features = {}
    parsed = urlparse(url)
    ext = tldextract.extract(url)

    # 1. URL Length (>75 chars = suspicious)
    features['url_length'] = len(url)

    # 2. Shortening Service (bit.ly, tinyurl etc.)
    shorteners = ['bit.ly','tinyurl','goo.gl','t.co','ow.ly']
    features['is_shortened'] = 1 if any(s in url for s in shorteners) else 0

    # 3. @ Symbol in URL (forces browser to ignore prefix)
    features['has_at_symbol'] = 1 if '@' in url else 0

    # 4. Double slash redirect (//)
    features['double_slash_redirect'] = 1 if url.rfind('//') > 6 else 0

    # 5. Prefix/Suffix hyphen in domain
    features['prefix_suffix'] = 1 if '-' in ext.domain else 0

    # 6. Subdomain depth (>3 dots = suspicious)
    features['subdomain_depth'] = url.count('.')

    # 7. HTTPS presence
    features['has_https'] = 1 if parsed.scheme == 'https' else 0

    # 8. Domain registration length (expired soon = suspicious)
    try:
        w = whois.whois(parsed.netloc)
        exp_date = w.expiration_date
        if isinstance(exp_date, list): exp_date = exp_date[^0]
        days_remaining = (exp_date - datetime.now()).days
        features['domain_reg_length'] = 0 if days_remaining < 365 else 1
    except:
        features['domain_reg_length'] = -1  # unknown

    # 9. IP address used instead of domain name
    ip_pattern = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    features['has_ip'] = 1 if ip_pattern.search(parsed.netloc) else 0

    return features
```

**Category B — HTML/JS Features (4 features)**

```python
import requests
from bs4 import BeautifulSoup

def extract_html_features(url):
    features = {}
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')

        # 10. Anchor tags pointing to external domains
        anchors = soup.find_all('a', href=True)
        ext_anchors = sum(1 for a in anchors
                          if urlparse(a['href']).netloc not in url)
        features['external_anchors_ratio'] = (
            ext_anchors / len(anchors) if anchors else 0
        )

        # 11. Form action pointing externally
        forms = soup.find_all('form', action=True)
        features['suspicious_form'] = any(
            urlparse(f['action']).netloc not in url for f in forms
        )

        # 12. Right-click disabled (JS obfuscation signal)
        features['right_click_disabled'] = 1 if (
            'event.button==2' in r.text or 'contextmenu' in r.text
        ) else 0

        # 13. iframe usage (invisible redirect)
        features['has_iframe'] = 1 if soup.find('iframe') else 0

    except:
        # If unreachable, treat as suspicious
        features.update({
            'external_anchors_ratio': 1,
            'suspicious_form': 1,
            'right_click_disabled': 0,
            'has_iframe': 0
        })
    return features
```

**Category C — Domain-Based Features (4 features)**

```python
import socket

def extract_domain_features(url):
    features = {}
    parsed = urlparse(url)
    domain = parsed.netloc

    # 14. DNS record exists
    try:
        socket.gethostbyname(domain)
        features['dns_record'] = 1
    except:
        features['dns_record'] = 0

    # 15. Google index check (via search query)
    # For hackathon: proxy via SerpAPI free tier or skip
    features['google_index'] = 1  # placeholder

    # 16. Statistical report (PhishTank API check)
    # Free API: https://checkurl.phishtank.com/checkurl/
    features['phishtank_reported'] = 0  # implement separately

    # 17. Age of domain via WHOIS
    try:
        w = whois.whois(domain)
        creation = w.creation_date
        if isinstance(creation, list): creation = creation[^0]
        age_days = (datetime.now() - creation).days
        features['domain_age'] = 0 if age_days < 180 else 1
    except:
        features['domain_age'] = -1

    return features
```


### Step 3 — Combine Features + Train XGBoost

```python
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

# Load dataset (PhishTank + ISCX, see Part 2)
df = pd.read_csv('phishing_dataset.csv')

# All feature columns (17 total)
feature_cols = [
    'url_length', 'is_shortened', 'has_at_symbol',
    'double_slash_redirect', 'prefix_suffix', 'subdomain_depth',
    'has_https', 'domain_reg_length', 'has_ip',
    'external_anchors_ratio', 'suspicious_form',
    'right_click_disabled', 'has_iframe',
    'dns_record', 'google_index', 'phishtank_reported', 'domain_age'
]

X = df[feature_cols]
y = df['label']  # 1 = phishing, 0 = legitimate

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# XGBoost with tuned params (from PhishNet paper benchmarks)
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric='logloss',
    random_state=42
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    early_stopping_rounds=20,
    verbose=50
)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred,
      target_names=['Legitimate', 'Phishing']))
# Expected: ~96–98% accuracy per published benchmarks [web:101][web:105]

# Save model
joblib.dump(model, 'phishnet_xgboost.pkl')
model.save_model('phishnet_xgboost.json')  # for ONNX export
```


### Step 4 — Add UPI Deeplink Layer (India-Specific Module)

This is your **zero-competition feature** — bolt it on top of the XGBoost pipeline:

```python
import re
from urllib.parse import parse_qs, urlparse

KNOWN_LEGITIMATE_VPAS = {
    # Bank official VPAs
    'hdfcbank', 'sbi', 'icici', 'axisbank', 'kotak',
    # Major merchants (sample — expand this list)
    'bigbazaar', 'amazon', 'flipkart', 'zomato', 'swiggy'
}

def analyze_upi_qr(upi_string):
    """
    Analyzes a decoded UPI QR string.
    Input example: upi://pay?pa=fraud@ybl&pn=BigBazaar&am=500
    """
    result = {
        'risk_score': 0,
        'flags': [],
        'recommendation': 'SAFE'
    }

    if not upi_string.startswith('upi://'):
        return result

    params = parse_qs(urlparse(upi_string).query)
    pa = params.get('pa', [''])[^0]   # payee VPA
    pn = params.get('pn', [''])[^0]   # display name
    am = params.get('am', ['0'])[^0]  # amount

    # Flag 1: VPA format invalid
    vpa_pattern = re.compile(r'^[a-zA-Z0-9._-]+@[a-zA-Z]+$')
    if not vpa_pattern.match(pa):
        result['flags'].append('INVALID_VPA_FORMAT')
        result['risk_score'] += 40

    # Flag 2: Display name vs VPA mismatch
    vpa_base = pa.split('@')[^0].lower()
    pn_lower = pn.lower().replace(' ', '')
    if pn_lower and not any(
        legit in vpa_base or legit in pn_lower
        for legit in KNOWN_LEGITIMATE_VPAS
    ):
        if pn_lower not in vpa_base and vpa_base not in pn_lower:
            result['flags'].append('NAME_VPA_MISMATCH')
            result['risk_score'] += 35

    # Flag 3: Suspicious amount (just below ₹50K reporting threshold)
    try:
        amount = float(am)
        if 45000 <= amount <= 49999:
            result['flags'].append('THRESHOLD_EVASION_AMOUNT')
            result['risk_score'] += 20
    except ValueError:
        pass

    # Flag 4: Known fraud VPA list check
    with open('fraud_vpas.json') as f:
        import json
        fraud_list = json.load(f)
    if pa in fraud_list:
        result['flags'].append('KNOWN_FRAUD_VPA')
        result['risk_score'] = 100

    # Final verdict
    if result['risk_score'] >= 70:
        result['recommendation'] = 'BLOCK'
    elif result['risk_score'] >= 40:
        result['recommendation'] = 'WARN'

    return result
```


***

## Part 2: Dataset Sources for Training

Use a **layered dataset strategy** — combine general phishing datasets with India-specific UPI fraud data:

### Phishing URL Datasets (Free)

| Dataset | Size | Format | Source | Best For |
| :-- | :-- | :-- | :-- | :-- |
| **PhishTank** | 50K+ URLs, updated hourly | CSV/JSON/XML | [phishtank.org](https://phishtank.org/developer_info.php) — free API key | Core training data [^3] |
| **ISCX-URL-2016** | 36K URLs (phishing + benign) | CSV | UNB repo | Balanced benchmark [^5] |
| **PhiUSIIL** | 235,795 URLs, rich lexical features | CSV | arXiv/Mendeley | Best for structural features — used in the 98.73% accuracy stacked model [^1] |
| **Kaggle Phishing Dataset** | 10K+ labelled URLs | CSV | `kaggle datasets download -d` `shashwatwork/web-page-phishing-detection-dataset` | Quick start [^6] |
| **OpenPhish** | Live feed, 30K+ active | TXT | [openphish.com/feed.txt](https://openphish.com/feed.txt) — no API key needed | Zero-day detection testing |
| **CIC-Trap4Phish (2026)** | Multi-format including QR code images | Multi | [arXiv:2602.09015](https://arxiv.org/abs/2602.09015) | QR-specific phishing — directly relevant [^7] |

### UPI Fraud Datasets (India-Specific)

| Dataset | What's Inside | Source |
| :-- | :-- | :-- |
| **Kaggle UPI Fraud Dataset** | Transaction ID, timestamp, sender/receiver, amount, fraud label — millions of rows [^8][^9] | Search: `kaggle datasets download -d` `"UPI fraud detection"` |
| **Synthetic UPI Generator** | Use `Faker` + Python to generate ₹-denominated transactions with fraud patterns | Build your own (10 min) |
| **MHA Cybercrime Portal** | Reported fraud UPI IDs and phone numbers (public disclosures) | [cybercrime.gov.in](https://cybercrime.gov.in) |
| **NPCI Fraud Reports** | Published quarterly fraud statistics, fraud UPI handle patterns | [npci.org.in/PDF/npci](https://www.npci.org.in/what-we-do/upi/product-statistics) |

### Download Commands (Quickstart)

```bash
# Install Kaggle CLI
pip install kaggle

# Phishing URL dataset
kaggle datasets download -d shashwatwork/web-page-phishing-detection-dataset

# UPI Fraud dataset
kaggle datasets download -d hk7232/upi-fraud-detection

# PhishTank live feed (no login)
curl -o phishtank.csv "http://data.phishtank.com/data/online-valid.csv"

# OpenPhish live feed
curl -o openphish.txt "https://openphish.com/feed.txt"
```


### Preprocessing Pipeline

```python
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Merge PhishTank + ISCX
phishtank = pd.read_csv('online-valid.csv')[['url']].assign(label=1)
legit = pd.read_csv('iscx_legitimate.csv')[['url']].assign(label=0)
df = pd.concat([phishtank, legit]).sample(frac=1).reset_index(drop=True)

# Extract features for every URL (this takes ~30 min for 10K URLs)
# Use joblib.Parallel for speed
from joblib import Parallel, delayed

def get_all_features(url):
    f = {}
    f.update(extract_url_features(url))
    f.update(extract_html_features(url))   # skip if slow
    f.update(extract_domain_features(url))
    return f

features = Parallel(n_jobs=-1)(
    delayed(get_all_features)(url) for url in df['url']
)

df_features = pd.DataFrame(features)
df_features['label'] = df['label'].values
df_features.to_csv('phishing_features.csv', index=False)
```


***

## Part 3: Streamlit Dashboard Deployment

Fork [firfircelik/fraud-detection-system-streamlit](https://github.com/firfircelik/fraud-detection-system-streamlit) — it's Docker-ready, supports 10,000+ TPS with a 4-model ensemble, and has 6 pre-built analytics modules. Use it as your visualization layer, replacing its backend with your XGBoost model.[^10]

### Step 1 — Build the Dashboard (`streamlit_app.py`)

```python
import streamlit as st
import pandas as pd
import joblib
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load model
model = joblib.load('phishnet_xgboost.pkl')

st.set_page_config(
    page_title="PhishGuard India — UPI & Phishing Detector",
    page_icon="🛡️",
    layout="wide"
)

# ── Header ──────────────────────────────────────────────
st.title("🛡️ PhishGuard India")
st.caption("Real-time phishing URL + UPI QR fraud detection")

# ── Sidebar ──────────────────────────────────────────────
st.sidebar.header("Detection Mode")
mode = st.sidebar.radio("Choose", ["🌐 URL Check", "📱 UPI QR Scan", "📊 Analytics"])

# ── URL Check Tab ─────────────────────────────────────────
if mode == "🌐 URL Check":
    st.subheader("Enter URL to Scan")
    url_input = st.text_input("Paste URL here", placeholder="https://example.com")

    if st.button("🔍 Scan Now") and url_input:
        with st.spinner("Extracting features and running XGBoost..."):
            features = extract_url_features(url_input)
            features.update(extract_html_features(url_input))
            features.update(extract_domain_features(url_input))
            df_input = pd.DataFrame([features])
            prob = model.predict_proba(df_input)[^0][^1]
            label = model.predict(df_input)[^0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Score", f"{prob*100:.1f}%")
        col2.metric("Verdict",
                    "🚨 PHISHING" if label == 1 else "✅ SAFE")
        col3.metric("Confidence",
                    f"{max(prob, 1-prob)*100:.1f}%")

        # Feature importance radar
        importances = model.feature_importances_
        fig = go.Figure(go.Bar(
            x=list(features.keys()),
            y=importances,
            marker_color='red' if label == 1 else 'green'
        ))
        fig.update_layout(title="Feature Contribution to Score")
        st.plotly_chart(fig, use_container_width=True)

# ── UPI QR Scan Tab ──────────────────────────────────────
elif mode == "📱 UPI QR Scan":
    st.subheader("Paste UPI Deeplink String")
    upi_input = st.text_area(
        "UPI String",
        placeholder="upi://pay?pa=merchant@ybl&pn=Store Name&am=500"
    )
    if st.button("🔍 Analyze QR") and upi_input:
        result = analyze_upi_qr(upi_input)

        if result['recommendation'] == 'BLOCK':
            st.error(f"🚨 HIGH RISK — Do NOT proceed with payment!")
        elif result['recommendation'] == 'WARN':
            st.warning("⚠️ Suspicious QR Code — Verify before paying")
        else:
            st.success("✅ QR Code appears legitimate")

        st.metric("Risk Score", f"{result['risk_score']}/100")
        if result['flags']:
            st.write("**Flags detected:**")
            for flag in result['flags']:
                st.code(flag)

# ── Analytics Tab ─────────────────────────────────────────
elif mode == "📊 Analytics":
    st.subheader("Fraud Trend Analytics")
    # Load your stored scan history from MongoDB/CSV
    try:
        history = pd.read_csv('scan_history.csv')
        history['timestamp'] = pd.to_datetime(history['timestamp'])

        col1, col2 = st.columns(2)

        # Daily scans
        daily = history.groupby(
            history['timestamp'].dt.date
        )['label'].value_counts().unstack().fillna(0)
        fig1 = px.line(daily, title="Daily Scans: Phishing vs Legitimate")
        col1.plotly_chart(fig1)

        # Fraud type pie
        flag_counts = (
            history[history['label']==1]['flags']
            .str.split(',').explode()
            .value_counts()
        )
        fig2 = px.pie(values=flag_counts.values,
                      names=flag_counts.index,
                      title="Fraud Flag Distribution")
        col2.plotly_chart(fig2)

        st.metric("Total Scans Today",
                  len(history[history['timestamp'].dt.date
                               == datetime.today().date()]))
        st.metric("Phishing Blocked Today",
                  len(history[(history['timestamp'].dt.date
                               == datetime.today().date())
                              & (history['label']==1)]))
    except FileNotFoundError:
        st.info("No scan history yet — run some URL checks first!")
```


### Step 2 — Deploy to Streamlit Community Cloud (Free, 5 Minutes)

Streamlit Community Cloud supports unlimited free public app deployments from GitHub, no credit card required:[^11][^12]

```
1. Push your project to a public GitHub repo

2. Go to → share.streamlit.io → "New App"

3. Fill in:
   Repository:  github.com/yourname/phishguard
   Branch:      main
   Main file:   streamlit_app.py

4. Click "Deploy" — live URL in ~2 minutes
   Format: https://yourname-phishguard-streamlit-app.streamlit.app
```

**`requirements.txt` for Streamlit Cloud:**

```
streamlit==1.35.0
xgboost==2.0.3
scikit-learn==1.4.2
pandas==2.2.1
numpy==1.26.4
requests==2.31.0
tldextract==5.1.1
python-whois==0.9.4
beautifulsoup4==4.12.3
plotly==5.20.0
joblib==1.4.0
```


### Step 3 — Persist Scan History (Free Backend)

```python
# Use MongoDB Atlas free tier (512MB, no expiry)
from pymongo import MongoClient
import os

client = MongoClient(os.environ['MONGODB_URI'])
db = client['phishguard']
scans = db['scans']

def log_scan(url, label, risk_score, flags):
    scans.insert_one({
        'url': url,
        'label': int(label),
        'risk_score': float(risk_score),
        'flags': flags,
        'timestamp': datetime.utcnow()
    })
```

Add `MONGODB_URI` as a **Secret** in Streamlit Cloud settings (Advanced → Secrets) — it maps to `st.secrets['MONGODB_URI']`.

***

## Full Pipeline Summary

```
Dataset (PhishTank + Kaggle UPI)
         │
         ▼
Feature Extraction (17 URL features + 5 UPI flags)
         │
         ▼
XGBoost Classifier (96–99% accuracy)
         │
    ┌────┴────┐
    │         │
 URL Mode   UPI Mode
    │         │
    └────┬────┘
         │
  Risk Score (0–100)
         │
  Streamlit Dashboard
  (Plotly charts, MongoDB logs)
         │
  Deploy → Streamlit Community Cloud
  (Free, public URL, live in 5 min)
```

The hackathon demo path is: paste a suspicious URL or UPI string → watch the XGBoost model fire in under 200ms → see the Streamlit dashboard update with risk score, flagged features, and trend charts — all from a single live public URL requiring zero infrastructure cost.[^11][^10]
<span style="display:none">[^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33]</span>

<div align="center">⁂</div>

[^1]: http://cjos.histr.edu.ly/index.php/journal/article/view/1517

[^2]: https://ieeexplore.ieee.org/document/9730579/

[^3]: https://github.com/sudoshivesh/Phishing-Website-Detection-using-XGBoost-and-RFM

[^4]: https://www.nature.com/articles/s41598-022-10841-5

[^5]: https://arxiv.org/abs/2407.04732

[^6]: https://ieeexplore.ieee.org/document/10115148/

[^7]: https://arxiv.org/abs/2602.09015

[^8]: https://ijsdr.org/viewpaperforall.php?paper=IJSDR2504164

[^9]: https://ijsdr.org/papers/IJSDR2504164.pdf

[^10]: https://github.com/firfircelik/fraud-detection-system-streamlit

[^11]: https://www.linkedin.com/pulse/5-free-platforms-deploy-your-machine-learning-models-2025-barnwal-mvpgc

[^12]: https://pattersonconsultingtn.com/blog/creditcard_fraud_detection_w_snowflake_sagemaker_part_5.html

[^13]: https://ieeexplore.ieee.org/document/10927064/

[^14]: https://publications.eai.eu/index.php/sis/article/view/4421

[^15]: https://ieeexplore.ieee.org/document/11134935/

[^16]: https://ieeexplore.ieee.org/document/11021929/

[^17]: https://ieeexplore.ieee.org/document/10797218/

[^18]: https://www.mdpi.com/2073-8994/16/2/248/pdf?version=1708330038

[^19]: https://arxiv.org/pdf/2409.19825.pdf

[^20]: https://dergipark.org.tr/tr/download/article-file/840307

[^21]: https://pmc.ncbi.nlm.nih.gov/articles/PMC8935623/

[^22]: https://www.mdpi.com/1424-8220/23/9/4403

[^23]: https://www.mdpi.com/2076-3417/13/8/4649/pdf?version=1680837183

[^24]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9133026/

[^25]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9628466/

[^26]: https://github.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/

[^27]: https://www.irjmets.com/upload_newfiles/irjmets80200090014/paper_file/irjmets80200090014.pdf

[^28]: https://github.com/vaibhavbichave/Phishing-URL-Detection

[^29]: https://hsnarman.github.io/CONF/21-BLACKSEA-PhishingDetection.pdf

[^30]: https://github.com/gangeshbaskerr/Phishing-Website-Detection

[^31]: https://www.jetir.org/papers/JETIR2503683.pdf

[^32]: https://phishing-url-detection-frontend.vercel.app

[^33]: https://www.ijrti.org/papers/IJRTI2510035.pdf

