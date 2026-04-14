/**
 * nvidia-explainer.js
 * Calls the NVIDIA NIM API (llama-nemotron-nano-4b-instruct) to generate
 * human-friendly explanations for flagged threats in Hinglish/English.
 */

async function explainThreat(context) {
  // Try to get the API key from local storage
  let apiKey = null;
  try {
    const data = await chrome.storage.local.get("nvidia_api_key");
    apiKey = data.nvidia_api_key;
  } catch (e) {
    console.warn("Could not access chrome.storage.local (might not be running in extension)");
  }

  // Pre-written static fallbacks if API fails or there is no key
  const fallbacks = {
    "PHISHING_URL": {
      "hinglish": "Bhai, ye website fake lag rahi hai! Iska URL suspicious hai, please apni details mat daalo.",
      "english": "Warning: This website appears to be a phishing site. Do not enter any sensitive information."
    },
    "FRAUD_QR": {
      "hinglish": "Ye QR code safe nahi hai! Ye kisi scam website par le ja sakta hai.",
      "english": "Warning: This QR code exhibits fraudulent patterns. It may direct you to a scam."
    },
    "VPA_MISMATCH": {
      "hinglish": "Yaar, ye QR code suspicious lag raha hai! Merchant name aur UPI handle match nahi kar raha. Payment mat karo!",
      "english": "Warning: The displayed merchant name does not match the actual UPI handle. Do not proceed with payment."
    },
    "DEFAULT": {
      "hinglish": "Kuch toh gadbad hai. Ye transaction suspicious lag rahi hai.",
      "english": "We detected suspicious activity regarding this transaction. Please proceed with caution."
    }
  };

  const threatType = context.type || "DEFAULT";
  const language = context.language === "hinglish" ? "hinglish" : "english";

  // Fallback immediately if no API key
  if (!apiKey) {
    return {
      explanation: fallbacks[threatType]?.[language] || fallbacks["DEFAULT"][language],
      source: "local"
    };
  }

  const promptText = `Direct warning for ${language}: ${context.type} threat found in ${context.vpa || context.url}. Flags: ${context.flags}. One sentence urgency!`;

  try {
    const response = await fetch("https://integrate.api.nvidia.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: "nvidia/llama-3.1-nemotron-nano-4b-v1.1",
        messages: [
          { role: "system", content: "You are a cybersecurity expert. You must provide a 1-sentence warning in Hinglish. Be direct." },
          { role: "user", content: `Threat: ${context.type} on ${context.vpa || context.url}. State the danger in one urgent Hinglish sentence.` }
        ],
        temperature: 0.1,
        top_p: 0.7,
        max_tokens: 512
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const json = await response.json();
    const content = json.choices[0].message.content.trim();
    
    return {
      explanation: content || "Warning: Suspicious transaction detected. Proceed with caution.",
      source: "nvidia"
    };
  } catch (err) {
    console.error("NVIDIA API failed, falling back to static strings:", err);
    return {
      explanation: fallbacks[threatType]?.[language] || fallbacks["DEFAULT"][language],
      source: "local"
    };
  }
}

// Export for module environments
if (typeof module !== 'undefined') {
  module.exports = { explainThreat };
}

