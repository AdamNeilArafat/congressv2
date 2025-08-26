#!/usr/bin/env node
import fs from "node:fs/promises";
import fetch from "node-fetch";
import { HttpsProxyAgent } from "https-proxy-agent";

const KEY = process.env.FEC_API_KEY;        // optional
const CYCLE = process.env.CYCLE || "2026";  // election cycle

const proxy = process.env.https_proxy || process.env.http_proxy;
const agent = proxy ? new HttpsProxyAgent(proxy) : undefined;

async function donorsFor(fecId){
  if(!KEY || !fecId) return null;
  const url = `https://api.open.fec.gov/v1/candidates/totals/?api_key=${KEY}&cycle=${CYCLE}&candidate_id=${fecId}`;
  const r = await fetch(url, { agent });
  if(!r.ok) return null;
  const j = await r.json();
  const row = (j.results||[])[0]; if(!row) return null;
  return {
    receipts: row.receipts || 0,
    individual: row.individual_contributions || 0,
    pac: row.pac_contributions || 0,
    transfers: row.transfers_from_other_authorized_committee || 0
  };
}

const members = JSON.parse(await fs.readFile("data/members.json","utf8"));
const out = {};
const queue = members.slice();
const CONCURRENCY = Number(process.env.CONCURRENCY) || 5;

async function worker(){
  while(queue.length){
    const m = queue.shift();
    const d = await donorsFor(m.fec);
    if(d) out[m.bioguide] = d;
  }
}

await Promise.all(Array.from({length: CONCURRENCY}, worker));
await fs.writeFile("data/donors-by-member.json", JSON.stringify(out,null,2));
console.log(`✅ wrote data/donors-by-member.json (${Object.keys(out).length})`);
