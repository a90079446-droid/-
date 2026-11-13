# Shot continuity

Load this for production-ready screenplays, shot lists, and any review where shots are specified.

## Contents
1. Cut types and what they are for
2. The rule of progression
3. Physical continuity: what to track
4. Spatial continuity: the 180° line, eyelines, screen direction
5. Time across cuts
6. The adjacent-shot validation pass
7. Fix patterns
8. Worked example

## 1. Cut types and what they are for

| Cut / shot | What it is | Use it to |
|---|---|---|
| Establishing shot | Wide view of the location | Orient the viewer when geography matters; often skippable in short-form |
| Hard cut (straight cut) | Instant change of shot | Move the story forward; the default |
| Action cut (cut on action) | Cut during a movement, which continues in the next shot | Make movement feel continuous across angles |
| Match cut | Two shots linked by a shared shape, motion, or sound | Connect ideas, times, or places |
| Reaction shot | A character responding to what was said or done | Show the impact; often more important than the line itself |
| Reverse shot | Opposite angle in a conversation (shot/reverse-shot) | Alternate between speakers or between speaker and listener |
| Over-the-shoulder (OTS) | Framed past one character toward another | Keep both in the relationship |
| Insert shot | Close-up of a detail (a hand, a ring, a phone screen) | Show information the audience must read |
| POV shot | What a character sees | Put the audience in their position |
| Cutaway | Shot of something else in the scene or elsewhere | Show parallel action, compress time |
| Continuous shot | One unbroken take | Sustain tension; harder to generate with AI video |
| Smash cut | Abrupt, contrasting cut | Shock or comedy |
| J-cut / L-cut | Sound of next shot starts early / sound of previous shot continues | Smooth dialogue flow and anticipation |

**A hard cut does not suspend continuity.** It changes the angle or moment; the physical world keeps its state.

## 2. The rule of progression

Every shot starts where the previous one left off, physically and narratively, unless the cut deliberately jumps time.

**Bad**
1. She starts pouring coffee.
2. Hard cut, new angle.
3. She starts pouring coffee again.

The action restarts for no reason.

**Better**
1. She starts pouring coffee.
2. Insert: the cup filling.
3. His reaction: he notices something behind her.

**Every cut needs a reason**: new information, a reaction, emphasis, a time jump, or a change of point of view. If a cut has no reason, merge the shots.

When an action continues across a cut, show its next stage, not its start:
- Shot A: he reaches for the drawer. → Shot B: the drawer slides open (insert). → Shot C: his face as he sees what's inside.
- Not: Shot A: he reaches for the drawer. → Shot B: he reaches for the drawer.

## 3. Physical continuity: what to track

For each shot, track the state at the **end** of the shot (it becomes the start of the next):

- **Hands:** which hand holds what; whether hands are free.
- **Objects:** open/closed, full/empty, on/off, intact/broken, where they are (on the table, in her bag, in his left hand).
- **Posture:** standing, sitting, kneeling, lying down.
- **Facing:** toward whom, toward what; back to the camera or not.
- **Position:** where in the room, relative to others and to landmarks.
- **Completed actions:** the letter has been read; the call has ended; the door is locked. Once done, they stay done.
- **Appearance:** clothing on/off, wet/dry, hair up/down, tears, injuries, makeup.
- **Light and environment:** lamp on/off, curtains open, rain, time of day.

Use `templates/continuity-ledger.md` for multi-shot sequences.

## 4. Spatial continuity: the 180° line, eyelines, screen direction

- **The 180° rule:** in a conversation, keep the camera on one side of the line between two characters, so A always looks screen-right and B screen-left. Crossing it flips them and disorients viewers. Cross deliberately (with a moving shot or a neutral shot in between) when the scene's power shifts.
- **Eyelines:** if A looks down at B (B is seated), B looks up at A in the reverse shot. Eyelines must match positions.
- **Screen direction:** a character leaving frame right enters the next shot from frame left if the movement continues.
- In AI video, specify facing and screen position explicitly ("she stands on the left of frame, facing right toward him").

## 5. Time across cuts

- **Continuous time:** consecutive shots follow each other in real time; states carry over exactly.
- **Compressed time:** a cut skips part of an action (she puts the key in the lock → she's inside). Legitimate, as long as the end state is consistent with the skipped steps.
- **Time jump:** must be legible (light, clothing, location, a line, a visual marker). Unmarked jumps look like errors.
- Don't let a cut accidentally imply that time passed (a full cup suddenly half-empty) or reversed (a cigarette longer than in the previous shot).

## 6. The adjacent-shot validation pass

Before finalizing a production script, check every pair of consecutive shots (N, N+1) for:

1. **Repeated action:** does N+1 restart an action N already began or completed?
2. **Impossible transition:** can a person get from N's position to N+1's in the elapsed time?
3. **Disappearing or teleporting props:** is every prop where N left it?
4. **Hand continuity:** is it in the same hand, or did we see it change?
5. **Posture and facing:** consistent, or shown changing?
6. **Inconsistent character state:** tears, wounds, clothes, wetness, breathlessness carried over?
7. **Unexplained time jump:** light, weather, completed actions consistent?
8. **Unmotivated cut:** does N+1 give new information, a reaction, emphasis, or a time step?
9. **Eyeline and screen direction:** consistent with positions?
10. **Cast in frame:** is everyone who should be visible accounted for, and no one appearing from nowhere?

Also check across scenes: the scene that follows a door slam picks up with the consequences in place.

**Fix the problems in the script.** Don't return a list of issues unless the user asked for review only. If a fix changes the story (for example, it needs an extra shot), make it and keep the runtime in check.

## 7. Fix patterns

| Problem | Fix |
|---|---|
| Action repeats across a cut | Cut to the action's next stage, a detail insert, or a reaction |
| Prop teleports | Add the move ("she slides the envelope across") or put the prop back |
| Prop switches hands | Keep the hand, or show the switch in a shot that motivates it |
| Character changes posture between shots | Add the movement, or make the posture consistent |
| Unexplained time jump | Add a marker (light change, a line, clothing) or remove the jump |
| Too many actions in one shot | Split across shots, each with one main action |
| Cut without purpose | Merge shots or give the second a job (reaction, insert, reveal) |
| Eyeline mismatch | Adjust positions or the direction of the look |
| 180° violation | Keep sides consistent, or add a neutral or moving shot to cross deliberately |

## 8. Worked example

**Draft**
- S02-01 MEDIUM: Dara stands at the counter, holding a mug in her right hand.
- S02-02 CLOSE: Dara picks up the mug from the counter.
- S02-03 MEDIUM: Dara, seated at the table, drinks.
- S02-04 CLOSE: The mug, full, on the counter.

**Problems**
- 01→02: She already holds the mug; picking it up repeats the action.
- 02→03: Standing at the counter, then seated at the table, with no movement.
- 03→04: She drinks at the table; the mug is then back on the counter, full.

**Fixed**
- S02-01 MEDIUM: Dara at the counter, mug in her right hand. Her phone buzzes on the counter.
- S02-02 INSERT: Phone screen: "Unknown number: Don't tell him you saw me."
- S02-03 CLOSE: Dara. She sets the mug down beside the phone without looking at it.
- S02-04 MEDIUM: She turns the phone face down. Behind her, the bedroom door opens.

Each cut has a reason, the mug stays where she put it, and the scene moves forward.
