const hre = require("hardhat");

async function main() {
  console.log("=== PHASE 5 VERIFICATION RUN ===\n");
  
  const FraudRegistry = await hre.ethers.getContractFactory("FraudRegistry");
  const fraudRegistry = await FraudRegistry.deploy();
  await fraudRegistry.waitForDeployment();
  const address = await fraudRegistry.getAddress();
  console.log("✅ Contract deployed to local Hardhat network at:", address);

  const testVpa = "scammer@sbi";
  console.log(`\nTesting VPA Reporting to the blockchain: [${testVpa}]`);
  
  const tx = await fraudRegistry.reportFraudVPA(testVpa);
  await tx.wait();
  console.log("✅ Report 1 submitted successfully.");

  // Get score
  const score = await fraudRegistry.getFraudScore(testVpa);
  console.log(`✅ Current Fraud Score for ${testVpa} is:`, score.toString());
  
  // Try duplicate report from same address
  try {
      console.log(`\nAttempting duplicate report for same VPA from same wallet...`);
      await fraudRegistry.reportFraudVPA(testVpa);
  } catch (err) {
      console.log(`✅ Duplicate report rejected successfully. Error: ${err.reason}`);
  }

  // To simulate another wallet reporting, we get signers
  const signers = await hre.ethers.getSigners();
  const wallet2 = signers[1];
  const wallet3 = signers[2];

  console.log(`\nSimulating 2 other community members reporting the same VPA...`);
  await fraudRegistry.connect(wallet2).reportFraudVPA(testVpa);
  console.log("✅ Report 2 submitted.");
  await fraudRegistry.connect(wallet3).reportFraudVPA(testVpa);
  console.log("✅ Report 3 submitted.");

  const newScore = await fraudRegistry.getFraudScore(testVpa);
  const isHighRisk = await fraudRegistry.isHighRisk(testVpa);
  
  console.log(`\n✅ Final Fraud Score for ${testVpa} is:`, newScore.toString());
  console.log(`✅ Is marked High Risk?`, isHighRisk);
  console.log("\n=== TEST COMPLETED SUCCESSFULLY ===");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
