#!/usr/bin/env node
// Runtime estimator for screenplays written in the drama-writer template format.
// Usage: node scripts/estimate-runtime.mjs <file.md | -> [--lang en|es|id|ms|other] [--target 75] [--json]
//        ("-" reads the screenplay from stdin)
// No dependencies. Numbers mirror references/runtime-timing.md; it is a planning aid, not a measurement.
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

export const LATIN_WORDS_PER_SEC = { en: 2.5, es: 2.6, id: 2.2, ms: 2.2, other: 2.4 };
export const CJK_UNITS_PER_SEC = { zh: 4.0, ja: 5.0, ko: 5.0 };

const DELIVERY = [
  { re: /cry|crying|sob|tears|choked|menangis|哭|울/i, factor: 1.4 },
  { re: /whisper|soft|quiet|murmur|berbisik|pelan|小声|低声|속삭/i, factor: 1.15 },
  { re: /nervous|hesita|stammer|stutter|unsure|ragu|gugup/i, factor: 1.15 },
  { re: /cold|slow|deliberate|menac|flat|dingin|pelan-pelan/i, factor: 1.1 },
  { re: /shout|yell|scream|angr|furious|teriak|marah|喊|소리/i, factor: 0.9 },
  { re: /excit|rush|panic|fast|quick|buru/i, factor: 0.85 },
];
const NONVERBAL = [
  { re: /^(long pauses?|silence|long beat|hening)$/i, add: 2.0 },
  { re: /^(pauses?|beat|jeda)$/i, add: 0.8 },
  { re: /sigh|menghela/i, add: 0.8 },
  { re: /laugh|chuckle|giggle|tertawa|笑|웃/i, add: 1.0 },
  { re: /gasp/i, add: 0.4 },
  { re: /sob|crying|menangis/i, add: 0.5 },
];
const CUE_PICKUP = 0.3;
const ELLIPSIS = 0.35;
const LONG_LINE_SEC = 8;

const META_KEYS = new Set([
  "cast", "characters", "setting", "location", "time", "language", "target", "format", "camera", "shot", "audio", "sfx",
  "music", "continuity", "props", "prop", "wardrobe", "notes", "note", "transition", "duration", "subject", "light",
  "lighting", "hook", "objective", "episode", "genre", "tone", "runtime", "estimated runtime", "start", "end",
  "start state", "end state", "ending beat", "logline", "title", "vo", "on-screen text", "text", "overlay", "frame",
  "present", "in the room", "on screen",
  // Localized labels for cast, setting, time and notes.
  "出场", "出場", "登场", "登場", "人物", "角色", "地点", "场景", "場景", "时间", "時間", "备注", "說明", "说明",
  "등장", "등장인물", "장소", "시간", "메모", "場所", "メモ", "キャスト",
  "pemeran", "tokoh", "lokasi", "waktu", "catatan", "presentes", "personajes", "reparto", "lugar", "notas",
]);

const NAME_RE = /^\s*(?:\*\*)?((?:\p{Lu}[\p{Lu}\p{M}0-9 .'’\-]*[\p{Lu}0-9.])|\p{Lu}|(?:[^\p{Script=Latin}\s\p{P}\p{S}\d]{1,12}(?:[·・ ][^\p{Script=Latin}\s\p{P}\p{S}\d]{1,8})?))(?:\*\*)?\s*(?:[(（]([^)）]*)[)）])?\s*(?:\*\*)?\s*[:：]\s*(?:\*\*)?\s*(.+)$/u;
const SCENE_HEADING_RE = /^##\s+(?:S\d+\b|.*\b(?:INT|EXT|I\/E|INT\.?\/EXT)\b|.*(?:内景|外景|內景|실내|실외|室内|屋外))/iu;
const SHOT_HEADING_RE = /^###\s+(.+)$/;
const DURATION_RE = /(\d+(?:\.\d+)?)\s*(?:s|sec|secs|seconds|detik|秒|초)(?![A-Za-z])/i;

function countScripts(text) {
  return {
    hangul: (text.match(/\p{Script=Hangul}/gu) ?? []).length,
    kana: (text.match(/[\p{Script=Hiragana}\p{Script=Katakana}]/gu) ?? []).length,
    han: (text.match(/\p{Script=Han}/gu) ?? []).length,
    latinWords: (text.replace(/[\p{Script=Han}\p{Script=Hangul}\p{Script=Hiragana}\p{Script=Katakana}]/gu, " ").match(/[\p{L}\p{N}][\p{L}\p{N}'’\-]*/gu) ?? []).length,
  };
}

/** Seconds to speak `text` (tags already removed) at neutral pace. */
export function speechSeconds(text, lang = "en") {
  const c = countScripts(text);
  const latinRate = LATIN_WORDS_PER_SEC[lang] ?? LATIN_WORDS_PER_SEC.other;
  let secs = c.latinWords / (c.hangul + c.kana + c.han > 0 ? LATIN_WORDS_PER_SEC.en : latinRate);
  if (c.hangul > 0 && c.hangul >= c.han) secs += (c.hangul + c.han) / CJK_UNITS_PER_SEC.ko;
  else if (c.kana > 0) secs += (c.kana + c.han) / CJK_UNITS_PER_SEC.ja;
  else if (c.han > 0) secs += c.han / CJK_UNITS_PER_SEC.zh;
  return secs;
}

function detectScriptLanguage(text) {
  const c = countScripts(text);
  if (c.hangul > 0 && c.hangul >= c.han) return "ko";
  if (c.kana > 0) return "ja";
  if (c.han > 0) return "zh";
  return "latin";
}

/** Time for a dialogue line, including tags, parenthetical delivery, and pauses. */
export function estimateLine(rawText, parenthetical = "", lang = "en") {
  const tags = [...rawText.matchAll(/\[([^\]]+)\]/g)].map((m) => m[1].trim());
  if (parenthetical) tags.unshift(parenthetical.trim());
  const spoken = rawText.replace(/\[[^\]]*\]/g, " ").replace(/\*\*/g, "").trim();
  let factor = 1;
  let extra = 0;
  for (const tag of tags) {
    const nv = NONVERBAL.find((n) => n.re.test(tag));
    if (nv) extra += nv.add;
    const d = DELIVERY.find((x) => x.re.test(tag));
    if (d && factor === 1) factor = d.factor; // first delivery tag wins
  }
  const ellipses = (spoken.match(/\.\.\.|…+/g) ?? []).length;
  // A trailing ellipsis or dash ends the line; it doesn't add a mid-line hesitation.
  const midEllipses = Math.max(0, ellipses - (/(\.\.\.|…+)\s*$/.test(spoken) ? 1 : 0));
  const speech = speechSeconds(spoken, lang) * factor;
  return { speech, pauses: extra + midEllipses * ELLIPSIS, total: speech + extra + midEllipses * ELLIPSIS, spoken, tags };
}

export function estimateAction(text) {
  const c = countScripts(text);
  const words = c.latinWords + Math.ceil((c.han + c.kana + c.hangul) / 3);
  return Math.min(6, 1.2 + Math.max(0, words - 6) * 0.15);
}

/**
 * Parse a screenplay and estimate its runtime.
 * Counting starts at the first scene heading (## S01 ..., ## INT. ...) and pauses at any other ## heading.
 */
export function estimateScript(text, opts = {}) {
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  let lang = opts.lang;
  if (!lang) {
    const m = /^\s*(?:\*\*)?(?:Language|Bahasa|Idioma|Langue|Sprache)(?:\*\*)?\s*:\s*\*?\*?\s*([A-Za-z]{2})/im.exec(text);
    lang = m ? m[1].toLowerCase() : "en";
  }
  const scenes = [];
  const warnings = [];
  let scene = null;
  let shot = null;
  let lastSpeaker = null;

  const newBucket = (title) => ({ title, speech: 0, action: 0, pauses: 0, lines: 0, words: 0 });

  for (const raw of lines) {
    const line = raw.trim();
    if (line.startsWith("## ") || line.startsWith("# ")) {
      if (SCENE_HEADING_RE.test(line)) {
        scene = { ...newBucket(line.replace(/^#+\s*/, "")), shots: [] };
        scenes.push(scene);
      } else {
        scene = null;
      }
      shot = null;
      lastSpeaker = null;
      continue;
    }
    if (!scene) continue;
    const sh = SHOT_HEADING_RE.exec(line);
    if (sh) {
      const d = DURATION_RE.exec(sh[1]);
      shot = { ...newBucket(sh[1]), stated: d ? Number(d[1]) : undefined };
      scene.shots.push(shot);
      continue;
    }
    // A horizontal rule closes the screenplay section; notes and tables after it don't count.
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(line)) {
      scene = null;
      shot = null;
      continue;
    }
    if (line === "" || line.startsWith(">") || line.startsWith("|") || line.startsWith("<!--") || line.startsWith("```")) continue;
    const bucket = shot ?? scene;

    const metaKey = /^\s*(?:[-*]\s*)?(?:\*\*)?([A-Za-z][A-Za-z\- ]{0,20})(?:\*\*)?\s*:/.exec(line);
    if (metaKey && META_KEYS.has(metaKey[1].trim().toLowerCase())) continue;

    const dl = NAME_RE.exec(line);
    if (dl && META_KEYS.has(dl[1].trim().toLowerCase())) continue;
    if (dl) {
      const speaker = dl[1].trim();
      const est = estimateLine(dl[3], dl[2] ?? "", lang);
      const pickup = lastSpeaker && lastSpeaker !== speaker ? CUE_PICKUP : 0;
      bucket.speech += est.speech;
      bucket.pauses += est.pauses + pickup;
      bucket.lines += 1;
      bucket.words += countScripts(est.spoken).latinWords;
      lastSpeaker = speaker;
      if (est.total > LONG_LINE_SEC) {
        warnings.push(`${scene.title.split(" ")[0]} ${speaker}: line runs ~${est.total.toFixed(1)} s ("${est.spoken.slice(0, 40)}${est.spoken.length > 40 ? "…" : ""}"). Consider splitting it with a reaction or action.`);
      }
      continue;
    }
    // Bold labels ("**Ending beat:** ...", "**Runtime breakdown**") are notes, not action.
    if (/^\*\*[^*]+\*\*/.test(line)) continue;
    // Everything else inside a scene is an action/description beat.
    const stripped = line.replace(/^[-*]\s+/, "").replace(/\*\*/g, "");
    const explicit = /^\(?\s*(\d+(?:\.\d+)?)\s*(?:s|sec|seconds)\s*\)?/i.exec(stripped);
    bucket.action += explicit ? Number(explicit[1]) : estimateAction(stripped);
  }

  let total = 0;
  const sceneReports = scenes.map((s) => {
    let sceneTotal = s.speech + s.action + s.pauses;
    const shotReports = s.shots.map((sh) => {
      const content = sh.speech + sh.action + sh.pauses;
      const needed = sh.speech + sh.pauses;
      // A shot can't be shorter than the dialogue inside it.
      const time = sh.stated === undefined ? content : Math.max(sh.stated, needed);
      if (sh.stated !== undefined && needed > sh.stated + 0.25) {
        warnings.push(`${sh.title.split(/\s/)[0]}: dialogue needs ~${needed.toFixed(1)} s but the shot is ${sh.stated} s.`);
      }
      return { title: sh.title, seconds: round(time), stated: sh.stated, speech: round(sh.speech), lines: sh.lines };
    });
    sceneTotal += shotReports.reduce((n, r) => n + r.seconds, 0);
    total += sceneTotal;
    const speech = s.speech + s.shots.reduce((n, x) => n + x.speech, 0);
    const lineCount = s.lines + s.shots.reduce((n, x) => n + x.lines, 0);
    return { title: s.title, seconds: round(sceneTotal), speech: round(speech), lines: lineCount, shots: shotReports };
  });

  const result = {
    lang,
    seconds: round(total),
    low: round(total * 0.85),
    high: round(total * 1.15),
    speechSeconds: round(sceneReports.reduce((n, s) => n + s.speech, 0)),
    dialogueLines: sceneReports.reduce((n, s) => n + s.lines, 0),
    scenes: sceneReports,
    warnings,
  };
  if (opts.target) {
    const t = Number(opts.target);
    const diff = total - t;
    result.target = t;
    result.verdict = Math.abs(diff) <= t * 0.1 ? "on target" : diff > 0 ? `over by ~${Math.round(diff)} s` : `under by ~${Math.round(-diff)} s`;
  }
  if (!scenes.length) warnings.push("No scene headings found (expected lines like '## S01 - INT. KITCHEN - NIGHT').");
  return result;
}

function round(n) {
  return Math.round(n * 10) / 10;
}

export { detectScriptLanguage };

function formatReport(r) {
  const out = [];
  out.push(`Estimated runtime: ${r.seconds} s (likely ${r.low}–${r.high} s)${r.target ? `, target ${r.target} s: ${r.verdict}` : ""}`);
  out.push(`Spoken: ~${r.speechSeconds} s across ${r.dialogueLines} line(s). Latin-script rate: ${r.lang}.`);
  for (const s of r.scenes) {
    out.push(`  ${s.title}: ${s.seconds} s (${s.lines} line(s), speech ~${s.speech} s)`);
    for (const sh of s.shots) out.push(`    ${sh.title}: ${sh.seconds} s${sh.stated === undefined ? " (estimated)" : ""}`);
  }
  if (r.warnings.length) {
    out.push("Notes:");
    for (const w of r.warnings) out.push(`  - ${w}`);
  }
  return out.join("\n");
}

function main(argv) {
  const args = { json: false };
  const files = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--json") args.json = true;
    else if (a === "--lang") args.lang = argv[++i];
    else if (a === "--target") args.target = argv[++i];
    else if (a === "-h" || a === "--help") {
      console.log("Usage: node estimate-runtime.mjs <file.md | -> [--lang en|es|id|ms|other] [--target seconds] [--json]\n  Use - to read the screenplay from stdin.");
      return 0;
    } else files.push(a);
  }
  // "-" (or no file with piped input) reads the screenplay from stdin, so no temp file is needed.
  const fromStdin = files[0] === "-" || (files.length === 0 && !process.stdin.isTTY);
  if (!fromStdin && files.length !== 1) {
    console.error("Give one screenplay file, or '-' to read from stdin. --help for usage.");
    return 2;
  }
  const r = estimateScript(readFileSync(fromStdin ? 0 : files[0], "utf8"), args);
  console.log(args.json ? JSON.stringify(r, null, 2) : formatReport(r));
  return 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) process.exitCode = main(process.argv.slice(2));
