#!/usr/bin/env node
import fs from "node:fs/promises";
import { createWriteStream } from "node:fs";
import fetch from "node-fetch";
import zlib from "node:zlib";
import { pipeline } from "node:stream/promises";
import { HttpsProxyAgent } from "https-proxy-agent";

// Download combined House and Senate member ideology scores from Voteview.
const SRC = "https://voteview.com/static/data/out/members/HSall_members.csv.zip";

const proxy = process.env.https_proxy || process.env.http_proxy;
const agent = proxy ? new HttpsProxyAgent(proxy) : undefined;

try {
  const res = await fetch(SRC, { agent });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  await fs.mkdir("data", { recursive: true });
  const file = createWriteStream("data/voteview_members.csv");
  await pipeline(res.body, zlib.createUnzip(), file);
  console.log("✅ wrote data/voteview_members.csv");
} catch (e) {
  console.error("❌ pull-voteview failed:", e.message || e);
  process.exit(1);
}
