# Mega-Serial Hierarchical Ledger Schemas

Use these exact markdown templates when initializing volume and arc ledgers for long-horizon serial fiction (500 to 5,000+ chapters).

---

## 1. Arc State Machine Ledger Schema (`docs/storycraft/arcs/YYYY-MM-DD-arc-[A]-ledger.md`)

```markdown
# Arc Ledger: Arc [Number] — [Arc Title]
- **Date Created**: YYYY-MM-DD
- **Volume**: Volume [V]
- **Chapter Span**: Chapters [Start] – [End] (Target: ~30 chapters)
- **Primary Setting**: [City / Province / Dungeon / Realm]
- **Active Ticking Clock**: [Concrete deadline or impending disaster]

## 1. Primary Conflict & Antagonists
- **Arc Boss**: [Name, power tier, concrete agenda]
- **Secondary Obstacles**: [Rival factions, environmental hazards, deadlines]
- **The Crucible Stakes**: [What is permanently lost if protagonist fails?]

## 2. Active Character Roster & Location States
| Character Name | Status | Location | Current Disposition to MC |
| :--- | :--- | :--- | :--- |
| [Protagonist] | ACTIVE | [Current Room / Coordinates] | Self |
| [Companion A] | ACTIVE | Traveling with MC | Loyal, but injured right knee |
| [Companion B] | DORMANT | Capital City Guild House | Researching ancient scroll |
| [Rival C] | ACTIVE | Pursuing party, 10 miles behind | Hostile |
| [Deceased D] | DECEASED (Ch 84) | Buried at Iron Valley | — |

## 3. Chekhov Open-Loop Ledger (Active in this Arc)
| Loop ID | Planted Ch | Description | Expected Payoff Window | Current State |
| :--- | :--- | :--- | :--- | :--- |
| LOOP-031 | Ch 62 | Sealed letter from the dying courier | Arc 3 Climax (Ch 85–90) | ACTIVE |
| LOOP-044 | Ch 71 | Protagonist promised 500 gold to alchemist | Arc 4 | DORMANT |

## 4. Power & Resource Governance
- **Protagonist Active Tier**: [Tier / Level / Cultivation Stage]
- **Active Skills / Spells**: [Max 5 active focus abilities in this arc]
- **Primary Inventory Assets**: [Max 5 active items carried on person]
- **Somatic Constraints**: [Lingering injuries, poison, exhaustion counters]
```

---

## 2. Volume Compendium Schema (`docs/storycraft/volumes/YYYY-MM-DD-volume-[V]-ledger.md`)

```markdown
# Volume Ledger: Volume [Number] — [Volume Title]
- **Date Created**: YYYY-MM-DD
- **Target Chapter Range**: Chapters [Start] – [End] (60–120 chapters)
- **Target Word Count**: [e.g., 120,000 – 180,000 words]
- **Central Thematic Argument**: [Thesis vs. Antithesis]

## 1. Multi-Arc Breakdown
- **Arc 1 (Ch [X]–[Y])**: [Title] — Inciting disruption, initial trials, establishing the new realm.
- **Arc 2 (Ch [Y]–[Z])**: [Title] — Escalation, faction tournament / regional conquest, midpoint inversion.
- **Arc 3 (Ch [Z]–[W])**: [Title] — All hope lost, siege / disaster, final volume breakthrough climax.

## 2. Macro Breakthrough Milestone
- **Starting Power Level**: [Tier at chapter 1 of this volume]
- **Ending Power Level**: [Maximum permitted tier at the volume climax]
- **Breakthrough Catalyst**: [The immense psychological or mortal trial required to advance]

## 3. Volume Climax & Transition Hook
- **Climactic Battle / Revelation**: [The central confrontation resolving this volume's main question]
- **The Greater Horizon Peephole**: [The reveal in the final 3 chapters showing the next higher realm or threat]
```
