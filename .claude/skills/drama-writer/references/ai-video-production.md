# Writing for AI video generation

Load for production-ready screenplays (Workflow D), shot lists, or whenever the user says the script will become AI-generated video.

## Contents
1. What changes when the "camera" is a generator
2. Staging that generates well
3. What to be careful with
4. Character and world consistency
5. Simplify the execution, keep the moment
6. Dialogue and lip-sync
7. Shot descriptions for generation handoff
8. Production checklist

Generators change quickly. The guidance below describes limitations common across current text- and image-to-video systems; when the user names a specific tool, ask about or follow its constraints (clip length, aspect ratio, reference-image support, audio).

## 1. What changes when the "camera" is a generator

- Each shot is often generated separately, as a short clip (commonly a few seconds to around ten). Long continuous takes are expensive and drift.
- The generator does not remember the previous shot unless given references: the same face, outfit, and set must be re-described or re-referenced every time.
- Precise, small physical interactions (hands with objects, contact between people) are where artefacts appear most.
- Each shot is effectively a prompt: it needs subject, action, setting, framing, light, and mood stated plainly.

## 2. Staging that generates well

- **One or two characters per shot.** Cover group scenes with singles and pairs, cut together.
- **One main action per shot**, with a clear start and end state ("she turns her head toward the door").
- **One camera behaviour per shot**: static, slow push-in, slow pan, handheld drift. Not a crane plus a zoom plus a whip-pan.
- **Readable faces and silhouettes**, in medium and close shots.
- **Simple, stable environments**: a kitchen, a corridor, a car interior, an office at night.
- **Clear lighting setups** described once per scene and repeated (warm lamp, cold window light, neon at night).
- **Reaction shots and inserts** carry emotion and information cheaply and reliably.
- **Stillness**: a held look, a slow breath, a tear forming; generators often do subtle stillness better than complex motion.

## 2b. Keep the hook, escalation and ending when the script becomes shots

Splitting a good script into clips often flattens it: the opening becomes an establishing shot, context lives in lines the viewer cannot lip-sync, and the last clip is a reaction that releases the tension. Prevent this.

- **Shot 1 is the hook image**, close on the person, object or anomaly (the signed certificate, the wrong floor number, the cufflink), not a wide of the location. Put the conflict in the first 2 to 3 seconds.
- **Orientation in the first 5 to 8 seconds**: who the lead is, who they face, their relation, and who holds power, using visible markers (uniform, car, logo, ring, seating) and a short caption when needed. A cold viewer should pass the cold-viewer test in `hooks-and-cliffhangers.md` §3 with sound off.
- **Story-critical information goes into the frame**: evidence as an insert with short, large text overlaid in editing (see §3), not as a spoken explanation.
- **One new fact or pressure every 10 to 20 seconds.** If three shots in a row show the same emotion, replace one with an escalation: a new arrival, a revealed object, a closed exit.
- **The double-duty detail** (the prop or mark planted early and reinterpreted at the end) gets its own insert shot both times, framed identically so the viewer recognises it.
- **The last shot is the ending image**, cut on the inhale: the doors opening, the card slot lighting, the call connecting. Do not append a closing reaction that resolves the tension.
- When writing the shot-prompt handoff, include the episode brief's hook, double-duty detail, final image and next-episode question in a header so every clip is generated toward the same turn.

## 3. What to be careful with

| Risky | Why | Safer execution |
|---|---|---|
| Many characters interacting at once | Identity drift, merging, extra limbs | Cut between singles/pairs; keep the group in a brief wide shot |
| Complex hand movements (typing, signing, tying, handing small objects) | Hands and fingers deform | Show the result (the signed page), or frame on faces; use a single simple grip |
| Multiple interacting props | Objects morph or swap | One key prop per shot; establish it in an insert |
| Complicated choreography (fights, dances, chases) | Physics and continuity break | Break into impact moments, reactions, and aftermath |
| Rapid physical transformation (injury appearing, costume change on screen) | Inconsistent results | Cut away and back; show the after-state |
| Long continuous actions (cooking a whole dish, walking a long route) | Drift and loops | Compress with cuts: start, detail, end state |
| Several simultaneous camera moves | Unstable motion | One move per shot |
| Complex environmental change (storm arriving, fire spreading) | Hard to control | Show the effect on people; sound design; cut to the result |
| Legible text in the frame | Text often renders garbled | Keep on-screen text short; plan to add messages and documents as overlays in editing |
| Mirrors, reflections, glass | Inconsistent reflections | Avoid unless essential; then keep simple |
| Physical contact (hugs, slaps, kisses) | Faces/limbs merge | Frame tight on one face at contact, or show just before and after |
| Liquids pouring, eating | Unnatural motion | Insert shots of results; brief, simple motions |

## 4. Character and world consistency

- Keep a **visual reference sheet** per recurring character in the bible: age, build, face features, hair, a signature wardrobe item, colour palette. Reuse the same wording in every shot description.
- Keep wardrobe constant within a scene, and note changes between scenes explicitly.
- Fix **recurring sets**: describe layout and key furnishings once and reuse the description.
- Avoid near-duplicate characters (two young men in white shirts) in the same scenes; differentiate visually.
- Note time of day and light per scene; reuse it.
- If the user's tool supports reference images or character IDs, say where they should be used.

## 5. Simplify the execution, keep the moment

Never drop an important story moment just because it is hard to generate. Find a simpler way to show it:
- **The slap**: the hand rising (wide), the sound and the head turning (close), the red mark and the silence (reaction).
- **The car crash**: headlights flaring through the windshield, a hard cut to black with sound, then the shattered phone on the road.
- **The proposal in a crowded restaurant**: tight on the ring box; the woman's face; the room's silence suggested through one or two reaction shots.
- **The fight**: a shove, the aftermath, one character on the floor touching their lip.

## 6. Dialogue and lip-sync

- Dialogue often requires separate TTS and lip-sync steps. Short lines are easier to sync and to fit within a single generated clip.
- Put long lines over a reaction shot or the listener's face (off-screen speech is easier than lip-sync).
- Voice-over and phone-call audio avoid lip-sync entirely; use them where the story allows, not as a crutch.
- Keep a line within one shot where possible; if it spans a cut, mark it (the line continues over the reaction).

## 7. Shot descriptions for generation handoff

When the user wants shot prompts, give each shot:

```
S03-02 · CLOSE-UP · ~3s
Subject: MIRA (30s, sharp black bob, charcoal coat) seated at the kitchen table, facing camera-left.
Action: her eyes move from the letter in her left hand up to someone off-screen right. Her jaw sets.
Setting: small apartment kitchen, night, single warm pendant light, rain on the window behind her.
Camera: static, eye level, shallow depth of field.
Audio: rain; fridge hum. Dialogue: none.
Continuity: letter in LEFT hand, coat still on, untouched tea on table.
```

Write in the user's preferred language for prompts (many tools work best with English prompts; ask if unsure), keeping dialogue in the screenplay language.

Do not include tool-specific parameters unless the user names the tool and you know its format.

## 8. Production checklist

- Each shot: one or two characters, one main action, one camera behaviour.
- Character descriptions repeated consistently.
- Key props introduced with an insert and tracked.
- Hard physical moments simplified into shot sequences.
- On-screen text short or planned as overlay.
- Dialogue lines short enough to sync; long lines covered by reactions.
- Continuity ledger complete; adjacent-shot pass done (`shot-continuity.md`).
- Total runtime within target (`runtime-timing.md`).
