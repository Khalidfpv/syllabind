# Authoring rules

## Course shape
- **4–12 modules** (`M00`…), plus optional appendices (`A1` cheat sheet, `A2` FAQ / troubleshooting).
- `M00` orients the learner (what the course covers, key vocabulary, how to read it). The last module is usually a
  hands-on recipe or capstone that uses everything before it.
- Group modules into **tracks** (`course.yaml › tracks`), e.g. Basics → Core → Advanced → Reference. Each module's
  `level:` is a track name. Tracks give the colour of the module header and the rail.
- Durations are honest reading + practice time (10–30 min per module).

## Module skeleton (always in this order)

```markdown
---
id: M03
title: Short title without a full stop
level: Core
duration_min: 20
objectives:                # exactly four, each starting with a verb, "After this module you can …"
  - Do the first thing
  - Do the second thing
  - Do the third thing
  - Do the fourth thing
---

!!! facts "At a glance"
    - **3** short fact (the bold part becomes the big number)
    - **Ctrl+S** works for keys too
    - **2 min** or durations
    - **0** or limits

## 3.1 First section          # N.x numbering; N = module number without the leading zero

## 3.2 Second section

!!! summary "In one screen"
    - The four or five things to remember.

## Self-check

<details><summary>Q1. Question?</summary>
Answer. Use <code>…</code> for code inside answers (raw HTML block).
</details>

## Sources

- Title of the document — URL (date read)
```

## Writing style
- Short sentences, active voice, second person ("Click **Export**").
- **Bold** the exact label of every button, menu and field, copied from the real UI.
- Menu paths with `›`: **File › Export › PDF**.
- Keyboard shortcuts as `Ctrl+Shift+S`; state the platform if they differ.
- Prefer a table to a paragraph when comparing options; prefer a figure to a table when showing a procedure.
- One idea per section; a section longer than one screen probably needs a figure or a split.
- Beginner courses: remove anything the learner does not need for the stated objectives.

## Boxes

| Syntax | Use for |
|---|---|
| `!!! tip "Title"` | a habit or shortcut that saves time |
| `!!! caution "Title"` | a common mistake and how to avoid it |
| `!!! note "Title"` | background, optional |
| `!!! safety "Title"` | risk to people, data or equipment |
| `!!! limit "Not confirmed"` | the source does not state it — say so, do not guess |
| `!!! facts "At a glance"` | the four tiles at the top of a module |
| `!!! summary "In one screen"` | the recap at the end of a module |

Box bodies are indented **4 spaces**.

## Evidence
- Every number, limit, shortcut, menu path and claim comes from a source you read or a screen you saw.
- Put a source line under fact tables:
  ```markdown
  Source: Product manual v2, p. 41 · https://example.com/specs
  {: .srcline }
  ```
- List everything used in the module's `## Sources`.
- If two sources disagree, use the newer one and mention the difference.

## Links
- To a module: `[text](#M03)`. To a section: `[text](#m03-32-second-section)` (module id in lower case + slugified heading).
