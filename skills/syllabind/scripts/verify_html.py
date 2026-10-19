"""Open an exported course in headless Chromium with ALL network blocked and check that it works offline.

usage:  python verify_html.py <export-folder> [--search WORD] [--shot screenshot.png]

PASS only if: 0 external requests, 0 failed file loads, 0 page errors, 0 broken images, fonts loaded, every module
section present, and hash navigation, the side rail, the pager, search, the lightbox, "mark complete", the theme
toggle and a 390 px mobile layout (no horizontal scroll on any module) all work.
"""
import argparse
import pathlib
import sys

import _setup  # noqa: F401
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("folder")
ap.add_argument("--search", default=None, help="a word that must give search hits (default: first module title word)")
ap.add_argument("--shot", default=None)
args = ap.parse_args()
folder = pathlib.Path(args.folder).resolve()
htmls = [p for p in folder.glob("*.html") if not p.name.startswith("_")]
if len(htmls) != 1:
    sys.exit(f"expected exactly one course .html in {folder}, found {len(htmls)}")
f = htmls[0]
external, failed, errors, r = [], [], [], {}


def block(route):
    if route.request.url.startswith(("file:", "data:", "blob:")):
        route.continue_()
    else:
        external.append(route.request.url)
        route.abort()


with sync_playwright() as p:
    b = _setup.launch_chromium(p)
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    pg.route("**/*", block)
    pg.on("requestfailed", lambda q: failed.append(q.url))
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(f.as_uri())
    pg.wait_for_timeout(2000)
    ids = pg.eval_on_selector_all("section.view.module", "e=>e.map(x=>x.id)")
    r["title"] = pg.title()
    r["modules"] = len(ids)
    r["fonts"] = pg.evaluate("document.fonts.check('700 16px \"Barlow Condensed\"') && document.fonts.check('16px Roboto')")
    r["contents_rows"] = pg.eval_on_selector_all("#contents-list li", "e=>e.length")
    r["images"] = pg.evaluate("""async()=>{const imgs=[...document.querySelectorAll('img:not(#lightbox-img)')];
      imgs.forEach(i=>i.loading='eager');
      await Promise.all(imgs.map(i=>i.complete?0:new Promise(res=>{i.onload=i.onerror=res})));
      return imgs.length}""")
    r["broken_images"] = pg.evaluate("[...document.querySelectorAll('img:not(#lightbox-img)')].filter(i=>!i.naturalWidth).map(i=>i.src)")
    first, last = ids[0], ids[-1]
    pg.goto(f.as_uri() + "#" + last); pg.wait_for_timeout(500)
    r["hash_nav"] = pg.eval_on_selector("#" + last, "e=>e.classList.contains('active')")
    pg.click(f"#rail a[href='#{first}']"); pg.wait_for_timeout(500)
    r["rail_click"] = pg.eval_on_selector("#" + first, "e=>e.classList.contains('active')")
    if len(ids) > 1:
        pg.click(f"#{first} .pager a.next"); pg.wait_for_timeout(500)
        r["pager_next"] = pg.eval_on_selector("#" + ids[1], "e=>e.classList.contains('active')")
    word = args.search or pg.eval_on_selector(f"#{first} h1", "e=>e.textContent.split(/\\s+/).find(w=>w.length>3)||e.textContent")
    pg.fill("#search", word); pg.wait_for_timeout(400)
    r["search_word"] = word
    r["search_hits"] = pg.eval_on_selector_all("#results a[href]", "e=>e.length")
    if r["search_hits"]:
        pg.click("#results a[href] >> nth=0"); pg.wait_for_timeout(400)
        r["search_click_opens"] = pg.evaluate("document.querySelector('.view.active').id")
    figs = [i for i in ids if pg.eval_on_selector_all(f"#{i} .fig-open", "e=>e.length")]
    if figs:
        pg.goto(f.as_uri() + "#" + figs[0]); pg.wait_for_timeout(400)
        pg.click(f"#{figs[0]} .fig-open >> nth=0"); pg.wait_for_timeout(300)
        r["lightbox"] = pg.evaluate("document.getElementById('lightbox').open")
        pg.keyboard.press("Escape")
    pg.goto(f.as_uri() + "#" + first); pg.wait_for_timeout(300)
    pg.click(f"#{first} .done-btn"); pg.wait_for_timeout(200)
    r["mark_complete"] = pg.eval_on_selector(f"#{first} .done-btn", "e=>e.getAttribute('aria-pressed')") == "true"
    pg.click(f"#{first} .done-btn")
    pg.click("#theme-btn"); pg.wait_for_timeout(200)
    r["theme_toggle"] = pg.evaluate("document.documentElement.getAttribute('data-theme')")
    if args.shot:
        pg.screenshot(path=args.shot)
    mob = b.new_page(viewport={"width": 390, "height": 844})
    mob.route("**/*", block)
    mob.goto(f.as_uri()); mob.wait_for_timeout(800)
    wide = []
    for mid in ["home"] + ids:                              # every module must fit a phone without sideways scrolling
        mob.goto(f.as_uri() + "#" + mid); mob.wait_for_timeout(350)
        if not mob.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"):
            wide.append(mid)
    r["mobile_no_hscroll"] = not wide
    r["mobile_wide_modules"] = wide
    b.close()

for k, v in r.items():
    print(f"{k}: {v}")
print("external requests:", len(external), external[:5])
print("failed file loads:", len(failed), failed[:5])
print("page errors:", len(errors), errors[:5])
checks = [not external, not failed, not errors, not r["broken_images"], r["fonts"], r["modules"] == r["contents_rows"],
          r["hash_nav"], r["rail_click"], r.get("pager_next", True), r["search_hits"] > 0, r.get("lightbox", True),
          r["mark_complete"], r["theme_toggle"] in ("dark", "light"), r["mobile_no_hscroll"]]
print("RESULT:", "PASS" if all(checks) else "FAIL")
sys.exit(0 if all(checks) else 1)
