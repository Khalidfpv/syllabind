"""PDF layout checks with PyMuPDF: A4 size, image placements, module starts and overflow outside the print margins.

usage:  python check_pdf.py <file.pdf> [--course <course-dir>] [--render <out-dir> 1,3,9]

Every image, vector drawing and text block must lie inside the A4 page with the 13 mm print margin (2 mm tolerance),
except on the full-bleed cover (page 1). With --course, every module kicker from build/modules.json must be found.
--render writes PNGs of the listed pages so you can look at them.
"""
import argparse
import json
import pathlib
import re
import sys

import fitz

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("--course", default=None)
ap.add_argument("--render", nargs=2, metavar=("DIR", "PAGES"), default=None)
args = ap.parse_args()
MM = 72 / 25.4
doc = fitz.open(args.pdf)
w, h = doc[0].rect.width / MM, doc[0].rect.height / MM
imgs, overflow, touching = 0, [], []
m, tol = 13 * MM, 2 * MM
for n, page in enumerate(doc, 1):
    R = page.rect
    inner = fitz.Rect(m - tol, m - tol, R.width - m + tol, R.height - 15 * MM + tol + 8 * MM)   # footer sits in the bottom margin
    infos = page.get_image_info()
    imgs += len(infos)
    if n == 1:
        continue
    for info in infos:
        bb = fitz.Rect(info["bbox"])
        if not inner.contains(bb):
            overflow.append((n, "image", [round(v / MM, 1) for v in bb]))
        if abs(bb.y0 - m) < 0.6 * MM and n > 2 and bb.height < 20 * MM:
            touching.append((n, "image starts on the top margin, maybe split", round(bb.height / MM, 1)))
    for d in page.get_drawings():
        bb = d["rect"] & R
        white = d.get("fill") and min(d["fill"]) > 0.98 and not d.get("color")
        if bb.is_empty or white:
            continue
        if not inner.contains(bb):
            overflow.append((n, "drawing", [round(v / MM, 1) for v in bb]))
    for blk in page.get_text("blocks"):
        if not inner.contains(fitz.Rect(blk[:4])):
            overflow.append((n, "text", blk[4][:40].replace("\n", " ")))
text = "".join(p.get_text() for p in doc)
starts_ok, found = True, {}
if args.course:
    mods = json.loads((pathlib.Path(args.course) / "build" / "modules.json").read_text(encoding="utf-8"))
    flat = [re.sub(r"\s+", "", p.get_text()).upper() for p in doc]
    for mo in mods:
        k = re.sub(r"\s+", "", mo["kicker"]).upper()
        found[mo["id"]] = next((i + 1 for i, t in enumerate(flat) if k in t), None)
    starts_ok = all(found.values())
print(f"pages {doc.page_count}  size {w:.0f}x{h:.0f} mm  image placements {imgs}")
if found:
    print("module start pages:", found)
print(f"overflowing objects {len(overflow)}  images starting on the top margin {len(touching)}")
for o in overflow[:20]:
    print("  OVERFLOW", o)
for o in touching[:10]:
    print("  CHECK", o)
print("literal 'MISSING' text:", text.count("MISSING"))
ok = doc.page_count > 0 and round(w) == 210 and round(h) == 297 and not overflow and "MISSING" not in text and starts_ok
if args.render:
    out = pathlib.Path(args.render[0])
    out.mkdir(parents=True, exist_ok=True)
    for pnum in [int(x) for x in args.render[1].split(",")]:
        if 1 <= pnum <= doc.page_count:
            doc[pnum - 1].get_pixmap(dpi=110).save(str(out / f"page-{pnum:03d}.png"))
    print("rendered pages to", out)
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
