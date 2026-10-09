# Demo skills

Everyday skills with **house rules a general model will not follow on its own**.
That is the demo: without skills you get plausible generic advice; with skills you
get a named protocol, a loaded reference file, and a telltale line you can point at.

No product, platform, or vendor names. Restart the stack after changing these files.

```yaml
skills:
  paths:
    - demo/skills
```

The chatbot has the same prompts as clickable actions. Each reply should include
the telltale below. The UI also lists `list_skills` / `load_skill` /
`read_skill_resource` when those tools run.

## Actions

### 1. Policy the model should not improvise — `allergen-gate`

**Send:**

> I'm making fried chicken and a sesame slaw. My guest is allergic to sesame. If I just leave the slaw off their plate, are they safe?

**Without the skill:** "Yes, if you skip the slaw."

**With the skill:** `Allergen gate: STOP`, cross-contact, do not cook the slaw
this meal. It should load `references/gate-rules.md`.

### 2. A procedure, not a guess — `split-check`

**Send:**

> We have $86 food, $24 drinks, and $9.60 tax. Split among 3 adults and a 10-year-old. What does each person owe?

**Without the skill:** even split of the grand total, or 20% on everything.

**With the skill:** `Split card:`, 18% food / 22% drinks, tax not tipped, kid
skips the tip, adults **$37.00**, kid **$30.00**. It should load
`references/rates.md`.

### 3. A fixed output contract — `now-next-need`

**Send:**

> Turn this into notes: we decided to delay the launch to May, Priya owns the blog post, and the API is still blocked on the vendor.

**Without the skill:** a generic Summary / Action items recap.

**With the skill:** only `## Now`, `## Next`, `## Need`, and footer
`Notes: now-next-need`. It should load `references/template.md`.

### 4. Discovery

**Send:**

> What skills are available?

Expect `list_skills` and the names `allergen-gate`, `split-check`, `now-next-need`.

### 5. Negative control (no domain skill)

**Send:**

> Why is the sky blue?

Expect no `load_skill` for the three skills above. The model may still call
`list_skills` to check the catalog.
