# course.yaml reference

`example/course.yaml` is fully commented; this is the summary.

| Key | Required | Purpose |
|---|---|---|
| `title` | yes | page title, PDF and HTML file name |
| `slug` | yes | browser storage key for progress and theme — unique per course |
| `brand.text`, `brand.accent`, `brand.logo` | no | top-left brand; logo = `.svg` (inlined) or `.png` path inside the course |
| `cover.kicker`, `title`, `subtitle`, `lede`, `meta[]` | no | cover texts |
| `cover.hero` | no | image or SVG from `img/` on the cover |
| `contents.sub`, `overview.sub`, `overview.figure` | no | texts and a diagram on the contents / overview sheets |
| `search_placeholder` | no | hint in the search box |
| `disclaimer` | no | small print on the overview sheet |
| `theme.accent`, `accent2`, `info`, `ok`, `panel` | no | colours; `theme.dark:` with the same keys for dark mode |
| `tracks[]` | yes | `{name, color, blurb}`; every module `level:` must be a track name |
| `figure_kinds` | yes | prefix → `{label, frame: dark|light, badge, color, legend, outlined}` |
| `stats[]` | no | `{kinds: [sc, ph], label: images}` — counters on the cover and module headers |
| `sources_file`, `require_sources` | no | default `sources.yaml`, `true` |
| `ui.module`, `ui.appendix`, `ui.goals`, `ui.modules`, `ui.study_time`, `ui.minutes` | no | wording (e.g. for another language) |
| `pdf.footer` | no | footer text on every PDF page |
| `notes.tags` | no | front-matter tags of exported notes |

## Folder layout of a course

```
my-course/
├─ course.yaml
├─ sources.yaml
├─ modules/      M00-….md … A1-….md
├─ figures/      raw/ (original captures), annotate.yaml, make_figures.py
├─ img/          generated figures used by the modules
├─ sources/      research notes, extracts, links (optional, recommended)
└─ build/        generated — do not edit
```
