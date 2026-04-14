// Background Service Worker
importScripts('nvidia-explainer.js');
importScripts('blockchain-logger.js');

let fraudLog = [];
let scanStats = { totalScans: 0, fraudBlocked: 0, lastScan: null };
let currentTabFeatures = {};

// PRODUCTION WASM PATHS (Per PhishGuard Build Guide)
// ort.env.wasm.wasmPaths = {
//   'ort-wasm.wasm': chrome.runtime.getURL('models/ort-wasm.wasm'),
//   'ort-wasm-simd.wasm': chrome.runtime.getURL('models/ort-wasm-simd.wasm'),
// };

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "HTML_FEATURES_UPDATE") {
        currentTabFeatures[sender.tab.id] = message.features;
        // Trigger a re-analysis with new HTML depth
        checkURL(message.url, sender.tab.id).then(score => {
            updateBadge(score, sender.tab.id);
        });
        sendResponse({status: "FEATURES_SYNCED"});
    } else if (message.type === "EXPLAIN_THREAT") {
        explainThreat(message.context)
            .then(result => {
                sendResponse(result);
            })
            .catch(err => {
                console.error("AI Explanation Error:", err);
                sendResponse({ explanation: "AI explainer is currently unavailable. Using local fallback..." });
            });
        return true; // async
    } else if (message.type === "UPI_SCAN_REQUEST") {
        scanStats.totalScans++;
        sendResponse({ status: "ACK" });
    } else if (message.type === "URL_SCAN_REQUEST") {
        scanStats.totalScans++;
        checkURL(message.url, sender.tab?.id).then(score => {
            updateBadge(score, sender.tab?.id);
            if (score > 70) {
                scanStats.fraudBlocked++;
                chrome.notifications.create({
                    type: "basic",
                    iconUrl: chrome.runtime.getURL("icons/icon128.png"),
                    title: "🚨 PhishGuard Alert",
                    message: "High-risk phishing threat detected!"
                });
            }
            sendResponse({ risk_score: score });
        });
        return true; 
    } else if (message.type === "REPORT_FRAUD") {
        // Live Sync: Global Community Reporting
        const VERCEL_URL = "https://ramsethi-rangesh-javris-2-0.vercel.app";
        fetch(VERCEL_URL + "/api/report-fraud", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: message.type_target || "UPI_FRAUD",
                target: message.vpa || message.url,
                evidence: message.evidence || "User Reported",
                flags: ["COMMUNITY_REPORT"]
            })
        }).catch(err => console.error("Central Reporting Error:", err));

        fraudLog.unshift({
            vpa: message.vpa,
            url: message.url,
            evidence: message.evidence,
            time: Date.now()
        });
        sendResponse({ status: "REPORT_LOGGED" });
    } else if (message.type === "GET_STATS") {
        sendResponse({ stats: scanStats, log: fraudLog });
    }
});

// Update URL as user browses
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        if (!tab.url.startsWith("http")) return;
        
        scanStats.totalScans++;
        checkURL(tab.url, tabId).then(score => {
            updateBadge(score, tabId);
        });
    }
});

function updateBadge(score, tabId) {
    let color = "#22c55e"; // Safe
    let text = "✓";
    
    if (score > 70) {
        color = "#ef4444"; // Danger
        text = "✗";
    } else if (score > 40) {
        color = "#f59e0b"; // Warn
        text = "!";
    }
    
    chrome.action.setBadgeBackgroundColor({ color: color, tabId: tabId });
    chrome.action.setBadgeText({ text: text, tabId: tabId });
}

// Proprietary 17-Feature Risk Engine
async function checkURL(url, tabId) {
    let risk_score = 10;
    
    try {
        let parsed = new URL(url);
        
        // --- CATEGORY A: Address Bar (Lexical) ---
        if (parsed.protocol !== "https:") risk_score += 30;
        let depth = parsed.hostname.split(".").length;
        if (depth > 3) risk_score += 20;
        if (url.length > 75) risk_score += 15;
        if (parsed.hostname.includes("@")) risk_score += 50;
        if (parsed.hostname.includes("-")) risk_score += 10; // Prefix/Suffix feature
        
        // Double Slash Redirect
        if (url.lastIndexOf("//") > 7) risk_score += 20;

        let shortened = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "rebrand.ly"];
        if (shortened.includes(parsed.hostname)) risk_score += 40;
        
        let ipRegex = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
        if (ipRegex.test(parsed.hostname)) risk_score += 50;
        
        // --- CATEGORY B: HTML/JS Behavioral (Synced from Content Script) ---
        if (tabId && currentTabFeatures[tabId]) {
            const html = currentTabFeatures[tabId];
            if (html.external_anchors_ratio > 0.6) risk_score += 25;
            if (html.suspicious_form === 1) risk_score += 40;
            if (html.right_click_disabled === 1) risk_score += 15;
            if (html.has_iframe === 1) risk_score += 15;
        }
        
        // --- CATEGORY C: Domain/Trust (Simulated API Check) ---
        // In a real prod environment, we would fetch(API_URL + '/check-domain')
        // For the portfolio, we bake in the heuristic logic.
        const suspiciousTLDs = [".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".xyz"];
        if (suspiciousTLDs.some(tld => parsed.hostname.endsWith(tld))) risk_score += 30;

    } catch(e) {}
    
    return Math.min(100, risk_score);
}
