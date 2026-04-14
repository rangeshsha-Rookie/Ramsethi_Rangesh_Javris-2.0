(() => {
  const VPA_REGEX = /^[a-zA-Z0-9._-]+@[a-zA-Z]+$/;
  const SUSPICIOUS_HANDLE_REGEX = /^(?=.*\d)[a-zA-Z0-9._-]{6,}$/;
  let fraudVpaCache = null;

  const similarity = (a, b) => {
    if (!a || !b) {
      return 0;
    }

    const dp = Array.from({ length: a.length + 1 }, () => []);
    for (let i = 0; i <= a.length; i += 1) {
      dp[i][0] = i;
    }
    for (let j = 0; j <= b.length; j += 1) {
      dp[0][j] = j;
    }

    for (let i = 1; i <= a.length; i += 1) {
      for (let j = 1; j <= b.length; j += 1) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        dp[i][j] = Math.min(
          dp[i - 1][j] + 1,
          dp[i][j - 1] + 1,
          dp[i - 1][j - 1] + cost
        );
      }
    }

    const distance = dp[a.length][b.length];
    const maxLen = Math.max(a.length, b.length) || 1;
    return ((maxLen - distance) / maxLen) * 100;
  };

  const loadFraudVpas = async () => {
    if (fraudVpaCache) {
      return fraudVpaCache;
    }

    try {
      const url = chrome.runtime.getURL("data/fraud_vpas.json");
      const response = await fetch(url);
      const data = await response.json();
      fraudVpaCache = new Set(data.map((value) => String(value).trim()).filter(Boolean));
    } catch (error) {
      console.warn("Failed to load fraud VPAs", error);
      fraudVpaCache = new Set();
    }

    return fraudVpaCache;
  };

  const analyzeUPIString = async (upiString) => {
    if (!upiString || !upiString.startsWith("upi://")) {
      return {
        risk_score: 0,
        flags: [],
        recommendation: "SAFE",
        parsed: {},
        explanation: "Not a UPI string"
      };
    }

    const url = new URL(upiString);
    const params = url.searchParams;
    const parsed = {
      pa: params.get("pa") || "",
      pn: params.get("pn") || "",
      am: params.get("am") || ""
    };

    const flags = [];
    let riskScore = 0;

    const pa = parsed.pa;
    const pn = parsed.pn;
    const amountText = parsed.am;

    // Check 1: VPA format validation
    if (pa && !VPA_REGEX.test(pa)) {
      flags.push("INVALID_VPA_FORMAT");
      riskScore += 40;
    }

    // Check 2: Name vs VPA mismatch
    const vpaLocal = pa.split("@", 1)[0].toLowerCase();
    const pnNorm = pn.toLowerCase().replace(/\s+/g, "");
    if (vpaLocal && pnNorm) {
      const matchScore = similarity(pnNorm, vpaLocal);
      if (matchScore < 30) {
        flags.push("NAME_VPA_MISMATCH");
        riskScore += 35;
      }
    }

    // Check 3: Threshold evasion amount
    const amountValue = Number(amountText);
    if (Number.isFinite(amountValue) && amountValue >= 45000 && amountValue <= 49999) {
      flags.push("THRESHOLD_EVASION_AMOUNT");
      riskScore += 20;
    }

    // Check 4: Known fraud VPA list
    const fraudVpas = await loadFraudVpas();
    if (pa && fraudVpas.has(pa)) {
      flags.push("KNOWN_FRAUD_VPA");
      riskScore = 100;
    }

    // Check 5: Suspicious handle pattern
    if (vpaLocal && SUSPICIOUS_HANDLE_REGEX.test(vpaLocal)) {
      flags.push("SUSPICIOUS_HANDLE");
      riskScore += 15;
    }

    let recommendation = "SAFE";
    if (riskScore >= 70) {
      recommendation = "BLOCK";
    } else if (riskScore >= 40) {
      recommendation = "WARN";
    }

    const explanation = flags.length
      ? "Risk flags detected for this UPI payment request."
      : "No risk indicators detected.";

    return {
      risk_score: Math.min(riskScore, 100),
      flags,
      recommendation,
      parsed,
      explanation
    };
  };

  const runSamples = async () => {
    const samples = [
      "upi://pay?pa=bigbazaar@icici&pn=Big Bazaar&am=200",
      "upi://pay?pa=randoms9291@ybl&pn=Amazon Pay&am=199",
      "upi://pay?pa=fraud@ybl&pn=HDFC Bank&am=49999"
    ];

    for (const sample of samples) {
      const result = await analyzeUPIString(sample);
      console.log("UPI sample", sample, result);
    }
  };

  window.PhishGuard = window.PhishGuard || {};
  window.PhishGuard.analyzeUPIString = analyzeUPIString;
  window.PhishGuard.runUPISamples = runSamples;
})();
