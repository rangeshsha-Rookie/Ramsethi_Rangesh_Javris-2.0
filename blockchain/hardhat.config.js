require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.19",
  networks: {
    amoy: {
      url: "https://rpc-amoy.polygon.technology/",
      chainId: 80002,
      // Provide a dummy private key if one isn't in env so Hardhat doesn't fail parsing config
      accounts: [process.env.PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000000"]
    }
  }
};
