"""Turn raw screenshots into course figures: crop, numbered callout boxes, resize, save as WebP.

usage:  python annotate.py <spec.yaml>

spec.yaml (paths are relative to the spec file):
  raw_dir: figures/raw          # where the original captures are
  out_dir: img                  # where figures are written
  scale: 1.0                    # multiply every coordinate (e.g. 1.6 if you measured on a 1600 px preview of a 2560 px capture)
  figures:
    sc-settings-page:           # output name -> img/sc-settings-page.webp
      raw: settings.png
      crop: [0, 0, 1200, 800]   # optional, x0 y0 x1 y1 in raw pixels (before scale)
      width: 1400               # optional max output width (default 1600)
      boxes:                    # optional; label numbers must match the list under the figure in the module
        - [40, 60, 300, 110, "1"]
        - [320, 60, 600, 110, "2"]

Box style: rounded red outline with a white-ringed numbered badge at the top-left corner. Stroke width and badge size
are scaled so they look the same after resizing.
"""
import pathlib
import sys

import yaml
from PIL import Image, ImageDraw, ImageFont

RED = (230, 57, 70)
FONTS = ["C:/Windows/Fonts/segoeuib.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans-Bold.ttf", "arialbd.ttf"]


def font(size):
    for f in FONTS:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make(raw_path, out_path, crop=None, boxes=(), width=1600, scale=1.0, color=RED):
    im = Image.open(raw_path).convert("RGB")
    d = ImageDraw.Draw(im)
    crop_px = [round(v * scale) for v in crop] if crop else None
    k = ((crop_px[2] - crop_px[0]) if crop_px else im.width) / width     # keep strokes and badges constant after resize
    k = max(k, 1.0)
    sw, r, f = max(3, round(4 * k)), round(17 * k), font(round(22 * k))
    for x0, y0, x1, y1, label in boxes:
        x0, y0, x1, y1 = (round(v * scale) for v in (x0, y0, x1, y1))
        d.rounded_rectangle([x0, y0, x1, y1], radius=round(8 * k), outline=color, width=sw)
        if label:
            cx = max(x0 - r // 2 if x0 > r else x0 + r, r + 2)
            cy = max(y0 - r // 2 if y0 > r else y0 + r, r + 2)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color, outline=(255, 255, 255), width=max(2, sw // 2))
            d.text((cx, cy), str(label), fill="white", font=f, anchor="mm")
    if crop_px:
        im = im.crop(tuple(crop_px))
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.Resampling.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, quality=84, method=6)
    return im.size


def main(spec_path):
    spec_path = pathlib.Path(spec_path).resolve()
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    base = spec_path.parent
    raw_dir, out_dir = base / spec.get("raw_dir", "figures/raw"), base / spec.get("out_dir", "img")
    scale = float(spec.get("scale", 1.0))
    for name, fig in (spec.get("figures") or {}).items():
        size = make(raw_dir / fig["raw"], out_dir / f"{name}.webp", fig.get("crop"), fig.get("boxes") or [],
                    fig.get("width", 1600), scale)
        print(f"{name}.webp {size[0]}x{size[1]}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
