# 📂 PhishGuard India Project Structure

This document provides a map of the PhishGuard India repository to help developers and judges understand the architecture.

## 📁 Project Overview

```text
root/
├── api/                # Vercel Serverless Functions (Phase 7)
│   ├── check-vpa.js    # Global VPA fraud lookup logic
│   └── report-fraud.js # Community fraud reporting to MongoDB
├── blockchain/         # Polygon Smart Contracts (Phase 5)
│   ├── contracts/      # Solidity Source (FraudRegistry.sol)
│   └── scripts/        # Deployment and interaction scripts
├── dashboard/          # Streamlit Analytics Dashboard (Phase 4)
│   ├── streamlit_app.py # Main UI and visualizations
│   └── requirements.txt # Python dependencies
├── extension/          # Chrome Extension (Phases 1-3 & 6)
│   ├── background/     # Service Workers (NVIDIA AI, Blockchain)
│   ├── popup/          # Extension UI and Settings
│   ├── content/        # Content scripts for on-page detection
│   └── models/         # Pre-trained ML models (ONNX)
└── ml-engine/          # Machine Learning Training (Phase 1)
    ├── train.py        # Model training script
    └── convert.py      # Script to convert models to ONNX
```

## 🛠️ Key Components

### 🧠 AI Analysis
- **Local (XGBoost/ONNX)**: Fast on-device phishing detection using `xgboost_phishing_model.onnx`.
- **Cloud (NVIDIA NIM)**: Human-friendly Hinglish explanations using Llama-3.1 via NVIDIA NIM.

### ⛓️ Blockchain Registry
- **Polygon Amoy**: Distributed ledger for immutable fraud logging.
- **Contract**: `FraudRegistry.sol` handles the secure reporting of suspicious handles.

### ☁️ Cloud Backend
- **Vercel**: Hosts the central API for data synchronization.
- **MongoDB**: Stores community-voted fraud reports for real-time protection.
