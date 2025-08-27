#!/usr/bin/env node
import fs from "node:fs/promises";
import fetch from "node-fetch";
import { HttpsProxyAgent } from "https-proxy-agent";

const KEY = process.env.FEC_API_KEY;        // required unless a fallback CSV is available
const CYCLE = process.env.CYCLE || "2026";  // election cycle
// allow overriding the fallback but default to a bundled sample CSV so the
// site can still render when the API is unreachable
const FALLBACK = process.env.FEC_FALLBACK_CSV || "data/fec-sample.csv";

const proxy = process.env.https_proxy || process.env.http_proxy;
const agent = proxy ? new HttpsProxyAgent(proxy) : undefined;

function parseCsv(text){
  const lines = text.trim().split(/\r?\n/);
  const headers = lines.shift().split(",").map(h=>h.trim());
  const map = {};
  for(const line of lines){
    if(!line.trim()) continue;
    const cols = line.split(",");
    const row = {};
    headers.forEach((h,i)=> row[h] = (cols[i]||"").trim());
    const id = row.candidate_id || row.cand_id || row.fec_id || row.FEC_ID;
    if(!id) continue;
    map[id] = {
      receipts: Number(row.receipts || row.total_receipts || 0),
      individual: Number(row.individual || row.individual_contributions || 0),
      pac: Number(row.pac || row.pac_contributions || 0),
      transfers: Number(row.transfers || row.transfers_from_other_authorized_committee || 0)
    };
  }
  return map;
}

let fallback = null;
try {
  const txt = await fs.readFile(FALLBACK, "utf8");
  fallback = parseCsv(txt);
  console.log(`ℹ️ loaded fallback FEC totals from ${FALLBACK}`);
} catch (e) {
  if (!KEY) {
    console.error(`FEC_API_KEY not set and fallback CSV not found at ${FALLBACK}`);
    process.exit(1);
  }
}

async function donorsFor(fecId){
  if(KEY && fecId){
    try{
      const url = `https://api.open.fec.gov/v1/candidates/totals/?api_key=${KEY}&cycle=${CYCLE}&candidate_id=${fecId}`;
      const r = await fetch(url, { agent });
      if(r.ok){
        const j = await r.json();
        const row = (j.results||[])[0];
        if(row){
          return {
            receipts: row.receipts || 0,
            individual: row.individual_contributions || 0,
            pac: row.pac_contributions || 0,
            transfers: row.transfers_from_other_authorized_committee || 0
          };
        }
      }
    }catch(e){
      console.warn(`⚠️ fetch failed for ${fecId}: ${e.message}`);
    }
  }
  if(fallback && fecId){
    return fallback[fecId] || null;
  }
  return null;
}

const members = JSON.parse(await fs.readFile("data/members.json","utf8"));
const out = {};
const queue = members.slice();
const CONCURRENCY = Number(process.env.CONCURRENCY) || 5;

async function worker(){
  while(queue.length){
    const m = queue.shift();
    const d = await donorsFor(m.fec);
    out[m.bioguide] = d || { receipts: 0, individual: 0, pac: 0, transfers: 0 };
  }
}

await Promise.all(Array.from({length: CONCURRENCY}, worker));
await fs.writeFile("data/donors-by-member.json", JSON.stringify(out,null,2));
console.log(`✅ wrote data/donors-by-member.json (${Object.keys(out).length})`);
