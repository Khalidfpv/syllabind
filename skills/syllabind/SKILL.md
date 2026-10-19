---
name: syllabind
description: Create a complete training course on any topic. Research the subject, write the lessons as structured Markdown modules with annotated screenshots, diagrams, self-check questions and cited sources, then build several versions from the same source (a searchable offline HTML course, a print-ready A4 PDF with a real contents page, and Markdown notes). Use when the user asks to create, write, build or update a course, training, tutorial series, handbook or step-by-step guide, to turn notes into a course, or to export a course as HTML and PDF.
license: MIT
compatibility: Python 3.10+ with markdown, pyyaml, pillow, playwright (Chromium), pymupdf, pypdf. Works on Windows, macOS and Linux.
---

# Syllabind

Give it a topic and it produces a complete course. The assistant researches the subject and writes the lessons as Markdown modules (workflow steps 3–5); the scripts then build and check them. One folder of Markdown modules plus one `course.yaml` becomes three outputs from the same source:

| Output | What the learner gets |
|---|---|
| `<Title>.html` | offline web course: cover, contents, side rail, search, figure lightbox, light/dark, "mark complete", mobile layout |
| `<Title>.pdf` | A4 print with a full-bleed cover, a contents page with real page numbers, one module per chapter |
| `notes/*.md` | one Markdown note per module (Obsidian-style callouts; readable in any Markdown viewer) |

All paths below are relative to this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}`).

## Setup (once per machine)

```bash
python -m pip install -r scripts/requirements.txt
python -m playwright install chromium
```

- Needs Python 3.10+. If `python` is not found, use `python3` (macOS, Linux) or `py` (Windows) in every command in this skill.
- If pip refuses with "externally-managed-environment", create a virtual environment and use its Python for every command:
  `python3 -m venv ~/.syllabind-venv`, then `~/.syllabind-venv/bin/python -m pip install -r scripts/requirements.txt`
  (on Windows the interpreter is `%USERPROFILE%\.syllabind-venv\Scripts\python.exe`).
- The Chromium download (about 150 MB) needs internet once. On a bare Linux server also run `python -m playwright install-deps chromium`.
- Smoke test: `python scripts/build.py example` must print `problems 0`. Fix setup before starting a real course.

## Workflow

Copy this checklist into your task list and complete every step in order. Do not skip verification.

1. **Scope.** Agree with the user on: audience and level, the outcome ("after the course you can …"), the 4–12 modules, what is out of scope, and the language. Keep beginner courses short: fewer modules, more figures, less text.
2. **Scaffold.** `python scripts/new_course.py <course-dir> --title "<Title>"` (add `--with-example-content` to start from the sample). Edit `course.yaml`: title, cover texts, tracks (one per part of the course), figure kinds, theme colours. Reference: `reference/config.md`.
3. **Research and evidence.** Collect the sources first (official docs, manuals, the real application). Every number, shortcut, menu path and claim must come from a source you actually read or a screen you actually saw. When a source does not state something, write it as "not confirmed" (`!!! limit`), never guess. Keep raw research notes in `<course>/sources/`.
4. **Figures.** Real screenshots of the real thing, cropped and annotated with numbered callouts (`scripts/annotate.py` + `figures/annotate.yaml`); diagrams drawn with `scripts/svgkit.py`. Every figure gets a source line in `sources.yaml`. Look at every generated figure before using it. Reference: `reference/figures.md`.
5. **Write the modules.** One file per module, `modules/M00-slug.md` … and appendices `A1-slug.md` (cheat sheet, FAQ). Follow the module skeleton and writing rules in `reference/authoring.md`. Explain each annotated figure with a numbered list directly under it, in callout order.
6. **Build.** `python scripts/build.py <course-dir>`. It must report `problems 0` — fix every reported missing image, missing source, unknown figure prefix or bad front matter.
7. **Export.** `python scripts/export.py <course-dir> --dest <output-dir>` (HTML + PDF + notes). It prints the PDF page of every module and fails if one is not found.
8. **Verify — all must pass before you call it done.**
   - `python scripts/verify_html.py <output-dir>` → `RESULT: PASS` (offline, no external requests, search, navigation, lightbox, theme, mobile).
   - `python scripts/check_pdf.py "<output-dir>/<Title>.pdf" --course <course-dir> --render <course-dir>/build/qa 1,2,3,<a few module pages>` → `RESULT: PASS`, then **look at the rendered pages** (cover, contents, a figure-heavy page, a table page).
   - Re-read every module once for facts without a source and callout lists that do not match their figure.
   Reference: `reference/verification.md`.
9. **Deliver.** Hand over the output folder (HTML must stay next to `assets/`). Report what was verified and what was not, honestly — including any "not confirmed" items.

## Rules that make the result professional

- **One skeleton for every module:** front matter → `!!! facts` (4 tiles) → numbered sections `## N.1` → `!!! summary "In one screen"` → `## Self-check` → `## Sources`.
- **Pictures first, words second.** A figure for every procedure; tables for comparisons; short sentences.
- **Numbered callouts match their list** exactly (number, order, wording of the control).
- **Every figure and fact table has a source.** The build refuses figures without one.
- **No invented UI.** Menu names, button labels and shortcuts are copied from the real application or its manual.
- **Neutral, self-contained output.** No external fonts, scripts or images — the HTML works offline from a USB stick.
- **Never claim it works without running the checks.** If something could not be verified, say so in the delivery note.

## Files in this skill

| Path | Purpose |
|---|---|
| `scripts/new_course.py` | scaffold a course folder from the example |
| `scripts/build.py` | modules + course.yaml → `build/index.html` (validates everything) |
| `scripts/export.py` | → offline HTML, two-pass A4 PDF, Markdown notes |
| `scripts/annotate.py` | screenshots → cropped figures with numbered callouts |
| `scripts/svgkit.py` | small library for clean SVG diagrams |
| `scripts/verify_html.py`, `scripts/check_pdf.py` | automated checks for the two outputs |
| `templates/template.html`, `templates/print.css` | page design (web and print) |
| `assets/fonts/` | bundled open-licence fonts (offline) |
| `example/` | a complete two-module sample course — build it to see every feature |
| `reference/*.md` | detailed rules: authoring, figures, config, verification |
