import { network } from "hardhat";
import { encodeFunctionData, decodeFunctionResult } from "viem";

const { viem } = await network.create();

const contractAddress =
  "0x5fbdb2315678afecb367f032d93f642f64180aa3";

const institutionAddress =
  "0x70997970c51812dc3a010c7d01b50e0d17dc79c8";

const publicClient = await viem.getPublicClient();

const isInstitutionAbi = [
  {
    type: "function",
    name: "isInstitution",
    inputs: [
      {
        name: "",
        type: "address",
      },
    ],
    outputs: [
      {
        name: "",
        type: "bool",
      },
    ],
    stateMutability: "view",
  },
] as const;

const data = encodeFunctionData({
  abi: isInstitutionAbi,
  functionName: "isInstitution",
  args: [institutionAddress],
});

const result = await publicClient.call({
  to: contractAddress,
  data,
});

const isRegistered = decodeFunctionResult({
  abi: isInstitutionAbi,
  functionName: "isInstitution",
  data: result.data!,
});

console.log("Institution Address:", institutionAddress);
console.log("Is Registered:", isRegistered);