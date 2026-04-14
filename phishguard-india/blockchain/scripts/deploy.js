async function main() {
  const FraudRegistry = await ethers.getContractFactory("FraudRegistry");
  const registry = await FraudRegistry.deploy();
  await registry.deployed();
  console.log("FraudRegistry deployed to:", registry.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
