import { defineConfig } from "hardhat/config";
import hardhatViem from "@nomicfoundation/hardhat-viem";
import "dotenv/config";

export default defineConfig({
  plugins: [hardhatViem],

  solidity: {
    version: "0.8.34",
  },

  networks: {
    hardhat: {
      type: "edr-simulated",
      chainType: "l1",
      chainId: 31337,
    },
    localhost: {
      type: "http",
      chainType: "l1",
      url: "http://127.0.0.1:8545",
    },
    amoy: {
      type: "http",
      chainType: "l1",
      url: "https://weathered-alien-meme.matic-amoy.quiknode.pro/fc65a79a3130dade12356eb932fc27f45f821293/",
      accounts: [process.env.PRIVATE_KEY || ""],
      chainId: 80002,
    },
  },
});