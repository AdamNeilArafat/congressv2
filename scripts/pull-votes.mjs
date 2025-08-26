#!/usr/bin/env node
import fs from "node:fs/promises";
import fetch from "node-fetch";
import { HttpsProxyAgent } from "https-proxy-agent";

const KEY = process.env.CONGRESS_API_KEY;
if (!KEY) { console.error("❌ CONGRESS_API_KEY missing"); process.exit(1); }

const BASE = "https://api.congress.gov/v3";
const UA = "congressv2/1.0 (AdamNeilArafat/congressv2)";
const sinceISO = new Date(Date.now() - 30*24*60*60*1000).toISOString(); // last 30d

const proxy = process.env.https_proxy || process.env.http_proxy;
const agent = proxy ? new HttpsProxyAgent(proxy) : undefined;

async function getJSON(url, attempt=1){
  const r = await fetch(url, {
    agent,
    headers: {
      "X-Api-Key": KEY,
      "User-Agent": UA,
      "Accept": "application/json"
    },
  });
  if (!r.ok) {
    const txt = await r.text().catch(()=> "");
    if ((r.status===429 || r.status>=500) && attempt<3) {
      const wait = 1000*attempt;
      console.warn(`⚠️ ${r.status} on ${url} — retrying in ${wait}ms`);
      await new Promise(res=>setTimeout(res, wait));
      return getJSON(url, attempt+1);
    }
    throw new Error(`HTTP ${r.status} ${url}\n${txt}`);
  }
  return r.json();
}

function offendersFromRoll(roll){
  const out = [];
  for (const v of roll.votes || []) {
    const choice = (v.vote || "").toLowerCase();
    if (choice==="no" || choice==="nay") {
      const m = v.member || {};
      out.push({
        bioguide: m.bioguideId || m.bioguide || m.id,
        name: m.fullName || m.name || "",
        party: m.partyName || m.party || "",
        state: m.stateCode || m.state || ""
      });
    }
  }
  return out.filter(x=>x.bioguide);
}

async function collectChamber(chamber){
  const out = {};
  // The API key is provided via header, so avoid leaking it in the request URL
  // which could be logged or cached. Rely solely on the header for auth.
  let url = `${BASE}/votes/${chamber}?fromDateTime=${encodeURIComponent(sinceISO)}&format=json&limit=250`;
  while (url) {
    const data = await getJSON(url);
    for (const v of data.votes || []) {
      const id = `${chamber}-${v.congress}-${v.session}-rc${v.rollNumber}`;
      out[id] = {
        title: v.voteQuestion || v.voteDesc || v.bill?.title || "Roll Call",
        short: v.bill?.number || `RC ${v.rollNumber}`,
        award: "Recorded Vote",
        meaning: v.voteQuestion || "",
        rc: { chamber, congress: Number(v.congress), session: Number(v.session), roll: Number(v.rollNumber) },
        offenders_vote: ["no","nay"],
        offenders: offendersFromRoll(v)
      };
    }
    // follow pagination if present
    url = data?.pagination?.next || "";
  }
  return out;
}

(async ()=>{
  const [house, senate] = await Promise.all([
    collectChamber("house"),
    collectChamber("senate")
  ]);
  const votes = { ...house, ...senate };
  await fs.mkdir("data", { recursive:true });
  await fs.writeFile("data/votes.json", JSON.stringify(votes,null,2));
  console.log(`✅ wrote data/votes.json (${Object.keys(votes).length} roll calls since ${sinceISO})`);
})().catch(e=>{
  console.error("❌ pull-votes failed:", e.message || e);
  process.exit(1);
});
