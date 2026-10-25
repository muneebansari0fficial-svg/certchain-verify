import { network } from "hardhat";
import { keccak256, toBytes } from "viem";

const { viem } = await network.create();

const contractAddress =
  "0x5fbdb2315678afecb367f032d93f642f64180aa3";

const [admin, institution] = await viem.getWalletClients();

const docHash =
  "0x138683f118900e721414a813fd991a56374037012b23182db6d53a6d474304f3" as `0x${string}`;

console.log("Institution:", institution.account.address);
console.log("Document Hash:", docHash);

const abi = [
  {
    type: "function",
    name: "revokeCertificate",
    inputs: [
      {
        name: "docHash",
        type: "bytes32",
      },
      {
        name: "reason",
        type: "string",
      },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
] as const;

const hash = await institution.writeContract({
  account: institution.account,
  chain: undefined,
  address: contractAddress,
  abi,
  functionName: "revokeCertificate",
  args: [
    docHash,
    "Certificate cancelled for testing",
  ],
});

console.log("Transaction hash:", hash);

const publicClient = await viem.getPublicClient();

await publicClient.waitForTransactionReceipt({
  hash,
});

console.log("Certificate revoked successfully!");