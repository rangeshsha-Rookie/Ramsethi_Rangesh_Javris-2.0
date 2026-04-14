const hre = require("hardhat");

async function main() {
  console.log("Starting deployment on network:", hre.network.name);

  // Deploy FraudRegistry
  const FraudRegistry = await hre.ethers.getContractFactory("FraudRegistry");
  const fraudRegistry = await FraudRegistry.deploy();

  await fraudRegistry.waitForDeployment();
  const address = await fraudRegistry.getAddress();

  console.log("FraudRegistry deployed to:", address);
  console.log("Deployment complete!");
  
  // NOTE: Copy the above address and place it into extension/background/service-worker.js
  // and your Vercel .env file as CONTRACT_ADDRESS
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
