/* eslint-disable no-console */
/* global importScripts, ort */

importScripts("../lib/ort.min.js");

(() => {
  console.log("PhishGuard India: Service worker initialized");

  const SETTINGS = {
    SCORE_THRESHOLD_FRAUD: 70,
    SCORE_THRESHOLD_WARN: 40,
    API_URL: "https://phishguard.vercel.app/api"
  };

  /**
   * Helper to update extension badge
   */
  const updateBadge = (score) => {
    let color = "#22c55e"; // Green (Safe)
    let text = "✓";

    if (score >= SETTINGS.SCORE_THRESHOLD_FRAUD) {
      color = "#ef4444"; // Red (Fraud)
      text = "✗";
    } else if (score >= SETTINGS.SCORE_THRESHOLD_WARN) {
      color = "#f59e0b"; // Yellow (Warn)
      text = "!";
    }

    chrome.action.setBadgeBackgroundColor({ color });
    chrome.action.setBadgeText({ text });
  };

  /**
   * Extract features from URL (Base for ONNX Model)
   */
  const extractUrlFeatures = (urlStr) => {
    try {
      const url = new URL(urlStr);
      return {
        url_length: urlStr.length,
        has_https: url.protocol === "https:" ? 1 : 0,
        subdomain_depth: url.hostname.split(".").length - 2,
        has_at_symbol: urlStr.includes("@") ? 1 : 0,
        is_shortened: ["bit.ly", "tinyurl.com", "t.co", "goo.gl"].includes(url.hostname) ? 1 : 0,
        has_ip: /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(url.hostname) ? 1 : 0
      };
    } catch (e) {
      return null;
    }
  };

  /**
   * Heuristic URL Risk Scorer (Stub for ONNX)
   */
  const scoreUrlRisk = (features) => {
    if (!features) return 0;
    let score = 0;
    if (features.has_https === 0) score += 30;
    if (features.has_ip === 1) score += 50;
    if (features.has_at_symbol === 1) score += 40;
    if (features.is_shortened === 1) score += 30;
    if (features.subdomain_depth > 3) score += 20;
    if (features.url_length > 100) score += 10;
    return Math.min(score, 100);
  };

  /**
   * Save scan to history
   */
  const saveToHistory = async (item) => {
    const { scan_history = [] } = await chrome.storage.local.get("scan_history");
    const newItem = {
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      ...item
    };
    scan_history.unshift(newItem);
    await chrome.storage.local.set({ scan_history: scan_history.slice(0, 50) }); // Keep last 50
    return newItem;
  };

  /**
   * Notification Dispatcher
   */
  const showNotification = (title, message, priority = 0) => {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "../icons/icon128.png",
      title: `🛡️ PhishGuard: ${title}`,
      message: message,
      priority: priority
    });
  };

  /**
   * Message Handler
   */
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    (async () => {
      try {
        if (message.type === "PING") {
          sendResponse({ ok: true, status: "ready" });
        }

        else if (message.type === "URL_SCAN_REQUEST") {
          const features = extractUrlFeatures(message.url);
          const risk_score = scoreUrlRisk(features);
          const verdict = risk_score >= SETTINGS.SCORE_THRESHOLD_FRAUD ? "FRAUD" : (risk_score >= SETTINGS.SCORE_THRESHOLD_WARN ? "WARN" : "SAFE");
          
          const historyItem = await saveToHistory({
            type: "url",
            input: message.url,
            risk_score,
            verdict,
            flags: [] // To be filled by detailed logic
          });

          if (verdict === "FRAUD") {
            showNotification("Phishing Detected", `Suspicious URL blocked: ${message.url}`, 2);
          }

          updateBadge(risk_score);
          sendResponse({ ok: true, result: historyItem });
        }

        else if (message.type === "UPI_SCAN_RESULT") {
          const { result } = message;
          const historyItem = await saveToHistory({
            type: "upi",
            input: result.parsed.pa || "Unknown VPA",
            risk_score: result.risk_score,
            verdict: result.recommendation,
            flags: result.flags,
            explanation: result.explanation
          });

          if (result.recommendation === "BLOCK") {
            showNotification("UPI Fraud Detected", `Warning: High risk UPI identifier: ${result.parsed.pa}`, 2);
          }

          sendResponse({ ok: true, result: historyItem });
        }

        else if (message.type === "GET_STATS") {
          const { scan_history = [] } = await chrome.storage.local.get("scan_history");
          const frauds = scan_history.filter(i => i.verdict === "FRAUD" || i.verdict === "BLOCK").length;
          sendResponse({ ok: true, stats: { scans: scan_history.length, frauds } });
        }

        else if (message.type === "GET_HISTORY") {
          const { scan_history = [] } = await chrome.storage.local.get("scan_history");
          sendResponse({ ok: true, history: scan_history });
        }

        else if (message.type === "CLEAR_HISTORY") {
          await chrome.storage.local.set({ scan_history: [] });
          sendResponse({ ok: true });
        }

        else {
          sendResponse({ ok: false, error: "Unknown message type" });
        }
      } catch (err) {
        console.error("Service worker message error", err);
        sendResponse({ ok: false, error: err.message });
      }
    })();
    return true; // Keep channel open for async response
  });

  /**
   * Monitor Tab Updates
   */
  chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url) {
      const features = extractUrlFeatures(changeInfo.url);
      const risk_score = scoreUrlRisk(features);
      updateBadge(risk_score);
    }
  });

})();

