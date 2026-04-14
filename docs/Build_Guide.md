<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# how to build this whole project which given in phaces with deatiled prompt give to ai with everything written prompt + link

Here is the complete **phase-by-phase build guide** for PhishGuard India — each phase has a ready-to-paste AI prompt (for Gemini, Copilot, or Cursor), the exact resources to reference, and what the AI should produce.

***

# PhishGuard India — Complete Phased Build Guide

## AI Prompts + Links for Every Phase


***

## How to Use This Guide

Each phase below has:

- 📋 **What to build** — clear scope
- 🤖 **Exact AI prompt** — paste directly into Gemini 2.5 Pro, Copilot Chat, or Cursor
- 🔗 **Reference links** — give these to the AI for context
- ✅ **Done when** — checklist to verify completion before moving to next phase

***

## Phase 0 — Project Scaffold (30 min)

**What to build:** Empty folder structure, `package.json`, Git init, all config files.

### 🤖 AI Prompt — Paste into Gemini CLI or Cursor Chat

```
You are a senior Chrome extension developer.

Create a complete project scaffold for a Chrome Extension called 
"PhishGuard India" with this exact folder structure:

phishguard-india/
├── extension/
│   ├── manifest.json          (Manifest V3)
│   ├── background/
│   │   └── service-worker.js
│   ├── content/
│   │   ├── qr-scanner.js
│   │   └── upi-parser.js
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.js
│   │   └── popup.css
│   ├── models/                (empty folder for .onnx file)
│   ├── data/
│   │   └── fraud_vpas.json    (empty array [])
│   └── icons/                 (placeholder)
├── ml-engine/
│   ├── feature_extraction.py
│   ├── train_xgboost.py
│   ├── upi_analyzer.py
│   └── requirements.txt
├── dashboard/
│   ├── streamlit_app.py
│   └── requirements.txt
├── blockchain/
│   ├── contracts/
│   │   └── FraudRegistry.sol
│   ├── scripts/
│   │   └── deploy.js
│   └── hardhat.config.js
├── api/
│   ├── check-vpa.js
│   └── report-fraud.js
├── .gitignore
├── README.md
└── package.json

Rules:
1. manifest.json must be Manifest V3 with these permissions: 
   activeTab, storage, scripting, notifications
2. Add "wasm-unsafe-eval" to CSP for onnxruntime-web support
3. package.json should include jsqr, onnxruntime-web as dependencies
4. .gitignore must exclude node_modules, *.pkl, *.onnx, .env
5. Every file should have correct boilerplate — no empty files

Output ALL file contents, one by one.

Reference: https://developer.chrome.com/docs/extensions/reference/manifest
Reference: https://github.com/yufuin/onnxruntime-web-on-extension
```


### ✅ Done When

- `manifest.json` loads in Chrome without errors (`chrome://extensions` → Load unpacked)
- All folders exist with boilerplate files

***

## Phase 1 — ML Engine: XGBoost Phishing Detector (2–3 hrs)

**What to build:** Python script that downloads PhishTank data, extracts 17 URL features, trains XGBoost, saves `.pkl` model.

### 🤖 AI Prompt — Paste into Gemini 2.5 Pro (gemini.google.com)

```
You are a machine learning engineer specializing in cybersecurity.

Build a complete Python pipeline for phishing URL detection. 
The output should be a trained XGBoost model saved as 
phishnet_xgboost.pkl and phishnet_xgboost.json.

STEP 1 — Data Collection:
Write code to download PhishTank's CSV from:
http://data.phishtank.com/data/online-valid.csv
AND a legitimate URL dataset from:
https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/legitimate.csv

STEP 2 — Feature Extraction:
Extract exactly these 17 features from every URL:
Address Bar Features (9):
  1. url_length          - total URL character count
  2. is_shortened        - 1 if bit.ly/tinyurl/goo.gl/t.co
  3. has_at_symbol       - 1 if @ in URL
  4. double_slash_redirect - 1 if // appears after position 6
  5. prefix_suffix       - 1 if hyphen in domain name
  6. subdomain_depth     - count of dots in URL
  7. has_https           - 1 if scheme is https
  8. domain_reg_length   - 0 if domain expires in <365 days, else 1
  9. has_ip              - 1 if IP address used instead of domain

HTML Features (4):
  10. external_anchors_ratio - ratio of external anchor tags
  11. suspicious_form    - 1 if form action points externally
  12. right_click_disabled - 1 if contextmenu JS found
  13. has_iframe         - 1 if <iframe> tag present

Domain Features (4):
  14. dns_record         - 1 if DNS resolves successfully
  15. google_index       - set to 1 as placeholder
  16. phishtank_reported - 0 as placeholder
  17. domain_age         - 0 if domain <180 days old, else 1

STEP 3 — Model Training:
Train XGBoost with these exact parameters:
  n_estimators=300, max_depth=6, learning_rate=0.1,
  subsample=0.8, colsample_bytree=0.8, random_state=42
Use 80/20 train-test split with stratify=y.
Print full classification_report at the end.
Target accuracy: 96%+

STEP 4 — Save:
joblib.dump(model, 'ml-engine/phishnet_xgboost.pkl')
model.save_model('ml-engine/phishnet_xgboost.json')

Also save the feature list to 'ml-engine/features.json' 
so it can be referenced later.

Use these libraries: xgboost, scikit-learn, pandas, numpy, 
requests, tldextract, python-whois, beautifulsoup4, joblib

Add error handling for every network call (timeouts, DNS fails).
Use joblib.Parallel(n_jobs=-1) for feature extraction to speed it up.

Output: Complete train_xgboost.py file + requirements.txt

Reference: https://arxiv.org/abs/2407.04732 (PhishNet paper)
Reference: https://github.com/sudoshivesh/Phishing-Website-Detection-using-XGBoost-and-RFM
Reference: https://github.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques
```


### ✅ Done When

```bash
cd ml-engine
pip install -r requirements.txt
python train_xgboost.py
# Output: "accuracy: 0.96+" and phishnet_xgboost.pkl saved
```


***

## Phase 2 — UPI Analyzer Module (1 hr)

**What to build:** Python module + standalone JS module that parse UPI deeplinks and return a risk score.

### 🤖 AI Prompt — Paste into Cursor (open `upi_analyzer.py`)

```
You are a cybersecurity developer who understands India's UPI 
payment system deeply.

Build TWO files:

FILE 1: ml-engine/upi_analyzer.py
A Python module with one main function: analyze_upi_qr(upi_string)

The UPI URI format is:
upi://pay?pa=merchant@ybl&pn=Display Name&am=500&cu=INR

Parse these fields:
  pa = payee VPA (Virtual Payment Address)
  pn = display name shown to user
  am = amount
  cu = currency

Apply these 5 fraud detection checks and return a risk score 0-100:

CHECK 1 — VPA Format Validation (40 points if fails)
  Valid VPA regex: ^[a-zA-Z0-9._-]+@[a-zA-Z]+$
  
CHECK 2 — Name vs VPA Mismatch (35 points if fails)
  If pn="BigBazaar" but pa="random123@ybl" → flag mismatch
  Use fuzzy string matching (fuzzywuzzy library)
  Threshold: similarity < 30% = mismatch
  
CHECK 3 — Threshold Evasion Amount (20 points if matches)
  If amount is between 45000-49999 (just below ₹50K RBI limit) → flag
  
CHECK 4 — Known Fraud VPA Check (100 points, instant block)
  Load from fraud_vpas.json
  If pa in fraud list → risk_score = 100, recommend = BLOCK
  
CHECK 5 — Suspicious TLD on VPA handle (15 points)
  List of suspicious handles: @ybl, @paytm can be legitimate
  BUT if VPA has numbers+random chars before @ → suspicious
  Example: fraud12345@ybl → suspicious
  Example: amazonpay@apl → legitimate

Return this dict:
{
  "risk_score": 0-100,
  "flags": ["NAME_VPA_MISMATCH", "THRESHOLD_EVASION_AMOUNT"],
  "recommendation": "SAFE" | "WARN" | "BLOCK",
  "parsed": {"pa": "...", "pn": "...", "am": "..."},
  "explanation": "One sentence plain English explanation"
}

FILE 2: extension/content/upi-parser.js
The same logic in JavaScript (no external libraries — pure JS only).
Use URLSearchParams to parse the UPI string.
Export a function: analyzeUPIString(upiString)
Load fraud_vpas.json via chrome.runtime.getURL() and fetch().
Return the same structure as above.

Include sample test cases at the bottom of each file:
  SAFE:  "upi://pay?pa=bigbazaar@icici&pn=Big Bazaar&am=200"
  WARN:  "upi://pay?pa=randoms9291@ybl&pn=Amazon Pay&am=199"
  BLOCK: "upi://pay?pa=fraud@ybl&pn=HDFC Bank&am=49999"

Reference: https://stackoverflow.com/questions/79045905/how-can-i-deep-link-to-upi-payment-apps
Reference: https://www.quickheal.co.in/knowledge-centre/qr-code-security-safe-urls-upi-transactions/
```


### ✅ Done When

```bash
python ml-engine/upi_analyzer.py
# Should print SAFE / WARN / BLOCK for the 3 test cases correctly
```


***

## Phase 3 — Chrome Extension Core (3–4 hrs)

**What to build:** The actual browser extension — QR scanner, phishing detector badge, alert modal.

### 🤖 AI Prompt — Paste into Cursor (open the `extension/` folder)

```
You are a Chrome Extension developer expert in Manifest V3.

Build a complete Chrome Extension called "PhishGuard India".
The extension scans every webpage for phishing URLs and 
detects fraudulent UPI QR codes before the user pays.

I'll describe each file needed:

═══════════════════════════════════════════
FILE: extension/background/service-worker.js
═══════════════════════════════════════════
This is the MV3 service worker. It must:

1. Listen for tab updates and send the current URL to the 
   phishing check function on every page load.

2. Run PhishLang ONNX model for URL phishing detection:
   - Load model from chrome.runtime.getURL('models/phishlang.onnx')
   - Use onnxruntime-web with these exact WASM path settings:
     ort.env.wasm.wasmPaths = chrome.runtime.getURL('models/')
     ort.env.wasm.numThreads = 1  // Required for service worker
   - Extract URL features: url_length, subdomain_depth, has_https,
     has_at_symbol, is_shortened, has_ip (6 fast features only)
   - If model not loaded, fallback to Google Safe Browsing API:
     https://safebrowsing.googleapis.com/v4/threatMatches:find
     API key stored in chrome.storage.local

3. Set extension badge:
   - GREEN badge "✓" = safe (score < 40)
   - YELLOW badge "!" = warning (score 40-70)
   - RED badge "✗" = phishing detected (score > 70)
   Use chrome.action.setBadgeText and setBadgeBackgroundColor

4. Listen for messages from content scripts:
   - "UPI_SCAN_REQUEST": run upi-parser.js logic, return result
   - "REPORT_FRAUD": save to chrome.storage.local fraud log
   - "GET_STATS": return scan count and fraud count

5. On RED alert: show chrome.notifications notification with
   title "🚨 PhishGuard Alert" and message about the threat.

═══════════════════════════════════════════
FILE: extension/content/qr-scanner.js
═══════════════════════════════════════════
This content script runs on every page. It must:

1. After DOM loads, find ALL <img> and <canvas> elements on page.

2. For each image with width > 50px and height > 50px:
   - Draw the image onto an offscreen <canvas>
   - Get ImageData from canvas context
   - Pass to jsQR() to attempt QR decode
   - jsQR is loaded via importScripts from:
     https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js
     (also bundle it locally as extension/lib/jsQR.js)

3. If jsQR returns a valid result:
   - Check if result.data starts with "upi://"
   - If YES: Send message to service worker:
     chrome.runtime.sendMessage({type: "UPI_SCAN_REQUEST", data: result.data})
   - If NO: Send message:
     chrome.runtime.sendMessage({type: "URL_SCAN_REQUEST", url: result.data})

4. Add a floating "🛡️ Scan QR" button to the page 
   (bottom-right corner, z-index: 99999):
   - On click: activate camera via getUserMedia() to scan 
     QR from physical paper/screen
   - Style: red background, white text, rounded, shadow

5. Listen for scan results from service worker:
   - If BLOCK: inject a full-screen overlay modal (red, urgent)
   - If WARN: inject a yellow toast notification (bottom of screen)
   - If SAFE: briefly flash a green checkmark

═══════════════════════════════════════════
FILE: extension/popup/popup.html + popup.js
═══════════════════════════════════════════
Build a popup UI (400px wide, clean design) with:

Tab 1 — "Current Page" status:
  - Large risk score circle (0-100, color coded)
  - List of flags detected
  - "Report this site" button

Tab 2 — "Scan QR" tab:
  - Text area: paste a UPI string here
  - "Analyze" button
  - Result card showing risk_score, flags, recommendation
  
Tab 3 — "History" tab:
  - Last 10 scans from chrome.storage.local
  - Each row: URL/VPA, risk score, timestamp

Use vanilla JS only (no React — keep popup fast to load).
Use CSS variables for theming:
  --safe: #22c55e
  --warn: #f59e0b  
  --danger: #ef4444
  --bg: #0f172a
  --text: #f1f5f9

Reference: https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3
Reference: https://github.com/yufuin/onnxruntime-web-on-extension
Reference: https://www.npmjs.com/package/jsqr
Reference: https://stackoverflow.com/questions/79671265/unable-to-get-onnxruntime-web-working-in-content-js-in-chrome-extension

CRITICAL NOTES:
- Never use eval() in any extension file (CSP will block it)
- All external scripts must be bundled locally (no CDN in production)
- Use chrome.storage.local not localStorage
- Service worker has no DOM access — never use document.* there
- Use return true inside onMessage listeners for async responses
```


### ✅ Done When

- Load extension at `chrome://extensions` → Load unpacked → `extension/`
- Visit `http://testsafebrowsing.appspot.com/s/phishing.html`
- Badge turns RED and notification fires

***

## Phase 4 — Streamlit Dashboard (1–2 hrs)

### 🤖 AI Prompt — Paste into Gemini 2.5 Pro

```
You are a Python developer building a fraud analytics dashboard.

Build a complete Streamlit app for PhishGuard India at 
dashboard/streamlit_app.py

The app has 3 pages (use st.sidebar radio):

PAGE 1 — "🌐 URL Scanner"
  - Text input for URL
  - On submit: call a function check_url(url) which:
    * Loads ml-engine/phishnet_xgboost.pkl
    * Extracts 6 fast features (url_length, subdomain_depth, 
      has_https, has_at_symbol, is_shortened, has_ip)
    * Returns probability score 0.0 to 1.0
  - Display: risk score gauge (plotly go.Indicator), 
    verdict badge, feature importance bar chart

PAGE 2 — "📱 UPI QR Analyzer"
  - Text area for UPI deeplink string
  - On submit: call analyze_upi_qr() from ml-engine/upi_analyzer.py
  - Display: risk score, flags as colored badges,
    recommendation as large colored banner
  - Also: QR image upload option — use pyzbar to decode uploaded QR

PAGE 3 — "📊 Analytics Dashboard"
  Load scan history from MongoDB Atlas (connection string from 
  st.secrets["MONGODB_URI"]) OR from a local CSV if no connection.
  Show:
    - Total scans counter (st.metric)
    - Phishing blocked today (st.metric)  
    - Line chart: scans per day (last 7 days), split by verdict
    - Pie chart: fraud flag distribution
    - World map (plotly express scatter_geo) showing fraud 
      origin by TLD (.cn, .ru, .tk most common)
    - Data table: last 20 scans with color coded rows

STYLING:
  st.set_page_config(layout="wide", page_icon="🛡️")
  Use dark theme CSS injection:
  st.markdown("""<style>
    .stApp { background-color: #0f172a; color: #f1f5f9; }
  </style>""", unsafe_allow_html=True)

Create dashboard/requirements.txt with all dependencies.
Create dashboard/sample_data.csv with 50 realistic mock rows
(mix of safe/warn/block verdicts) so the analytics page 
works without a database.

Reference: https://github.com/firfircelik/fraud-detection-system-streamlit
Reference: https://docs.streamlit.io/deploy/streamlit-community-cloud
```


### ✅ Done When

```bash
cd dashboard
pip install -r requirements.txt
streamlit run streamlit_app.py
# Opens at localhost:8501 with all 3 pages working
```


***

## Phase 5 — Blockchain Fraud Registry (1 hr)

### 🤖 AI Prompt — Paste into Cursor (open `blockchain/` folder)

```
You are a Solidity developer building a fraud reporting system.

Build a complete Hardhat project for a FraudRegistry smart 
contract deployed on Polygon Amoy testnet (chainId: 80002).

FILE: blockchain/contracts/FraudRegistry.sol

// SPDX-License-Identifier: MIT
// Solidity ^0.8.19

Build a contract with these features:

1. STRUCTS:
   FraudReport { vpa, urlHash, reporterCount, firstReported, lastReported }

2. MAPPINGS:
   fraudVPAs: string => FraudReport
   fraudURLs: bytes32 => FraudReport
   hasReported: address => string => bool  (prevent duplicate reports)

3. FUNCTIONS:
   reportFraudVPA(string vpa) public
     - Require: valid VPA format (contains @)
     - Require: not already reported by this address
     - Increment reporterCount
     - Emit FraudReported event

   reportFraudURL(string url) public
     - Hash the URL: keccak256(abi.encodePacked(url))
     - Same logic as above

   getFraudScore(string vpa) public view returns (uint256)
     - Returns reporterCount for VPA

   isHighRisk(string vpa) public view returns (bool)
     - Returns true if reporterCount >= 3

4. EVENTS:
   FraudReported(string indexed identifier, string fraudType, 
                 uint256 reportCount, address reporter)

FILE: blockchain/scripts/deploy.js
Hardhat deploy script for Polygon Amoy testnet.
Log the deployed contract address.

FILE: blockchain/hardhat.config.js
Configure for Polygon Amoy:
  chainId: 80002
  rpcUrl: "https://rpc-amoy.polygon.technology/"
  Get private key from process.env.PRIVATE_KEY

FILE: blockchain/scripts/interact.js
Example script showing how to:
  1. Connect to deployed contract
  2. Report a fraud VPA
  3. Get fraud score
  4. Check if high risk

Also create a simple helper function for the extension:
FILE: extension/background/blockchain-logger.js
  async function logFraudToBlockchain(vpa, contractAddress, privateKey)
  Uses ethers.js to call reportFraudVPA() from browser context.

Add to package.json: hardhat, ethers, @nomicfoundation/hardhat-toolbox

Include step-by-step deployment instructions as comments:
  1. Get free MATIC from https://faucet.polygon.technology/
  2. npx hardhat compile
  3. npx hardhat run scripts/deploy.js --network amoy
  4. Copy contract address to extension/background/service-worker.js

Reference: https://hardhat.org/tutorial
Reference: https://wiki.polygon.technology/docs/tools/ethereum/hardhat/
```


### ✅ Done When

```bash
cd blockchain
npx hardhat compile   
# 0 errors, FraudRegistry.sol compiled
npx hardhat test      
# All tests pass
```


***

## Phase 6 — NVIDIA NIM Integration (30 min)

### 🤖 AI Prompt — Paste into any AI

```
You are building a real-time fraud explanation feature.

Create ONE file: extension/background/nvidia-explainer.js

This module calls NVIDIA NIM API to generate short Hindi/English 
explanations when PhishGuard detects a threat.

The NVIDIA NIM API is OpenAI-compatible:
  Base URL: https://integrate.api.nvidia.com/v1
  Model: nvidia/llama-nemotron-nano-4b-instruct
  API key: stored in chrome.storage.local as "nvidia_api_key"
  Get free key at: https://build.nvidia.com

Build ONE exported async function:
  async function explainThreat(context)

Where context = {
  type: "PHISHING_URL" | "FRAUD_QR" | "VPA_MISMATCH",
  url: "...",         // if URL threat
  vpa: "...",         // if UPI threat  
  displayName: "...", // if name mismatch
  riskScore: 75,
  flags: ["NAME_VPA_MISMATCH"],
  language: "hinglish" | "english"  // detect from chrome locale
}

The function should:
1. Build a prompt based on context.type and context.language
2. Call NVIDIA NIM API with max_tokens: 60, temperature: 0.3
3. Return explanation string in 1-2 sentences

Example outputs:
  HINGLISH: "Yaar, ye QR code fraud lag raha hai! Merchant 
    'BigBazaar' bata raha hai but UPI handle kuch aur hai — 
    payment mat karo!"
  ENGLISH: "Warning: This QR code displays 'BigBazaar' but 
    routes to an unverified UPI handle. Do not make this payment."

Also add a fallback: if NVIDIA API fails or no API key set,
return a pre-written static explanation from a lookup table.

The static fallback table should cover all 5 flag types:
  INVALID_VPA_FORMAT, NAME_VPA_MISMATCH, THRESHOLD_EVASION_AMOUNT,
  KNOWN_FRAUD_VPA, PHISHING_URL_DETECTED

Reference: https://build.nvidia.com/nvidia/llama-nemotron-nano-4b-instruct
```


***

## Phase 7 — Vercel API Backend (30 min)

### 🤖 AI Prompt — Paste into Cursor (open `api/` folder)

```
Build two Vercel serverless functions for PhishGuard India.

FILE: api/check-vpa.js
  Method: GET
  Query params: ?vpa=merchant@ybl
  
  Logic:
  1. Validate VPA format with regex
  2. Check against hardcoded fraud list (top 20 known fraud VPAs)
  3. Query MongoDB Atlas (connection via process.env.MONGODB_URI)
     for community-reported fraud count
  4. Call Polygon Amoy RPC to get on-chain fraud score
     Contract address from process.env.CONTRACT_ADDRESS
  5. Return JSON:
     { vpa, riskScore, reportCount, isKnownFraud, source }

FILE: api/report-fraud.js
  Method: POST
  Body: { vpa, url, reporterHash, evidence }
  
  Logic:
  1. Validate inputs
  2. Save to MongoDB Atlas collection "fraud_reports"
  3. Return { success: true, reportId }

FILE: vercel.json
  Configure both routes.

IMPORTANT: 
  - Never expose MongoDB URI or private keys in response
  - Add rate limiting: max 10 requests per IP per minute
  - Add CORS headers for Chrome extension origin

Create a .env.example file showing all required env vars:
  MONGODB_URI=mongodb+srv://...
  CONTRACT_ADDRESS=0x...
  POLYGON_RPC=https://rpc-amoy.polygon.technology/
```


***

## Phase 8 — Deploy Everything (30 min)

### 🤖 AI Prompt

```
Write step-by-step deployment instructions for PhishGuard India.
Format as a shell script with comments.

Cover:
1. Deploy Streamlit dashboard to Streamlit Community Cloud
   - Assumes code is on GitHub at github.com/USERNAME/phishguard
   - Steps to connect at share.streamlit.io
   - How to add MONGODB_URI as a Secret

2. Deploy Vercel API functions
   - npm i -g vercel
   - vercel login
   - cd api && vercel --prod
   - How to add environment variables via vercel env add

3. Deploy smart contract to Polygon Amoy
   - Get free MATIC: https://faucet.polygon.technology/
   - npx hardhat run scripts/deploy.js --network amoy
   - Save contract address

4. Package Chrome extension for submission
   - Build step (if using Vite/webpack)
   - Create ZIP of extension/ folder
   - Submit to Chrome Web Store at chrome.google.com/webstore/devconsole
   - $5 one-time developer registration fee

5. Update extension/background/service-worker.js with:
   - Deployed Vercel API URL
   - Deployed contract address

Include expected output after each step so I know it worked.
```


***

## Quick Reference: All Key Links Per Phase

| Phase | Key GitHub/Doc Links |
| :-- | :-- |
| 0 — Scaffold | [MV3 Docs](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3) · [ONNX in Extension](https://github.com/yufuin/onnxruntime-web-on-extension) |
| 1 — XGBoost | [PhishNet Paper](https://arxiv.org/abs/2407.04732) · [Shrey's Repo](https://github.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques) · [XGBoost Repo](https://github.com/sudoshivesh/Phishing-Website-Detection-using-XGBoost-and-RFM) |
| 2 — UPI Parser | [UPI URI Spec](https://stackoverflow.com/questions/79045905/how-can-i-deep-link-to-upi-payment-apps) · [Quick Heal QR](https://www.quickheal.co.in/knowledge-centre/qr-code-security-safe-urls-upi-transactions/) |
| 3 — Extension | [jsQR npm](https://www.npmjs.com/package/jsqr) · [ONNX Web Deploy](https://onnxruntime.ai/docs/tutorials/web/deploy.html) · [ONNX in Service Worker Fix](https://stackoverflow.com/questions/79671265/unable-to-get-onnxruntime-web-working-in-content-js-in-chrome-extension) |
| 4 — Streamlit | [Fraud Dashboard Repo](https://github.com/firfircelik/fraud-detection-system-streamlit) · [Streamlit Deploy](https://docs.streamlit.io/deploy/streamlit-community-cloud) |
| 5 — Blockchain | [Hardhat Tutorial](https://hardhat.org/tutorial) · [Polygon Amoy Docs](https://wiki.polygon.technology/docs/tools/ethereum/hardhat/) · [Polygon Faucet](https://faucet.polygon.technology/) |
| 6 — NVIDIA NIM | [Nemotron Nano](https://build.nvidia.com/nvidia/llama-nemotron-nano-4b-instruct) · [NIM API Docs](https://developer.nvidia.com/ai-models) |
| 7 — Vercel API | [Vercel Functions](https://vercel.com/docs/functions) · [MongoDB Atlas](https://www.mongodb.com/atlas) |


***

## Recommended AI Tool Per Phase

| Phase | Best Tool | Why |
| :-- | :-- | :-- |
| 0 — Scaffold | **Gemini CLI** in terminal | Generates full folder trees fast |
| 1 — ML Engine | **Gemini 2.5 Pro** (education plan) | Best at Python + data science |
| 2 — UPI Parser | **Cursor** (open file, inline edit) | Best for precise function writing |
| 3 — Extension | **Cursor** (multi-file awareness) | Sees all your extension files at once |
| 4 — Streamlit | **Gemini 2.5 Pro** | Best at Streamlit + Plotly combos |
| 5 — Blockchain | **Copilot** (GitHub = Solidity training data) | Solidity autocomplete is strong |
| 6 — NVIDIA NIM | Any (it's just a fetch call) | 30 lines, any AI handles it |
| 7 — Vercel API | **Cursor** | Node.js serverless is its strength |

<span style="display:none">[^1][^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^2][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://arxiv.org/pdf/2404.08310.pdf

[^2]: https://arxiv.org/html/2410.20862v1

[^3]: https://arxiv.org/pdf/2503.01000.pdf

[^4]: http://arxiv.org/pdf/2405.00596.pdf

[^5]: https://www.npmjs.com/package/jsqr

[^6]: https://stackoverflow.com/questions/79045905/how-can-i-deep-link-to-upi-payment-apps-and-pay-without-being-a-merchant

[^7]: https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3

[^8]: https://www.groovyweb.co/blog/chrome-extension-development-guide-2026

[^9]: https://chrome-stats.com/d/hkojjajclkgeijhcmfjcjkddfjpaimek

[^10]: https://github.com/yufuin/onnxruntime-web-on-extension/

[^11]: https://learnwithhasan.com/blog/built-chrome-extension-ai/

[^12]: https://stackoverflow.com/questions/79671265/unable-to-get-onnxruntime-web-working-in-content-js-in-chrome-extension

[^13]: https://dev.to/ryu0705/building-chrome-extensions-in-2026-a-practical-guide-with-manifest-v3-12h2

[^14]: https://github.com/microsoft/onnxruntime/issues/20876

[^15]: https://developer.chrome.com/docs/extensions/reference/manifest

[^16]: https://onnxruntime.ai/docs/tutorials/web/deploy.html

[^17]: https://dev.to/paulasantamaria/chrome-extensions-migrating-to-manifest-v3-5e88

[^18]: https://onnxruntime.ai/docs/tutorials/web/build-web-app.html

[^19]: https://github.com/crxjs/chrome-extension-tools/discussions/79

