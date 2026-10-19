"""Make the README showcase images from a built and exported course.

usage:  python tools/make_readme_images.py <export-folder> [--out docs/images]

<export-folder> is the output of export.py for the sample course (the .html and .pdf side by side). Writes
  showcase-web.webp   desktop window (light theme) + phone (dark theme), real renders in mockup frames
  showcase-pdf.webp   a fan of A4 pages from the PDF
Everything is a real render of the course; nothing is drawn by hand.
"""
import argparse
import pathlib
import sys
import tempfile

import pymupdf as fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from playwright.sync_api import sync_playwright

FONTS = ["C:/Windows/Fonts/segoeui.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf"]
BG1, BG2, ACCENT, ACCENT2 = (22, 23, 27), (38, 41, 47), (211, 48, 47), (245, 163, 0)


def font(size):
    for f in FONTS:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def backdrop(w, h):
    """Dark gradient with a dot grid and two soft colour glows, matching the repository banner."""
    t = np.linspace(0, 1, h)[:, None, None]
    base = np.array(BG1, dtype="float32") * (1 - t) + np.array(BG2, dtype="float32") * t
    base = np.broadcast_to(base, (h, w, 3)).copy()
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([w * 0.62, -h * 0.30, w * 1.10, h * 0.30], fill=tuple(c // 5 for c in ACCENT))
    g.ellipse([-w * 0.12, h * 0.80, w * 0.30, h * 1.30], fill=tuple(c // 8 for c in ACCENT2))
    glow = glow.filter(ImageFilter.GaussianBlur(h * 0.10))
    im = Image.fromarray(np.clip(base + np.asarray(glow, dtype="float32"), 0, 255).astype("uint8"))
    d = ImageDraw.Draw(im)
    for y in range(24, h, 48):
        for x in range(24, w, 48):
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(58, 61, 68))
    return im


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius, fill=255)
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def with_shadow(canvas, layer, xy, blur=40, offset=(0, 28), opacity=150):
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    alpha = layer.split()[-1].point(lambda v: v * opacity // 255)
    shape = Image.new("RGBA", layer.size, (0, 0, 0, 255))
    shape.putalpha(alpha)
    sh.paste(shape, (xy[0] + offset[0], xy[1] + offset[1]), shape)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    canvas.alpha_composite(sh)
    canvas.alpha_composite(layer, xy)


def browser_window(shot, title, scale=1.0):
    """Wrap a screenshot in a window frame with a title bar and an address pill."""
    bar = 64
    body = shot.convert("RGB")
    win = Image.new("RGB", (body.width, body.height + bar), (42, 44, 49))
    win.paste(body, (0, bar))
    d = ImageDraw.Draw(win)
    for i, c in enumerate([(229, 83, 75), (224, 169, 58), (67, 181, 129)]):
        d.ellipse([28 + i * 36, 22, 28 + i * 36 + 20, 42], fill=c)
    f = font(26)
    pill_w = min(900, body.width - 300)
    x0 = (body.width - pill_w) // 2
    d.rounded_rectangle([x0, 12, x0 + pill_w, bar - 12], 20, fill=(28, 29, 33))
    d.text((body.width // 2, bar // 2), title, fill=(190, 194, 201), font=f, anchor="mm")
    win = rounded(win, 30)
    if scale != 1.0:
        win = win.resize((round(win.width * scale), round(win.height * scale)), Image.Resampling.LANCZOS)
    return win


def phone(shot, height):
    ratio = height / shot.height
    shot = shot.convert("RGB").resize((round(shot.width * ratio), height), Image.Resampling.LANCZOS)
    pad = 18
    frame = Image.new("RGBA", (shot.width + 2 * pad, shot.height + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle([0, 0, frame.width - 1, frame.height - 1], 78, fill=(10, 10, 12), outline=(70, 73, 80), width=4)
    frame.alpha_composite(rounded(shot, 62), (pad, pad))
    d.rounded_rectangle([frame.width // 2 - 70, pad + 12, frame.width // 2 + 70, pad + 34], 11, fill=(10, 10, 12))
    return frame


def capture(html, tmp):
    paths = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 960, "height": 640}, device_scale_factor=2, color_scheme="light")
        pg = ctx.new_page()
        pg.goto(html.as_uri() + "#M01")
        pg.wait_for_timeout(1200)
        pg.evaluate("document.documentElement.style.scrollBehavior = 'auto'")      # the page scrolls smoothly by default
        pg.evaluate("window.scrollTo(0, document.querySelector('#m01-11-a-screenshot-with-numbered-callouts').getBoundingClientRect().top + window.scrollY - 92)")
        pg.wait_for_timeout(600)
        paths["desktop"] = tmp / "desktop.png"
        pg.screenshot(path=str(paths["desktop"]))
        ctx.close()
        m = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, color_scheme="dark",
                          is_mobile=True, has_touch=True)
        pg = m.new_page()
        pg.goto(html.as_uri() + "#M01")
        pg.wait_for_timeout(1200)
        paths["phone"] = tmp / "phone.png"
        pg.screenshot(path=str(paths["phone"]))
        b.close()
    return paths


def web_image(paths, title, out):
    w, h = 2400, 1500
    canvas = backdrop(w, h).convert("RGBA")
    win = browser_window(Image.open(paths["desktop"]), title)
    with_shadow(canvas, win, (70, 110))
    ph = phone(Image.open(paths["phone"]), 1180)
    with_shadow(canvas, ph, (w - ph.width - 60, 250), blur=36, offset=(-8, 24))
    canvas.convert("RGB").save(out, quality=90, method=6)


def pdf_image(pdf, out):
    doc = fitz.open(pdf)
    pages = [doc[i].get_pixmap(dpi=170) for i in (0, 3, 6) if i < doc.page_count]
    imgs = [Image.frombytes("RGB", (p.width, p.height), p.samples) for p in pages]
    w, h = 2400, 1400
    canvas = backdrop(w, h).convert("RGBA")
    spec = [(-5, 0.60, 470, 190), (5, 0.60, 1930, 215), (0, 0.66, 1200, 100)]        # angle, scale to canvas height, x, y
    order = [0, 1, 2] if len(imgs) == 3 else range(len(imgs))
    for i in order:
        angle, s, x, y = spec[i]
        page = imgs[i].resize((round(imgs[i].width * (h * s / imgs[i].height) * 1.55),
                               round(imgs[i].height * (h * s / imgs[i].height) * 1.55)), Image.Resampling.LANCZOS)
        layer = rounded(page, 10)
        layer = layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        with_shadow(canvas, layer, (x - layer.width // 2, y), blur=34, offset=(0, 22), opacity=170)
    canvas.convert("RGB").save(out, quality=90, method=6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("export_folder")
    ap.add_argument("--out", default="docs/images")
    a = ap.parse_args()
    folder = pathlib.Path(a.export_folder).resolve()
    html = next(p for p in folder.glob("*.html") if not p.name.startswith("_"))
    pdf = next(folder.glob("*.pdf"))
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        paths = capture(html, pathlib.Path(t))
        web_image(paths, html.name, out / "showcase-web.webp")
    pdf_image(pdf, out / "showcase-pdf.webp")
    print("wrote", out / "showcase-web.webp", out / "showcase-pdf.webp")


if __name__ == "__main__":
    sys.exit(main())
