// Simple Levenshtein distance for fuzzy matching
function levenshteinDistance(s1, s2) {
    if (s1.length === 0) return s2.length;
    if (s2.length === 0) return s1.length;
    const matrix = Array(s2.length + 1).fill(null).map(() => Array(s1.length + 1).fill(null));
    for (let i = 0; i <= s1.length; i++) matrix[0][i] = i;
    for (let j = 0; j <= s2.length; j++) matrix[j][0] = j;

    for (let j = 1; j <= s2.length; j++) {
        for (let i = 1; i <= s1.length; i++) {
            const indicator = s1[i - 1] === s2[j - 1] ? 0 : 1;
            matrix[j][i] = Math.min(
                matrix[j][i - 1] + 1,
                matrix[j - 1][i] + 1,
                matrix[j - 1][i - 1] + indicator
            );
        }
    }
    return matrix[s2.length][s1.length];
}

function getSimilarity(s1, s2) {
    let distance = levenshteinDistance(s1, s2);
    let maxLen = Math.max(s1.length, s2.length);
    if (maxLen === 0) return 100;
    return (1 - distance / maxLen) * 100;
}

// Global cached instance
let cachedFraudVPAs = null;

async function loadFraudVPAs() {
    if (cachedFraudVPAs !== null) return cachedFraudVPAs;
    try {
        let url = chrome.runtime.getURL('data/fraud_vpas.json');
        let response = await fetch(url);
        cachedFraudVPAs = await response.json();
    } catch (e) {
        console.error("Failed to load fraud VPAs map, check if running in extension context.");
        cachedFraudVPAs = []; // Safe fallback
    }
    return cachedFraudVPAs;
}

async function analyzeUPIString(upiString) {
    let result = {
        risk_score: 0,
        flags: [],
        recommendation: "SAFE",
        parsed: { pa: "", pn: "", am: "", cu: "" },
        explanation: ""
    };

    if (!upiString.startsWith("upi://pay")) {
        result.flags.push("INVALID_URI");
        result.recommendation = "BLOCK";
        result.explanation = "This is not a valid UPI payment string.";
        return result;
    }

    try {
        // Strip out base to use standard URL API parsing safely
        let queryString = upiString.replace("upi://pay", "http://localhost");
        let parsedUrl = new URL(queryString);
        
        let pa = (parsedUrl.searchParams.get("pa") || "").toLowerCase();
        let pn = parsedUrl.searchParams.get("pn") || "";
        let am = parsedUrl.searchParams.get("am") || "0";
        let cu = parsedUrl.searchParams.get("cu") || "INR";

        result.parsed = { pa, pn, am, cu };

        // CHECK 1: VPA Format Validation
        const vpaRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z]+$/;
        if (pa && !vpaRegex.test(pa)) {
            result.risk_score += 40;
            result.flags.push("INVALID_VPA_FORMAT");
        }

        // CHECK 2: Name vs VPA Mismatch
        if (pn && pa) {
            let handlePrefix = pa.split("@")[0];
            let cleanPn = pn.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
            let cleanHandle = handlePrefix.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
            
            // Substring or fuzzy. If handle is substring of name or name substring of handle, similarity is high.
            if (!cleanPn.includes(cleanHandle) && !cleanHandle.includes(cleanPn)) {
                let similarity = getSimilarity(cleanPn, cleanHandle);
                if (similarity < 30) {
                    result.risk_score += 35;
                    result.flags.push("NAME_VPA_MISMATCH");
                }
            }
        }

        // CHECK 3: Threshold Evasion Amount
        let amount = parseFloat(am);
        if (!isNaN(amount) && amount >= 45000 && amount <= 49999) {
            result.risk_score += 20;
            result.flags.push("THRESHOLD_EVASION_AMOUNT");
        }

        // CHECK 4: Known Fraud VPA Check
        let frauds = await loadFraudVPAs();
        if (frauds.some(f => f.vpa === pa)) {
            result.risk_score = 100;
            result.flags.push("KNOWN_FRAUD_VPA");
        }

        // CHECK 5: Suspicious TLD on VPA handle
        if (pa) {
            let prefix = pa.split("@")[0];
            let digits = prefix.replace(/[^0-9]/g, "").length;
            if (prefix.length > 0 && (digits / prefix.length) > 0.4) {
                result.risk_score += 15;
                result.flags.push("HIGH_DIGIT_RATIO");
            }
        }

        // Evaluation
        if (result.risk_score >= 60) {
            result.recommendation = "BLOCK";
            result.explanation = "Warning: This QR code exhibits strong indicators of fraud. Do not proceed with this payment.";
        } else if (result.risk_score >= 35) {
            result.recommendation = "WARN";
            result.explanation = "Caution: The merchant name does not match the UPI handle cleanly. Proceed with extreme caution.";
        } else {
            result.recommendation = "SAFE";
            result.explanation = "This appears to be a legitimate UPI payment link.";
        }

        result.risk_score = Math.min(100, result.risk_score);
    } catch (err) {
        console.error("UPI parse error", err);
        result.flags.push("PARSE_ERROR");
        result.recommendation = "WARN";
    }

    return result;
}

// Export for module systems or just attach to window for content script inclusion
if (typeof module !== "undefined" && module.exports) {
    module.exports = { analyzeUPIString, getSimilarity };
} else {
    window.analyzeUPIString = analyzeUPIString;
}

// Simple test wrapper (browser-safe testing check)
async function runTests() {
    if (typeof process !== "undefined" && process.title !== 'browser') {
        const safe_case = "upi://pay?pa=bigbazaar@icici&pn=Big Bazaar&am=200&cu=INR";
        const warn_case = "upi://pay?pa=randoms9291@ybl&pn=Amazon Pay&am=199&cu=INR";
        const block_case = "upi://pay?pa=fraud@ybl&pn=HDFC Bank&am=49999&cu=INR";
        
        let r1 = await analyzeUPIString(safe_case);
        let r2 = await analyzeUPIString(warn_case);
        let r3 = await analyzeUPIString(block_case);
        
        console.log("SAFE:", r1.recommendation);
        console.log("WARN:", r2.recommendation);
        console.log("BLOCK:", r3.recommendation);
    }
}
runTests();
