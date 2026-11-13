# drama-writer (skill folder)

This folder is a complete Agent Skill. Claude reads `SKILL.md` first and loads the other files only when a task needs them.

- `SKILL.md`: workflows, language rules, core craft rules, output format, and a map of the other files.
- `references/`: in-depth guidance (storytelling, plot, character, dialogue, multilingual writing, emotion and TTS, short-form pacing, visual storytelling, scenes, shot continuity, series continuity, AI video, runtime, editorial review).
- `templates/`: project overview, story state, episode index and record, series bible, character profile, story outline, episode outline, screenplay (standard and production), continuity ledger.
- `examples/`: natural dialogue in six languages, weak vs strong storytelling, binge hooks and ending cuts, flat vs performed voice delivery, a full production-ready episode.
- `scripts/estimate-runtime.mjs`: optional runtime checker for scripts in the template format (`node scripts/estimate-runtime.mjs file.md --target 75`). Needs Node.js 18+; the skill works without it. Use `-` to read from stdin.

To install by hand, copy this whole folder to `~/.claude/skills/drama-writer/` (all projects) or `<project>/.claude/skills/drama-writer/` (one project). The plugin, `npx skills add` and the npm CLI are covered in the repository's GUIDE.md. `VERSION` names the release this folder came from.
