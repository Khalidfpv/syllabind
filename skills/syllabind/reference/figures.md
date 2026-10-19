# Figures

## Kinds and file names
- Files live in `<course>/img/` and are named `<kind>-<name>.<ext>`, e.g. `sc-export-dialog.webp`, `dg-workflow.svg`.
- `<kind>` must be a key of `course.yaml › figure_kinds` (the build refuses unknown prefixes). Defaults in the example:
  `sc` screenshot (dark frame), `ph` photo (dark frame), `dg` diagram (light frame). Add your own, e.g.
  `ch: {label: Chart, frame: light}` or `tp: {label: Third-party, frame: dark, outlined: true}`.
- Screenshots and photos: **WebP** (or PNG/JPG). Diagrams: **SVG** (inlined, stays sharp in the PDF).

## In a module

```markdown
![Fig 3.2 — Short caption that says what to look at.](img/sc-export-dialog.webp)

1. **Format** — what this control does.
2. **Export** — what happens when you click it.
```

- `Fig N.M` numbers figures per module (N = module number).
- The numbered list **directly** under a figure becomes its callout key. Same count and order as the red numbers.
  A figure without callouts needs no list.

## Screenshots
1. Capture the real application at a large window size (e.g. 2560 px wide). Keep originals in `figures/raw/`, never
   edit them by hand.
2. Describe crops and callouts in `figures/annotate.yaml`:
   ```yaml
   raw_dir: raw
   out_dir: ../img
   scale: 1.0          # 1.6 if you measured on a 1600 px preview of a 2560 px capture
   figures:
     sc-export-dialog:
       raw: export.png
       crop: [400, 200, 1500, 900]
       width: 1200
       boxes:
         - [520, 300, 760, 340, "1"]
         - [1180, 820, 1320, 860, "2"]
   ```
3. `python scripts/annotate.py figures/annotate.yaml` → `img/sc-export-dialog.webp`.
4. **Open the result and check every box** sits on the right control before writing the list.
- Capture the state that matters (menu open, dialog filled in, result visible). Hide personal data.
- Use a dedicated practice project or demo data so screenshots are reproducible.

## Diagrams
```python
import sys; sys.path.insert(0, "<skill>/scripts")
from svgkit import Svg
s = Svg(1200, 320, "How export works")
s.node(30, 80, 240, 100, "Edit", ["timeline"], actor="info", tag="1")
s.node(330, 80, 240, 100, "Export", ["settings"], actor="ok", tag="2")
s.arrow([(272, 130), (328, 130)])
open("img/dg-export-flow.svg", "w", encoding="utf-8").write(s.svg())
```
Primitives: `node`, `decision`, `tile`, `pill`, `arrow`, `rect`, `text`, `lines`, `circle`, `raw`. Keep diagrams simple:
one idea, 3–8 boxes, labels a learner can read at A4 width. Put the script in `figures/` so it can be re-run.

## Sources (`sources.yaml`)
```yaml
defaults:                         # per-kind fallback
  dg: "Drawn for this course"
images:
  sc-export-dialog:
    credit: "Screenshot of Example App 4.2 on Windows, captured 2026-01-15"
  ph-device-front:
    credit: "Example Corp"
    url: "https://example.com/product"
    note: "cropped"
```
- Third-party photos: name the owner and the page you took it from; only crop, resize or adjust brightness — never
  generate or retouch an image that is presented as real.
- The source line is printed under the figure in the HTML, the PDF and the notes.
