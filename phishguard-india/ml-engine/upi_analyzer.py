"""UPI analyzer for QR strings."""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import parse_qs, urlparse


VPA_REGEX = re.compile(r"^[a-zA-Z0-9._-]+@[a-zA-Z]+$")
SUSPICIOUS_HANDLE_REGEX = re.compile(r"^(?=.*\d)[a-zA-Z0-9._-]{6,}$")


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio() * 100


def _load_fraud_vpas() -> set[str]:
    data_path = Path(__file__).resolve().parents[1] / "extension" / "data" / "fraud_vpas.json"
    if not data_path.exists():
        return set()
    try:
        with data_path.open("r", encoding="utf-8") as handle:
            values = json.load(handle)
            return {str(vpa).strip() for vpa in values if str(vpa).strip()}
    except (json.JSONDecodeError, OSError):
        return set()


def analyze_upi_qr(upi_string: str) -> dict:
    if not upi_string.startswith("upi://"):
        return {
            "risk_score": 0,
            "flags": [],
            "recommendation": "SAFE",
            "parsed": {},
            "explanation": "Not a UPI string"
        }

    params = parse_qs(urlparse(upi_string).query)
    parsed = {
        "pa": params.get("pa", [""])[0],
        "pn": params.get("pn", [""])[0],
        "am": params.get("am", [""])[0]
    }

    flags: list[str] = []
    risk_score = 0

    pa = parsed.get("pa", "")
    pn = parsed.get("pn", "")
    amount_text = parsed.get("am", "")

    # Check 1: VPA format validation
    if pa and not VPA_REGEX.match(pa):
        flags.append("INVALID_VPA_FORMAT")
        risk_score += 40

    # Check 2: Name vs VPA mismatch
    vpa_local = pa.split("@", maxsplit=1)[0].lower()
    pn_norm = pn.lower().replace(" ", "")
    if pn_norm and vpa_local:
        similarity = _similarity(pn_norm, vpa_local)
        if similarity < 30:
            flags.append("NAME_VPA_MISMATCH")
            risk_score += 35

    # Check 3: Threshold evasion amount
    try:
        amount_value = float(amount_text)
        if 45000 <= amount_value <= 49999:
            flags.append("THRESHOLD_EVASION_AMOUNT")
            risk_score += 20
    except ValueError:
        pass

    # Check 4: Known fraud VPA list
    fraud_vpas = _load_fraud_vpas()
    if pa and pa in fraud_vpas:
        flags.append("KNOWN_FRAUD_VPA")
        risk_score = 100

    # Check 5: Suspicious handle pattern
    if vpa_local and SUSPICIOUS_HANDLE_REGEX.match(vpa_local):
        flags.append("SUSPICIOUS_HANDLE")
        risk_score += 15

    recommendation = "SAFE"
    if risk_score >= 70:
        recommendation = "BLOCK"
    elif risk_score >= 40:
        recommendation = "WARN"

    explanation = "No risk indicators detected."
    if flags:
        explanation = "Risk flags detected for this UPI payment request."

    return {
        "risk_score": min(risk_score, 100),
        "flags": flags,
        "recommendation": recommendation,
        "parsed": parsed,
        "explanation": explanation
    }


if __name__ == "__main__":
    samples = [
        "upi://pay?pa=bigbazaar@icici&pn=Big Bazaar&am=200",
        "upi://pay?pa=randoms9291@ybl&pn=Amazon Pay&am=199",
        "upi://pay?pa=fraud@ybl&pn=HDFC Bank&am=49999"
    ]
    for sample in samples:
        print(analyze_upi_qr(sample))
