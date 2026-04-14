import re
from urllib.parse import urlparse, parse_qs
from fuzzywuzzy import fuzz
import json
import os

def analyze_upi_qr(upi_string):
    # Base response
    result = {
        "risk_score": 0,
        "flags": [],
        "recommendation": "SAFE",
        "parsed": {"pa": "", "pn": "", "am": "", "cu": ""},
        "explanation": ""
    }
    
    # 0. Basic URI parsing
    if not upi_string.startswith("upi://pay"):
        result["flags"].append("INVALID_URI")
        result["recommendation"] = "BLOCK"
        result["explanation"] = "This is not a valid UPI payment string."
        return result
        
    parsed = urlparse(upi_string)
    query_params = parse_qs(parsed.query)
    
    # Extract
    pa = query_params.get("pa", [""])[0].lower()
    pn = query_params.get("pn", [""])[0]
    am = query_params.get("am", ["0"])[0]
    cu = query_params.get("cu", ["INR"])[0]
    
    result["parsed"] = {"pa": pa, "pn": pn, "am": am, "cu": cu}
    
    # CHECK 1: VPA Format Validation (40 points if fails)
    if not re.match(r"^[a-zA-Z0-9._-]+@[a-zA-Z]+$", pa):
        result["risk_score"] += 40
        result["flags"].append("INVALID_VPA_FORMAT")
        
    # CHECK 2: Name vs VPA Mismatch (35 points if fails)
    if pn and pa:
        handle_prefix = pa.split("@")[0]
        # remove spaces and lower case display name
        clean_pn = re.sub(r'[^a-zA-Z0-9]', '', pn).lower()
        clean_handle = re.sub(r'[^a-zA-Z0-9]', '', handle_prefix).lower()
        
        sim = fuzz.partial_ratio(clean_pn, clean_handle)
        if sim < 30:
            result["risk_score"] += 35
            result["flags"].append("NAME_VPA_MISMATCH")
            
    # CHECK 3: Threshold Evasion Amount (20 points if matches)
    try:
        amount = float(am)
        if 45000 <= amount <= 49999:
            result["risk_score"] += 20
            result["flags"].append("THRESHOLD_EVASION_AMOUNT")
    except:
        pass
        
    # CHECK 4: Known Fraud VPA Check (100 points, instant block)
    try:
        fraud_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "phishguard-india", "extension", "data", "fraud_vpas.json")
        if os.path.exists(fraud_path):
            with open(fraud_path, 'r') as f:
                fraud_data = json.load(f)
                for item in fraud_data:
                    if item.get("vpa", "").lower() == pa:
                        result["risk_score"] = 100
                        result["flags"].append("KNOWN_FRAUD_VPA")
                        break
    except:
        pass
        
    # CHECK 5: Suspicious TLD on VPA handle (15 points if high digit ratio)
    if pa:
        handle_prefix = pa.split("@")[0]
        digits = sum(c.isdigit() for c in handle_prefix)
        if len(handle_prefix) > 0 and (digits / len(handle_prefix)) > 0.4:
            result["risk_score"] += 15
            result["flags"].append("HIGH_DIGIT_RATIO")

    # Recommendation
    if result["risk_score"] >= 60:
        result["recommendation"] = "BLOCK"
        result["explanation"] = "Warning: This QR code exhibits strong indicators of fraud. Do not proceed with this payment."
    elif result["risk_score"] >= 35:
        result["recommendation"] = "WARN"
        result["explanation"] = "Caution: The merchant name does not match the UPI handle cleanly. Proceed with extreme caution."
    else:
        result["recommendation"] = "SAFE"
        result["explanation"] = "This appears to be a legitimate UPI payment link."
        
    # Cap
    result["risk_score"] = min(100, result["risk_score"])
    
    return result

if __name__ == "__main__":
    print("--- Test Cases ---")
    safe_case = "upi://pay?pa=bigbazaar@icici&pn=Big Bazaar&am=200&cu=INR"
    warn_case = "upi://pay?pa=randoms9291@ybl&pn=Amazon Pay&am=199&cu=INR"
    block_case = "upi://pay?pa=fraud@ybl&pn=HDFC Bank&am=49999&cu=INR"
    
    print("SAFE:", analyze_upi_qr(safe_case)["recommendation"])
    print("WARN:", analyze_upi_qr(warn_case)["recommendation"])
    print("BLOCK:", analyze_upi_qr(block_case)["recommendation"])
