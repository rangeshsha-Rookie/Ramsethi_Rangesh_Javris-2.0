/**
 * blockchain-logger.js
 * Helper function to interact with the deployed Hardhat contract on Polygon Amoy.
 * Intended to be bundled in the extension service worker or executed in popup.
 */

try {
    // If running in browser context with ethers bundled:
    // import { ethers } from "ethers";
} catch(e) {}

async function logFraudToBlockchain(vpa, contractAddress, privateKey) {
  if (typeof ethers === 'undefined') {
      console.error("Ethers.js not found. Make sure it is bundled or included.");
      return;
  }

  try {
    const provider = new ethers.JsonRpcProvider("https://rpc-amoy.polygon.technology/");
    const wallet = new ethers.Wallet(privateKey, provider);

    // Minimal ABI needed to call the reportFraudVPA function
    const abi = [
      "function reportFraudVPA(string vpa) public"
    ];

    const contract = new ethers.Contract(contractAddress, abi, wallet);

    console.log(`Sending fraud report to blockchain for VPA: ${vpa}`);
    const tx = await contract.reportFraudVPA(vpa);
    
    console.log(`Transaction sent! Waiting for confirmation... Hash: ${tx.hash}`);
    const receipt = await tx.wait();
    
    console.log(`Successfully logged fraud to blockchain. Block details:`, receipt);
    return receipt;
  } catch (err) {
    console.error("Failed to log fraud to blockchain:", err);
    throw err;
  }
}

// Export for module systems or just leave in global scope for extension background.
if (typeof module !== 'undefined') {
    module.exports = { logFraudToBlockchain };
}
