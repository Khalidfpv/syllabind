"""Export a built course into a self-contained folder: offline HTML, A4 PDF and Markdown notes.

usage:  python build.py <course-dir>  &&  python export.py <course-dir> --dest <output-folder> [--no-pdf] [--no-notes]

Writes into --dest:
  <title>.html          offline web course (local fonts, inline SVG, local images, no network needed)
  <title>.pdf           A4 print, printed twice so the contents page carries real page numbers
  notes/NN - Title.md   one Markdown note per module (Obsidian-style callouts; readable in any Markdown viewer)
  assets/img, assets/fonts
The PDF is printed by Playwright's Chromium (Windows, macOS, Linux):
  pip install playwright && python -m playwright install chromium
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import sys

import yaml

KIT = pathlib.Path(__file__).resolve().parent.parent
CALLOUTS = {"note": ("Note", "note"), "tip": ("Tip", "tip"), "caution": ("Caution", "warning"), "safety": ("Safety", "danger"),
            "limit": ("Not confirmed", "failure"), "facts": ("At a glance", "abstract"), "summary": ("In one screen", "success")}
BASE_CSS = "html,body{margin:0}img{max-width:100%}[hidden]{display:none!important}"
PRINT_CSS = (KIT / "templates" / "print.css").read_text(encoding="utf-8")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def safe(title):
    return re.sub(r'[\\/:*?"<>|]', "-", title).strip()


def document(page, fonts_css, printing, footer, pages=None):
    """Wrap the built page in a full HTML document; printing=True gives the PDF variant."""
    split = page.index('<header class="topbar">')
    head, body = page[:split], page[split:]
    head = head.replace('src="img/', 'src="assets/img/')
    body = body.replace('src="img/', 'src="assets/img/')
    if pages is not None:
        body = body.replace('"pages": {}', '"pages": ' + json.dumps(pages))
    if printing:
        body = body.replace(' loading="lazy"', "").replace('src="assets/img/', 'src="_print_img/')
        body = re.sub(r'(src="_print_img/[^"]+)\.(webp|png)"', r'\1.jpg"', body)
    theme = ' data-theme="light" data-print="1"' if printing else ""
    extra = "<script>document.querySelectorAll('details').forEach(function(d){d.open=true;});</script>" if printing else ""
    pcss = PRINT_CSS.replace("__FOOTER__", footer.replace('"', "'")) if printing else ""
    return ("<!doctype html>\n<html lang=\"en\"%s>\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            "<style>%s\n%s</style>\n%s%s\n</head>\n<body>\n%s%s\n</body>\n</html>\n") % (
        theme, BASE_CSS, fonts_css, head, f"<style>{pcss}</style>" if printing else "", body, extra)


def notes_body(body, sources):
    """Python-Markdown admonitions -> Obsidian callouts; image paths -> ../assets/img; source line under each image."""
    lines, out, i = body.split("\n"), [], 0
    while i < len(lines):
        m = re.match(r'^(\s*)!!!\s+(\w+)(?:\s+"(.*)")?\s*$', lines[i])
        if not m:
            out.append(lines[i]); i += 1; continue
        indent, kind = m.group(1), m.group(2)
        label, ob = CALLOUTS.get(kind, (kind.title(), "note"))
        out.append(f"{indent}> [!{ob}] {m.group(3) or label}")
        i += 1
        inner = indent + "    "
        while i < len(lines) and (lines[i].startswith(inner) or lines[i].strip() == ""):
            if lines[i].strip() == "" and (i + 1 >= len(lines) or not lines[i + 1].startswith(inner)):
                break
            out.append(f"{indent}> " + lines[i][len(inner):] if lines[i].strip() else f"{indent}>")
            i += 1
    text = "\n".join(out).replace("](img/", "](../assets/img/")
    text = re.sub(r"\n\{: \.srcline \}", "", text)

    def rep(m):
        stem = m.group(2).rsplit("/", 1)[-1].rsplit(".", 1)[0]
        item = (sources.get("images") or {}).get(stem) or (sources.get("defaults") or {}).get(stem.split("-")[0])
        if not item:
            return m.group(0)
        if isinstance(item, str):
            item = {"credit": item}
        url = item.get("url") or (item.get("urls") or [None])[0]
        return m.group(0) + "\n*" + item.get("credit", "") + (f" · Source: <{url}>" if url else "") + "*"
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", rep, text)


def module_starts(pdf_path, kickers):
    """Find the page on which each module's kicker ("MODULE 03 · BASICS") appears."""
    import fitz
    doc = fitz.open(pdf_path)
    starts = {}
    for n in range(doc.page_count):
        t = re.sub(r"\s+", "", doc[n].get_text()).upper()      # kickers are letter-spaced in the PDF text layer
        for mid, kick in kickers.items():
            if mid not in starts and re.sub(r"\s+", "", kick).upper() in t:
                starts[mid] = n + 1
    return starts


def print_pdf(html_path, pdf_path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(html_path.resolve().as_uri(), wait_until="load")
        pg.evaluate("document.fonts.ready.then(() => true)")
        pg.wait_for_timeout(800)
        pg.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
        b.close()


def main():
    ap = argparse.ArgumentParser(description="Export a built course (run build.py first).")
    ap.add_argument("course")
    ap.add_argument("--dest", required=True)
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--no-notes", action="store_true")
    args = ap.parse_args()
    cdir, dest = pathlib.Path(args.course).resolve(), pathlib.Path(args.dest).resolve()
    cfg = yaml.safe_load((cdir / "course.yaml").read_text(encoding="utf-8"))
    src_file = cdir / cfg.get("sources_file", "sources.yaml")
    sources = (yaml.safe_load(src_file.read_text(encoding="utf-8")) if src_file.exists() else None) or {}
    name = safe(cfg["title"])
    footer = (cfg.get("pdf") or {}).get("footer", cfg["title"])
    build = cdir / "build"
    if not (build / "index.html").exists():
        sys.exit("run build.py first")
    page = (build / "index.html").read_text(encoding="utf-8")
    used = json.loads((build / "used_images.json").read_text(encoding="utf-8"))
    mods = json.loads((build / "modules.json").read_text(encoding="utf-8"))

    for sub in ("assets/img", "assets/fonts"):
        (dest / sub).mkdir(parents=True, exist_ok=True)
    for n in used:
        shutil.copy2(cdir / "img" / n, dest / "assets" / "img" / n)
    logo = (cfg.get("brand") or {}).get("logo")
    if logo and not logo.endswith(".svg"):                         # raster logos are linked, SVG logos are inlined
        (dest / pathlib.Path(logo).parent).mkdir(parents=True, exist_ok=True)
        shutil.copy2(cdir / logo, dest / logo)
    fonts = KIT / "assets" / "fonts"
    for f in fonts.iterdir():
        shutil.copy2(f, dest / "assets" / "fonts" / f.name)
    fonts_css = (fonts / "fonts.css").read_text(encoding="utf-8").replace("url(", "url(assets/fonts/")
    html_path = dest / f"{name}.html"
    html_path.write_text(document(page, fonts_css, False, footer), encoding="utf-8")
    summary = {"html": str(html_path), "html_sha256": sha256(html_path), "html_bytes": html_path.stat().st_size, "images": len(used)}

    if not args.no_notes:
        (dest / "notes").mkdir(exist_ok=True)
        srcs = sorted((cdir / "modules").glob("M*.md")) + sorted((cdir / "modules").glob("A*.md"))
        notes = []
        for src in srcs:
            _, fm, body = src.read_text(encoding="utf-8").split("---", 2)
            meta = yaml.safe_load(fm)
            meta.update({"tags": (cfg.get("notes") or {}).get("tags", ["course", "lesson"]), "course": cfg["title"]})
            num = meta["id"][1:] if meta["id"].startswith("M") else meta["id"]
            notes.append((meta, body, f"{num} - {safe(meta['title'])}.md"))
        goals_label = (cfg.get("ui") or {}).get("goals", "After this module you can")
        for i, (meta, body, fname) in enumerate(notes):
            prev = f"[[{notes[i - 1][2][:-3]}|← {notes[i - 1][0]['id']}]]" if i else ""
            nxt = f"[[{notes[i + 1][2][:-3]}|{notes[i + 1][0]['id']} →]]" if i + 1 < len(notes) else ""
            front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=200)
            goals = f"**{goals_label}**\n" + "\n".join(f"- {o}" for o in meta["objectives"]) + "\n"
            (dest / "notes" / fname).write_text(f"---\n{front}---\n# {meta['id']} — {meta['title']}\n\n{goals}"
                                                + notes_body(body, sources) + f"\n---\n{prev}  ·  {nxt}\n", encoding="utf-8")
        summary["notes"] = len(notes)

    ok = True
    if not args.no_pdf:
        from PIL import Image
        jpg_dir = dest / "_print_img"
        jpg_dir.mkdir(exist_ok=True)
        for n in used:                                              # JPEG copies keep the PDF small
            if not n.endswith(".svg"):
                im = Image.open(cdir / "img" / n)
                if im.mode in ("RGBA", "LA", "P"):
                    im = im.convert("RGBA")
                    bg = Image.new("RGB", im.size, "white")
                    bg.paste(im, mask=im.split()[-1])
                    im = bg
                im.convert("RGB").save(jpg_dir / (n.rsplit(".", 1)[0] + ".jpg"), quality=86)
        pdf_path, print_html = dest / f"{name}.pdf", dest / "_print.html"
        kickers = {m["id"]: m["kicker"] for m in mods}
        print_html.write_text(document(page, fonts_css, True, footer), encoding="utf-8")
        print_pdf(print_html, pdf_path)                             # pass 1: find where modules start
        pages = module_starts(pdf_path, kickers)
        print_html.write_text(document(page, fonts_css, True, footer, pages), encoding="utf-8")
        print_pdf(print_html, pdf_path)                             # pass 2: contents page with page numbers
        pages2 = module_starts(pdf_path, kickers)
        print_html.unlink()
        shutil.rmtree(jpg_dir)
        from pypdf import PdfReader
        summary.update({"pdf": str(pdf_path), "pdf_sha256": sha256(pdf_path), "pdf_bytes": pdf_path.stat().st_size,
                        "pdf_pages": len(PdfReader(str(pdf_path)).pages), "module_pages": pages2,
                        "pages_found": f"{len(pages2)}/{len(mods)}", "pages_stable": pages == pages2})
        ok = len(pages2) == len(mods) and pages == pages2
    (build / "export_summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
