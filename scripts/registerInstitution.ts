import { network } from "hardhat";

const { viem } = await network.connect();

const contractAddress = "0x5fbdb2315678afecb367f032d93f642f64180aa3";

// Dono wallet clients lo — Admin aur Institution
const [admin, institution] = await viem.getWalletClients();

console.log("Admin:", admin.account.address);
console.log("Institution:", institution.account.address);

const hash = await admin.writeContract({
  account: admin.account,
  chain: undefined,
  address: contractAddress,
  abi: [
    {
      type: "function",
      name: "registerInstitution",
      inputs: [
        { name: "inst", type: "address" },
        { name: "name", type: "string" },
      ],
      outputs: [],
      stateMutability: "nonpayable",
    },
  ],
  functionName: "registerInstitution",
  args: [
    institution.account.address,
    "University of Azad Jammu & Kashmir (UAJK)",
  ],
});

console.log("Transaction hash:", hash);

const publicClient = await viem.getPublicClient();

await publicClient.waitForTransactionReceipt({ hash });

console.log("Institution registered successfully!");