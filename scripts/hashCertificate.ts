import fs from "fs";
import crypto from "crypto";

const filePath = "./certificates/test-certificate.pdf";

if (!fs.existsSync(filePath)) {
  throw new Error(`Certificate file not found: ${filePath}`);
}

const fileBuffer = fs.readFileSync(filePath);

const hash = crypto
  .createHash("sha256")
  .update(fileBuffer)
  .digest("hex");

console.log("================================");
console.log("CERTIFICATE SHA-256");
console.log("================================");
console.log("File:", filePath);
console.log("SHA-256:", hash);
console.log("================================");