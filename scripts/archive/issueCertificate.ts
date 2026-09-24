import { network } from "hardhat";
import { keccak256, toBytes } from "viem";

const { viem } = await network.connect();

const contractAddress =
  "0x5fbdb2315678afecb367f032d93f642f64180aa3";

const [admin, institution] = await viem.getWalletClients();

console.log("Admin:", admin.account.address);
console.log("Institution:", institution.account.address);

const docHash = keccak256(
  toBytes("TEST-CERTIFICATE-002")
);

const studentRef = keccak256(
  toBytes("STUDENT-002")
);


const ipfsCid =
  "bafkreifvatlxv6r5d63unk6roxzya3vsiyo4b22cpwawxb3funpmuehf3q";

const aiRiskScore = 5;

const abi = [
  {
    type: "function",
    name: "issueCertificate",
    inputs: [
      {
        name: "docHash",
        type: "bytes32",
      },
      {
        name: "studentRef",
        type: "bytes32",
      },
      {
        name: "ipfsCid",
        type: "string",
      },
      {
        name: "aiRiskScore",
        type: "uint8",
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
  functionName: "issueCertificate",
  args: [
    docHash,
    studentRef,
    ipfsCid,
    aiRiskScore,
  ],
});

console.log("Transaction hash:", hash);

const publicClient = await viem.getPublicClient();

await publicClient.waitForTransactionReceipt({
  hash,
});

console.log("Certificate issued successfully!");
console.log("Document Hash:", docHash);
console.log("Student Reference:", studentRef);
console.log("IPFS CID:", ipfsCid);
console.log("AI Risk Score:", aiRiskScore);