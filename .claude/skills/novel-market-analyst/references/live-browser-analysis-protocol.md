# Live Browser & Web Market Research Protocol

This reference instructs AI agents on how to execute real-time competitive market intelligence using browser subagents, web scraping, and search tools when authorized by the author.

---

## 1. When to Activate Live Market Research

Activate this protocol when:
1. The author requests real-time data on current genre trends (e.g., *"What is currently trending on Royal Road's Rising Stars?"* or *"What are top psychological thrillers doing on Amazon KU right now?"*).
2. Triangulating competitive titles ("comps") published within the past 12–24 months.
3. Scraping keyword tags, blurb structures, and review sentiments for market positioning.
4. Testing whether a proposed high-concept hook has already been saturated in the market.

> **Permission Note**: Live browsing or web search must adhere to workspace safety guidelines. If browser tools are disabled or network is restricted, gracefully fall back to the offline heuristics detailed in `publishing-platforms-deep-dive.md`.

---

## 2. Research Vectors by Platform

### Vector A: Royal Road & Progression Webnovels
1. **Target URLs**:
   - `https://www.royalroad.com/fictions/rising-stars`
   - `https://www.royalroad.com/fictions/best-rated`
2. **Data Extraction Points**:
   - **Top 10 Rising Stars Titles**: Note title syntax, subtitle length, and primary premise.
   - **Tag Frequencies**: Count the occurrences of tags (e.g., `LitRPG`, `Progression`, `Time Loop`, `Villainous Lead`, `Anti-Hero`, `Deckbuilding`, `Female Lead`).
   - **Chapter Count at Ascent**: At how many chapters and total pages did the fiction hit Rising Stars? (Typically between chapters 12 and 25).
   - **Average Chapter Length**: Page count divided by chapter count (target: 7–10 pages / ~2,000 words per chapter).
3. **Sentiment & Review Analysis**:
   - Inspect the top 3-star and 4-star reviews: What caused readers to downgrade? (Look for complaints about pacing drag, sudden system nerfs, unlikable MC decisions, or bloated stat screens).

### Vector B: Amazon Kindle Direct Publishing (KDP) & Kindle Unlimited
1. **Target Search Queries**:
   - `"Amazon best sellers in [Target Subcategory]"`
   - Subcategory examples:
     - `Kindle Store > Kindle eBooks > Mystery, Thriller & Suspense > Thrillers > Psychological`
     - `Kindle Store > Kindle eBooks > Science Fiction & Fantasy > Fantasy > Paranormal & Urban`
     - `Kindle Store > Kindle eBooks > Romance > Romantic Suspense`
2. **Data Extraction Points**:
   - **Best Sellers Rank (BSR)**: Note the BSR of the #1, #20, and #50 books in the subcategory.
     - BSR < 1,000: High commercial demand ($5,000–$20,000+/month revenue).
     - BSR < 10,000: Solid sustainable niche ($1,000–$3,000/month).
     - BSR > 50,000: Lower demand or saturated category.
   - **Cover Aesthetic Archetypes**: Color palettes, typography font styling (serif vs sans-serif vs display script), character silhouettes vs illustrated art.
   - **Blurb Blueprint Extraction**: Identify the paragraph structure of the top 3 blurbs (Hook sentence $\rightarrow$ Character introduction & dilemma $\rightarrow$ Rising stakes $\rightarrow$ Final punchline question $\rightarrow$ Tropes checklist).

### Vector C: Wattpad & Romance Apps
1. **Target Search Queries**:
   - Wattpad Hot Lists by tag: `#darkromance`, `#mafia`, `#enemiestolovers`, `#werewolf`.
2. **Data Extraction Points**:
   - Inline comment hotspots: Which scenes elicit 500+ comments per paragraph? (Usually razor-sharp dialogue clapbacks, intense physical proximity, or betrayals).
   - Hook in Chapter 1: How many lines until the love interest or primary conflict is introduced? (Usually under 100 words).

### Vector D: Southeast Asian Apps (KBM App, Fizzo)
1. **Target Inquiries**:
   - Fizzo trending banner titles and KBM App top ranking tabs.
2. **Data Extraction Points**:
   - Title Formulas: Typically direct and descriptive (e.g., *"Pembalasan Istri yang Dibuang"*, *"Mertua Menyesal Menantu Ternyata Konglomerat"*).
   - Chapter 1 Conflict Density: The immediate confrontation (confronting the husband at a hotel, being handed divorce papers, being insulted at a family banquet).

---

## 3. Analysis Synthesis Format

When live browser data is collected, compile it into the following structured format inside `docs/storycraft/market-analysis.md`:

```markdown
### Live Market Intelligence Report
- **Scan Date**: YYYY-MM-DD
- **Target Platform(s)**: [Royal Road / Amazon KDP / KBM / etc.]
- **Scanned Sample Size**: [e.g., Top 25 Titles in Subcategory]

#### 1. Dominant Tag & Trope Clusters
- Primary Cluster (present in >60% of top titles): [List tropes]
- Emerging / Underserved Trope (rising fast with low saturation): [List tropes]

#### 2. Reader Pain Points (Extracted from 2-star & 3-star reviews)
- Friction Point 1: [e.g., "Pacing slows down after Chapter 15"]
- Friction Point 2: [e.g., "Protagonist becomes completely passive in Act 2"]

#### 3. Strategic Counter-Positioning
- How our novel will avoid these pitfalls: [Actionable plan]
- Our unique hook ("X meets Y with a twist"): [Specific premise pitch]
```
