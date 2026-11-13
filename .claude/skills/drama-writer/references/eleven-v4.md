# Eleven v4 voice direction for screenplay JSON

When the user requests ElevenLabs v4-ready screenplay JSON, read the complete scene first. Consider the setting, relationships, previous dialogue, actions, body language, stakes and next beat. Treat `delivery` as a starting point, not a literal instruction. Give each character a consistent vocal personality that can evolve with the scene. Do not invent emotions that contradict the material. Aim for human, spontaneous speech rather than stiff, uniformly measured narration. Express the full range of the scene: warmth, playful energy and audible delight in cheerful moments; vulnerability, grief, urgency or restraint when supported by the context. Let emotion rise and change across a line, with each character reacting to the other. Ordinary conversation can be lively without becoming theatrical.

For every object containing `speaker` and `line`, preserve `line` and `delivery` exactly and add `ttsText` containing the original spoken words with square-bracket performance directions. In `ttsText` only, adjust punctuation, capitalization and pauses when they help the actor deliver the line; do not add, remove, translate or replace spoken words. Preserve all other fields, values, ordering and structure, including episode and scene metadata. Do not add `ttsText` to action-only objects. Return valid JSON without commentary or fences when JSON alone is requested. Never translate or rewrite the dialogue. Support every language and mixed-language dialogue: retain the original pronunciation cues, conversational rhythm, dialect, script and register. Use concise English audio tags without translating the spoken words.

Direct the intention and the change within a line, not just an emotion. Anger need not be loud: `[low, controlled anger]` can be more effective than shouting. Give emotionally significant lines a specific, audible performance, not just a generic label. Use multiple tags within a line when the voice changes: a sob, a broken breath, then a more determined tone can each mark a distinct beat. Shape timing with punctuation and pauses when the situation warrants it. A brief neutral line may need only one tag; do not impose a tag quota or limit. Avoid contradictory or repeated directions, random placement, excessive ellipses and forced melodrama. Use breathing, laughter and other reactions only when justified. Punctuation and pauses should serve the moment; never insert SSML break tags for Eleven v4. Do not add spoken words or instructions that might be read aloud. Tags are expressive guidance, not a guarantee of a particular acoustic result; audition and adjust the voice and tags in the target model.

Example input:

```json
{"scenes":[{"sceneId":"S1","flow":[{"action":"She holds her breath."},{"speaker":"C01","line":"I already know. But I want to hear it from you.","delivery":"quiet, then firm"}]}]}
```

Example output:

```json
{"scenes":[{"sceneId":"S1","flow":[{"action":"She holds her breath."},{"speaker":"C01","line":"I already know. But I want to hear it from you.","delivery":"quiet, then firm","ttsText":"[quietly] I already know. [firmer] But I want to hear it from you."}]}]}
```

A joyful reunion can sound spontaneous and energetic, rather than flat. For example:

```json
{"speaker":"C02","line":"We did it! You're really here!","delivery":"excited, laughing","ttsText":"[laughs joyfully] We did it! [breathless with excitement] You're really here!"}
```

A charged line can start in grief and find strength as it goes on. For example, when Alya wipes away tears and her voice grows stronger, a possible interpretation is:

```json
{"speaker":"Alya_Noda","line":"Tiga tahunnya sudah habis, Pa. Alya pulang.","delivery":"menghapus air mata, suara menguat","ttsText":"[sobbing] Tiga tahunnya... sudah habis, Pa. [voice steadying through tears] Alya pulang."}
```

Let the scene justify the sob and the shift; do not make every emotional line cry. If only a brief delivery note is available, use it as evidence, avoid inventing unsupported history, and make the most expressive choice it supports. Apply the same principle in any language.

Before returning, check each spoken line for unchanged spoken words and unchanged original fields, appropriate context, consistent character voice, believable shifts and justified reactions. Check JSON validity and ensure every spoken line has direction and action-only objects have no added `ttsText`.
