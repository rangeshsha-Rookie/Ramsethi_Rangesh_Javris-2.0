// QR Scanner content script
// Injected into every page

console.log("PhishGuard: QR Scanner Active");

function processImages() {
    const images = Array.from(document.querySelectorAll('img')).filter(img => 
        img.naturalWidth > 50 && img. प्राकृतिकHeight > 50 && !img.dataset.phishguardScanned
    );

    images.forEach(img => {
        img.dataset.phishguardScanned = "true";
        try {
            const canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            
            // Requires jsQR loaded in content scripts via manifest
            if (typeof jsQR !== 'undefined') {
                const code = jsQR(imageData.data, imageData.width, imageData.height);
                if (code) {
                    handleQRResult(code.data);
                }
            }
        } catch (e) {
            // CORS issues mainly
        }
    });
}

function handleQRResult(data) {
    if (data.startsWith("upi://")) {
        // We have the parser natively loaded before this script via manifest
        if (typeof window.analyzeUPIString === 'function') {
            window.analyzeUPIString(data).then(result => {
                showToast(result);
            });
        }
    } else if (data.startsWith("http")) {
        chrome.runtime.sendMessage({type: "URL_SCAN_REQUEST", url: data}, response => {
            if (response && response.risk_score > 70) {
                showToast({ recommendation: "BLOCK", explanation: "Phishing URL detected in QR Code!" });
            }
        });
    }
}

function showToast(result) {
    const overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.bottom = "20px";
    overlay.style.right = "20px";
    overlay.style.padding = "16px";
    overlay.style.borderRadius = "8px";
    overlay.style.color = "white";
    overlay.style.zIndex = "999999";
    overlay.style.maxWidth = "350px";
    overlay.style.fontFamily = "sans-serif";
    overlay.style.boxShadow = "0 10px 25px rgba(0,0,0,0.3)";
    
    let html = `<strong>🛡️ PhishGuard Alert</strong><br/>`;
    
    if (result.recommendation === "BLOCK") {
        overlay.style.backgroundColor = "#ef4444";
        overlay.style.left = "0"; overlay.style.right = "0"; overlay.style.top = "0"; overlay.style.bottom = "0";
        overlay.style.maxWidth = "100%"; overlay.style.borderRadius = "0";
        overlay.style.display = "flex"; overlay.style.flexDirection = "column"; overlay.style.justifyContent = "center"; overlay.style.alignItems = "center";
        overlay.style.backgroundColor = "rgba(239, 68, 68, 0.95)";
        
        html = `<div style="text-align:center; max-width: 600px; padding: 40px; background: white; color: #1e293b; border-radius: 12px;">
                    <h1 style="color: #ef4444; font-size: 32px; margin-bottom: 10px;">⚠️ STOP! SCAM DETECTED</h1>
                    <p style="font-size: 18px;">${result.explanation}</p>
                    <div style="margin-top:20px; font-weight: bold; background: #fee2e2; padding: 10px; border-radius: 6px;">Flags: ${result.flags?.join(", ")}</div>
                    <button id="pg-close-btn" style="margin-top: 30px; background: #ef4444; color: white; border: none; padding: 12px 24px; font-weight: bold; border-radius: 6px; cursor:pointer;">I UNDERSTAND THE RISK. CONTINUE</button>
                </div>`;
    } else if (result.recommendation === "WARN") {
        overlay.style.backgroundColor = "#f59e0b";
        html += `<p style="margin-top:8px">${result.explanation}</p>`;
    } else {
        overlay.style.backgroundColor = "#22c55e";
        html += `<p style="margin-top:8px">UPI QR Code verified safe!</p>`;
        setTimeout(() => overlay.remove(), 4000);
    }
    
    overlay.innerHTML = html;
    document.body.appendChild(overlay);
    
    if (result.recommendation === "BLOCK") {
        document.getElementById("pg-close-btn").addEventListener("click", () => overlay.remove());
    }
}

// Active MutationObserver to catch dynamic QR codes (e.g. in modals/popups)
let scanTimeout;
const observer = new MutationObserver((mutations) => {
    clearTimeout(scanTimeout);
    scanTimeout = setTimeout(() => {
        // Only run scan if new images or canvases were added
        const hasNewImages = mutations.some(m => 
            Array.from(m.addedNodes).some(n => 
                n.nodeName === 'IMG' || n.nodeName === 'CANVAS' || (n.querySelectorAll && n.querySelectorAll('img, canvas').length > 0)
            )
        );
        if (hasNewImages) processImages();
    }, 1000); // 1s debounce to save CPU
});

observer.observe(document.body, { childList: true, subtree: true });

// Initial sweep
setTimeout(processImages, 1500);

// Add a floating manual scan button as requested by PRD
function injectFloatButton() {
    const btn = document.createElement("button");
    btn.innerHTML = "🛡️ PhishGuard Active";
    btn.title = "PhishGuard is protecting you. Click to re-scan.";
    btn.style.cssText = "position:fixed; bottom:20px; right:20px; z-index:99998; background:#1e293b; color:white; border:none; border-radius:30px; padding:10px 16px; font-weight:bold; cursor:pointer; box-shadow:0 4px 15px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); font-size: 12px;";
    
    btn.onclick = () => {
        processImages();
        const originalText = btn.innerHTML;
        btn.innerHTML = "Scanning... 🔍";
        setTimeout(() => btn.innerHTML = originalText, 1000);
    };
    
    document.body.appendChild(btn);
}

injectFloatButton();
