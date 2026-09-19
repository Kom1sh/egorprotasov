"""Превью для соцсетей (1200×630) и иконки сайта. Рендер через Google Chrome без интерфейса.

Запускается из build.py с флагом --og. Результат коммитится в репозиторий,
поэтому пересобирать превью нужно только при смене заголовков или данных.
"""
import os
import pathlib
import shutil
import struct
import subprocess
import tempfile
import time

from .text import esc, plain

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#0a6ee0"/>
<path d="M12 46 L22 45 L29 40 L35 30 L42 26 L48 18 L53 15" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="53" cy="15" r="4.5" fill="#fff"/>
</svg>
"""

OG_CSS = """*{box-sizing:border-box}html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:#fff}
body{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,sans-serif;color:#1d1d1f;-webkit-font-smoothing:antialiased;
padding:64px 72px;display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:18px;font-size:26px;color:#6e6e73}
.top img{width:56px;height:70px;object-fit:cover;object-position:50% 18%;border-radius:12px}
.top b{color:#1d1d1f;font-weight:600}
h1{font-size:74px;line-height:1.02;letter-spacing:-.025em;font-weight:600;margin:44px 0 18px;max-width:1000px}
p{font-size:32px;line-height:1.3;color:#6e6e73;margin:0;max-width:880px}
svg.tr{position:absolute;right:72px;bottom:64px;width:470px;height:170px;overflow:visible}
svg.tr path{fill:none;stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
.url{margin-top:auto;font-size:24px;color:#86868b}"""


def _trace_svg(series):
    """Несколько линий в одной системе координат 0..470 × 0..170."""
    allv = [v for s in series for v in s["values"] if v is not None]
    if not allv:
        return ""
    mx = max(allv) or 1
    parts = []
    for s in series:
        vals = s["values"]
        n = len(vals)
        pts, pen = [], False
        for i, v in enumerate(vals):
            if v is None:
                pen = False
                continue
            x, y = 470 * i / (n - 1), 165 - 160 * v / mx
            pts.append(f"{'L' if pen else 'M'}{x:.1f},{y:.1f}")
            pen = True
        parts.append(f'<path d="{" ".join(pts)}" style="stroke:{s["color"]}"/>')
        lx, ly = pts[-1][1:].split(",")
        parts.append(f'<circle cx="{lx}" cy="{ly}" r="7" fill="{s["color"]}"/>')
    return f'<svg class="tr" viewBox="0 0 470 170">{"".join(parts)}</svg>'


def _render(html_path, png_path, w, h):
    """Chrome пишет скриншот и не всегда сам выходит, поэтому ждём файл и завершаем процесс."""
    if png_path.exists():
        png_path.unlink()
    profile = tempfile.mkdtemp(prefix="og-chrome-")
    proc = subprocess.Popen([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
                             f"--user-data-dir={profile}", f"--window-size={w},{h}",
                             f"--screenshot={png_path}", html_path.as_uri()],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < 40:
        if png_path.exists() and png_path.stat().st_size > 0:
            time.sleep(0.5)
            break
        time.sleep(0.3)
    proc.kill()
    shutil.rmtree(profile, ignore_errors=True)
    if not png_path.exists():
        raise RuntimeError(f"Chrome не отрисовал {png_path.name}")


def _ico(png32_path, ico_path):
    """ICO с одной картинкой 32×32 в формате PNG внутри."""
    data = png32_path.read_bytes()
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(data), 6 + 16)
    ico_path.write_bytes(header + entry + data)


def build(root, site, projects, traces):
    root = pathlib.Path(root)
    out = root / "assets" / "og"
    out.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="og-src-"))
    ava = (root / "assets" / "img" / "egor-192.jpg").as_uri()

    pages = [("home", "Егор Протасов", "Свои проекты и клиентские кейсы на данных Search Console и Яндекс.Метрики",
              traces.get("home"), "egorprotasov.ru")]
    for p in projects:
        pages.append((p["slug"], plain(p["title"]), plain(p["row"]).capitalize(), traces.get(p["slug"]),
                      f"egorprotasov.ru/projects/{p['slug']}/"))

    for slug, title, sub, tr, url in pages:
        top = ('<div class="top"><img src="' + ava + '" alt=""><span><b>Егор Протасов</b>'
               + ('' if slug == "home" else ', SEO Lead') + '</span></div>')
        heading = "SEO Lead и проектный менеджер" if slug == "home" else esc(title)
        html = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{OG_CSS}</style></head><body>'
                f'{top}<h1>{heading}</h1><p>{esc(sub)}</p>{_trace_svg(tr) if tr else ""}'
                f'<div class="url">{esc(url)}</div></body></html>')
        src = tmp / f"{slug}.html"
        src.write_text(html, encoding="utf-8")
        _render(src, out / f"{slug}.png", 1200, 630)
        subprocess.run(["sips", "-s", "format", "png", str(out / f"{slug}.png")], capture_output=True, check=True)
        print(f"  превью: assets/og/{slug}.png")

    (root / "favicon.svg").write_text(FAVICON_SVG, encoding="utf-8")
    icon_html = tmp / "icon.html"
    icon_html.write_text('<!doctype html><html><body style="margin:0;background:#fff">'
                         f'<img src="{(root / "favicon.svg").as_uri()}" style="display:block;width:512px;height:512px">'
                         '</body></html>', encoding="utf-8")
    big = tmp / "icon-512.png"
    _render(icon_html, big, 512, 512)
    shutil.copy(big, root / "apple-touch-icon.png")
    subprocess.run(["sips", "-z", "180", "180", str(root / "apple-touch-icon.png")], capture_output=True, check=True)
    small = tmp / "icon-32.png"
    shutil.copy(big, small)
    subprocess.run(["sips", "-z", "32", "32", str(small)], capture_output=True, check=True)
    _ico(small, root / "favicon.ico")
    shutil.rmtree(tmp, ignore_errors=True)
    print("  иконки: favicon.svg, favicon.ico, apple-touch-icon.png")
