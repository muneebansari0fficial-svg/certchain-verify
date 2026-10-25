import fs from "fs";
import crypto from "crypto";
import { execFileSync } from "child_process";
import { network } from "hardhat";
import {
  encodeFunctionData,
  decodeAbiParameters,
} from "viem";

const filePath =
  process.env.CERTIFICATE || "./certificates/test-certificate.pdf";

if (!fs.existsSync(filePath)) {
  throw new Error(`Certificate file not found: ${filePath}`);
}

// ========================================
// 1. READ PDF
// ========================================

const fileBuffer = fs.readFileSync(filePath);

// ========================================
// 2. GENERATE SHA-256
// ========================================

const sha256Hash = crypto
  .createHash("sha256")
  .update(fileBuffer)
  .digest("hex");

const docHash = `0x${sha256Hash}` as `0x${string}`;

console.log("================================");
console.log("REAL CERTIFICATE VERIFICATION");
console.log("================================");
console.log("Certificate:", filePath);
console.log("SHA-256:", sha256Hash);
console.log("Document Hash:", docHash);

// ========================================
// 3. CONNECT TO BLOCKCHAIN
// ========================================

const { viem } = await network.create();

const contractAddress =
  "0x5fbdb2315678afecb367f032d93f642f64180aa3";

const verifyAbi = [
  {
    type: "function",
    name: "verify",
    inputs: [
      {
        name: "docHash",
        type: "bytes32",
      },
    ],
    outputs: [
      { name: "exists", type: "bool" },
      { name: "valid", type: "bool" },
      { name: "issuer", type: "address" },
      { name: "issuerName", type: "string" },
      { name: "issuedAt", type: "uint64" },
      { name: "revokedAt", type: "uint64" },
      { name: "ipfsCid", type: "string" },
      { name: "aiRiskScore", type: "uint8" },
    ],
    stateMutability: "view",
  },
] as const;

// ========================================
// 4. CALL VERIFY
// ========================================

const publicClient = await viem.getPublicClient();

const data = encodeFunctionData({
  abi: verifyAbi,
  functionName: "verify",
  args: [docHash],
});

const response = await publicClient.call({
  to: contractAddress,
  data,
});

// ========================================
// 5. DECODE RESULT
// ========================================

const decoded = decodeAbiParameters(
  [
    { type: "bool" },
    { type: "bool" },
    { type: "address" },
    { type: "string" },
    { type: "uint64" },
    { type: "uint64" },
    { type: "string" },
    { type: "uint8" },
  ],
  response.data
);

const [
  exists,
  valid,
  issuer,
  issuerName,
  issuedAt,
  revokedAt,
  ipfsCid,
  aiRiskScore,
] = decoded;

// ========================================
// 6. DISPLAY RESULT
// ========================================

console.log("================================");
console.log("BLOCKCHAIN RESULT");
console.log("================================");
console.log("Exists:", exists);
console.log("Valid:", valid);
console.log("Issuer:", issuer);
console.log("Issuer Name:", issuerName);
console.log("Issued At:", issuedAt);
console.log("Revoked At:", revokedAt);
console.log("IPFS CID:", ipfsCid);
console.log("AI Risk Score:", aiRiskScore);
console.log("================================");

if (exists && valid) {
  console.log("RESULT: CERTIFICATE IS AUTHENTIC");
} else if (exists && !valid) {
  console.log("RESULT: CERTIFICATE IS REVOKED / INVALID");
} else {
  console.log("RESULT: CERTIFICATE NOT REGISTERED");
  console.log("Running AI forensic analysis...");

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

  if (match) {
    const aiRiskScore = Number(match[1]);

    console.log(
      "AI Risk Score:",
      aiRiskScore,
      "/ 100"
    );

    if (aiRiskScore >= 70) {
      console.log(
        "AI RESULT: HIGH FORGERY RISK"
      );
    } else if (aiRiskScore >= 40) {
      console.log(
        "AI RESULT: MEDIUM FORGERY RISK"
      );
    } else {
      console.log(
        "AI RESULT: LOW FORGERY RISK"
      );
    }
  } else {
    console.log(
      "AI RESULT: Risk score unavailable"
    );
  }
}