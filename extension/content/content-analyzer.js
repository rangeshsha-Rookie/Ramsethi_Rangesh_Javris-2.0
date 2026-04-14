/**
 * PhishGuard Content Analyzer
 * Extracts Stage 2 (HTML/JS) features for high-precision phishing detection.
 * Developed as part of the PhishGuard India Core Engine.
 */

function extractHTMLFeatures() {
    const features = {
        external_anchors_ratio: 0,
        suspicious_form: 0,
        right_click_disabled: 0,
        has_iframe: 0,
        timestamp: Date.now()
    };

    try {
        const anchors = document.querySelectorAll('a[href]');
        const currentDomain = window.location.hostname;
        let externalCount = 0;

        anchors.forEach(a => {
            try {
                const url = new URL(a.href);
                if (url.hostname !== currentDomain && !url.hostname.includes(currentDomain)) {
                    externalCount++;
                }
            } catch (e) {}
        });

        features.external_anchors_ratio = anchors.length > 0 ? (externalCount / anchors.length) : 0;

        // Check for suspicious forms (pointing to different domains)
        const forms = document.querySelectorAll('form[action]');
        forms.forEach(f => {
            try {
                const actionUrl = new URL(f.action, window.location.origin);
                if (actionUrl.hostname !== currentDomain) {
                    features.suspicious_form = 1;
                }
            } catch (e) {}
        });

        // Check for right-click disabled (obfuscation signal)
        // We check common attributes or if the contextmenu event is canceled
        features.right_click_disabled = (document.body.getAttribute('oncontextmenu') !== null) ? 1 : 0;

        // Check for iframes (can be used for overlays)
        features.has_iframe = document.querySelectorAll('iframe').length > 0 ? 1 : 0;

    } catch (err) {
        console.error("PhishGuard Analysis Error:", err);
    }

    return features;
}

// Send features to background script
function syncFeatures() {
    const htmlFeatures = extractHTMLFeatures();
    chrome.runtime.sendMessage({
        type: "HTML_FEATURES_UPDATE",
        features: htmlFeatures,
        url: window.location.href
    });
}

// Initial sync
setTimeout(syncFeatures, 2000);

// Watch for DOM changes (MutationObserver) to detect dynamic phishing injections
let analysisTimeout;
const observer = new MutationObserver(() => {
    clearTimeout(analysisTimeout);
    analysisTimeout = setTimeout(syncFeatures, 3000); // 3s debounce
});

observer.observe(document.body, { childList: true, subtree: true });
