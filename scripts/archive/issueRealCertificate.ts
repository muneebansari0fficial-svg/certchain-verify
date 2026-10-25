import "dotenv/config";
import fs from "fs";
import crypto from "crypto";
import axios from "axios";
import FormData from "form-data";
import { execFileSync } from "child_process";
import { network } from "hardhat";
import { keccak256, toBytes } from "viem";

const PINATA_JWT = process.env.PINATA_JWT;

if (!PINATA_JWT) {
  throw new Error("PINATA_JWT is missing in .env file");
}

const filePath = "./certificates/certificate-002.pdf";

if (!fs.existsSync(filePath)) {
  throw new Error(`Certificate file not found: ${filePath}`);
}

// ========================================
// 1. READ CERTIFICATE
// ========================================

const fileBuffer = fs.readFileSync(filePath);

console.log("================================");
console.log("REAL CERTIFICATE ISSUANCE");
console.log("================================");
console.log("Certificate:", filePath);

// ========================================
// 2. SHA-256 HASH
// ========================================

const sha256Hash = crypto
  .createHash("sha256")
  .update(fileBuffer)
  .digest("hex");

const docHash = `0x${sha256Hash}` as `0x${string}`;

console.log("SHA-256:", sha256Hash);
console.log("Document Hash:", docHash);

// ========================================
// 3. UPLOAD TO IPFS
// ========================================

console.log("Uploading certificate to IPFS...");

const formData = new FormData();

formData.append(
  "file",
  fs.createReadStream(filePath)
);

const ipfsResponse = await axios.post(
  "https://uploads.pinata.cloud/v3/files",
  formData,
  {
    headers: {
      Authorization: `Bearer ${PINATA_JWT}`,
      ...formData.getHeaders(),
    },
  }
);

const ipfsCid = ipfsResponse.data.data.cid;

console.log("IPFS upload successful!");
console.log("IPFS CID:", ipfsCid);

// ========================================
// 4. CONNECT TO HARDHAT
// ========================================

const { viem } = await network.create();

const [, institution] = await viem.getWalletClients();

const contractAddress =
  "0x5fbdb2315678afecb367f032d93f642f64180aa3";

console.log(
  "Institution:",
  institution.account.address
);

// ========================================
// 5. STUDENT REFERENCE
// ========================================

const studentRef = keccak256(
  toBytes("STUDENT-003")
);

// ========================================
// 6. AI RISK SCORE
// ========================================

// ========================================
// 6. AI RISK SCORE
// ========================================

console.log("Running AI certificate analysis...");

const aiOutput = execFileSync(
  "python",
  ["ai/predict.py"],
  {
    encoding: "utf-8",
  }
);

console.log(aiOutput);

const match = aiOutput.match(
  /AI_RISK_SCORE=(\d+)/
);

if (!match) {
  throw new Error(
    "AI risk score was not returned by predict.py"
  );
}

const aiRiskScore = Number(match[1]);

console.log(
  "AI Risk Score received:",
  aiRiskScore
);

// ========================================
// 7. SMART CONTRACT ABI
// ========================================

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

// ========================================
// 8. ISSUE ON BLOCKCHAIN
// ========================================

console.log("Issuing certificate on blockchain...");

const txHash = await institution.writeContract({
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

console.log("Transaction hash:", txHash);

// ========================================
// 9. WAIT FOR TRANSACTION
// ========================================

const publicClient = await viem.getPublicClient();

await publicClient.waitForTransactionReceipt({
  hash: txHash,
});

// ========================================
// 10. FINAL RESULT
// ========================================

console.log("================================");
console.log("CERTIFICATE ISSUED SUCCESSFULLY");
console.log("================================");
console.log("Document Hash:", docHash);
console.log("Student Reference:", studentRef);
console.log("IPFS CID:", ipfsCid);
console.log("AI Risk Score:", aiRiskScore);
console.log("Transaction:", txHash);
console.log("================================");