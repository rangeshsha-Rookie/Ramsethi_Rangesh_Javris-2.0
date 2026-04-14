/* eslint-disable no-console */
/* global jsQR */

(() => {
  const SCAN_INTERVAL = 3000; // Scan images every 3 seconds
  const scannedImages = new Set();

  /**
   * Scans a single image for QR codes
   */
  const scanImage = (img) => {
    if (!img.complete || img.naturalWidth < 50 || img.naturalHeight < 50) return;
    if (scannedImages.has(img.src)) return;

    try {
      const canvas = document.createElement("canvas");
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0);

      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);

      if (code) {
        console.log("PhishGuard: QR detected in image", code.data);
        handleDetectedQR(code.data);
        scannedImages.add(img.src); // Only alert once per image URL
      }
    } catch (err) {
      // Cross-origin images will throw security error here
      // We log silently as many images will be cross-origin
    }
  };

  /**
   * Handles decoded QR data
   */
  const handleDetectedQR = async (data) => {
    if (data.startsWith("upi://")) {
      if (window.PhishGuard && window.PhishGuard.analyzeUPIString) {
        const result = await window.PhishGuard.analyzeUPIString(data);
        chrome.runtime.sendMessage({ type: "UPI_SCAN_RESULT", result });
      }
    } else if (data.startsWith("http")) {
      chrome.runtime.sendMessage({ type: "URL_SCAN_REQUEST", url: data });
    }
  };

  const scannedImages = new Set();

  /**
   * Scans all images on the page
   */
  const scanAllImages = () => {
    const images = document.querySelectorAll("img");
    images.forEach(img => {
      // Use src as key, but also check if it's already scanned
      if (img.src && !scannedImages.has(img.src)) {
        scanImage(img).then(result => {
          if (result) {
            handleScanResult(result);
          }
          scannedImages.add(img.src);
        }).catch(() => {
          // Silent fail for individual image scans
        });
      }
    });
  };

  /**
   * Injects the floating scan button
   */
  const injectFloatingButton = () => {
    if (document.getElementById("phishguard-scan-btn")) return;

    const btn = document.createElement("div");
    btn.id = "phishguard-scan-btn";
    btn.innerHTML = "🛡️";
    btn.title = "PhishGuard India: Manual QR Scan";
    btn.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 50px;
      height: 50px;
      background: #1e293b;
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      cursor: pointer;
      z-index: 999999;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      transition: transform 0.2s;
    `;

    btn.onmouseover = () => { btn.style.transform = "scale(1.1)"; };
    btn.onmouseout = () => { btn.style.transform = "scale(1.0)"; };
    btn.onclick = toggleCameraOverlay;

    document.body.appendChild(btn);
  };

  /**
   * Toggles the live camera scan overlay
   */
  let overlay = null;
  let videoStream = null;

  const toggleCameraOverlay = async () => {
    if (overlay) {
      closeOverlay();
      return;
    }

    try {
      videoStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      
      overlay = document.createElement("div");
      overlay.style.cssText = `
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8);
        z-index: 1000000;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
        font-family: sans-serif;
      `;

      const video = document.createElement("video");
      video.srcObject = videoStream;
      video.setAttribute("playsinline", true);
      video.style.width = "80%";
      video.style.maxWidth = "400px";
      video.style.borderRadius = "10px";
      video.play();

      const closeBtn = document.createElement("button");
      closeBtn.innerText = "Close";
      closeBtn.style.cssText = "margin-top: 20px; padding: 10px 20px; cursor: pointer;";
      closeBtn.onclick = closeOverlay;

      const info = document.createElement("div");
      info.innerText = "Align QR code within the camera view";
      info.style.marginBottom = "10px";

      overlay.appendChild(info);
      overlay.appendChild(video);
      overlay.appendChild(closeBtn);
      document.body.appendChild(overlay);

      // Start scan loop
      const scanLoop = () => {
        if (!overlay) return;
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
          const canvas = document.createElement("canvas");
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const ctx = canvas.getContext("2d");
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const code = jsQR(imageData.data, imageData.width, imageData.height);

          if (code) {
            console.log("PhishGuard: Live QR detected", code.data);
            handleDetectedQR(code.data);
            closeOverlay();
            return;
          }
        }
        requestAnimationFrame(scanLoop);
      };
      
      requestAnimationFrame(scanLoop);

    } catch (err) {
      console.error("PhishGuard: Camera access denied", err);
      alert("Camera access is required for manual QR scanning.");
    }
  };

  const closeOverlay = () => {
    if (overlay) {
      document.body.removeChild(overlay);
      overlay = null;
    }
    if (videoStream) {
      videoStream.getTracks().forEach(track => track.stop());
      videoStream = null;
    }
  };

  const init = () => {
    console.log("PhishGuard India: Content script active");
    injectFloatingButton();
    scanAllImages();
    setInterval(scanAllImages, SCAN_INTERVAL);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();

