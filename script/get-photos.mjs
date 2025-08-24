// scripts/get-photos.mjs
import fs from "node:fs/promises";
import path from "node:path";
const members = JSON.parse(await fs.readFile("data/members.json","utf8"));
await fs.mkdir("images/headshots",{recursive:true});

for (const m of members) {
  const bio = m.bioguide;
  const dest = path.join("images/headshots", `${bio}.jpg`);
  try { await fs.access(dest); continue; } catch {}
  const url = `https://unitedstates.github.io/images/congress/225x275/${bio}.jpg`;
  const res = await fetch(url);
  if (res.ok) {
    const buf = Buffer.from(await res.arrayBuffer());
    await fs.writeFile(dest, buf);
    console.log("saved", dest);
  } else {
    console.warn("missing on CDN", bio);
  }
}
