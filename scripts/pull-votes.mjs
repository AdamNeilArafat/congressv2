#!/usr/bin/env node
import fs from "node:fs/promises";
import fetch from "node-fetch";

const KEY = process.env.CONGRESS_API_KEY; // api.data.gov key
if (!KEY) { console.error("❌ CONGRESS_API_KEY missing"); process.exit(1); }

const BASE = "https://api.congress.gov/v3";
const nowIso = () => new Date().toISOString();

// Example: last 60 days House & Senate roll calls; map offenders who voted "No"/"Nay" on selected categories you care about
const since = new Date(Date.now() - 1000*60*60*24*60).toISOString();

async function page(url){
  const r = await fetch(url);
  if(!r.ok) throw new Error(`HTTP ${r.status} ${url}`);
  return r.json();
}

function offendersFromRoll(roll){
  const res = [];
  for (const m of roll.votes || []) {
    const choice = (m.vote || "").toLowerCase();
    if (choice==="no" || choice==="nay") {
      res.push({ bioguide: m.member?.bioguideId, name: m.member?.fullName, party: m.member?.partyName, state: m.member?.stateCode });
    }
  }
  return res.filter(o=>o.bioguide);
}

async function collectChamber(chamber){
  const out = {};
  const url = `${BASE}/votes/${chamber}?fromDateTime=${encodeURIComponent(since)}&format=json&api_key=${KEY}`;
  const data = await page(url);
  for (const v of data.votes || []) {
    const id = `${chamber}-${v.congress}-${v.session}-rc${v.rollNumber}`;
    out[id] = {
      title: v.voteQuestion || v.voteDesc || v.bill?.title || "Roll Call",
      short: v.bill?.number || v.voteQuestion || `RC ${v.rollNumber}`,
      award: "Recorded Vote",
      meaning: v.voteQuestion || "",
      rc: { chamber, congress: Number(v.congress), session: Number(v.session), roll: Number(v.rollNumber) },
      offenders_vote: ["no","nay"],
      offenders: offendersFromRoll(v)
    };
  }
  return out;
}

const votes = { ...(await collectChamber("house")), ...(await collectChamber("senate")) };
await fs.mkdir("data",{recursive:true});
await fs.writeFile("data/votes.json", JSON.stringify(votes,null,2));
console.log(`✅ wrote data/votes.json (${Object.keys(votes).length} roll calls since ${since}) at ${nowIso()}`);
