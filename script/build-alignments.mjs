import fs from "node:fs/promises";
const donors = JSON.parse(await fs.readFile("data/donors-by-member.json","utf8"));
const votes  = JSON.parse(await fs.readFile("data/votes.json","utf8"));

const out = {};
for (const bio of Object.keys(donors)) {
  let seen=0, aligned=0;
  for (const [key, meta] of Object.entries(votes)) {
    // starter rule: count alignment when a member is an offender on "money" bills
    if (!/campaign|finance|lobby|dark|ethic/i.test(meta.title||"")) continue;
    const off = (meta.offenders||[]).some(o => o.bioguide===bio);
    seen += 1; if (off) aligned += 1;
  }
  out[bio] = { donor_alignment_index: seen ? aligned/seen : 0 };
}
await fs.writeFile("data/vote-alignments.json", JSON.stringify(out,null,2));
console.log("wrote data/vote-alignments.json");
