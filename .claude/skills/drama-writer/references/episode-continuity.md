# Series and episode continuity

## Contents
1. The series bible
2. State of the story (updated every episode)
3. Character knowledge tracking
4. Continuation protocol (Workflow F)
5. Handling gaps and contradictions
6. Avoiding repetition across episodes
7. Episode-to-episode checks

## 1. The series bible

### A project a writer can read

For a new project, offer a plain Markdown folder. Use episodes, chapters, or parts as appropriate:

```text
my-series/
  project.md          # overview, progress, links
  series-bible.md     # foundations and clearly marked plans
  story-state.md      # state after the latest accepted installment
  episode-index.md    # brief chronological guide
  characters/         # optional profiles
  episodes/           # accepted story and clearly identified drafts
  episode-records/    # concise records of accepted installments
```

Use the project, story-state, episode-index, and episode-record templates in `templates/`. A small project can combine notes or omit folders. Adapt links and names to the user's existing files; do not move or rename them just to match this example. Use headings and short prose a person can edit. Save the accepted story itself, not just summaries: summaries can omit voice, dialogue, and context. Keep records selective and point to the episode and scene for important facts. Do not archive whole conversations by default; record accepted decisions instead.

### What counts as established

Mark installments and records as draft or accepted. Keep future plans distinct from events that have happened, and exclude rejected ideas from canon. The accepted story is evidence of what happened; the index and current state are aids that may need correction. A plan, a newer note, or a draft does not automatically override an accepted scene. If accepted sources conflict, point out the conflict and ask the user to decide when it matters. Never invent a missing event. If acceptance or the latest installment is unclear and matters, ask or state a provisional assumption.

For any multi-episode project, keep a bible (`templates/series-bible.md`) containing:
- Series premise and logline.
- Genre, tone, target audience, platform, episode length.
- Writing language and variety, register conventions per relationship.
- Main characters (link to profiles) and their relationships.
- World rules (anything that constrains what can happen).
- Main conflict and central dramatic question.
- Central mystery (if any) and its true answer.
- Long-term arc: phases, midpoint, endgame.
- Planned reveals: plant, clues, misdirection, payoff episode.
- Open threads and promised payoffs.
- Locations (with fixed layout notes for recurring sets).
- Visual reference notes for recurring characters (wardrobe, distinguishing features) for AI video consistency.
- Episode log: one line per episode.

The bible records foundations and plans. If project files differ from conversation memory, check the files; verify specific events against the accepted story when needed.

## 2. State of the story (updated every episode)

After an episode is accepted, update the state and its episode record if the user has authorized those edits; otherwise provide proposed updates for review. A draft can have a provisional state, clearly labeled and kept separate from the accepted state:

```
STATE AFTER EP 07
Timeline: Friday night, two days after the funeral.
Knows: Mira knows the will was changed. Jun does NOT know Mira knows.
Believes (wrongly): Jun believes the lawyer is on his side.
Emotional: Mira cold, decided. Jun anxious, overconfident in public.
Relationships: Mira–Jun: polite war. Mira–Auntie Sol: new, fragile alliance.
Possessions: Mira has the original will (hidden in the sewing tin).
Physical: Jun's right hand bandaged (ep 06 glass).
Open questions: Who witnessed the second will? Why did Grandfather call Sol the night he died?
Promised payoffs: The sewing tin (planted ep 02). The second witness.
Last ending types: ep05 arrival, ep06 reveal, ep07 decision.
```

## 3. Character knowledge tracking

Most continuity errors in drama are knowledge errors: a character acts on information they don't have, or forgets information they do.

For each important secret, track:
- Who knows it, and since when (episode/scene).
- How they learned it (seen on screen, told, inferred).
- Who suspects it.
- Who believes something false about it.

Rules:
- A character can only act on what they know or reasonably suspect.
- When a character learns something, the audience should usually see or clearly infer the moment.
- Dramatic irony depends on precise knowledge tracking: the audience must know exactly who doesn't know.

## 4. Continuation protocol (Workflow F)

When asked to continue a story or write the next episode:
1. **Find the material.** Identify the project and latest accepted installment. Read the overview, bible, current state, index, relevant character profiles, and recent accepted episodes when available. If the user pasted material, use it as a source. Work with existing names and layout.
2. **Extract the state.** Where/when we are, who knows what, emotional states, physical states (injuries, possessions, clothes if continuous), open threads, recent ending types.
3. **Identify the obligation.** What did the previous episode promise? A cliffhanger must be addressed. Look up relevant earlier records and scenes for returning secrets, characters, and events; use the original scene when wording or context matters.
4. **Write**, keeping register, voice, and established facts.
5. **Check against the source** (section 7).
6. **Record accepted changes.** Once accepted, save the episode, add its concise record and index entry, and update the current state when authorized. Otherwise provide proposed updates. Do not promote a draft to accepted story merely because it was generated or saved.

### Revisions to earlier installments

When an accepted installment changes, compare the change with later records, the current state, and relevant later scenes. Identify affected knowledge, chronology, setups, and payoffs; flag conflicts and uncertainty to the user. Propose the smallest necessary corrections. Update tracking files only when authorized, and do not silently rewrite later episodes. If a complete impact check is not possible, say which material was not checked.

Never invent earlier events as if they happened. If the next episode needs a past event that was never shown, present it as new information (a revelation, with a reason it wasn't known), and flag it to the user if it changes established material.

## 5. Handling gaps and contradictions

- **Missing information:** if it matters (e.g. whether a character already knows the secret), ask, or proceed with a clearly marked assumption ("Assuming Jun hasn't yet seen the photo; tell me if he has.").
- **Contradictions in the source:** point them out briefly. Distinguish accepted scenes from plans and drafts; ask the user to resolve conflicts between accepted sources when the choice matters.
- **The user wants a change** that contradicts earlier episodes: note what it affects (which earlier scenes no longer fit) and offer the smallest set of fixes.

## 6. Avoiding repetition across episodes

- **No resetting.** Characters remember. Emotional consequences carry: a betrayal in ep 4 still colours ep 5.
- **No re-explaining.** Don't repeat exposition each episode. Give new viewers just enough orientation through action (a hostile look, a line with history in it), not recaps.
- **Vary the beats.** Track hook types, ending types, and confrontation formats. Change them deliberately.
- **Escalate, don't loop.** If the same conflict repeats, raise the stakes or change the terms each time.

## 7. Episode-to-episode checks

Before returning a continuation:
- Does it address the previous ending?
- Is everyone where they were left (or is the move explained)?
- Do characters know only what they should?
- Are physical states (injuries, objects in hand, clothes in continuous scenes) carried over?
- Are relationships and speech levels consistent with the latest state?
- Is any earlier fact contradicted?
- Is any setup about to be forgotten that should be paid off soon?
- Does the episode's ending type differ from the last few?
