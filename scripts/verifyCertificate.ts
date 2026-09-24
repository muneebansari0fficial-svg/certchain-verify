import { network } from "hardhat";
import {
  encodeFunctionData,
  decodeAbiParameters,
  keccak256,
  toBytes,
} from "viem";

const { viem } = await network.connect();

const contractAddress =
  "0x5fbdb2315678afecb367f032d93f642f64180aa3";

const docHash = keccak256(
  toBytes("TEST-CERTIFICATE-002")
);

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
      {
        name: "exists",
        type: "bool",
      },
      {
        name: "valid",
        type: "bool",
      },
      {
        name: "issuer",
        type: "address",
      },
      {
        name: "issuerName",
        type: "string",
      },
      {
        name: "issuedAt",
        type: "uint64",
      },
      {
        name: "revokedAt",
        type: "uint64",
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
    stateMutability: "view",
  },
] as const;

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

console.log("================================");
console.log("CERTIFICATE VERIFICATION");
console.log("================================");

console.log("Document Hash:", docHash);
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
  console.log("RESULT: CERTIFICATE IS VALID");
} else if (exists && !valid) {
  console.log("RESULT: CERTIFICATE IS NOT VALID");
} else {
  console.log("RESULT: CERTIFICATE NOT FOUND");
}