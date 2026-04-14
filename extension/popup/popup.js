document.addEventListener('DOMContentLoaded', () => {
    // Tab Switching Logic
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            document.getElementById(tab.dataset.target).classList.add('active');
        });
    });

    // Load active tab info 
    chrome.tabs.query({active: true, currentWindow: true}, (tabsArray) => {
        const activeTab = tabsArray[0];
        if (activeTab && activeTab.url) {
            document.getElementById('current-url').textContent = activeTab.url;
            
            // Ask Service Worker for current score
            chrome.runtime.sendMessage({type: "URL_SCAN_REQUEST", url: activeTab.url}, (res) => {
                const circle = document.getElementById('score-circle');
                const val = document.getElementById('score-val');
                const rec = document.getElementById('recommendation');
                
                if (res && res.risk_score !== undefined) {
                    val.textContent = res.risk_score;
                    circle.className = "score-circle"; // reset
                    
                    if (res.risk_score > 70) {
                        circle.classList.add("danger");
                        rec.textContent = "PHISHING DETECTED";
                        rec.style.color = "var(--danger)";
                    } else if (res.risk_score > 40) {
                        circle.classList.add("warn");
                        rec.textContent = "SUSPICIOUS";
                        rec.style.color = "var(--warn)";
                    } else {
                        circle.classList.add("safe");
                        rec.textContent = "SAFE";
                        rec.style.color = "var(--safe)";
                    }
                }
            });
        }
    });

    // Stats
    chrome.runtime.sendMessage({type: "GET_STATS"}, (res) => {
        if (res && res.stats) {
            document.getElementById('stat-scans').textContent = res.stats.totalScans;
            document.getElementById('stat-blocks').textContent = res.stats.fraudBlocked;
        }
    });

    // UPI Analysis
    document.getElementById('btn-analyze').addEventListener('click', async () => {
        const input = document.getElementById('upi-input').value.trim();
        if(!input) return;

        // Requires upi-parser.js to be loaded in the html
        if(typeof window.analyzeUPIString === 'undefined') {
            alert("UPI Analyzer library not loaded properly.");
            return;
        }

        const result = await window.analyzeUPIString(input);
        
        const resDiv = document.getElementById('upi-result');
        const badgesContainer = document.getElementById('upi-badges');
        const explanation = document.getElementById('upi-explanation');
        
        resDiv.classList.remove('hidden');
        badgesContainer.innerHTML = '';
        explanation.textContent = "Generating AI explanation... ✨";

        // Request AI explanation from background
        chrome.runtime.sendMessage({
            type: "EXPLAIN_THREAT",
            context: {
                type: result.flags[0] || "GENERAL",
                vpa: result.parsed.pa,
                flags: result.flags,
                language: "hinglish"
            }
        }, (aiRes) => {
            const expEl = document.getElementById('upi-explanation');
            if (aiRes && aiRes.explanation) {
                // Add a source badge
                const sourceText = aiRes.source === "nvidia" ? "✨ NVIDIA AI Powered" : "🛡️ Local Smart Engine";
                const sourceClass = aiRes.source === "nvidia" ? "bg-primary" : "bg-safe";
                
                expEl.innerHTML = `<div class="badge ${sourceClass} text-xs mb-5" style="font-size: 10px; opacity: 0.8;">${sourceText}</div><br/>${aiRes.explanation}`;
            } else {
                expEl.textContent = result.explanation; // Fallback
            }
        });

        // Add main recommendation badge
        let recBadge = document.createElement('span');
        recBadge.className = 'badge';
        if(result.recommendation === "BLOCK") recBadge.classList.add('bg-danger');
        else if(result.recommendation === "WARN") recBadge.classList.add('bg-warn');
        else recBadge.classList.add('bg-safe');
        recBadge.textContent = result.recommendation + ` (Score: ${result.risk_score})`;
        badgesContainer.appendChild(recBadge);

        // Add other flags
        // Handle WhatsApp Sharing
        document.getElementById('btn-share-whatsapp').onclick = () => {
            const vpa = result.parsed.pa || "Unknown";
            const text = `🚨 *PhishGuard India Alert* 🚨\n\nI just detected a suspicious UPI payment to *${vpa}*.\n\nPhishGuard flagged this as a threat. Please stay safe and don't pay unknown handles!\n\nCheck for yourself: https://ramsethi-rangesh-javris-2-0.vercel.app`;
            window.open(`https://wa.me/?text=${encodeURIComponent(text)}`);
        };

        // Handle Blockchain Link (Dynamic)
        const blockchainLink = document.getElementById('link-blockchain');
        blockchainLink.href = `https://amoy.polygonscan.com/address/0xF777B6D8a0B6e000000000000000000000000000`; // Link to the registry
    });

    // Settings logic: Load key
    const apiKeyInput = document.getElementById('nvidia-api-key');
    const saveBtn = document.getElementById('btn-save-settings');
    const statusMsg = document.getElementById('settings-status');

    chrome.storage.local.get(['nvidia_api_key'], (result) => {
        if (result.nvidia_api_key) {
            apiKeyInput.value = result.nvidia_api_key;
        }
    });

    // Save key
    saveBtn.addEventListener('click', () => {
        const key = apiKeyInput.value.trim();
        chrome.storage.local.set({ 'nvidia_api_key': key }, () => {
            statusMsg.textContent = "Key saved successfully!";
            statusMsg.classList.remove('hidden');
            setTimeout(() => statusMsg.classList.add('hidden'), 3000);
        });
    });
});
