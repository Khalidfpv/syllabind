# Verification

A course is done only when all of this passes. Report the results (and anything not verified) when delivering.

## 1. Build — `problems 0`
`python scripts/build.py <course>` lists every problem: missing image, missing source, unknown figure prefix,
bad or missing front matter, level not in tracks, duplicate id, unfilled template placeholder.

## 2. Offline HTML — `RESULT: PASS`
`python scripts/verify_html.py <out> [--search WORD] [--shot shot.png]` opens the course in headless Chromium with
**all network blocked** and checks: 0 external requests, 0 failed loads, 0 page errors, 0 broken images, fonts
loaded, contents rows = modules, hash navigation, rail, pager, search (+ click), lightbox, mark complete, theme toggle,
and no horizontal scroll at 390 px on **every** module (a long unbreakable URL or identifier is the usual cause).

## 3. PDF — `RESULT: PASS` and a visual look
`python scripts/check_pdf.py "<out>/<Title>.pdf" --course <course> --render <course>/build/qa 1,2,3,7,12`
checks A4 size, objects outside the print margins, figures split by a page break, **headings stranded at the bottom of a page**
(reported as `ORPHAN`), literal "MISSING" text, and that every module start is found. Then **open the rendered PNGs** and look for: cut-off diagrams, unreadable text on dark
boxes, orphan headings at a page bottom, figures too small to read.

## 4. Content review
- Every annotated figure: callout count and order = its list.
- Every fact table has a source line; every module has `## Sources`.
- No guessed facts — unknowns are written as `!!! limit "Not confirmed"`.
- Spelling of UI labels matches the application exactly.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `no source for x.webp` | add `x:` under `images:` in `sources.yaml`, or a per-kind default |
| `unknown prefix` | add the prefix to `figure_kinds` or rename the file |
| module page not found in PDF | kicker text must be unique per module; do not change `ui.module` between build and export |
| PDF figure cut by a page break | make it smaller (`width` in annotate.yaml) or split the section |
| fonts missing in PDF | run `python -m playwright install chromium`; keep `assets/fonts/` next to the HTML |
| text in `<details>` shows backticks | answers are raw HTML: use `<code>…</code>` |
| playwright error on Linux | `python -m playwright install-deps chromium` |
| "Missing Python packages" / "Chromium is not installed" | run the two commands the message prints (they use the same Python that ran the script) |
| `ORPHAN heading` in check_pdf | add or move content so the heading and its first paragraph share a page, then re-export |
| mobile check names a module | find the long unbreakable text in that module (URL, path, identifier) and put it in `code` or a link |
