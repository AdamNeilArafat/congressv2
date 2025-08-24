import fs from "node:fs/promises";
const KEY = process.env.CONGRESS_API_KEY;
if(!KEY) throw new Error("Missing CONGRESS_API_KEY");

// in votes.json, add optional fields per bill: { "congress": 119, "roll": 42 }
const V = JSON.parse(await fs.readFile("data/votes.json","utf8"));

for (const [billKey, meta] of Object.entries(V)) {
  if (!meta.congress || !meta.roll) continue; // keep your hand-curated offenders as-is
  const url = `https://api.congress.gov/v3/house/roll-call-votes/${meta.congress}/${meta.roll}/member-votes?api_key=${KEY}`;
  const res = await fetch(url);
  if (!res.ok) { console.warn("vote fetch failed", billKey, res.status); continue; }
  const j = await res.json();
  const offenders = (j?.results?.members || [])
    .filter(m => (m.vote||"").toUpperCase()==="NO")
    .map(m => ({ bioguide: m.bioguideId, vote: m.vote }));
  meta.offenders = offenders;
}
await fs.writeFile("data/votes.json", JSON.stringify(V,null,2));
console.log("updated data/votes.json offenders");
