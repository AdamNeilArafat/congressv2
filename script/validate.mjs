import fs from "node:fs/promises";
const [members, votes, donors, align] = await Promise.all([
  fs.readFile("data/members.json","utf8").then(JSON.parse),
  fs.readFile("data/votes.json","utf8").then(JSON.parse),
  fs.readFile("data/donors-by-member.json","utf8").then(JSON.parse),
  fs.readFile("data/vote-alignments.json","utf8").then(JSON.parse)
]);
const bioSet = new Set(members.map(m=>m.bioguide));
let bad=0;
for(const [k,v] of Object.entries(votes)){
  for(const o of (v.offenders||[])){
    if(!bioSet.has(o.bioguide)){ console.warn("Unknown BioGuide in votes:", k, o.bioguide); bad++; }
  }
}
for(const b of Object.keys(donors)) if(!bioSet.has(b)){ console.warn("Unknown BioGuide in donors:", b); bad++; }
for(const b of Object.keys(align)) if(!bioSet.has(b)){ console.warn("Unknown BioGuide in align:", b); bad++; }
console.log(bad ? `Found ${bad} issues` : "All good");
