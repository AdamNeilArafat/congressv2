// scripts/pull-votes.mjs
import fs from "node:fs/promises";

const API_KEY = process.env.CONGRESS_API_KEY;
if (!API_KEY) {
  console.error("❌ Missing CONGRESS_API_KEY");
  process.exit(1);
}

const API_BASE = "https://api.data.gov/congress/v3";
const fromISO = process.env.FROM || new Date(Date.now() - 1000*60*60*24*30).toISOString();
const toISO   = process.env.TO   || new Date().toISOString();

function buildUrl(nextUrl = null) {
  if (nextUrl) return nextUrl; // pagination.next may be absolute
  const u = new URL(`${API_BASE}/house/roll-call-votes`);
  u.searchParams.set("fromDateTime", fromISO);
  u.searchParams.set("toDateTime", toISO);
  u.searchParams.set("format", "json");
  u.searchParams.set("limit", "250");
  return u.toString();
}

async function fetchAllVotes() {
  let url = buildUrl();
  const all = [];
  const seen = new Set();

  while (url) {
    const res = await fetch(url, { headers: { "X-Api-Key": API_KEY } });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status} ${url}\n${text}`);
    }
    const json = await res.json();

    const items = json?.votes ?? json?.results ?? json?.data ?? [];
    for (const v of items) {
      const key = v?.rollCallNumber
        ? `${v.congress}-${v.session}-${v.rollCallNumber}`
        : JSON.stringify(v).slice(0,200);
      if (!seen.has(key)) { seen.add(key); all.push(v); }
    }

    let next = json?.pagination?.next || null;
    if (next && !next.startsWith("http")) {
      const u = new URL(next, API_BASE);
      next = u.toString();
    }
    url = next;
  }
  return all;
}

(async () => {
  try {
    const votes = await fetchAllVotes();
    await fs.mkdir("data", { recursive: true });
    await fs.writeFile("data/votes.json", JSON.stringify(votes, null, 2));
    console.log(`✅ Pulled ${votes.length} votes → data/votes.json`);
  } catch (err) {
    console.error(`❌ pull-votes failed: ${err.message}`);
    process.exit(1);
  }
})();
