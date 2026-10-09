---
name: allergen-gate
description: Apply the house allergen-gate kitchen protocol before calling a menu safe. Use when a guest has a food allergy, when someone asks if a dish is safe if they just skip or scrape off an ingredient, or when the user mentions sesame, peanut, lupin, shared fryers, cross-contact, or allergen gate.
---

# Allergen gate

This skill has **no executable scripts**. There is no `scripts/` directory. Do not call `run_skill_script`. Follow `SKILL.md` and `references/` only.

A kitchen safety protocol. Generic "just leave it off the plate" advice is not this skill.

## When to use

The user is cooking, ordering, or planning a menu for someone with a food allergy.

## Required tools

1. Load this skill with `load_skill` (`skill_name`: `allergen-gate`).
2. Read [references/gate-rules.md](references/gate-rules.md) with `read_skill_resource` before answering. The Gate-9 list and CLEAR / HOLD / STOP rules live only there.
3. Do not invent allergens or verdicts from general knowledge.

## Classify

1. Identify the guest's allergen.
2. Identify every dish and shared tool (fryer, board, tongs, oil).
3. Apply the gate rules from the reference, including cross-contact.

## Response format

Use this exact shape. No preamble.

```
Allergen gate: <CLEAR | HOLD | STOP>
Allergen: <name>
Cross-contact: <yes | no> — <one sentence>
Why: <one sentence citing a gate rule>
Fix: <the matching next step from the reference>
```
