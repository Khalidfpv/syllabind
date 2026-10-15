"""Build a course: <course>/modules/*.md + course.yaml -> <course>/build/index.html.

usage:  python build.py <course-dir>

Module files: modules/M00-slug.md ... modules/M12-slug.md, appendices modules/A1-slug.md ...
Figures:      ![Fig N.M — caption](img/<prefix>-<name>.webp|.png|.jpg|.svg)
              <prefix> is a figure kind from course.yaml (figure_kinds:), e.g. sc screenshot, ph photo, dg diagram.
              Every figure needs a source line (sources.yaml); the build fails without one when require_sources is true.
A numbered list placed right after a figure becomes the "keys" list that explains the figure's numbered callouts.
"""
import html
import json
import pathlib
import re
import sys

import markdown
import yaml
from PIL import Image

KIT = pathlib.Path(__file__).resolve().parent.parent
ID_RE = re.compile(r"^(M\d{2}|A\d+)-")


def load_course(cdir):
    cfg = yaml.safe_load((cdir / "course.yaml").read_text(encoding="utf-8"))
    for key in ("title", "slug", "tracks", "figure_kinds"):
        if key not in cfg:
            sys.exit(f"course.yaml: missing '{key}'")
    cfg.setdefault("ui", {})
    ui = {"module": "Module", "appendix": "Appendix", "modules": "modules", "study_time": "study time",
          "goals": "After this module you can", "minutes": "min"}
    ui.update(cfg["ui"])
    cfg["ui"] = ui
    for t in cfg["tracks"]:
        t["slug"] = re.sub(r"[^a-z0-9]+", "-", t["name"].lower()).strip("-")
    src_file = cdir / cfg.get("sources_file", "sources.yaml")
    cfg["_sources"] = yaml.safe_load(src_file.read_text(encoding="utf-8")) if src_file.exists() else {}
    return cfg


def read_module(path, levels):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw, re.S)
    if not m:
        sys.exit(f"{path.name}: missing front matter")
    meta = yaml.safe_load(m.group(1)) or {}
    for key in ("id", "title", "level", "duration_min", "objectives"):
        if key not in meta:
            sys.exit(f"{path.name}: front matter lacks '{key}'")
    if meta["level"] not in levels:
        sys.exit(f"{path.name}: level '{meta['level']}' is not a track in course.yaml ({', '.join(levels)})")
    if not path.name.startswith(meta["id"] + "-"):
        sys.exit(f"{path.name}: file name must start with its id '{meta['id']}-'")
    return meta, m.group(2)


def slugger(prefix):
    def slugify(value, separator):
        s = re.sub(r"[^\w\s-]", "", value).strip().lower()
        return f"{prefix}-" + re.sub(r"[\s_-]+", "-", s)
    return slugify


def esc(s):
    return html.escape(str(s))


class Builder:
    def __init__(self, cdir):
        self.cdir = cdir
        self.cfg = load_course(cdir)
        self.missing = []

    # ---------------------------------------------------------------- figures
    def source_html(self, stem, kind):
        src = self.cfg["_sources"] or {}
        item = (src.get("images") or {}).get(stem)
        if item is None and kind in (src.get("defaults") or {}):
            item = src["defaults"][kind]
        if item is None:
            return ""
        if isinstance(item, str):
            item = {"credit": item}
        parts = [esc(item.get("credit", ""))]
        if item.get("note"):
            parts.append(esc(item["note"]))
        urls = item.get("urls") or ([item["url"]] if item.get("url") else [])
        if urls:
            parts.append("Source: " + " · ".join(f'<a href="{esc(u)}">{esc(u)}</a>' for u in urls))
        return '<span class="fig-src">' + " · ".join(p for p in parts if p) + "</span>"

    def inline_svg(self, path):
        return re.sub(r"^<\?xml[^>]*>\s*", "", path.read_text(encoding="utf-8"))

    def figure_html(self, alt, src, mid):
        name = src.split("/")[-1]
        path = self.cdir / "img" / name
        if not path.exists():
            self.missing.append(f"{mid}: missing image {name}")
            return f"<p>MISSING {esc(name)}</p>"
        prefix = name.split("-")[0]
        kind = self.cfg["figure_kinds"].get(prefix)
        if kind is None:
            self.missing.append(f"{mid}: {name} has unknown prefix '{prefix}' (add it to figure_kinds)")
            kind = {"label": "Figure", "frame": "light"}
        label, _, caption = alt.partition("—")
        srch = self.source_html(name.rsplit(".", 1)[0], prefix)
        if not srch and self.cfg.get("require_sources", True):
            self.missing.append(f"{mid}: no source for {name} (add it to sources.yaml)")
        color = kind.get("color", "var(--ink-2)")
        cap = (f'<span class="fig-no">{esc(label.strip())}</span><span class="fig-kind" style="--c:{color}">{esc(kind["label"])}</span>'
               f'<span>{esc(caption.strip())}</span>{srch}')
        classes = ["fig", prefix, kind.get("frame", "light")] + (["outlined"] if kind.get("outlined") else [])
        if name.endswith(".svg"):
            return (f'<figure class="{" ".join(classes)}"><div class="frame">{self.inline_svg(path)}</div>'
                    f'<figcaption>{cap}</figcaption></figure>')
        w, h = Image.open(path).size
        if h / w > 0.85:
            classes.append("tall")
        img = f'<img loading="lazy" src="img/{name}" width="{w}" height="{h}" alt="{esc(alt)}">'
        return (f'<figure class="{" ".join(classes)}"><button class="fig-open" type="button" aria-label="Open full size: {esc(alt)}">'
                f'<div class="frame">{img}</div></button><figcaption>{cap}</figcaption></figure>')

    # ---------------------------------------------------------------- modules
    def render(self, meta, body):
        mid = meta["id"]
        md = markdown.Markdown(extensions=["admonition", "tables", "attr_list", "md_in_html", "sane_lists", "toc"],
                               extension_configs={"toc": {"slugify": slugger(mid.lower()), "toc_depth": "2-2"}})
        out = md.convert(body)
        out = re.sub(r'<p>\s*<img alt="([^"]*)" src="([^"]+)"\s*/?>\s*</p>',
                     lambda m: self.figure_html(html.unescape(m.group(1)), m.group(2), mid), out)

        def keys(m):
            n = m.group(2).count("<li>")
            return f'{m.group(1)}<ol class="keys{" one" if n <= 2 else ""}">{m.group(2)}</ol>'
        out = re.sub(r"(</figure>\s*)<ol>(.*?)</ol>", keys, out, flags=re.S)
        out = re.sub(r"<table>", '<div class="table-wrap"><table>', out).replace("</table>", "</table></div>")
        out = re.sub(r'<h2 id="([^"]+)">Sources</h2>', r'<h2 id="\1" class="srcs">Sources</h2>', out)
        return out, md.toc_tokens

    @staticmethod
    def plain(t):
        t = re.sub(r"<svg.*?</svg>", " ", t, flags=re.S)
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()

    def search_entries(self, meta, html_text):
        # one entry for the module itself (so its title is searchable), then one per ## section
        entries = [{"m": meta["id"], "id": meta["id"], "t": meta["title"], "x": " ".join(meta["objectives"])}]
        current = None
        for part in re.split(r'(<h2[^>]*id="[^"]+"[^>]*>.*?</h2>)', html_text):
            h = re.match(r'<h2[^>]*id="([^"]+)"[^>]*>(.*?)</h2>', part)
            if h:
                current = {"m": meta["id"], "id": h.group(1), "t": self.plain(h.group(2)), "x": ""}
                entries.append(current)
            elif current is not None:
                current["x"] = (current["x"] + " " + self.plain(part))[:700]
        return entries

    def kicker(self, meta):
        ui, mid = self.cfg["ui"], meta["id"]
        if mid.startswith("M"):
            return f"{ui['module'].upper()} {mid[1:]} · {meta['level'].upper()}"
        return f"{ui['appendix'].upper()} {mid} · {meta['level'].upper()}"

    def module_section(self, m):
        meta, ui = m["meta"], self.cfg["ui"]
        lv, mid = meta["level"], meta["id"]
        slug = next(t["slug"] for t in self.cfg["tracks"] if t["name"] == lv)
        num = mid[1:] if mid.startswith("M") else mid
        goals = "".join(f"<li>{esc(o)}</li>" for o in meta["objectives"])
        toc_items = "".join(f'<li><a href="#{t["id"]}">{esc(t["name"])}</a></li>' for t in m["toc"])
        counts = "".join(f"<span>{n} {esc(lbl)}</span>" for lbl, n in m["counts"].items() if n)
        return (f'<section class="view module" id="{mid}" data-level="{esc(lv)}" aria-hidden="true" style="--c:var(--t-{slug})">'
                f'<header class="mhead"><div class="mhead-in"><div class="bignum" aria-hidden="true">{num}</div>'
                f'<p class="kicker">{esc(self.kicker(meta))}</p><h1>{esc(meta["title"])}</h1>'
                f'<div class="meta"><span>{meta["duration_min"]} {esc(ui["minutes"])}</span>{counts}</div>'
                f'<p class="goals-label">{esc(ui["goals"])}</p><ul class="goals">{goals}</ul></div></header>'
                f'<div class="page prose">{m["html"]}</div>'
                f'<footer class="mfoot"><button class="done-btn" type="button" data-module="{mid}">Mark module complete</button>'
                f'<nav class="pager"></nav></footer><template class="module-toc"><ul>{toc_items}</ul></template></section>')

    # ---------------------------------------------------------------- page
    def theme_css(self):
        th = self.cfg.get("theme") or {}
        names = {"accent": "--accent", "accent2": "--accent2", "info": "--info", "ok": "--ok", "panel": "--panel"}
        light = ";".join(f"{names[k]}:{v}" for k, v in th.items() if k in names)
        dark = ";".join(f"{names[k]}:{v}" for k, v in (th.get("dark") or {}).items() if k in names) or light
        tracks = ";".join(f'--t-{t["slug"]}:{t["color"]}' for t in self.cfg["tracks"])
        css = f":root{{{tracks}{';' + light if light else ''}}}"
        if dark:
            css += (f'@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{{dark}}}}}'
                    f':root[data-theme="dark"]{{{dark}}}')
        return f"<style>{css}</style>"

    def brand(self):
        b = self.cfg.get("brand") or {}
        logo = ""
        if b.get("logo"):
            p = self.cdir / b["logo"]
            logo = self.inline_svg(p) if p.suffix == ".svg" else f'<img src="{esc(b["logo"])}" alt="">'
        text = f'<span>{esc(b.get("text", ""))}<b>{esc(b.get("accent", ""))}</b></span>' if b.get("text") else ""
        return logo + text, (f'<div class="cover-logo">{logo}</div>' if logo else "")

    def figure_block(self, rel):
        if not rel:
            return ""
        p = self.cdir / rel
        if not p.exists():
            self.missing.append(f"course.yaml: missing image {rel}")
            return ""
        if p.suffix == ".svg":
            return f'<figure class="fig light"><div class="frame">{self.inline_svg(p)}</div></figure>'
        return f'<figure class="cover-hero"><img src="{esc(rel)}" alt=""></figure>'

    def legend(self):
        kinds = "".join(f'<div style="--c:{k.get("color", "#16181B")}"><i>{esc(k.get("badge", p.upper()))}</i>{esc(k.get("legend", k["label"]))}</div>'
                        for p, k in self.cfg["figure_kinds"].items())
        tracks = "".join(f'<div style="--c:var(--t-{t["slug"]})"><i>{esc(t["name"][:1])}</i>{esc(t["name"])} — {esc(t.get("blurb", ""))}</div>'
                         for t in self.cfg["tracks"])
        return (f'<h3 class="display" style="margin:26px 0 4px;font-size:22px">Reading the figures</h3>'
                f'<div class="legend">{kinds}</div><div class="legend">{tracks}</div>')

    def build(self):
        cfg = self.cfg
        levels = [t["name"] for t in cfg["tracks"]]
        paths = sorted((self.cdir / "modules").glob("M*.md")) + sorted((self.cdir / "modules").glob("A*.md"))
        if not paths:
            sys.exit("no modules found in modules/")
        modules, index, ids = [], [], set()
        for path in paths:
            meta, body = read_module(path, levels)
            if meta["id"] in ids:
                sys.exit(f"duplicate module id {meta['id']}")
            ids.add(meta["id"])
            html_body, toc = self.render(meta, body)
            index += self.search_entries(meta, html_body)
            prose = re.sub(r"```.*?```|`[^`\n]*`", "", body, flags=re.S)        # ignore example syntax in code
            names = re.findall(r"\]\(img/([\w.-]+)\)", prose)
            counts = {}
            for st in cfg.get("stats", []):
                counts[st["label"]] = sum(1 for n in names if n.split("-")[0] in st["kinds"])
            modules.append({"meta": meta, "html": html_body, "toc": toc, "names": names, "counts": counts})
        cover, overview = cfg.get("cover") or {}, cfg.get("overview") or {}
        extra = [x for x in (cover.get("hero"), overview.get("figure")) if x]
        all_names = sorted({n for m in modules for n in m["names"]} | {pathlib.Path(x).name for x in extra})
        stats = [{"label": st["label"], "n": sum(1 for n in all_names if n.split("-")[0] in st["kinds"])} for st in cfg.get("stats", [])]
        data = {"title": cfg["title"], "storage_key": cfg["slug"], "appendix_prefix": "A", "ui": cfg["ui"],
                "modules": [{"id": m["meta"]["id"], "title": m["meta"]["title"], "level": m["meta"]["level"],
                             "duration": m["meta"]["duration_min"], "figures": len(m["names"])} for m in modules],
                "levels": levels, "tracks": [{"name": t["name"], "slug": t["slug"], "blurb": t.get("blurb", "")} for t in cfg["tracks"]],
                "stats": stats, "pages": {}}
        brand, cover_logo = self.brand()
        meta_spans = "".join(f"<span>{esc(x)}</span>" for x in cover.get("meta", []))
        hero = self.figure_block(cover.get("hero"))
        if hero and "cover-hero" not in hero:
            hero = hero.replace('class="fig light"', 'class="cover-hero"')
        fill = {
            "TITLE": esc(cfg["title"]), "BRAND": brand, "COVER_LOGO": cover_logo,
            "SEARCH_PLACEHOLDER": esc(cfg.get("search_placeholder", "Search the course")),
            "COVER_KICKER": esc(cover.get("kicker", "")), "COVER_TITLE": esc(cover.get("title", cfg["title"])),
            "COVER_SUBTITLE": esc(cover.get("subtitle", "")), "COVER_LEDE": esc(cover.get("lede", "")),
            "COVER_HERO": hero, "COVER_META": meta_spans,
            "CONTENTS_KICKER": esc((cfg.get("contents") or {}).get("kicker", "Contents")),
            "CONTENTS_TITLE": esc((cfg.get("contents") or {}).get("title", "What is inside")),
            "CONTENTS_SUB": esc((cfg.get("contents") or {}).get("sub", "")),
            "OVERVIEW_KICKER": esc(overview.get("kicker", "Course overview")),
            "OVERVIEW_TITLE": esc(overview.get("title", "How the course fits together")),
            "OVERVIEW_SUB": esc(overview.get("sub", "")), "OVERVIEW_FIGURE": self.figure_block(overview.get("figure")),
            "LEGEND": self.legend(), "DISCLAIMER": esc(cfg.get("disclaimer", "")),
        }
        page = (KIT / "templates" / "template.html").read_text(encoding="utf-8")
        for k, v in fill.items():
            page = page.replace("{{" + k + "}}", v)
        left = re.findall(r"\{\{[A-Z_]+\}\}", page)
        if left:
            sys.exit(f"template placeholders not filled: {left}")
        page = page.replace("</style>", "</style>\n" + self.theme_css(), 1)   # course theme overrides the template tokens
        page = (page.replace("/*__DATA__*/null", json.dumps(data)).replace("/*__INDEX__*/null", json.dumps(index))
                    .replace("<!--__SECTIONS__-->", "\n".join(self.module_section(m) for m in modules)))
        out = self.cdir / "build"
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(page, encoding="utf-8")
        (out / "used_images.json").write_text(json.dumps(all_names), encoding="utf-8")
        (out / "modules.json").write_text(json.dumps([{"id": m["meta"]["id"], "level": m["meta"]["level"],
                                                       "kicker": self.kicker(m["meta"])} for m in modules]), encoding="utf-8")
        print(f"modules {len(modules)}  images {len(all_names)}  page {(out / 'index.html').stat().st_size / 1024:.0f} KB  "
              f"search {len(index)}  problems {len(self.missing)}")
        for miss in self.missing:
            print("  PROBLEM", miss)
        return 1 if self.missing else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(Builder(pathlib.Path(sys.argv[1]).resolve()).build())
