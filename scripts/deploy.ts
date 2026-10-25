import { network } from "hardhat";

const { viem } = await network.create();

const certificateRegistry = await viem.deployContract(
  "CertificateRegistry"
);

console.log(
  "CertificateRegistry deployed to:",
  certificateRegistry.address
);