"""Rebuild every figure of the example course.

usage:  python figures/make_figures.py        (from the course folder; needs Playwright's Chromium)

1. renders figures/demo-app.html to figures/raw/demo-app.png (the "raw screenshot")
2. annotates it with figures/annotate.yaml  ->  img/sc-demo-form.webp
3. draws the diagrams with svgkit           ->  img/dg-pipeline.svg, img/dg-module-anatomy.svg
In a real course, step 1 is taking screenshots of the real app; steps 2-3 stay the same.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
COURSE = HERE.parent
SKILL = COURSE.parent if (COURSE.parent / "scripts").exists() else None
for cand in (SKILL, *COURSE.parents):
    if cand and (cand / "scripts" / "svgkit.py").exists():
        sys.path.insert(0, str(cand / "scripts"))
        break
else:
    sys.exit("cannot find the skill's scripts/ folder (svgkit.py); set PYTHONPATH to <skill>/scripts")

import _setup                      # noqa: E402,F401
import annotate                    # noqa: E402
from svgkit import Svg             # noqa: E402


def screenshot():
    from playwright.sync_api import sync_playwright
    (HERE / "raw").mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = _setup.launch_chromium(p)
        pg = b.new_page(viewport={"width": 1100, "height": 620})
        pg.goto((HERE / "demo-app.html").as_uri())
        pg.screenshot(path=str(HERE / "raw" / "demo-app.png"))
        b.close()


def pipeline():
    s = Svg(1200, 300, "From Markdown to three outputs")
    steps = [("Write", ["modules/*.md", "course.yaml"], "neutral"), ("Figures", ["annotate.py", "svgkit.py"], "info"),
             ("Build", ["build.py", "→ build/index.html"], "info"), ("Export", ["export.py", "HTML · PDF · notes"], "ok")]
    x = 30
    for i, (t, sub, actor) in enumerate(steps):
        s.node(x, 70, 230, 100, t, sub, actor=actor, tag=f"{i + 1}")
        if i < len(steps) - 1:
            s.arrow([(x + 232, 120), (x + 268, 120)], color="ink2")
        x += 270
    s.tile(300, 210, 600, 60, ["Verify: verify_html.py + check_pdf.py"], kind="ok")
    s.arrow([(1065, 172), (1065, 240), (902, 240)], color="ok")
    return s.svg()


def anatomy():
    s = Svg(1200, 340, "Anatomy of a module")
    parts = [("Front matter", ["id · title · level", "duration · 4 objectives"]), ("At a glance", ["4 fact tiles"]),
             ("Sections N.1 …", ["text · tables", "figures + keys"]), ("In one screen", ["summary box"]),
             ("Self-check", ["2–4 questions"]), ("Sources", ["where facts come from"])]
    for i, (t, sub) in enumerate(parts):
        x, y = 30 + (i % 3) * 390, 40 + (i // 3) * 150
        s.node(x, y, 360, 110, t, sub, actor=["neutral", "info", "info", "ok", "ok", "neutral"][i], tag=str(i + 1))
    return s.svg()


if __name__ == "__main__":
    screenshot()
    annotate.main(HERE / "annotate.yaml")
    img = COURSE / "img"
    img.mkdir(exist_ok=True)
    (img / "dg-pipeline.svg").write_text(pipeline(), encoding="utf-8")
    (img / "dg-module-anatomy.svg").write_text(anatomy(), encoding="utf-8")
    print("dg-pipeline.svg, dg-module-anatomy.svg")
