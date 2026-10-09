---
name: now-next-need
description: Turn a conversation, meeting, or status update into now-next-need notes. Use when the user asks to summarize a meeting, capture a decision, write action items, or produce notes; mentions now-next-need, Now / Next / Need headings.
---

# Now / Next / Need notes

This skill has **no executable scripts**. There is no `scripts/` directory. Do not call `run_skill_script`. Follow `SKILL.md` and `references/` only.

A three-heading notes contract. Generic "Summary" and "Action items" headings are out of contract.

## When to use

The user wants notes, a recap, a decision log, or action items from a discussion.

## Required tools

1. Load this skill with `load_skill` (`skill_name`: `now-next-need`).
2. Read [references/template.md](references/template.md) with `read_skill_resource` before writing. Heading names, owner syntax, and the footer live only there.
3. Do not add extra headings. If a fact has no home, put it under Need.

## Response format

Emit markdown that matches the template in the reference. No preamble before `## Now`. No extra sections.
