// scripts/pull-votes.mjs
import fs from "node:fs/promises";
import path from "node:path";

// Uses Congress.gov API (needs api.data.gov key)
// https://api.congress.gov/#/roll-call-vote/getV3RollCallVoteCongressChamberSessionRollCallNumber
const API_KEY = process.env.CONGRESS_API_KEY;
if (!API_KEY) {
  console.error("CONGRESS_API_KEY env var is required (api.data.gov key).");
  process.exit(1);
}

const VOTES_PATH = path.resolve("data/votes.json");
const nowIso = () => new Date().toISOString();

const norm = (s="") => s.toString().trim().toLowerCase();
const YES = new Set(["yea","aye","yes","y"]);
const NO  = new Set(["nay","no","n"]);
const PRESENT = new Set(["present","not voting","nv","present, giving live pair"]);

function normalizeVoteLabel(v) {
  const x = norm(v);
  if (YES.has(x)) return "yea";
  if (NO.has(x))  return "nay";
  if (PRESENT.has(x)) return "present";
  return x || "unknown";
}

function offendersMatcher(config) {
  // offenders_vote can be "no" | "nay" | "yea" | ["no","nay"] etc.
  const arr = Array.isArray(config) ? config : [config];
  const want = new Set(arr.map(normalizeVoteLabel));
  return (actualVote) => want.has(normalizeVoteLabel(actualVote));
}

async function fetchRollCall({congress, chamber, session, roll}) {
  const url = `https://api.congress.gov/v3/roll-call-vote/${congress}/${chamber}/${session}/${roll}?api_key=${API_KEY}`;
  const r = await fetch(url, { headers: { "accept": "application/json" }});
  if (!r.ok) throw new Error(`HTTP ${r.status} for ${url}`);
  const j = await r.json();

  // Congress.gov shape (as of 2024/2025):
  // j.rollCallVote.members.member[] with fields: bioguideId, voteCast, ...
  const members =
    j?.rollCallVote?.members?.member
    || j?.rollCallVote?.members      // sometimes already an array
    || j?.results?.votes?.vote?.positions
    || [];

  // Map into a simple { bio, vote }
  return members
    .map(m => {
      const bio = m.bioguideId || m.bioguide_id || m.member_id || m.id;
      const vote = m.voteCast || m.vote_position || m.vote || m.position || m?.["@attributes"]?.vote;
      return bio ? { bioguide: bio, vote: vote || "" } : null;
    })
    .filter(Boolean);
}

async function main() {
  // 1) load current file
  const raw = await fs.readFile(VOTES_PATH, "utf8").catch(()=> "{}");
  const votes = JSON.parse(raw || "{}");

  let touched = 0;

  // 2) iterate each vote that has an rc pointer
  for (const [key, item] of Object.entries(votes)) {
    const rc = item.rc;
    if (!rc || !rc.congress || !rc.session || !rc.chamber || !rc.roll) {
      // no rollcall pointer → skip
      continue;
    }

    console.log(`→ ${key}: fetching roll call ${rc.chamber} ${rc.congress}-${rc.session} #${rc.roll}`);
    let roster;
    try {
      roster = await fetchRollCall(rc);
    } catch (e) {
      console.error(`   FAILED to fetch: ${e.message}`);
      continue;
    }

    const isOffender = offendersMatcher(item.offenders_vote || ["no","nay"]);
    const offenders = roster
      .filter(r => isOffender(r.vote))
      .map(r => ({ bioguide: r.bioguide, vote: r.vote.toUpperCase() }));

    // write back offenders + a couple nice-to-have fields
    item.offenders = offenders;
    item.updatedAt = nowIso();
    // Optional: add a public vote URL (nice for debugging)
    if (rc.chamber === "senate") {
      const pad = String(rc.roll).padStart(5, "0");
      item.vote_url = `https://www.senate.gov/legislative/LIS/roll_call_votes/vote${rc.congress}${rc.session}/vote_${rc.congress}_${rc.session}_${pad}.htm`;
    } else if (rc.chamber === "house") {
      // Clerk uses year-based URLs; Congress/session→year is approximate, so omit if unsure.
      item.vote_url = `https://api.congress.gov/v3/roll-call-vote/${rc.congress}/${rc.chamber}/${rc.session}/${rc.roll}`;
    }

    votes[key] = item;
    console.log(`   offenders: ${offenders.length}`);
    touched++;
  }

  // 3) save file (pretty)
  if (touched) {
    await fs.writeFile(VOTES_PATH, JSON.stringify(votes, null, 2));
    console.log(`✅ Updated ${touched} vote(s) in ${VOTES_PATH}`);
  } else {
    console.log("No votes updated.");
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
