"""A tiny SVG kit for course diagrams: nodes, decisions, outcome tiles, pills and arrows.

usage (from a figures script):  sys.path.insert(0, "<skill>/scripts"); from svgkit import Svg
    s = Svg(1200, 400, "Pipeline"); s.node(40, 60, 220, 90, "Write", ["Markdown modules"], actor="info"); ...
    open("img/dg-pipeline.svg", "w").write(s.svg())

Nodes: white cards with a coloured actor bar; decisions: amber-edged cards with a '?' chip;
outcomes: solid tiles. Colours are plain hex values, so the file looks the same inlined in the HTML,
printed in the PDF and shown as an image in Markdown notes. Edit C to match your course theme.
"""
import html

C = {
    "ink": "#212121", "ink2": "#454A52", "muted": "#6B717A", "rule": "#D5D9DF", "soft": "#F3F4F6",
    "paper": "#FFFFFF", "info": "#2F5BD3", "ok": "#12A08C", "neutral": "#4A4F57", "red": "#D3302F",
    "amber": "#F5A300", "good": "#12A08C", "bad": "#D3302F",
}
DISPLAY = "'Barlow Condensed','Arial Narrow',Arial,sans-serif"
LABEL = "'Roboto Condensed','Arial Narrow',Arial,sans-serif"
BODY = "Roboto,Arial,sans-serif"


def col(name):
    return C.get(name, name)


def esc(s):
    return html.escape(str(s), quote=True)


class Svg:
    def __init__(self, w, h, title, grid=True, key="d"):
        self.w, self.h, self.title, self.k = w, h, title, key
        self.parts = []
        if grid:
            self.parts.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>'
                              f'<rect width="{w}" height="{h}" fill="url(#{key}-dots)"/>')
        else:
            self.parts.append(f'<rect width="{w}" height="{h}" fill="{C["paper"]}"/>')

    # ---------- primitives
    def text(self, x, y, s, size=14, weight=400, color="ink", anchor="start", font=LABEL, upper=False, italic=False):
        s = s.upper() if upper else s
        st = ' font-style="italic"' if italic else ""
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
                          f'fill="{col(color)}" text-anchor="{anchor}"{st}>{esc(s)}</text>')

    def lines(self, x, y, rows, size=13, lh=None, **kw):
        lh = lh or size * 1.3
        for i, r in enumerate(rows):
            self.text(x, y + i * lh, r, size=size, **kw)

    def rect(self, x, y, w, h, fill="paper", stroke="rule", sw=1.5, r=10, dash=None, opacity=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{col(fill)}" '
                          f'fill-opacity="{opacity}" stroke="{col(stroke)}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill, stroke="none", sw=0):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col(fill)}" stroke="{col(stroke)}" stroke-width="{sw}"/>')

    def raw(self, s):
        self.parts.append(s)

    # ---------- composites
    def node(self, x, y, w, h, title, sub=(), actor="info", tag=None, fill="paper"):
        self.parts.append(f'<g><title>{esc(title)}</title>')
        self.rect(x + 2, y + 3, w, h, fill="#000000", stroke="none", opacity=0.06)
        self.rect(x, y, w, h, fill=fill, stroke="rule")
        self.parts.append(f'<path d="M{x + 10},{y} h6 v{h} h-6 a10,10 0 0 1 -10,-10 v-{h - 20} a10,10 0 0 1 10,-10z" fill="{col(actor)}"/>')
        ty = y + 26 if sub else y + h / 2 + 7
        self.text(x + 20, ty, title, size=19, weight=700, font=DISPLAY, upper=True)
        self.lines(x + 20, ty + 20, sub, size=13, color="ink2")
        if tag:
            tw = len(tag) * 6.8 + 16
            self.rect(x + w - tw - 8, y + 8, tw, 20, fill=actor, stroke="none", r=10)
            self.text(x + w - tw / 2 - 8, y + 22, tag, size=11, weight=700, color="#FFFFFF", anchor="middle")
        self.parts.append("</g>")

    def decision(self, x, y, w, h, rows):
        self.rect(x, y, w, h, fill="#FFF8E6", stroke="amber", sw=2)
        self.circle(x + 20, y + h / 2, 12, "amber")
        self.text(x + 20, y + h / 2 + 5, "?", size=15, weight=700, anchor="middle", color="ink")
        n = len(rows)
        self.lines(x + 40, y + h / 2 - (n - 1) * 8.5 + 5, rows, size=14, weight=700, lh=17)

    def tile(self, x, y, w, h, rows, kind="ok", sub=()):
        self.rect(x, y, w, h, fill=kind, stroke="none")
        n = len(rows) + len(sub)
        yy = y + h / 2 - (n - 1) * 9 + 6
        self.lines(x + w / 2, yy, rows, size=17, weight=700, lh=18, color="#FFFFFF", anchor="middle", font=DISPLAY, upper=True)
        self.lines(x + w / 2, yy + len(rows) * 18, sub, size=12, lh=15, color="#FFFFFF", anchor="middle")

    def pill(self, x, y, text, fill="paper", color="ink", stroke="rule", size=12, anchor="middle"):
        w = len(text) * size * 0.52 + 16
        x0 = x - w / 2 if anchor == "middle" else x
        self.rect(x0, y - size, w, size * 1.75, fill=fill, stroke=stroke, sw=1, r=size * 0.9)
        self.text(x0 + w / 2, y + size * 0.32, text, size=size, weight=700, color=color, anchor="middle")

    def arrow(self, pts, color="ink2", label=None, dash=False, both=False, lpos=0.5, width=2, lfill="paper"):
        c = col(color)
        mid = {"ink2": "a", "info": "b", "ok": "c", "red": "d", "amber": "e", "neutral": "f", "muted": "g"}.get(color, "a")
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        da = ' stroke-dasharray="6 5"' if dash else ""
        ms = f' marker-start="url(#{self.k}-s{mid})"' if both else ""
        self.parts.append(f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{width}" stroke-linejoin="round" '
                          f'marker-end="url(#{self.k}-m{mid})"{ms}{da}/>')
        if label:
            # label on the longest segment
            segs = list(zip(pts, pts[1:]))
            (x0, y0), (x1, y1) = max(segs, key=lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1]))
            lx, ly = x0 + (x1 - x0) * lpos, y0 + (y1 - y0) * lpos
            self.pill(lx, ly + 4, label, fill=lfill, color=color if color != "ink2" else "ink", stroke=color)

    def svg(self):
        marks = ""
        for k, c in {"a": C["ink2"], "b": C["info"], "c": C["ok"], "d": C["red"], "e": C["amber"], "f": C["neutral"], "g": C["muted"]}.items():
            marks += (f'<marker id="{self.k}-m{k}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                      f'<path d="M1,1 L9,5 L1,9 z" fill="{c}"/></marker>'
                      f'<marker id="{self.k}-s{k}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                      f'<path d="M1,1 L9,5 L1,9 z" fill="{c}"/></marker>')
        defs = (f'<defs>{marks}<pattern id="{self.k}-dots" width="22" height="22" patternUnits="userSpaceOnUse">'
                f'<circle cx="2" cy="2" r="1.1" fill="#E3E6EA"/></pattern></defs>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" height="{self.h}" '
                f'role="img" aria-label="{esc(self.title)}"><title>{esc(self.title)}</title>{defs}{"".join(self.parts)}</svg>')
