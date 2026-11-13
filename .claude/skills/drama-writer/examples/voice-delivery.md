# Example: writing lines that perform when spoken

The same 30-second moment written twice: once flat, once with the performance built into the text. Then the delivery sheet, and how it converts for different kinds of TTS. All material here is original.

**Situation.** 2 a.m. Tomas (58) is driving his daughter Lena (19) home from the police station. She was picked up with friends who were shoplifting. He hasn't said anything since the station.

---

## Flat

```markdown
## S01 - INT. TOMAS'S CAR - NIGHT
Cast: TOMAS, LENA

TOMAS: I can't believe you did this. I'm so disappointed in you.
LENA: I know, Dad. I'm sorry. I made a mistake.
TOMAS: Do you know how worried I was? I thought something terrible had happened.
LENA: [crying] I'm sorry. I didn't mean for any of this to happen.
TOMAS: [sighs] Let's just go home.
```

Read aloud, or put through any voice engine, this sounds synthetic even with a good voice:
- Both speakers sit at the same intensity for the whole scene.
- Every line is a complete, balanced sentence with a falling end.
- The emotion is named ("disappointed", "worried") so the voice has nothing to hide, and nothing to leak.
- `[crying]` does the work the words should do, and runs over the whole line.
- Nobody is listening. Each line waits politely for the last to finish.

## Performed

```markdown
## S01 - INT. TOMAS'S CAR - NIGHT
Cast: TOMAS, LENA

The indicator ticks. Tomas watches the empty junction. Lena is still wearing a borrowed jacket.

TOMAS: You eat?
LENA: ...What?
TOMAS: In there. They give you anything.
LENA: Something from a machine.
TOMAS: Hm.

The light turns green. He doesn't move.

LENA: Dad, I wasn't-- I didn't take anything. I was just with them.
TOMAS: Okay.
LENA: I wasn't.
TOMAS: I said okay.

He turns the wheel at last.

TOMAS: [voice drops] They called the house at one. Your mother picked up.

Lena looks at him.

TOMAS: She thought it was the hospital. She thought it was the hospital, Lena.
LENA: [sharp inhale]
TOMAS: There's bread at home. I'll make you something.
```

What changed:
- **Surface and underneath.** Tomas's surface is practical (food, bread). Underneath is the hour he spent thinking she was dead. It leaks once, in the repeated line, and the voice should crack there and nowhere else.
- **Intensity in contrast.** Lena rises (defensive, then pleading); Tomas stays low. His peak is the quietest line in the scene.
- **The text carries the timing.** The ellipsis on "...What?" is her surprise that he's asking about food. "I wasn't-- I didn't take anything" is a false start that tells us she's afraid of not being believed. "Hm." is a whole line of judgement.
- **Repetition as the leak.** Saying "She thought it was the hospital" twice, adding her name the second time, does what `[crying]` couldn't.
- **The listener is heard.** Lena's sharp inhale is her only response to the worst news. It tells the audience she understood.
- **Two tags, both doing a job.** `[voice drops]` marks a shift a reader could miss; `[sharp inhale]` is a sound, not an emotion.

## Delivery sheet

Only the lines that carry the scene.

| Line | Surface | Underneath | Intensity (1-5) | Pace / volume | Leak or shift |
|---|---|---|---|---|---|
| TOMAS: "You eat?" | Practical | Can't say the real thing yet | 1 | Slow, low | None. Flat is the point |
| LENA: "Dad, I wasn't-- I didn't take anything." | Explaining | Afraid he won't believe her | 3 | Fast, rising | Stumbles at the restart |
| TOMAS: "I said okay." | Closing the subject | Not okay | 2 | Clipped | Slight edge on "said" |
| TOMAS: "She thought it was the hospital. She thought it was the hospital, Lena." | Reporting | An hour of terror | 4 | Slower the second time, quieter | Catch on "Lena" |
| TOMAS: "There's bread at home." | Practical again | Forgiveness he can't say | 2 | Soft, steady | Steadier than the line before; he's chosen |

## Converting the sheet

The sheet is provider-neutral. Convert it to what the user's tool accepts, and check the tool's current documentation for exact syntax.

- **Instruction-steered voices:** each row becomes the instruction for that line. For the hospital line: "Tired father, quiet and slow. Holds it together the first time; on the repeat, the voice nearly breaks on her name."
- **Inline-tag voices:** keep the text as written and use at most one tag where the leak is, if the words alone don't produce it.
- **SSML engines:** turn the beats into breaks and prosody, for example a short `<break time="600ms"/>` between the two hospital sentences and a slower rate on the second.
- **Generating line by line** (or at least splitting at the hospital line) often gives the peak its own delivery instead of averaging it with the calmer lines around it.
