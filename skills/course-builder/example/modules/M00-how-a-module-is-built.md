---
id: M00
title: How a module is built
level: Basics
duration_min: 10
objectives:
  - Name the six parts every module has, in order
  - Write the front matter so the build accepts the file
  - Use fact tiles, tables and callout boxes
  - Build the course and open the three outputs
---

!!! facts "At a glance"
    - **6** parts per module, always in the same order
    - **4** objectives in the front matter
    - **1** Markdown file per module
    - **3** outputs: HTML, PDF, notes

## 0.1 The six parts

![Fig 0.1 — Every module follows the same skeleton, so learners always know where they are.](img/dg-module-anatomy.svg)

1. **Front matter** — `id`, `title`, `level` (a track from `course.yaml`), `duration_min`, four `objectives`.
2. **At a glance** — a `!!! facts` box with four `- **Number** short label` lines.
3. **Sections** — `## N.1 Title`, `## N.2 …`; short paragraphs, tables, figures.
4. **In one screen** — a `!!! summary "In one screen"` box with the four or five things to remember.
5. **Self-check** — two to four `<details><summary>` questions with the answer inside.
6. **Sources** — where every fact comes from.

## 0.2 Front matter

| Key | Example | Rule |
|---|---|---|
| `id` | `M03` or `A1` | file name must start with it: `M03-speed.md` |
| `title` | `Speed and slow motion` | short, no full stop |
| `level` | `Basics` | one of the `tracks:` names in `course.yaml` |
| `duration_min` | `15` | honest reading + practice time |
| `objectives` | four bullet lines | "After this module you can …" |

Source: `scripts/build.py` (`read_module`) — the build stops with a clear message when a key is missing
{: .srcline }

## 0.3 Boxes

!!! tip "Tip"
    A practical shortcut or habit.

!!! caution "Caution"
    Something that can go wrong, and how to avoid it.

!!! note "Note"
    Background that is useful but not essential.

!!! limit "Not confirmed"
    Say clearly when a source does not state something — never guess.

## 0.4 Build it

![Fig 0.2 — Four steps from Markdown to a checked course.](img/dg-pipeline.svg)

1. **Write** the modules and `course.yaml`.
2. **Figures** — annotate screenshots, draw diagrams.
3. **Build** — `python scripts/build.py <course>` checks every figure and source.
4. **Export** — `python scripts/export.py <course> --dest <out>` writes HTML, PDF and notes; then run both checks.

!!! summary "In one screen"
    - One Markdown file per module, named after its id.
    - Front matter → facts → sections → summary → self-check → sources.
    - Boxes: tip, caution, note, limit, facts, summary.
    - Build, export, then verify the HTML and the PDF.

## Self-check

<details><summary>Q1. The build says "level 'Advanced' is not a track". What do you fix?</summary>
Either add a track named Advanced to <code>course.yaml</code>, or set the module's <code>level</code> to an existing track.
</details>

<details><summary>Q2. Where do the "After this module you can" lines come from?</summary>
The four <code>objectives</code> in the module's front matter.
</details>

## Sources

- `scripts/build.py` and `templates/template.html` of this kit
