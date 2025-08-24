#!/usr/bin/env node
import fs from "node:fs/promises";

const votes = JSON.parse(await fs.readFile("data/votes.json","utf8").catch(()=> "{}"));
const counts = {}; let total=0;

for (const v of Object.values(votes||{})) {
  if (!Array.isArray(v.offenders)) continue;
  total++;
  for (const o of v.offenders) counts[o.bioguide] = (counts[o.bioguide]||0)+1;
}

const out = {};
for (const [bio, n] of Object.entries(counts)) out[bio] = { offender_votes: n, share: total? +(n/total).toFixed(3) : 0 };

await fs.writeFile("data/vote-alignments.json", JSON.stringify(out,null,2));
console.log(`✅ wrote data/vote-alignments.json (from ${total} roll calls)`);
