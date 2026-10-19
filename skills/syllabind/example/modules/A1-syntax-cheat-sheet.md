---
id: A1
title: Syntax cheat sheet
level: Reference
duration_min: 5
objectives:
  - Write every block the template understands
  - Add a source line under a table
  - Link to another module or section
  - Keep it open while writing
---

!!! facts "At a glance"
    - **Python-Markdown** + admonition, tables, attr_list
    - **`!!! kind "Title"`** for boxes, body indented 4 spaces
    - **`{: .srcline }`** after a table's source line
    - **`#M01`** links to a module

## A1.1 Blocks

| You write | You get |
|---|---|
| `## 2.1 Title` | a section heading (also in the right-hand contents and search) |
| `![Fig 2.1 — Caption](img/sc-x.webp)` | a framed figure with number, kind badge, caption and source line |
| numbered list right after a figure | the callout key under the figure |
| `!!! facts "At a glance"` + 4 bullets | four fact tiles; `**bold**` part becomes the big number |
| `!!! tip`, `caution`, `note`, `limit`, `safety` | coloured boxes |
| `!!! summary "In one screen"` | the dark summary panel |
| `<details><summary>Q…</summary>answer</details>` | a self-check question with a "Show answer" toggle |
| `Source: …` then `{: .srcline }` on the next line | a small grey source line under a table |
| `[text](#M01)` or `[text](#m01-11-a-screenshot-…)` | link to a module or a section |

Source: `scripts/build.py` (Markdown extensions and post-processing)
{: .srcline }

## Sources

- Python-Markdown documentation — <https://python-markdown.github.io/extensions/>
