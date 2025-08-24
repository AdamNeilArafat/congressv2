// scripts/pull-votes.mjs
import fs from "node:fs/promises";

const API_KEY = process.env.CONGRESS_API_KEY;
if (!API_KEY) {
  console.error("❌ Missing CONGRESS_API_KEY");
  process.exit(1);
}

// Congress.gov recommends using the api.data.gov proxy for authenticated calls
// Ref: https://www.loc.gov/apis/additional-apis/congress-dot-gov-api/
const API_BASE = "https://api.data.gov/congress/v3";

// House roll call votes endpoints were added in 2025 (beta → enhanced).
// We’ll use the list endpoint and follow pagination.next.
// Blog refs: May 13, 2025; Aug 4, 2025. 
// https://blogs.loc.gov/law/2025/05/introducing-house-roll-call-votes-in-the-congress-gov-api/
// https://blogs.loc.gov/law/2025/08/congress-gov-enhanced-access-to-house-roll-call-votes-is-now-available/

const fromISO = process.env.FROM || new Date(Date.now() - 1000*60*60*24*30).toISOString(); // default last 30 days
const toISO   = process.env.TO   || new Date().toISOString();

function buildUrl(url = null) {
  if (url) return url; // already a fully-qualified pagination.next URL
  const u = new URL(`${API_BASE}/house/roll-call-votes`);
  u.searchParams.set("fromDateTime", fromISO);
  u.searchParams.set("toDateTime", toISO);
  u.searchParams.set("format", "json");
  u.searchParams.set("limit", "250");
  u.searchParams.set("api_key", API_KEY);     // ✅ only api_key — no authkey
  return u.toString();
}

async function fetchAllVotes() {
  let url = buildUrl();
  const all = [];
  const seen = new Set();

  while (url) {
    const res = await fetch(url, { redirect: "follow" });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`HTTP ${res.status} on ${url}\n${text}`);
    }
    const json = await res.json();

    // Normalize where items live; adjust if schema differs
    const items = json?.votes ?? json?.results ?? json?.data ?? [];
    for (const v of items) {
      // de-dupe by a stable key if present
      const key = v?.rollCallNumber
        ? `${v.congress}-${v.session}-${v.rollCallNumber}`
        : JSON.stringify(v).slice(0,200);
      if (!seen.has(key)) {
        seen.add(key);
        all.push(v);
      }
    }

    // Follow pagination.next (exact field name per API docs)
    url = json?.pagination?.next || null;
    // Ensure next carries api_key if API returns bare URL
    if (url && !url.includes("api_key=")) {
      const u = new URL(url);
      u.searchParams.set("api_key", API_KEY);
      url = u.toString();
    }
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
