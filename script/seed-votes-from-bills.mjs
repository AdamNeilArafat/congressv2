import fs from "node:fs/promises";
import path from "node:path";

const billsDir = "Bills";
const files = (await fs.readdir(billsDir)).filter(f => f.toLowerCase().endsWith(".html"));

const out = {};
for (const f of files) {
  const title = f.replace(/\.html$/i,"");
  const key = title.toLowerCase()
    .replace(/\s+/g,"-")
    .replace(/[()'&]/g,"")
    .replace(/-{2,}/g,"-");
  out[key] = {
    title,
    short: title.replace(/\s*\(2027\)\s*/,""),
    href: `/Bills/${f}`,
    award: "",
    meaning: "",
    offenders: []
    // Optional: add these when you know them to auto-fill offenders:
    // "congress": 119, "roll": 42
  };
}

await fs.mkdir("data",{recursive:true});
await fs.writeFile("data/votes.json", JSON.stringify(out,null,2));
console.log("wrote data/votes.json with", Object.keys(out).length, "bills");
