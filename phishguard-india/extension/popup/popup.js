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
        explanation.textContent = result.explanation;

        // Add main recommendation badge
        let recBadge = document.createElement('span');
        recBadge.className = 'badge';
        if(result.recommendation === "BLOCK") recBadge.classList.add('bg-danger');
        else if(result.recommendation === "WARN") recBadge.classList.add('bg-warn');
        else recBadge.classList.add('bg-safe');
        recBadge.textContent = result.recommendation + ` (Score: ${result.risk_score})`;
        badgesContainer.appendChild(recBadge);

        // Add other flags
        result.flags.forEach(flag => {
            let badge = document.createElement('span');
            badge.className = 'badge bg-danger'; // Usually flags represent danger
            badge.textContent = flag;
            badgesContainer.appendChild(badge);
        });
    });
});
