/**
 * Cloudflare Worker (แนะนำ) สำหรับรับ LINE webhook แล้วอัปเดต data/today.json ใน GitHub repo
 *
 * ENV vars (Cloudflare):
 * - LINE_CHANNEL_SECRET
 * - GH_PAT
 * - GH_OWNER
 * - GH_REPO
 * - GH_BRANCH (optional, default: main)
 *
 * NOTE: ตัวนี้ทำแบบ MVP: ใช้ LINE user เดียว ไม่แยกหลาย user
 */
import { createHmac } from 'node:crypto';

function base64ToArrayBuffer(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes.buffer;
}

async function verifySignature(request, secret) {
  const body = await request.clone().text();
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  const sigB64 = btoa(String.fromCharCode(...new Uint8Array(sig)));
  const headerSig = request.headers.get("x-line-signature");
  return headerSig === sigB64;
}

async function ghGetFile(env, path) {
  const branch = env.GH_BRANCH || "main";
  const url = `https://api.github.com/repos/${env.GH_OWNER}/${env.GH_REPO}/contents/${path}?ref=${branch}`;
  const res = await fetch(url, {
    headers: {
      "Authorization": `Bearer ${env.GH_PAT}`,
      "Accept": "application/vnd.github+json",
      "User-Agent": "money-line-bot"
    }
  });
  if (!res.ok) throw new Error(`GitHub GET failed: ${res.status} ${await res.text()}`);
  return await res.json();
}

async function ghPutFile(env, path, contentText, sha, message) {
  const branch = env.GH_BRANCH || "main";
  const url = `https://api.github.com/repos/${env.GH_OWNER}/${env.GH_REPO}/contents/${path}`;
  const contentB64 = btoa(unescape(encodeURIComponent(contentText)));
  const body = {
    message,
    content: contentB64,
    sha,
    branch
  };
  const res = await fetch(url, {
    method: "PUT",
    headers: {
      "Authorization": `Bearer ${env.GH_PAT}`,
      "Accept": "application/vnd.github+json",
      "User-Agent": "money-line-bot",
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error(`GitHub PUT failed: ${res.status} ${await res.text()}`);
  return await res.json();
}

function parseFirstInt(text) {
  const m = text.match(/-?\d+/);
  if (!m) return null;
  return Math.abs(parseInt(m[0], 10));
}

function isBudget(text) {
  return text.includes("งบ");
}

function isClear(text) {
  const t = text.trim().toLowerCase();
  return t === "ล้าง" || t === "clear" || t === "reset";
}

function ictDateStr() {
  const now = new Date();
  // ICT = UTC+7
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const ict = new Date(utc + 7 * 3600000);
  const y = ict.getFullYear();
  const m = String(ict.getMonth() + 1).padStart(2, "0");
  const d = String(ict.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

export default {
  async fetch(request, env) {
    if (request.method !== "POST") return new Response("OK", { status: 200 });

    // verify signature (recommended)
    if (env.LINE_CHANNEL_SECRET) {
      const ok = await verifySignature(request, env.LINE_CHANNEL_SECRET);
      if (!ok) return new Response("Bad signature", { status: 401 });
    }

    const payload = await request.json();
    const events = payload.events || [];
    const msgTexts = events
      .filter(e => e.type === "message" && e.message && e.message.type === "text")
      .map(e => e.message.text);

    if (msgTexts.length === 0) return new Response("No text", { status: 200 });

    // load today.json from GitHub
    const file = await ghGetFile(env, "data/today.json");
    const decoded = decodeURIComponent(escape(atob(file.content.replace(/\n/g, ""))));
    let state = JSON.parse(decoded);

    const today = ictDateStr();
    if (state.date !== today) state = { date: today, budget: 0, items: [] };

    for (const text of msgTexts) {
      if (isClear(text)) {
        state.items = [];
        continue;
      }
      if (isBudget(text)) {
        const b = parseFirstInt(text);
        if (b !== null) state.budget = b;
        continue;
      }
      const amt = parseFirstInt(text);
      if (amt === null) continue;
      state.items.push({ text, amount: amt });
    }

    await ghPutFile(env, "data/today.json", JSON.stringify(state, null, 2), file.sha, "Update today.json from LINE");
    return new Response("OK", { status: 200 });
  }
};
