---
id: M01
title: Figures, callouts and sources
level: Figures
duration_min: 10
objectives:
  - Name figure files with the right kind prefix
  - Add numbered callouts to a screenshot and explain them in a list
  - Give every figure a source line in sources.yaml
  - Draw a simple diagram with svgkit
---

!!! facts "At a glance"
    - **sc / ph / dg** figure kinds (set in course.yaml)
    - **1 list** under each annotated figure
    - **0** figures without a source
    - **WebP** for screenshots, **SVG** for diagrams

## 1.1 A screenshot with numbered callouts

![Fig 1.1 — A screenshot of the demo app with four numbered callouts.](img/sc-demo-form.webp)

1. **Tab** — where the user clicks first.
2. **Side list** — the section that opens.
3. **Fields** — what to fill in.
4. **Buttons** — confirm or cancel.

The numbered list **directly under** a figure becomes the callout key. Its order must match the red numbers.

## 1.2 How the figure was made

| Step | File | What happens |
|---|---|---|
| Capture | `figures/raw/demo-app.png` | the original screenshot, never edited by hand |
| Describe | `figures/annotate.yaml` | crop, width and one box per callout: `[x0, y0, x1, y1, "1"]` |
| Render | `scripts/annotate.py` | draws the boxes and badges, writes `img/sc-demo-form.webp` |
| Cite | `sources.yaml` | `sc-demo-form: {credit: …, note: …}` |

Source: `figures/annotate.yaml` and `sources.yaml` of this example
{: .srcline }

!!! caution "Measure on the real image"
    Coordinates are pixels of the raw capture. If you measured on a smaller preview, set `scale:` in the spec
    (e.g. `1.6` for a 1600 px preview of a 2560 px capture). Always look at the result before you write the list.

## 1.3 Figure kinds and file names

| Prefix | Kind | Frame | Typical source |
|---|---|---|---|
| `sc-` | Screenshot | dark | app version + capture date |
| `ph-` | Photo | dark | owner + page URL |
| `dg-` | Diagram | light | "Drawn for this course" + the data it shows |

Add your own kinds in `course.yaml › figure_kinds`. The build refuses an unknown prefix.

!!! summary "In one screen"
    - File name = `<kind>-<name>.webp|png|jpg|svg` in `img/`.
    - Numbered list under the figure = callout key, same order as the red numbers.
    - Every figure has an entry in `sources.yaml` (or a per-kind default).
    - Screenshots via `annotate.py`, diagrams via `svgkit.py`.

## Self-check

<details><summary>Q1. The build says "no source for ph-bridge.webp". What do you add?</summary>
An entry <code>ph-bridge: {credit: "Owner", url: "https://…"}</code> under <code>images:</code> in <code>sources.yaml</code>.
</details>

<details><summary>Q2. Your callout 3 points at the wrong field. Where do you fix it?</summary>
In <code>figures/annotate.yaml</code> (the box coordinates), then run <code>annotate.py</code> again.
</details>

## Sources

- `scripts/annotate.py`, `scripts/svgkit.py` and `figures/make_figures.py` of this kit
