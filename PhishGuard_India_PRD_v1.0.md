
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           PRODUCT REQUIREMENTS DOCUMENT (PRD)
           PhishGuard India — v1.0
           UPI QR Phishing + Fake Site Detector
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Document Version  : 1.0.0
Last Updated      : April 14, 2026
Author            : Rangesh Gupta
Institution       : KJSIT, Panvel, Maharashtra
Hackathon Track   : Track 2 — Cybersecurity (UPI QR Phishing + Fake Site Detector)
Status            : Draft — Ready for Development

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TABLE OF CONTENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1.  Executive Summary
  2.  Problem Statement
  3.  Target Users (Personas)
  4.  Goals & Success Metrics
  5.  Scope — In/Out
  6.  System Architecture
  7.  Feature Specifications (P0 / P1 / P2)
  8.  Technical Stack
  9.  API Contracts
  10. Data Models
  11. ML Model Specifications
  12. Security & Privacy
  13. Non-Functional Requirements
  14. Release Phases & Timeline
  15. Risk Register
  16. Appendix

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PhishGuard India is a browser-native cybersecurity tool delivered as a Chrome
Extension + Streamlit Dashboard + Blockchain Evidence Registry. It detects
phishing websites and fraudulent UPI QR codes in real time — before the user
clicks a malicious link or completes a fraudulent payment.

The core innovation is a UPI deeplink parser that cross-checks the merchant
display name (pn=) against the actual UPI VPA handle (pa=) — a mismatch
detection capability that no existing tool (including Google Safe Browsing,
PhishTank, or any published extension) currently provides.

Business Context:
  ▸ India processed 18.68 billion UPI transactions in May 2025
  ▸ ₹22,842 crore was lost to digital fraud in FY2024 (MHA Annual Report)
  ▸ 10.64 lakh cybercrime complaints registered on NCRP portal in 2024
  ▸ 67% of digital fraud in India begins with a phishing link or QR scan

Unique Value:
  "We are the first tool globally to detect UPI VPA name-handle mismatches
   in real time, directly inside the browser, without any server dependency."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. PROBLEM STATEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2.1  The Gap in Existing Tools
───────────────────────────────────────────────────────────────────────────────
  Tool                  | URL Detection | QR Scanning | UPI VPA Check
  ────────────────────────────────────────────────────────────────────
  Google Safe Browsing  |      ✅       |     ❌      |      ❌
  PhishTank             |      ✅       |     ❌      |      ❌
  Netcraft Extension    |      ✅       |     ❌      |      ❌
  NoPhish (research)    |      ✅       |     ❌      |      ❌
  PhishShield (hackathon)|     ✅       |     ❌      |      ❌
  ANY existing tool     |      -        |     -       |      ❌
  ────────────────────────────────────────────────────────────────────
  PhishGuard India      |      ✅       |     ✅      |      ✅  ← Only one

2.2  The Attack Vectors We Stop
───────────────────────────────────────────────────────────────────────────────
  VECTOR 1 — Phishing URLs in browser
    User receives a WhatsApp message: "Your HDFC account is locked.
    Verify here: http://hdfc-kyc-secure-2026.xyz/login"
    Current tools: May detect if URL is in PhishTank database.
    PhishGuard: ML model detects suspicious patterns (score > 70) even for
    brand-new URLs not yet in any database.

  VECTOR 2 — Fake QR codes on websites / social media
    Scammer posts a QR code image on a fake "Paytm Cashback" website.
    Current tools: No tool scans QR images on webpages.
    PhishGuard: Automatically scans all QR images on page load using jsQR.

  VECTOR 3 — UPI VPA name-handle mismatch (THE KILLER VECTOR)
    QR code encodes: upi://pay?pa=fraud91827@ybl&pn=Amazon Pay&am=199
    Display shows: "Amazon Pay" ← looks legitimate
    Actual VPA routes to: fraud91827@ybl ← completely unrelated account
    Current tools: ZERO tools catch this. None parse UPI deeplinks at all.
    PhishGuard: Detects mismatch, fires BLOCK alert, logs to blockchain.

  VECTOR 4 — Threshold evasion payments
    Scammer sets amount to ₹49,999 to stay below RBI's ₹50,000 alert limit.
    Current tools: No UPI awareness.
    PhishGuard: Flags amounts in ₹45,000–₹49,999 range as suspicious.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. TARGET USERS (PERSONAS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERSONA 1 — Ramesh, 52, Small Shop Owner, Pune
  Tech Level : Basic Chrome user, uses Google Pay / PhonePe daily
  Pain Point : Received fake "Amazon refund" QR via WhatsApp, lost ₹12,000
  Goal       : Wants a warning before he scans and pays
  Usage      : Extension auto-runs, sees red alert if QR is suspicious

PERSONA 2 — Priya, 24, IT Professional, Bangalore
  Tech Level : Intermediate, uses Chrome with multiple extensions
  Pain Point : Often clicks links from Telegram groups, fears phishing
  Goal       : Real-time URL check without slowing her browser
  Usage      : Extension badge shows green/yellow/red per tab

PERSONA 3 — Arnav, 19, Engineering Student, Mumbai (like you, Rangesh)
  Tech Level : Advanced, uses Chrome + VS Code + GitHub
  Pain Point : College group forwards fake "scholarship application" links
  Goal       : One-click scan for any suspicious URL or QR
  Usage      : Popup tab + UPI string manual check

PERSONA 4 — Vikram, 38, Payment Gateway Product Manager, Chennai
  Tech Level : Expert, needs B2B API integration
  Pain Point : Wants to add VPA verification to their checkout flow
  Goal       : REST API that returns fraud score for any VPA in <100ms
  Usage      : Calls /api/check-vpa before displaying payment confirmation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. GOALS & SUCCESS METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4.1  Hackathon Goals (48-hour target)
───────────────────────────────────────────────────────────────────────────────
  METRIC                        TARGET          MEASUREMENT
  ─────────────────────────────────────────────────────────────────
  URL phishing detection accuracy  ≥ 96%         Held-out test set (PhishTank)
  UPI fraud detection accuracy     ≥ 92%         Held-out UPI fraud test set
  Extension page analysis time     < 300ms       Chrome DevTools performance tab
  ONNX inference time              < 200ms       service-worker performance log
  VPA mismatch detection           100% recall   Manual test: 20 crafted cases
  Demo crash-free run              3/3 attempts  Live demo on judge's machine
  ─────────────────────────────────────────────────────────────────

4.2  Post-Hackathon Goals (3-month target)
───────────────────────────────────────────────────────────────────────────────
  METRIC                        TARGET
  ──────────────────────────────────────────────────────────
  Chrome Web Store installs        500+ in first month
  Community fraud reports          100+ VPAs reported in first 2 weeks
  B2B API calls                    1 payment company pilot integration
  False positive rate              < 3% (users not annoyed by wrong alerts)
  ──────────────────────────────────────────────────────────

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. SCOPE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IN SCOPE (Build in 48 hours):
  ✅ Chrome Extension MV3
  ✅ XGBoost URL phishing detection (ONNX in-browser)
  ✅ jsQR-based QR code scanning on webpages
  ✅ UPI deeplink parser (pa= vs pn= mismatch detection)
  ✅ Blockchain fraud registry (Polygon Amoy testnet)
  ✅ NVIDIA Nemotron Nano — Hinglish fraud explanations
  ✅ Streamlit analytics dashboard
  ✅ Vercel serverless API (/check-vpa, /report-fraud)

OUT OF SCOPE (Future versions):
  ❌ Firefox / Safari / Mobile browser extensions
  ❌ SMS phishing (smishing) detection
  ❌ Voice call fraud (vishing) detection
  ❌ Real NPCI VPA validation API (requires banking partnership)
  ❌ iOS / Android native app
  ❌ Machine learning retraining pipeline (automated)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. SYSTEM ARCHITECTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ┌────────────────────────────────────────────────────────────────┐
  │                    USER'S CHROME BROWSER                        │
  │                                                                  │
  │  ┌─────────────┐    ┌──────────────────────────────────────┐   │
  │  │   POPUP UI  │    │         SERVICE WORKER               │   │
  │  │  (React)    │◄──►│  - PhishLang ONNX inference          │   │
  │  │  3 tabs:    │    │  - Tab URL monitoring                 │   │
  │  │  · Status   │    │  - Badge color management            │   │
  │  │  · QR Scan  │    │  - Notification dispatcher           │   │
  │  │  · History  │    │  - Message router                    │   │
  │  └─────────────┘    └──────────────┬───────────────────────┘   │
  │                                    │ chrome.runtime.sendMessage  │
  │  ┌─────────────────────────────────▼──────────────────────────┐ │
  │  │                  CONTENT SCRIPTS                            │ │
  │  │  qr-scanner.js          upi-parser.js                      │ │
  │  │  - Scan all <img> tags  - Parse upi:// deeplinks           │ │
  │  │  - jsQR decode          - Check pa= vs pn= mismatch        │ │
  │  │  - Inject alerts/modals - Score 0-100 risk calculation     │ │
  │  └────────────────────────────────────────────────────────────┘ │
  └────────────────────────────────────────────────────────────────┘
            │                           │
            ▼                           ▼
  ┌──────────────────┐       ┌──────────────────────────┐
  │  VERCEL API      │       │  POLYGON AMOY TESTNET     │
  │  (Serverless)    │       │  FraudRegistry.sol        │
  │  /check-vpa      │       │  - reportFraudVPA()       │
  │  /report-fraud   │       │  - getFraudScore()        │
  │       │          │       │  - isHighRisk()           │
  │       ▼          │       └──────────────────────────┘
  │  MongoDB Atlas   │
  │  (fraud_reports) │       ┌──────────────────────────┐
  └──────────────────┘       │  STREAMLIT DASHBOARD      │
                             │  (Community Cloud)        │
                             │  - URL Scanner            │
                             │  - UPI QR Analyzer        │
                             │  - Analytics + Map        │
                             └──────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │              NVIDIA NIM API                              │
  │  llama-nemotron-nano-4b-instruct                        │
  │  Called when risk_score > 40                            │
  │  Returns Hinglish/English explanation (max 60 tokens)   │
  └─────────────────────────────────────────────────────────┘

DATA FLOW — URL Phishing Detection:
  1. User opens any tab
  2. Service worker intercepts URL via chrome.tabs.onUpdated
  3. Extracts 6 features (url_length, has_https, subdomain_depth,
     has_at_symbol, is_shortened, has_ip)
  4. Runs ONNX inference on PhishLang model (in-browser, no server)
  5. Score returned in < 200ms
  6. Badge color updated + optional notification if score > 70
  7. If score > 70: calls NVIDIA NIM for explanation text
  8. Explanation shown in popup / notification

DATA FLOW — UPI QR Fraud Detection:
  1. Page loads, content script injects into DOM
  2. qr-scanner.js finds all <img> elements > 50x50px
  3. Canvas decode → jsQR → UPI string extracted
  4. If upi:// prefix found: upi-parser.js runs 5 checks
  5. Risk score 0-100 computed in JS (no server call needed)
  6. If score > 60: red blocking modal injected into page
  7. If KNOWN_FRAUD_VPA: calls /api/check-vpa for blockchain confirmation
  8. If user clicks Report: calls /api/report-fraud + logs to Polygon

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. FEATURE SPECIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIORITY KEY:
  P0 = Must have (demo breaks without it)
  P1 = Should have (judges will notice if missing)
  P2 = Nice to have (bonus points)

─────────────────────────────────────────────────────────────────────────────
FEATURE 1 — URL Phishing Detection                                    [P0]
─────────────────────────────────────────────────────────────────────────────
  ID            : F-001
  Component     : Chrome Extension → Service Worker
  Description   : Every URL the user opens is scored 0-100 for phishing
                  risk using an ONNX model running locally in the browser.

  Inputs        : Active tab URL (string)

  Processing    :
    Step 1 — Feature extraction (6 features):
      · url_length         : len(url)
      · has_https          : 1 if scheme == "https" else 0
      · subdomain_depth    : url.split(".").length - 2
      · has_at_symbol      : 1 if "@" in url else 0
      · is_shortened       : 1 if domain in [bit.ly, tinyurl.com, t.co, goo.gl]
      · has_ip             : 1 if IPv4 pattern in host

    Step 2 — ONNX Inference:
      · Model: phishlang.onnx (MobileBERT, NDSS 2026)
      · Runtime: onnxruntime-web, WASM backend
      · numThreads: 1 (service worker limitation)
      · Input shape: [1, 6] float32 tensor
      · Output: probability score [0.0, 1.0]

    Step 3 — Score mapping:
      · score * 100 = risk_score (0-100)
      · risk_score < 40  → SAFE  (green badge "✓")
      · risk_score 40-70 → WARN  (yellow badge "!")
      · risk_score > 70  → FRAUD (red badge "✗")

  Outputs       :
    · Badge text + color on extension icon
    · chrome.notifications if FRAUD
    · Popup displays score + flags

  Fallback      : If ONNX fails, call Google Safe Browsing API v4

  Acceptance Criteria:
    · AC-001: Badge updates within 300ms of tab URL change
    · AC-002: Score ≥ 90 for known PhishTank URLs
    · AC-003: Score ≤ 20 for google.com, amazon.in, hdfc.com
    · AC-004: No browser crash or memory leak after 50 URL checks
    · AC-005: Model loads once at service worker startup, cached thereafter

─────────────────────────────────────────────────────────────────────────────
FEATURE 2 — QR Code Page Scanner                                      [P0]
─────────────────────────────────────────────────────────────────────────────
  ID            : F-002
  Component     : Chrome Extension → Content Script (qr-scanner.js)
  Description   : Automatically scans all QR code images visible on any
                  webpage and decodes them using jsQR.

  Trigger       : document "load" event on every page

  Processing    :
    Step 1 — Image discovery:
      · querySelectorAll('img, canvas')
      · Filter: naturalWidth > 50 && naturalHeight > 50
      · Skip already-scanned images (data attribute flag)

    Step 2 — QR decode:
      · Draw image to offscreen <canvas> element
      · getImageData from 2D context
      · Pass to jsQR(imageData.data, width, height)
      · jsQR returns null (not a QR) or { data: "decoded string" }

    Step 3 — Route by QR content:
      · Starts with "upi://"  → send to F-003 (UPI Parser)
      · Starts with "http"    → send to F-001 (URL check)
      · Starts with "tel:"    → show info (phone number in QR)
      · Other                 → log silently, no alert

    Step 4 — Floating button:
      · Inject "🛡️ Scan QR" button (bottom-right, z-index: 99999)
      · On click: getUserMedia() camera stream for live QR scanning
      · Camera stream decoded by jsQR in 200ms polling loop

  Outputs       :
    · Send message to service worker with QR content
    · Overlay alert modal if fraud detected

  Acceptance Criteria:
    · AC-006: QR in <img> tag decoded within 500ms of page load
    · AC-007: Floating button visible on all pages, not covering content
    · AC-008: Camera scan correctly decodes physical QR held to camera
    · AC-009: Non-QR images produce zero false positives (jsQR returns null)
    · AC-010: Works on popular payment pages (PhonePe website, Paytm, BillDesk)

─────────────────────────────────────────────────────────────────────────────
FEATURE 3 — UPI Deeplink VPA Mismatch Detector                        [P0]
─────────────────────────────────────────────────────────────────────────────
  ID            : F-003
  Component     : Chrome Extension → Content Script (upi-parser.js)
  Description   : Parses UPI URI strings and detects fraud through 5
                  independent checks. This is the zero-competition feature.

  Input         : UPI URI string
                  Format: upi://pay?pa=<VPA>&pn=<DisplayName>&am=<Amount>&cu=INR

  Processing — 5 Fraud Checks:
    ┌─────┬──────────────────────────────┬────────────┬──────────────────────┐
    │Check│ Name                         │ Points     │ Logic                │
    ├─────┼──────────────────────────────┼────────────┼──────────────────────┤
    │ C1  │ VPA Format Validation        │ +40 if FAIL│ regex: ^[a-zA-Z0-9   │
    │     │                              │            │ ._-]+@[a-zA-Z]+$     │
    ├─────┼──────────────────────────────┼────────────┼──────────────────────┤
    │ C2  │ Name-VPA Mismatch            │ +35 if FAIL│ fuzzy similarity     │
    │     │ (THE CORE INNOVATION)        │            │ pn words vs pa prefix│
    │     │                              │            │ < 30% match = flag   │
    ├─────┼──────────────────────────────┼────────────┼──────────────────────┤
    │ C3  │ Threshold Evasion Amount     │ +20 if MATCH│ 45000 ≤ am ≤ 49999  │
    ├─────┼──────────────────────────────┼────────────┼──────────────────────┤
    │ C4  │ Known Fraud VPA              │ = 100 BLOCK│ pa in fraud_vpas.json│
    ├─────┼──────────────────────────────┼────────────┼──────────────────────┤
    │ C5  │ VPA Digit Ratio Suspicious   │ +15 if HIGH│ digit_count/vpa_len  │
    │     │                              │            │ > 40% digits = flag  │
    └─────┴──────────────────────────────┴────────────┴──────────────────────┘

  Output        : JSON object:
    {
      risk_score:     Number (0-100),
      flags:          Array<String>,    // ["NAME_VPA_MISMATCH", ...]
      recommendation: "SAFE"|"WARN"|"BLOCK",
      parsed: {
        pa:           String,           // VPA
        pn:           String,           // Display name
        am:           String,           // Amount
        handle:       String            // part after @
      },
      explanation:    String            // Hinglish/English (from NVIDIA NIM)
    }

  Thresholds    :
    · score < 35  → SAFE  (green toast, 2 seconds)
    · score 35-60 → WARN  (yellow banner, user must acknowledge)
    · score > 60  → BLOCK (full-screen red modal, must click "I understand risk")
    · score = 100 → BLOCK + auto-report to blockchain

  Acceptance Criteria:
    · AC-011: "upi://pay?pa=amazonpay@apl&pn=Amazon Pay&am=200" → SAFE
    · AC-012: "upi://pay?pa=rnd9182@ybl&pn=Amazon Pay&am=199" → WARN/BLOCK
    · AC-013: "upi://pay?pa=hdfc_kyc@paytm&pn=HDFC Bank&am=1" → BLOCK
    · AC-014: Amount ₹49,999 with unknown VPA → WARN (threshold_evasion flag)
    · AC-015: Known fraud VPA from fraud_vpas.json → BLOCK instantly

─────────────────────────────────────────────────────────────────────────────
FEATURE 4 — Extension Popup UI                                        [P0]
─────────────────────────────────────────────────────────────────────────────
  ID            : F-004
  Component     : Chrome Extension → Popup (popup.html + popup.js)
  Description   : The user-facing control center. 3-tab interface.

  Dimensions    : 400px wide × auto height (max 600px)

  Tab 1 — "Current Page":
    · Large circular risk score gauge (0-100, color-coded)
    · Current URL (truncated to 40 chars)
    · Detected flags as pill badges (red)
    · "Report this site" button → calls /api/report-fraud
    · "Check another URL" text input

  Tab 2 — "Scan UPI":
    · Textarea: "Paste UPI string here..."
    · "Analyze" button
    · Result card:
      - Risk score bar (0-100)
      - Recommendation badge (SAFE/WARN/BLOCK)
      - Flags list
      - Parsed details (VPA, display name, amount)
      - AI explanation (Hinglish/English)
    · QR image upload button (triggers camera or file picker)

  Tab 3 — "History":
    · Last 10 scans from chrome.storage.local
    · Each row: favicon, URL/VPA, score circle, time ago
    · "Clear History" button

  Design Tokens :
    --safe:   #22c55e
    --warn:   #f59e0b
    --danger: #ef4444
    --bg:     #0f172a
    --surface:#1e293b
    --text:   #f1f5f9
    --muted:  #94a3b8
    Font: Inter (system-ui fallback)

  Acceptance Criteria:
    · AC-016: Popup opens in < 100ms
    · AC-017: Tab switches animate smoothly (no flash)
    · AC-018: History persists after browser restart
    · AC-019: "Report" button shows success toast after click
    · AC-020: UPI analyze from popup matches content script result

─────────────────────────────────────────────────────────────────────────────
FEATURE 5 — Blockchain Fraud Registry                                 [P1]
─────────────────────────────────────────────────────────────────────────────
  ID            : F-005
  Component     : Solidity → Polygon Amoy Testnet
  Description   : Immutable, decentralized record of community-reported
                  fraud VPAs and URLs. Tamper-proof evidence for FIR filing.

  Contract      : FraudRegistry.sol
  Network       : Polygon Amoy (chainId: 80002)

  Functions     :
    reportFraudVPA(string vpa)
      · Requires: VPA not already reported by this address
      · Increments: reporterCount
      · Emits: FraudReported(vpa, "VPA", count, reporter)

    getFraudScore(string vpa) → uint256
      · Returns community report count for VPA

    isHighRisk(string vpa) → bool
      · Returns true if reporterCount ≥ 3

    reportFraudURL(string url)
      · Same as VPA but hashes URL first (keccak256)

  Events        :
    FraudReported(string indexed identifier, string fraudType,
                  uint256 reportCount, address reporter)

  Acceptance Criteria:
    · AC-021: reportFraudVPA() completes in < 5 seconds on Amoy
    · AC-022: Transaction hash displayed to user in popup after report
    · AC-023: Same address cannot report same VPA twice (require)
    · AC-024: Contract deployed and verified on Polygon Amoy Explorer

─────────────────────────────────────────────────────────────────────────────
FEATURE 6 — NVIDIA NIM AI Explanations                                [P1]
─────────────────────────────────────────────────────────────────────────────
  ID            : F-006
  Component     : Extension → NVIDIA NIM API
  Description   : When a threat is detected, generate a human-friendly
                  explanation in Hinglish (default) or English.

  Model         : nvidia/llama-nemotron-nano-4b-instruct
  Endpoint      : https://integrate.api.nvidia.com/v1/chat/completions
  Max tokens    : 60
  Temperature   : 0.3

  Triggered when: risk_score > 40 (any detection)

  Input context :
    · type: "PHISHING_URL" | "FRAUD_QR" | "VPA_MISMATCH"
    · url or vpa (depending on type)
    · flags array
    · risk_score
    · language: "hinglish" (default for IN locale) | "english"

  Sample output :
    Hinglish: "Yaar, ye QR code suspicious lag raha hai! Merchant
    'Amazon Pay' bata raha hai but VPA handle match nahi kar raha.
    Payment mat karo, pehle verify karo!"

    English: "Warning: This QR code displays 'Amazon Pay' but the
    actual UPI handle appears fraudulent. Do not proceed."

  Fallback      : Static lookup table (5 entries, one per flag type)
                  Used when: API key missing, rate limit, network error

  Acceptance Criteria:
    · AC-025: Explanation appears within 2 seconds of threat detection
    · AC-026: Hinglish used when Chrome locale is en-IN or hi-IN
    · AC-027: Fallback table triggers on API failure with no UX break
    · AC-028: Response is max 2 sentences (enforced via max_tokens: 60)

─────────────────────────────────────────────────────────────────────────────
FEATURE 7 — Streamlit Analytics Dashboard                             [P1]
─────────────────────────────────────────────────────────────────────────────
  ID            : F-007
  Component     : Streamlit → Community Cloud
  Description   : Public-facing fraud analytics dashboard.

  Page 1 — URL Scanner:
    · Text input → check any URL → returns risk gauge + feature breakdown
    · Powered by phishnet_xgboost.pkl (Python server-side)

  Page 2 — UPI QR Analyzer:
    · Paste UPI string OR upload QR image (pyzbar decode)
    · Returns risk score, flags, recommendation banner

  Page 3 — Analytics:
    · Total scans (st.metric)
    · Phishing blocked today (st.metric)
    · Line chart: scans per day, split by verdict (Plotly)
    · Pie chart: flag type distribution
    · World map: fraud URL origin by TLD
    · Data table: last 20 reports (color-coded rows)

  Acceptance Criteria:
    · AC-029: All 3 pages load in < 3 seconds on Streamlit Community Cloud
    · AC-030: Analytics page works with sample_data.csv when no MongoDB
    · AC-031: QR image upload correctly decodes and analyzes UPI string
    · AC-032: Dark theme applied consistently across all pages

─────────────────────────────────────────────────────────────────────────────
FEATURE 8 — Vercel REST API                                           [P2]
─────────────────────────────────────────────────────────────────────────────
  ID            : F-008
  Component     : Vercel Serverless Functions

  Endpoint 1    : GET /api/check-vpa?vpa=merchant@ybl
    Response:
      {
        "vpa": "merchant@ybl",
        "riskScore": 75,
        "reportCount": 3,
        "isKnownFraud": true,
        "source": "community_reports",
        "onChainScore": 3
      }

  Endpoint 2    : POST /api/report-fraud
    Body: { vpa, url, reporterHash, evidence }
    Response: { success: true, reportId: "uuid" }

  Rate Limiting : 10 requests/IP/minute (in-memory, Vercel Edge)
  CORS          : Allow chrome-extension://* origins

  Acceptance Criteria:
    · AC-033: /check-vpa responds in < 200ms (p95)
    · AC-034: Rate limiting returns 429 on excess requests
    · AC-035: No MongoDB URI or private keys in any response body

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. TECHNICAL STACK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Layer            │ Technology            │ Version   │ License
  ─────────────────┼───────────────────────┼───────────┼──────────────
  Extension        │ Chrome Extension MV3  │ MV3       │ -
  Extension UI     │ Vanilla JS + CSS      │ -         │ -
  QR Decode        │ jsQR                  │ 1.4.0     │ Apache 2.0
  ML Inference     │ onnxruntime-web       │ 1.18.0    │ MIT
  ML Model         │ PhishLang ONNX        │ NDSS 2026 │ MIT
  Base ML Training │ XGBoost               │ 2.0.3     │ Apache 2.0
  UPI Fine-tune    │ XGBoost (incremental) │ 2.0.3     │ Apache 2.0
  Blockchain       │ Solidity              │ ^0.8.19   │ -
  Blockchain Dev   │ Hardhat               │ 2.22.x    │ MIT
  Blockchain Net   │ Polygon Amoy          │ chainId:  │ -
                   │                       │ 80002     │ -
  Contract Interact│ ethers.js             │ 6.x       │ MIT
  AI Explanations  │ NVIDIA NIM            │ -         │ NVIDIA ToS
  AI Model         │ Nemotron Nano 4B      │ -         │ NVIDIA ToS
  Dashboard        │ Streamlit             │ 1.35.x    │ Apache 2.0
  Charts           │ Plotly Express        │ 5.x       │ MIT
  Database         │ MongoDB Atlas         │ Free tier │ SSPL
  API Backend      │ Vercel Functions      │ -         │ -
  Data Imbalance   │ imbalanced-learn      │ 0.12.x    │ MIT
  Training Data    │ PhishTank             │ live CSV  │ CC BY-SA 2.5
  ─────────────────┴───────────────────────┴───────────┴──────────────

  Environment Variables (all stored in .env, never committed):
    MONGODB_URI          = mongodb+srv://...
    CONTRACT_ADDRESS     = 0x...
    POLYGON_RPC          = https://rpc-amoy.polygon.technology/
    PRIVATE_KEY          = 0x... (deployment only)
    NVIDIA_API_KEY       = nvapi-...
    GOOGLE_SAFE_BROWSING = AIza...
    VERCEL_API_URL       = https://phishguard.vercel.app

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. API CONTRACTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  GET /api/check-vpa
  ──────────────────
  Request:
    GET /api/check-vpa?vpa=amazon_refund91%40ybl
    Headers: { Origin: "chrome-extension://..." }

  Response 200:
    {
      "vpa": "amazon_refund91@ybl",
      "riskScore": 78,
      "reportCount": 5,
      "isKnownFraud": false,
      "isHighRisk": true,
      "source": "community_reports",
      "onChainScore": 5,
      "flags": ["HIGH_DIGIT_RATIO", "NAME_VPA_MISMATCH"],
      "recommendation": "BLOCK"
    }

  Response 429:
    { "error": "Rate limit exceeded. Try again in 60 seconds." }

  ─────────────────────────────────────────────────────────────────

  POST /api/report-fraud
  ──────────────────────
  Request:
    POST /api/report-fraud
    Content-Type: application/json
    {
      "vpa": "amazon_refund91@ybl",
      "url": null,
      "reporterHash": "sha256(extensionId + timestamp)",
      "evidence": "UPI QR found at https://example.com/payment"
    }

  Response 200:
    {
      "success": true,
      "reportId": "550e8400-e29b-41d4-a716-446655440000",
      "message": "Report saved. Thank you for making India safer."
    }

  ─────────────────────────────────────────────────────────────────

  Internal Message Schema (Extension chrome.runtime.sendMessage):

    UPI_SCAN_REQUEST:
      { type: "UPI_SCAN_REQUEST", data: "upi://pay?pa=...&pn=...&am=..." }

    URL_SCAN_REQUEST:
      { type: "URL_SCAN_REQUEST", url: "https://..." }

    REPORT_FRAUD:
      { type: "REPORT_FRAUD", vpa: "...", url: "...", evidence: "..." }

    GET_STATS:
      { type: "GET_STATS" }
      → Response: { totalScans: 42, fraudBlocked: 7, lastScan: timestamp }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
10. DATA MODELS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  chrome.storage.local Schema:
    {
      "scan_history": [
        {
          "id":           "uuid",
          "type":         "url" | "upi",
          "input":        "https://..." | "upi://...",
          "risk_score":   Number,
          "verdict":      "SAFE" | "WARN" | "FRAUD" | "BLOCK",
          "flags":        Array<String>,
          "timestamp":    ISO8601 string,
          "explanation":  String
        }
      ],
      "fraud_count":      Number,
      "total_scans":      Number,
      "settings": {
        "language":       "hinglish" | "english",
        "notifications":  Boolean,
        "nvidia_api_key": String
      }
    }

  MongoDB fraud_reports Collection:
    {
      "_id":          ObjectId,
      "type":         "vpa" | "url",
      "identifier":   String,        // VPA or URL hash
      "reporterHash": String,
      "evidence":     String,
      "timestamp":    Date,
      "ip_hash":      String,        // SHA256 of reporter IP
      "resolved":     Boolean        // false = still active
    }

  fraud_vpas.json (bundled with extension):
    [
      {
        "vpa":         "fraud@ybl",
        "reportCount": 15,
        "firstSeen":   "2025-01-15",
        "tags":        ["kyc_scam", "fake_bank"]
      }
    ]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
11. ML MODEL SPECIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Model A — PhishLang ONNX (URL Detection)
  ─────────────────────────────────────────
    Source     : UTA-SPRLab/phishlang (NDSS 2026)
    Type       : MobileBERT-based classifier
    File       : phishlang.onnx + WASM runtime files
    Features   : 6 URL features (fast extraction, no network calls)
    Target     : > 96% accuracy on PhishTank test set
    Runtime    : onnxruntime-web, service worker, WASM backend
    Inference  : < 200ms per URL

  Model B — PhishNet XGBoost (URL + UPI unified)
  ───────────────────────────────────────────────
    Source     : Trained from scratch (shreyagopal dataset + PhishTank)
    Type       : XGBoost binary classifier (300 base trees)
    File       : phishnet_xgboost.pkl
    Features   : 17 URL features (full feature set for offline analysis)
    Target     : > 96% accuracy
    Used in    : Streamlit dashboard (server-side Python)

  Model C — PhishNet UPI Fine-tuned (UPI-specific)
  ─────────────────────────────────────────────────
    Source     : Fine-tuned from Model B using incremental training
    Type       : XGBoost (300 + 80 = ~350 trees)
    File       : phishnet_upi.pkl
    Features   : 12 features (6 URL base + 6 UPI-specific)
    UPI features:
      · legit_handle       (1/0 — known handle like ybl, oksbi)
      · vpa_digit_ratio    (float — suspicious if > 0.4)
      · name_vpa_match     (1/0 — key innovation feature)
      · threshold_evasion  (1/0 — ₹45K-₹49999 range)
      · zero_amount        (1/0 — ₹0 used in scam QRs)
      · vpa_length         (int — unusually long VPAs)
    Training   : SMOTE oversampling + scale_pos_weight
    learning_rate: 0.03 (lower than base to prevent forgetting)
    Target     : > 92% accuracy on UPI fraud test set
    Used in    : Streamlit dashboard + /api/check-vpa endpoint

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
12. SECURITY & PRIVACY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Data Privacy:
    · No URL or UPI data sent to any server by default
    · ML inference runs 100% in browser (ONNX)
    · UPI parser runs 100% in browser (pure JS)
    · Only FRAUD-confirmed reports are sent to API (user-initiated)
    · Reporter IP is hashed (SHA256) before storage, never stored raw
    · No cookies, no tracking, no analytics on user browsing

  Extension Permissions Minimization:
    · "activeTab"    — only current tab, not all tabs
    · "storage"      — local only (chrome.storage.local)
    · "scripting"    — required for content script injection
    · "notifications" — for fraud alerts only
    · NO: "history", "bookmarks", "cookies", "webRequest" (not needed)

  Content Security Policy:
    · "script-src 'self' 'wasm-unsafe-eval'" — required for ONNX WASM
    · No inline scripts, no eval() anywhere
    · All third-party scripts bundled locally (no CDN in production)

  API Security:
    · All API keys stored in chrome.storage.local (not hardcoded)
    · NVIDIA API key is user-provided (not bundled)
    · Vercel API: rate limiting per IP, CORS restricted to extension origin
    · MongoDB: read-only user for dashboard, write-only for report endpoint

  Blockchain Privacy:
    · Fraud reports are public (by design — community protection)
    · Reporter address is pseudonymous (Ethereum address, not name)
    · User warned before on-chain report: "This will be public forever"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
13. NON-FUNCTIONAL REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Performance:
    · URL badge update          < 300ms (p95)
    · ONNX inference            < 200ms (p95)
    · UPI parse + score         < 50ms  (pure JS, synchronous)
    · Popup open                < 100ms
    · Extension memory          < 50MB RAM (Chrome budget)
    · QR page scan              < 500ms per image

  Reliability:
    · Extension must not crash on any page (try/catch all content scripts)
    · Service worker must restart gracefully after idle kill (MV3 behavior)
    · All features must degrade gracefully when offline

  Compatibility:
    · Chrome 120+ (Manifest V3)
    · Windows 10/11, macOS 12+, Ubuntu 22.04
    · Screen resolutions: 1024×768 minimum

  Offline Behavior:
    · URL check: ONNX inference works offline ✅
    · UPI parse: Works offline ✅
    · NVIDIA NIM: Fallback to static table if no internet ✅
    · Blockchain report: Queued and retried when online ⚠️
    · Vercel API: Cached last results used if offline ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
14. RELEASE PHASES & 48-HOUR TIMELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Hour  0-2   | Phase 0: Project scaffold + Git setup + manifest.json
  Hour  2-6   | Phase 1: ML Engine — XGBoost train (17 features, 300 trees)
  Hour  6-10  | Phase 2: UPI Analyzer — pa= vs pn= mismatch module
  Hour 10-14  | Phase 3: QR Scanner content script (jsQR + DOM injection)
  Hour 14-18  | Phase 3: Service worker (ONNX + badge + notifications)
  Hour 18-22  | Phase 3: Popup UI (3 tabs, vanilla JS)
  Hour 22-26  | Phase 5: Blockchain — FraudRegistry.sol + Amoy deploy
  Hour 26-30  | Phase 6: NVIDIA NIM integration (30 min — just API call)
  Hour 30-36  | Phase 4: Streamlit dashboard (3 pages)
  Hour 36-40  | Phase 7: Vercel API endpoints + MongoDB connection
  Hour 40-44  | QA: End-to-end testing with real phishing URLs + fake QRs
  Hour 44-48  | Devpost write-up + demo video + pitch rehearsal

  CRITICAL PATH (never skip, directly affects judge demo):
    Phase 2 (UPI mismatch) → Phase 3 (QR scanner) → Phase 3 (extension loads)
    If time runs short: skip Phase 5 (blockchain), ship Phase 0-3+6 first.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
15. RISK REGISTER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  RISK                      │ LIKELIHOOD │ IMPACT │ MITIGATION
  ──────────────────────────┼────────────┼────────┼────────────────────────────
  ONNX fails in SW (CSP)    │  HIGH      │  HIGH  │ Add wasm-unsafe-eval to
                            │            │        │ manifest CSP. Use WASM not
                            │            │        │ WebGPU backend.
  ──────────────────────────┼────────────┼────────┼────────────────────────────
  jsQR false negatives on   │  MEDIUM    │  MEDIUM│ Use pyzbar in Streamlit as
  low-res QR images         │            │        │ secondary decode fallback.
  ──────────────────────────┼────────────┼────────┼────────────────────────────
  PhishLang .onnx model     │  MEDIUM    │  HIGH  │ Export from their PyTorch
  not available as download │            │        │ model using torch.onnx.export
  ──────────────────────────┼────────────┼────────┼────────────────────────────
  Polygon Amoy faucet slow  │  MEDIUM    │  LOW   │ Request MATIC 12 hrs before
  or down                   │            │        │ hackathon start. Keep backup.
  ──────────────────────────┼────────────┼────────┼────────────────────────────
  NVIDIA NIM rate limit     │  LOW       │  LOW   │ Static fallback table ready.
  during demo               │            │        │ Pre-cache demo explanations.
  ──────────────────────────┼────────────┼────────┼────────────────────────────
  XGBoost model accuracy    │  LOW       │  MEDIUM│ Use PhishTank live dataset
  < 90%                     │            │        │ + shreyagopal dataset combo.
  ──────────────────────────┼────────────┼────────┼────────────────────────────
  Service worker killed mid │  HIGH      │  MEDIUM│ MV3 behavior — model session
  inference (MV3 timeout)   │            │        │ persisted in globalThis cache.
                            │            │        │ loadModel() checks cache first.
  ──────────────────────────┴────────────┴────────┴────────────────────────────

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
16. APPENDIX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  A. UPI URI Specification Reference
    Format:  upi://pay?pa=VPA&pn=NAME&am=AMOUNT&cu=CURRENCY&tn=NOTE
    pa  = Payee Virtual Payment Address (VPA) — ROUTING field
    pn  = Payee Name (Display) — DISPLAY ONLY, not validated by UPI system
    am  = Amount in INR
    cu  = Currency (always INR)
    tn  = Transaction note (optional)

    CRITICAL: pn is NEVER validated by NPCI or any UPI app.
    A scammer can set pn="SBI Bank" while pa routes to their account.
    This is the exploit PhishGuard uniquely detects.

  B. Known Legitimate VPA Handle List (for C1 check)
    ybl, oksbi, okaxis, okhdfcbank, paytm, icici, hdfcbank,
    kotak, apl, airtel, jio, upi, okicici, ibl, sbi, aubank,
    pnb, boi, citi, hsbc, axisbank, idbi, fbl, rbl

  C. Hackathon Judge Scoring Rubric (from file:131)
    Innovation        : 30% weight → our zero-competition UPI feature scores max
    Real-world impact : 25% weight → ₹22,842 Cr fraud number = instant win
    Technical execution: 25% weight → ONNX in-browser = strong technical signal
    Scalability/business: 20% weight → B2B API + ₹0.05/check model

  D. Demo Script Summary (3 minutes)
    0:00-0:30  Hook with ₹22,842 Cr stat
    0:30-1:00  Demo 1: URL phishing (red badge appears in 200ms)
    1:00-2:00  Demo 2: UPI QR mismatch (THE KILLER DEMO — red modal fires)
    2:00-2:30  Demo 3: Blockchain evidence (transaction hash visible)
    2:30-3:00  Business model (₹0.05 × 18B transactions pitch)

  E. GitHub Repos Used
    Reference (DO NOT import directly):
    · cprite/phishing-detection-ext     → extension UI structure
    · UTA-SPRLab/phishlang              → ONNX model extraction
    · shreyagopal/Phishing-Website-Detection → training datasets
    · gangeshbaskerr/Phishing-Website-Detection → feature extractor
    · Vindhyaa-Saravanan/PhishShield    → alert modal CSS
    · firfircelik/fraud-detection-system-streamlit → dashboard template
    · Vatshayan/UPI-Fraud-Detection     → UPI dataset

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  END OF DOCUMENT
  PhishGuard India PRD v1.0 | April 14, 2026 | KJSIT Hackathon Track 2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
