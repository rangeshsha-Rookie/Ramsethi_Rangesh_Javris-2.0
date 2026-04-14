# 🧠 PhishGuard India: ML Engine

This directory contains the training and conversion logic for the phishing detection model.

## 📈 Model Overview

We use an **XGBoost Classifier** trained on 30+ URL features (length, special characters, TLD risk, etc.) to detect phishing attempts in real-time.

- **Primary Model**: `xgboost_phishing_model.onnx`
- **Inference Engine**: ONNX Runtime (Client-side)
- **Accuracy**: ~96-98% (verified on labeled datasets)

## 📁 Files

- `train.py`: Script to train the model using Scikit-Learn and XGBoost.
- `convert_to_onnx.py`: Script to export the trained model to the ONNX format for browser use.
- `features.txt`: List of the 30 features extracted from each URL.

## 🚀 Deployment

The model is exported to `../extension/models/` and loaded by the Chrome extension's content script to provide instant, offline-capable protection.
