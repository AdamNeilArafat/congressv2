import fs from "node:fs/promises";
const KEY = process.env.FEC_API_KEY; if(!KEY) throw new Error("Missing FEC_API_KEY");
const cycle = parseInt(process.env.CYCLE||"2026",10);

const members = JSON.parse(await fs.readFile("data/members.json","utf8"));
const out = {};

for (const m of members) {
  if(!m.fec) continue;
  const fec = m.fec;

  // PAC vs individual vs total receipts
  const tURL = `https://api.open.fec.gov/v1/candidate/totals/?api_key=${KEY}&candidate_id=${fec}&cycle=${cycle}&election_full=true&per_page=1`;
  const t = await fetch(tURL).then(r=>r.json()).catch(()=>({}));
  const totals = t?.results?.[0] || {};
  const receipts = totals.receipts || 0;
  const pac_pct = receipts ? (totals.pac_contributions||0) / receipts : 0;

  // in-state vs out-of-state
  const sURL = `https://api.open.fec.gov/v1/schedules/schedule_a/by_state/by_candidate/?api_key=${KEY}&candidate_id=${fec}&cycle=${cycle}&election_full=true&per_page=100`;
  const s = await fetch(sURL).then(r=>r.json()).catch(()=>({}));
  let in_state_dollars=0, out_state_dollars=0;
  for (const row of (s?.results||[])) {
    const amt = row.total || 0;
    if (row.state === m.state) in_state_dollars += amt; else out_state_dollars += amt;
  }

  // small-dollar share (<= $200 bin)
  const zURL = `https://api.open.fec.gov/v1/schedules/schedule_a/by_size/by_candidate/?api_key=${KEY}&candidate_id=${fec}&cycle=${cycle}&election_full=true&per_page=100`;
  const z = await fetch(zURL).then(r=>r.json()).catch(()=>({}));
  let indivTotal=0, small=0;
  for (const r of (z?.results||[])) { indivTotal += r.total||0; if (r.size===0) small += r.total||0; }
  const small_share = indivTotal ? small/indivTotal : 0;

  out[m.bioguide] = { pac_pct, small_share, in_state_dollars, out_state_dollars, industries:{} };
}

await fs.writeFile("data/donors-by-member.json", JSON.stringify(out,null,2));
console.log("wrote data/donors-by-member.json");
