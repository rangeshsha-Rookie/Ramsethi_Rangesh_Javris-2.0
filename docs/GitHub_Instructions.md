<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# which github repo using and how how to use in that project without breaking the project

Here is the complete, safe guide for every GitHub repo used in PhishGuard — exactly what to take from each, what NOT to touch, and how to integrate without breaking anything.

***

# PhishGuard GitHub Repos — Complete Integration Guide


***

## The 7 Repos You're Using

```
REPO 1  → cprite/phishing-detection-ext       (Extension shell)
REPO 2  → UTA-SPRLab/phishlang                (ML brain)
REPO 3  → shreyagopal/Phishing-Website-Detection (Training data + features)
REPO 4  → gangeshbaskerr/Phishing-Website-Detection (17-feature extractor)
REPO 5  → Vindhyaa-Saravanan/PhishShield       (Alert UI)
REPO 6  → firfircelik/fraud-detection-system-streamlit (Dashboard)
REPO 7  → Vatshayan/UPI-Fraud-Detection-Using-Machine-Learning (UPI ML)
```


***

## Repo 1 — `cprite/phishing-detection-ext`

### Your Extension Scaffold

🔗 **Link:** [github.com/cprite/phishing-detection-ext](https://github.com/cprite/phishing-detection-ext)

**What it is:** A working Chrome extension that detects phishing with 91% accuracy using a local ML server. It's your **starting skeleton** — you take its structure and replace its brain with yours.[^1]

**What to TAKE:**

```
✅ manifest.json         → study its permissions structure
✅ popup/popup.html      → steal the HTML layout/tabs idea
✅ popup/popup.css       → steal the dark UI theme variables
✅ content/content.js    → see how it injects into pages
✅ icons/                → use as placeholder icons
```

**What NOT to TAKE:**

```
❌ background/server calls → it calls a LOCAL Flask server (port 5000)
                              your version runs ONNX in-browser, no server
❌ model/ folder          → its model format is different from PhishLang ONNX
❌ requirements.txt       → that's for its Flask backend, you don't need it
```

**How to clone safely:**

```bash
# Clone into a SEPARATE folder — never clone into your project directly
git clone https://github.com/cprite/phishing-detection-ext.git reference/cprite-ext

# Now COPY only what you need — never move
cp reference/cprite-ext/popup/popup.html extension/popup/popup.html
cp reference/cprite-ext/popup/popup.css extension/popup/popup.css
cp -r reference/cprite-ext/icons/ extension/icons/

# Never run npm install from this repo's folder in your project
# Keep it purely as reference/copy source
```

**The ONE critical difference:** cprite's extension makes a `fetch("http://localhost:5000/predict")` call to a local Python server. Your version must **never** do this — you run everything inside the browser using ONNX. When you copy `content.js`, delete every `fetch("localhost")` line before pasting.

***

## Repo 2 — `UTA-SPRLab/phishlang`

### Your ML Brain (Most Important Repo)

🔗 **Link:** [github.com/UTA-SPRLab/phishlang](https://github.com/UTA-SPRLab/phishlang)[^2]

**What it is:** The PhishLang MobileBERT model — accepted at NDSS 2026, runs 100% client-side, outperforms Google Safe Browsing. This is the actual intelligence of your extension.

**What to TAKE:**

```
✅ The trained .onnx model file     → your primary asset
✅ requirements.txt                 → for understanding dependencies
✅ The feature extraction logic     → how it reads webpage content
✅ phishlang_clientside_app/        → study how they load model in browser
```

**What NOT to TAKE:**

```
❌ installer.deb                    → Linux desktop app, not for Chrome
❌ training.py                      → only needed if you retrain from scratch
❌ training_data/ folder            → 2GB+, only needed for retraining
❌ The full client-side app         → it's a Chromium app, not a Chrome extension
```

**Step-by-step model extraction:**

```bash
# Step 1: Clone the repo
git clone https://github.com/UTA-SPRLab/phishlang.git reference/phishlang

# Step 2: Install Python deps to run their export script
cd reference/phishlang
pip install -r requirements.txt

# Step 3: Find and export the ONNX model
# Look inside phishlang_clientside_app/ for any .onnx file
find . -name "*.onnx" 2>/dev/null

# If no .onnx found, convert their PyTorch model:
python3 -c "
import torch
from transformers import MobileBertForSequenceClassification
model = MobileBertForSequenceClassification.from_pretrained('./model')
dummy = torch.zeros(1, 128, dtype=torch.long)
torch.onnx.export(model, (dummy, dummy), 'phishlang.onnx',
    opset_version=12,
    input_names=['input_ids', 'attention_mask'],
    output_names=['logits'],
    dynamic_axes={'input_ids':{0:'batch'}, 'attention_mask':{0:'batch'}}
)
print('Exported: phishlang.onnx')
"

# Step 4: Copy ONLY the .onnx file into your project
cp phishlang.onnx ../../extension/models/phishlang.onnx

# Step 5: Also copy the WASM files from onnxruntime-web
# These go in extension/models/ alongside the .onnx file
npm install onnxruntime-web
cp node_modules/onnxruntime-web/dist/*.wasm extension/models/
```

**Critical setup for service worker** (the most common breaking point):[^3]

```javascript
// extension/background/service-worker.js
// MUST set these BEFORE any ort.InferenceSession.create() call
import * as ort from './lib/ort.min.js';  // bundled locally

// Point WASM files to your extension's models/ folder
ort.env.wasm.wasmPaths = {
  'ort-wasm.wasm': chrome.runtime.getURL('models/ort-wasm.wasm'),
  'ort-wasm-simd.wasm': chrome.runtime.getURL('models/ort-wasm-simd.wasm'),
  'ort-wasm-threaded.wasm': chrome.runtime.getURL('models/ort-wasm-threaded.wasm'),
};
ort.env.wasm.numThreads = 1;  // CRITICAL — service workers are single-threaded
ort.env.wasm.simd = true;

// Load model ONCE at startup, cache the session
let session = null;
async function loadModel() {
  if (session) return session;
  const modelPath = chrome.runtime.getURL('models/phishlang.onnx');
  session = await ort.InferenceSession.create(modelPath, {
    executionProviders: ['wasm'],
    graphOptimizationLevel: 'all'
  });
  return session;
}
```


***

## Repo 3 — `shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques`

### Your Training Dataset Source

🔗 **Link:** [github.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques](https://github.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques)[^4]

**What it is:** A complete ML pipeline with pre-collected PhishTank + legitimate URL datasets, already cleaned and formatted. Saves you 3+ hours of data collection.

**What to TAKE:**

```
✅ DataFiles/legitimate.csv         → 5000 clean legitimate URLs, labelled
✅ DataFiles/phishing.csv           → 5000 phishing URLs, labelled
✅ Phishing Website Detection_Feature Extraction.ipynb → copy feature logic
✅ Phishing Website Detection_Models & Training.ipynb  → copy XGBoost params
```

**What NOT to TAKE:**

```
❌ Any .pkl model files             → trained on old data, retrain on fresh data
❌ The Flask app files              → you're using Streamlit, not Flask
❌ requirements.txt as-is           → pin versions yourself for compatibility
```

**Safe download (no git clone needed):**

```bash
# Download ONLY the data files — no need to clone whole repo
curl -L -o ml-engine/data/legitimate.csv \
  "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/legitimate.csv"

curl -L -o ml-engine/data/phishing.csv \
  "https://raw.githubusercontent.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques/master/DataFiles/phishing.csv"

# Verify download
wc -l ml-engine/data/legitimate.csv
wc -l ml-engine/data/phishing.csv
# Expected: ~5001 lines each (5000 rows + header)
```


***

## Repo 4 — `gangeshbaskerr/Phishing-Website-Detection`

### Your 17-Feature Extractor

🔗 **Link:** [github.com/gangeshbaskerr/Phishing-Website-Detection](https://github.com/gangeshbaskerr/Phishing-Website-Detection)[^5]

**What it is:** The cleanest implementation of the exact 17-feature extraction logic used in all phishing ML papers. Copy its feature code directly.

**What to TAKE:**

```
✅ feature_extraction.py            → the core logic, cleanly written
✅ The 17 feature definitions       → cross-check against your own
```

**What NOT to TAKE:**

```
❌ Jupyter notebooks                → good reference only, not production code
❌ Their trained model              → outdated dataset, train fresh
```

**Integration:**

```bash
# Download just the feature extractor
curl -L -o reference/gangesh_features.py \
  "https://raw.githubusercontent.com/gangeshbaskerr/Phishing-Website-Detection/master/feature_extraction.py"

# Compare with your ml-engine/feature_extraction.py
# Port any missing features into your file
diff reference/gangesh_features.py ml-engine/feature_extraction.py
```


***

## Repo 5 — `Vindhyaa-Saravanan/PhishShield`

### Your Alert UI Component

🔗 **Link:** [github.com/Vindhyaa-Saravanan/PhishShield](https://github.com/Vindhyaa-Saravanan/PhishShield)[^6]

**What it is:** A hackathon-built Chrome extension with a pre-built alert modal UI. Its ONNX model loading and the visual alert popup are directly reusable.

**What to TAKE:**

```
✅ The alert modal HTML/CSS          → red overlay popup design
✅ The toast notification CSS        → yellow warning banner style
✅ popup/popup.html badge design     → risk score circle component
```

**What NOT to TAKE:**

```
❌ Their ONNX model                  → use PhishLang's instead (more accurate)
❌ Their manifest.json               → use your own (theirs may be MV2)
❌ package-lock.json                 → always regenerate this yourself
```

**Safe integration:**

```bash
git clone https://github.com/Vindhyaa-Saravanan/PhishShield.git reference/phishshield

# Copy only CSS — styles are safe to copy
cp reference/phishshield/popup/style.css reference/phishshield-style.css
# Open and manually copy the alert modal CSS into:
# extension/content/alert-modal.css
# DO NOT blindly paste entire files — read first, copy needed blocks
```


***

## Repo 6 — `firfircelik/fraud-detection-system-streamlit`

### Your Dashboard Template

🔗 **Link:** [github.com/firfircelik/fraud-detection-system-streamlit](https://github.com/firfircelik/fraud-detection-system-streamlit)[^7]

**What it is:** A production-ready Streamlit fraud dashboard with Docker support, 6 analytics modules, and 10,000+ TPS load testing built in. Your dashboard/streamlit_app.py is 70% based on this.

**What to TAKE:**

```
✅ The Plotly chart components       → line charts, pie charts, gauge
✅ The dark theme CSS injection      → CSS hack for dark Streamlit UI
✅ The metrics row (st.columns)      → Total scans / Blocked / Safe counts
✅ requirements.txt (base versions)  → good starting point, update versions
✅ The sample data generator         → fake CSV for demo when no MongoDB
```

**What NOT to TAKE:**

```
❌ Their ML model calls              → they use a different fraud model
❌ Docker files                      → you're deploying to Streamlit Cloud, no Docker needed
❌ Their database schema             → you're using MongoDB, they use PostgreSQL
```

**Integration:**

```bash
git clone https://github.com/firfircelik/fraud-detection-system-streamlit.git \
  reference/streamlit-dashboard

# Open their app.py and your streamlit_app.py side by side
# Cherry-pick these specific functions:
#   - create_gauge_chart()     → for risk score gauge
#   - render_metrics_row()     → for KPI cards at top
#   - apply_dark_theme()       → for the CSS hack
# Copy function by function — never copy the full file
```


***

## Repo 7 — `Vatshayan/UPI-Fraud-Detection-Using-Machine-Learning`

### Your UPI Dataset + ML Reference

🔗 **Link:** [github.com/Vatshayan/UPI-Fraud-Detection-Using-Machine-Learning](https://github.com/Vatshayan/UPI-Fraud-Detection-Using-Machine-Learning)[^8]

**What it is:** A full UPI fraud detection project with dataset, model, and web app — closest existing project to your UPI analyzer module.

**What to TAKE:**

```
✅ The dataset CSV                   → transaction features with fraud labels
✅ The feature column list           → what fields matter for UPI fraud
✅ The Random Forest pipeline        → as a second opinion to your XGBoost
```

**What NOT to TAKE:**

```
❌ Their web app                     → Flask-based, not Streamlit
❌ Their trained model               → retrain on fresh data
❌ Any hardcoded UPI VPAs            → build your own fraud_vpas.json fresh
```

```bash
git clone https://github.com/Vatshayan/UPI-Fraud-Detection-Using-Machine-Learning.git \
  reference/upi-vatshayan

# Get the dataset
cp reference/upi-vatshayan/dataset/*.csv ml-engine/data/upi_fraud_raw.csv

# Check columns
python3 -c "import pandas as pd; df=pd.read_csv('ml-engine/data/upi_fraud_raw.csv'); print(df.columns.tolist()); print(df.head(3))"
```


***

## Safe Integration Master Checklist

Follow this order exactly — each step prevents the most common breaking points:

```
BEFORE TOUCHING ANY REPO:
□ Create a reference/ folder in project root
□ All external repos clone INTO reference/ only
□ Never run npm install or pip install from reference/ folders
□ Add reference/ to .gitignore immediately

CLONING ORDER (must follow this sequence):
□ Phase 1: Clone all repos into reference/
□ Phase 2: Read each repo's README fully before copying anything
□ Phase 3: Copy files ONE BY ONE with explicit intent
□ Phase 4: Test after each file copy (load extension, check no errors)
□ Phase 5: Only then move to next repo

SPECIFIC RULES PER FILE TYPE:
□ .html/.css    → safe to copy, adjust paths and IDs
□ .py (ML)     → safe to copy functions, never copy full files
□ .js (extension) → DANGEROUS — read every line before copying
                    Delete any localhost/fetch calls first
□ .json (manifest) → NEVER copy, always write from scratch
□ .pkl/.onnx   → safe to copy as binary assets
□ package.json → NEVER copy, add deps manually one by one
□ requirements.txt → copy as reference, pin all versions yourself

TESTING AFTER EACH INTEGRATION:
□ chrome://extensions → Load unpacked → check 0 errors
□ Open Chrome DevTools → Extensions → service worker → check console
□ Visit any URL → badge should appear (even if it shows "?" initially)
□ python -c "import module_you_copied" → verify no import errors

NEVER DO THESE:
❌ Copy a whole repo folder into your project
❌ Copy-paste from GitHub web UI (loses encoding)
❌ Mix two repos' package.json dependencies
❌ Use a .pkl model file from any repo (train your own)
❌ Leave localhost:5000 calls from cprite's code in your extension
❌ Use their API keys or tokens (all hardcoded ones are expired/fake)
```


***

## Your `reference/` Folder Structure

After all clones, your reference folder looks like this — completely isolated from your real project:

```
reference/                          ← NEVER imported or run
├── cprite-ext/                     ← UI + structure reference
├── phishlang/                      ← Extract .onnx model only
├── shreyagopal-detection/          ← Download CSV datasets only
├── gangesh-detection/              ← Copy feature extraction logic
├── phishshield/                    ← Copy alert modal CSS only
├── streamlit-dashboard/            ← Copy chart components only
└── upi-vatshayan/                  ← Copy dataset CSV only
```

And your actual project never directly `import`s or `require`s anything from `reference/` — everything is manually ported, understood, and adapted line by line into your own files.
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^9]</span>

<div align="center">⁂</div>

[^1]: https://github.com/cprite/phishing-detection-ext

[^2]: https://github.com/UTA-SPRLab/phishlang

[^3]: https://github.com/yufuin/onnxruntime-web-on-extension/

[^4]: https://github.com/shreyagopal/Phishing-Website-Detection-by-Machine-Learning-Techniques

[^5]: https://github.com/gangeshbaskerr/Phishing-Website-Detection

[^6]: https://github.com/Vindhyaa-Saravanan/PhishShield

[^7]: https://github.com/firfircelik/fraud-detection-system-streamlit

[^8]: https://github.com/Vatshayan/UPI-Fraud-Detection-Using-Machine-Learning

[^9]: https://arxiv.org/pdf/2106.12343.pdf

[^10]: https://arxiv.org/pdf/2409.10547.pdf

[^11]: http://arxiv.org/pdf/2408.01667v2.pdf

[^12]: https://arxiv.org/pdf/2210.08273.pdf

[^13]: https://www.mdpi.com/2073-8994/16/2/248/pdf?version=1708330038

[^14]: https://arxiv.org/pdf/2407.04732.pdf

[^15]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9133026/

[^16]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11013960/

[^17]: https://github.com/cprite/phishing-detection-ext/blob/main/.DS_Store

[^18]: https://github.com/Phishing-Detection-System/Detection-Chrome-Extension

[^19]: https://versprite.com/threat-briefings/versprite-weekly-threat-intelligence-44/

[^20]: https://github.com/RakhithJK/Cyber-Security_Collection/blob/master/Readme_en.md

[^21]: https://www.facebook.com/zSecurty/posts/discover-a-powerful-osint-tool-that-lets-you-search-emails-phone-numbers-face-im/1202373411900742/

[^22]: https://onnxruntime.ai/docs/genai/tutorials/phi3-python.html

[^23]: https://www.youtube.com/watch?v=I1refTZp-pg

[^24]: https://stackoverflow.com/questions/66877085/github-actions-detect-changes-in-submodule

[^25]: https://github.com/UTA-SPRLab

[^26]: https://gist.github.com/samidunimsara/a1cf5a56a3028d9c6995650aa7c50604

[^27]: https://github.com/UTA-SPRLab/phishlang/releases

