"""Фото из src/img → assets/img: WebP и JPEG нужных ширин, разметка <picture>.

Нужны системные sips (macOS) и cwebp (brew install webp). Готовые файлы
пересобираются, только если исходник новее.
"""
import pathlib
import re
import subprocess

from .text import esc

# ширины, которые реально используются в вёрстке (1x и 2x)
WIDTHS = {
    "egor": [192, 384],
    "winners": [600],
    "track": [800, 1280],
}


def _dims(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
                         capture_output=True, text=True, check=True).stdout
    w = int(re.search(r"pixelWidth: (\d+)", out).group(1))
    h = int(re.search(r"pixelHeight: (\d+)", out).group(1))
    return w, h


def build(src_dir, out_dir):
    src_dir, out_dir = pathlib.Path(src_dir), pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {}
    for src in sorted(src_dir.iterdir()):
        name = src.stem
        if name not in WIDTHS:
            continue
        w0, h0 = _dims(src)
        meta[name] = {"ratio": h0 / w0, "widths": []}
        for w in WIDTHS[name]:
            w = min(w, w0)
            meta[name]["widths"].append(w)
            jpg, webp = out_dir / f"{name}-{w}.jpg", out_dir / f"{name}-{w}.webp"
            if not jpg.exists() or jpg.stat().st_mtime < src.stat().st_mtime:
                subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82",
                                "--resampleWidth", str(w), str(src), "--out", str(jpg)],
                               capture_output=True, check=True)
            if not webp.exists() or webp.stat().st_mtime < src.stat().st_mtime:
                subprocess.run(["cwebp", "-quiet", "-q", "80", "-resize", str(w), "0", str(src), "-o", str(webp)],
                               check=True)
    return meta


def picture(meta, name, alt, *, display_w, cls="", eager=False):
    """display_w — ширина в вёрстке в CSS-пикселях; браузер сам выберет 1x или 2x."""
    m = meta[name]
    ws = m["widths"]
    webp = ", ".join(f"/assets/img/{name}-{w}.webp {w}w" for w in ws)
    jpg = ", ".join(f"/assets/img/{name}-{w}.jpg {w}w" for w in ws)
    h = round(display_w * m["ratio"])
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    sizes = f"(max-width: 720px) calc(100vw - 40px), {display_w}px"
    return (f'<picture class="{cls}"><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="/assets/img/{name}-{ws[-1]}.jpg" srcset="{jpg}" sizes="{sizes}" '
            f'width="{display_w}" height="{h}" alt="{esc(alt)}" {load} decoding="async"></picture>')
