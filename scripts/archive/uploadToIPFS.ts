import "dotenv/config";
import axios from "axios";
import fs from "fs";
import FormData from "form-data";

const PINATA_JWT = process.env.PINATA_JWT;

if (!PINATA_JWT) {
  throw new Error("PINATA_JWT is missing in .env file");
}

const filePath = "./certificates/test-certificate.pdf";

if (!fs.existsSync(filePath)) {
  throw new Error(`Certificate file not found: ${filePath}`);
}

const formData = new FormData();

formData.append(
  "file",
  fs.createReadStream(filePath)
);

console.log("Uploading certificate to IPFS...");

const response = await axios.post(
  "https://uploads.pinata.cloud/v3/files",
  formData,
  {
    headers: {
      Authorization: `Bearer ${PINATA_JWT}`,
      ...formData.getHeaders(),
    },
  }
);

console.log("Upload successful!");
console.log("IPFS CID:", response.data.data.cid);