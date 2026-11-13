# Runtime and dialogue timing

## Contents
1. Why word count is not enough
2. Speech rates by language
3. Delivery modifiers
4. Non-speech time
5. Method: budgeting an episode
6. Using the estimator script
7. Cutting to fit

## 1. Why word count is not enough

Screen time = spoken time + reaction time + pauses + action + transitions. A 90-word scene can run 25 seconds as a rapid-fire argument or 60 seconds as a halting confession with long looks. Different languages also fill time differently: a Korean or Japanese line has a different number of "words" than its English equivalent, so word counts don't compare across languages.

## 2. Speech rates by language

Approximate rates for natural drama delivery (slower than fast conversation, faster than formal narration). Use the unit that matches the language.

| Language | Unit | Neutral drama pace |
|---|---|---|
| English | words | ~2.5 / s (≈150 wpm) |
| Spanish | words | ~2.6 / s |
| Indonesian / Malay | words | ~2.2 / s (longer words on average) |
| Other Latin-script languages (default) | words | ~2.4 / s |
| Mandarin Chinese | characters (each ≈ one syllable) | ~4.0 / s |
| Japanese | kana + kanji characters | ~5.0 / s |
| Korean | Hangul syllable blocks | ~5.0 / s |

These are planning numbers, not measurements of any particular actor or voice. Real delivery varies ±20% or more with the speaker, emotion, and TTS voice.

## 3. Delivery modifiers

Multiply the spoken time of a line by:

| Delivery | Factor |
|---|---|
| Whispered, soft, quiet | ×1.15 |
| Hesitant, nervous, stammering | ×1.15 |
| Cold, slow, deliberate, menacing | ×1.1 |
| Crying, through tears, choked | ×1.4 |
| Shouting, angry outburst | ×0.9 |
| Excited, rushed, panicked | ×0.85 |

## 4. Non-speech time

| Element | Add |
|---|---|
| `[pause]` or `[beat]` | ~0.8 s |
| `[long pause]` or `[silence]` | ~2 s |
| `[sighs]` | ~0.8 s |
| `[laughs]` | ~1 s |
| `[gasps]` | ~0.4 s |
| Ellipsis inside a line (hesitation) | ~0.35 s each |
| Speaker change (cue pickup) | ~0.3 s |
| Action line (a visible beat) | ~1.2 s, plus ~0.15 s per word after the first six (cap ~6 s) |
| Held reaction after a reveal | 1–2 s (write it as an action line) |
| Insert shot (phone screen, letter) | 1.5–3 s, long enough to read |

If shots carry explicit durations (production mode), the total runtime is the sum of shot durations, and the job is to check that each shot's dialogue fits inside it.

## 5. Method: budgeting an episode

1. Start from the target (e.g. 75 s).
2. Reserve non-dialogue time: hook image (1–3 s), held reactions (2–4 s total), action beats, ending image (2–3 s). In a 75-second episode, 20–35 s often goes to non-dialogue moments.
3. The remainder is the speech budget. At ~2.5 words/s (English), 45 s of speech ≈ 110 words.
4. Write. Then estimate each line: units ÷ rate × delivery factor + tags and pauses.
5. Add it up with action and reactions. Report the estimate as a range (±15%).
6. If over, cut (section 7). If far under, check the story has room to breathe rather than padding with dialogue.

Example (English): `MAYA: [quietly] You signed it. Before you even asked me.` → 8 words ÷ 2.5 = 3.2 s × 1.15 (quiet) ≈ 3.7 s, plus 0.3 s cue pickup ≈ 4 s.

## 6. Using the estimator script

When code execution is available, the bundled script checks scripts written in the `templates/screenplay.md` format:

```
node scripts/estimate-runtime.mjs episode.md --lang id --target 75
```

- `--lang` sets the rate for Latin-script text (en, es, id, ms, other). CJK and Hangul are detected per line automatically.
- `--target` (seconds) adds a pass/fail line against the target.
- `--json` prints machine-readable output.
- Use `-` instead of a file name to read the script from stdin (useful when you can't write files): `node scripts/estimate-runtime.mjs - --target 60 <<'EOF'` … `EOF`.
- It reports per-scene and per-shot times, flags long single lines (over ~8 s), and flags shots whose dialogue exceeds their stated duration.

It uses the same numbers as this file. It is a cross-check, not a substitute for judgement; read the script aloud in your head as well.

## 7. Cutting to fit

Cut in this order:
1. Lines that repeat information the audience already has.
2. Exposition that the visuals already deliver.
3. Politeness padding, greetings, and filler.
4. Second and third tactics in a scene that already turned.
5. Secondary threads, if the episode can survive without them.

Protect:
- The held reaction after the key reveal.
- The line that hurts most.
- The ending image.

When a single line runs long (over ~8 seconds), split it with a reaction, an interruption, or an action, or put part of it over the listener's face.
