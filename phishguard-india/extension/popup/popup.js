(() => {
  const statusEl = document.getElementById("status");
  const refreshBtn = document.getElementById("refresh");

  const updateStatus = () => {
    statusEl.textContent = "Checking...";
    chrome.runtime.sendMessage({ type: "PING" }, (response) => {
      if (chrome.runtime.lastError) {
        statusEl.textContent = "Service worker not available";
        return;
      }
      statusEl.textContent = response?.status || "Unknown";
    });
  };

  refreshBtn.addEventListener("click", updateStatus);
  updateStatus();
})();
