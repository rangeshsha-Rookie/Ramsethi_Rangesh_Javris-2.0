const hre = require("hardhat");

async function main() {
  const contractAddress = "YOUR_CONTRACT_ADDRESS_HERE"; // replace after deployment
  
  if (contractAddress === "YOUR_CONTRACT_ADDRESS_HERE") {
    console.log("Please replace the contract address in scripts/interact.js before running!");
    return;
  }

  const fraudRegistry = await hre.ethers.getContractAt("FraudRegistry", contractAddress);

  console.log("Connected to FraudRegistry at:", contractAddress);

  const testVpa = "scammer@ybl";
  
  // 1. Report the VPA
  console.log(`Reporting VPA: ${testVpa}...`);
  try {
      const tx = await fraudRegistry.reportFraudVPA(testVpa);
      const receipt = await tx.wait();
      console.log("Transaction confirmed:", receipt.hash);
  } catch(e) {
      console.log("Report failed (maybe already reported by you?).", e.message);
  }

  // 2. Get the fraud score
  const score = await fraudRegistry.getFraudScore(testVpa);
  console.log(`Fraud Score for ${testVpa}:`, score.toString());

  // 3. Check high risk
  const isHighRisk = await fraudRegistry.isHighRisk(testVpa);
  console.log(`Is High Risk?`, isHighRisk);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
