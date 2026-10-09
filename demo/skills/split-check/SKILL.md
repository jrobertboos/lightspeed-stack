---
name: split-check
description: Split a restaurant or shared meal bill with the house split-check rules (separate food and drink tip rates, tax not tipped, kids under 12 skip the tip, round each person up to a quarter). Use when the user asks to split a bill, check, tab, or tip; mentions split card; or asks what each person owes.
---

# Split check

This skill has **no executable scripts**. There is no `scripts/` directory. Do not call `run_skill_script`. Follow `SKILL.md` and `references/` only.

A house protocol for splitting a bill. Equal split of the grand total, or a flat 20% on everything, is not this skill.

## When to use

The user has a food bill, drinks, tax, and a group, and wants to know who pays what.

## Required tools

1. Load this skill with `load_skill` (`skill_name`: `split-check`).
2. Read [references/rates.md](references/rates.md) with `read_skill_resource` before calculating. Tip rates, the kid rule, and rounding live only there.
3. Do not use a single tip percent on the whole check.

## Response format

Use this exact shape. No preamble. Currency to two decimals, then the rounded due.

```
Split card:
- Food: ...
- Drinks: ...
- Tax: ...
- Tip: ... (show the two rates)
- Adult due (each): ... → rounded ...
- Kid due (each): ... → rounded ...   # omit if no kids
```

If a kid is at the table, they still share food, drinks, and tax. They do not share the tip.
