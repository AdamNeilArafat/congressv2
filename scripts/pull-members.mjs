#!/usr/bin/env node
import fs from "node:fs/promises";
import fetch from "node-fetch";
import { HttpsProxyAgent } from "https-proxy-agent";

const SRC = "https://raw.githubusercontent.com/unitedstates/congress-legislators/gh-pages/legislators-current.json";
const img = (bio)=>`https://unitedstates.github.io/images/congress/225x275/${bio}.jpg`;
const normalizeParty = p => (p||"")[0]?.toUpperCase() || "";
const partyLabel = c => c==="D"?"Democrat":c==="R"?"Republican":c==="I"?"Independent":"";

const proxy = process.env.https_proxy || process.env.http_proxy;
const agent = proxy ? new HttpsProxyAgent(proxy) : undefined;

try {
  const res = await fetch(SRC, { agent });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const raw = await res.json();
  const out = [];
  for (const m of raw) {
    const bio = m.id?.bioguide; if(!bio) continue;
    const t = (m.terms||[]).at(-1) || {};
    const p = normalizeParty(t.party);
    out.push({
      bioguide: bio,
      name: `${m.name?.first||""} ${m.name?.last||""}`.trim(),
      party: p, partyLabel: partyLabel(p),
      chamber: t.type==="sen"?"senate":"house",
      state: t.state||"", district: t.type==="rep"?(t.district||""):"",
      fec: m.id?.fec?.[0] || "",
      photo: img(bio)
    });
  }
  await fs.mkdir("data",{recursive:true});
  await fs.writeFile("data/members.json", JSON.stringify(out,null,2));
  console.log("✅ wrote data/members.json");
} catch (e) {
  console.error("❌ pull-members", e);
  process.exit(1);
}
