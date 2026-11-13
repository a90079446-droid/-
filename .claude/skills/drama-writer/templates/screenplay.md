# Screenplay template

Two variants. Use **Standard** for story and episode writing (Workflow C). Use **Production** only when the user wants production-ready output, shots, or AI-video handoff (Workflow D). If the user or project has its own format, use theirs.

Format rules (both variants):
- Scene heading: `## S01 - INT. LOCATION - TIME OF DAY` (INT., EXT., or INT./EXT.).
- `Cast:` lists everyone present in the scene, including silent characters.
- Speaker lines: `NAME: line`. Latin-script names in CAPS; other scripts spelled identically every time. Optional delivery in brackets before the words: `NAME: [softly] line`. Use `NAME (V.O.):` for voice-over, `NAME (O.S.):` for off-screen.
- Action lines: present tense, one visual idea per line, no camera jargon in Standard.
- Interruptions end with `--` at the cut-off point (the standard screenplay mark); trailing off ends with an ellipsis.
- This format is what `scripts/estimate-runtime.mjs` reads.

---

## Standard

```markdown
# <SERIES TITLE> - EP <NN>: <Episode title>
Language: <code and variety, e.g. en-US, id (Jakarta colloquial), zh-TW, ko>
Target: <seconds> s · Format: vertical 9:16

**Episode objective:** <the episode's dramatic question; what changes by the end>
**Opening hook:** <first image + first line>

## S01 - INT. <LOCATION> - <TIME>
Cast: <NAME>, <NAME>

<Action: who is where, doing what. The one visual detail that matters.>

<NAME>: <line>
<NAME>: [<delivery>] <line>

<Action / reaction beat.>

<NAME>: <line>--
<NAME>: <interrupting line>

## S02 - EXT. <LOCATION> - <TIME>
Cast: <NAME>

<...>

**Ending beat:** <type: reveal / decision / threat / emotional landing / reversal / reframing line / arrival>

---

**Delivery sheet** (only when the script will be voiced; the lines that carry the scene, not every line)
| Line | Surface | Underneath | Intensity (1-5) | Pace / volume | Leak or shift |
|---|---|---|---|---|---|
| <NAME>: "<line>" | | | | | |
```

The delivery sheet sits after the `---` rule so it stays out of the spoken text and out of the runtime estimate. See `references/emotional-performance.md` §6 for how to fill it and convert it to a TTS provider's format.

---

## Production

```markdown
# <SERIES TITLE> - EP <NN>: <Episode title> (production)
Language: <code> · Target: <seconds> s · Format: vertical 9:16
Video tool: <if known> · TTS: <provider if known, else "provider-neutral tags">

## S01 - INT. <LOCATION> - <TIME>
Cast: <NAME> (<visual reference: age, hair, wardrobe>), <NAME> (<...>)
Setting: <layout: door, window, key furniture; light source; weather>
Props: <key props and where they start>

### S01-01 · <SHOT TYPE: WIDE / MEDIUM / CU / ECU / OTS / POV / INSERT / TWO-SHOT> · <n>s
<Who is in frame, where, facing which way. The single main action, start → end.>
<NAME>: <line, if spoken in this shot>
Camera: <static / slow push-in / pan ... one behaviour> (only if requested)
Continuity: <end state: hands, props, posture, facing>

### S01-02 · <SHOT TYPE> · <n>s
<Reason for the cut is visible here: reaction, insert, reveal, time step.>
Continuity: <...>

**Continuity ledger:** see table below (or `templates/continuity-ledger.md`).
**Estimated runtime:** <n> s (range), against target <n> s.
```

Production notes:
- Each shot: one or two characters, one main action, one camera behaviour.
- Shot duration includes the time any dialogue in it needs.
- Long lines go over the listener's reaction shot.
- On-screen text (messages, documents): keep it short; note `On-screen text:` so editors can add it as an overlay.
