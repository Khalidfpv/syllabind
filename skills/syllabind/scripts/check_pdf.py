"""PDF layout checks with PyMuPDF: A4 size, image placements, module starts and overflow outside the print margins.

usage:  python check_pdf.py <file.pdf> [--course <course-dir>] [--render <out-dir> 1,3,9]

Every image, vector drawing and text block must lie inside the A4 page with the 13 mm print margin (2 mm tolerance),
except on the full-bleed cover (page 1). With --course, every module kicker from build/modules.json must be found.
A heading stranded at the bottom of a page (its content starts on the next page) is reported as ORPHAN.
--render writes PNGs of the listed pages so you can look at them.
"""
import argparse
import json
import pathlib
import re
import sys

import _setup  # noqa: F401
import pymupdf as fitz

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("--course", default=None)
ap.add_argument("--render", nargs=2, metavar=("DIR", "PAGES"), default=None)
args = ap.parse_args()
MM = 72 / 25.4
doc = fitz.open(args.pdf)
w, h = doc[0].rect.width / MM, doc[0].rect.height / MM

def orphan_headings(page):
    """Headings (>= 14 pt) in the bottom band of a page with no body content below them (before the footer)."""
    H = page.rect.height
    footer_top = H - 16 * MM
    found = []
    for blk in page.get_text("dict")["blocks"]:
        for line in blk.get("lines", []):
            size = max((sp["size"] for sp in line["spans"]), default=0)
            text = "".join(sp["text"] for sp in line["spans"]).strip()
            y1 = line["bbox"][3]
            if size < 14 or not text or y1 < H - 45 * MM or y1 > footer_top:
                continue
            below = [b for b in page.get_text("blocks") if b[1] > y1 + 2 and b[1] < footer_top]
            below += [i for i in page.get_image_info() if i["bbox"][1] > y1 + 2]
            below += [d for d in page.get_drawings() if d["rect"].y0 > y1 + 2 and d["rect"].y0 < footer_top
                      and d["rect"].width < page.rect.width * 0.95]
            if not below:
                found.append(text[:60])
    return found

imgs, overflow, touching, orphans = 0, [], [], []
m, tol = 13 * MM, 2 * MM
for n, page in enumerate(doc, 1):
    R = page.rect
    inner = fitz.Rect(m - tol, m - tol, R.width - m + tol, R.height - 15 * MM + tol + 8 * MM)   # footer sits in the bottom margin
    infos = page.get_image_info()
    imgs += len(infos)
    if n == 1:
        continue
    orphans += [(n, t) for t in orphan_headings(page)]
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
for o in orphans:
    print("  ORPHAN heading at the bottom of page", o[0], "->", o[1])
print("orphan headings:", len(orphans))
print("literal 'MISSING' text:", text.count("MISSING"))
ok = doc.page_count > 0 and round(w) == 210 and round(h) == 297 and not overflow and not orphans and "MISSING" not in text and starts_ok
if args.render:
    out = pathlib.Path(args.render[0])
    out.mkdir(parents=True, exist_ok=True)
    for pnum in [int(x) for x in args.render[1].split(",")]:
        if 1 <= pnum <= doc.page_count:
            doc[pnum - 1].get_pixmap(dpi=110).save(str(out / f"page-{pnum:03d}.png"))
    print("rendered pages to", out)
print("RESULT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
