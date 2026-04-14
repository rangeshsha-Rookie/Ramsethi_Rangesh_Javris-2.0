// Background Service Worker
importScripts('nvidia-explainer.js');
importScripts('blockchain-logger.js');

let fraudLog = [];
let scanStats = { totalScans: 0, fraudBlocked: 0, lastScan: null };

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "EXPLAIN_THREAT") {
        explainThreat(message.context)
            .then(explanation => {
                sendResponse({ explanation: explanation });
            })
            .catch(err => {
                console.error("AI Explanation Error:", err);
                sendResponse({ explanation: "AI explainer is currently unavailable. Using local fallback..." });
            });
        return true; // async
    } else if (message.type === "UPI_SCAN_REQUEST") {
        // Will be handled by popup calling analyzeUPIString normally,
        // but if content script sends it, we can log it.
        scanStats.totalScans++;
        sendResponse({ status: "ACK" });
    } else if (message.type === "URL_SCAN_REQUEST") {
        scanStats.totalScans++;
        checkURL(message.url).then(score => {
            updateBadge(score, sender.tab?.id);
            if (score > 70) {
                scanStats.fraudBlocked++;
                chrome.notifications.create({
                    type: "basic",
                    iconUrl: chrome.runtime.getURL("icons/icon128.png"),
                    title: "🚨 PhishGuard Alert",
                    message: "Phishing threat detected on scanned URL!"
                });
            }
            sendResponse({ risk_score: score });
        });
        return true; // Keep channel open for async
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
        checkURL(tab.url).then(score => {
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

// Fast heuristic fallback since in-browser DNS feature extraction is restricted
async function checkURL(url) {
    let risk_score = 10;
    
    try {
        let parsed = new URL(url);
        if (parsed.protocol !== "https:") risk_score += 30;
        
        let depth = parsed.hostname.split(".").length;
        if (depth > 3) risk_score += 20;
        
        if (url.length > 75) risk_score += 15;
        if (parsed.hostname.includes("@")) risk_score += 50;
        
        let shortened = ["bit.ly", "tinyurl.com", "goo.gl", "t.co"];
        if (shortened.includes(parsed.hostname)) risk_score += 40;
        
        let ipRegex = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
        if (ipRegex.test(parsed.hostname)) risk_score += 50;
        
    } catch(e) {}
    
    return Math.min(100, risk_score);
}
