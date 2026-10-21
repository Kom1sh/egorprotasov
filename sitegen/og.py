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

from .hero import LOGO as LOGO_SVG
from .text import esc, plain

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#000"/>
<g fill="#f4f4f2"><rect x="14" y="16" width="10" height="34"/><rect x="14" y="16" width="27" height="9"/>
<rect x="14" y="28" width="22" height="8"/><rect x="14" y="41" width="27" height="9"/></g>
<circle cx="49" cy="45" r="5.5" fill="#bfe828"/>
</svg>
"""

OG_CSS = """*{box-sizing:border-box}html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:#000}
body{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,sans-serif;color:#f4f4f2;-webkit-font-smoothing:antialiased;
padding:62px 72px;display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:16px;font-size:25px;color:#9a9a9a}
.top svg{width:44px;height:44px}
.top svg g{fill:#f4f4f2}
.top b{color:#fff;font-weight:600}
h1{font-size:76px;line-height:1;letter-spacing:-.04em;font-weight:800;margin:40px 0 20px;max-width:1010px}
p{font-size:31px;line-height:1.3;color:#a8a8a6;margin:0;max-width:900px}
svg.tr{position:absolute;right:72px;bottom:62px;width:470px;height:170px;overflow:visible}
svg.tr path{fill:none;stroke-width:4;stroke-linecap:round;stroke-linejoin:round}
.url{margin-top:auto;font-size:23px;color:#6f6f6f}"""


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


SW_CSS = """*{box-sizing:border-box}html,body{margin:0;width:1200px;height:630px;overflow:hidden}
body{position:relative;color:#f4f4f2;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,sans-serif;
-webkit-font-smoothing:antialiased;background:radial-gradient(110% 90% at 85% 0%,color-mix(in srgb,var(--prog) 50%,#000) 0%,
color-mix(in srgb,var(--prog) 16%,#000) 45%,#000 75%)}
.t{position:absolute;left:64px;top:62px;width:560px}
.lbl{display:flex;align-items:center;gap:12px;margin:0;font-size:17px;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:#9aa95c}
.lbl:before{content:"";width:28px;height:1.5px;background:#bfe828}
h1{margin:24px 0 22px;font-size:96px;line-height:.92;letter-spacing:-.05em;font-weight:800;color:#fff}
.pr{margin:0;font-size:27px;line-height:1.34;color:#e2e2e0}
.url{position:absolute;left:64px;bottom:44px;font-size:20px;color:#8a8a88}
.shot{position:absolute;left:660px;top:72px;width:640px;border-radius:14px;overflow:hidden;background:#121316;
box-shadow:0 40px 80px rgba(0,0,0,.6),0 0 0 1px rgba(255,255,255,.12)}
.shot .v{position:relative}
.shot img{position:absolute;display:block}"""


def software(root, programs):
    """Превью посадочных программ: название, обещание и настоящий кадр на фоне цвета программы."""
    from .software import figure_geometry
    root = pathlib.Path(root)
    out = root / "assets" / "og"
    out.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="og-sw-"))
    for p in programs:
        f = p["figs"][p["hero"]]
        im = figure_geometry(f)["img"]
        src_img = (root / "src" / "img" / f"{f['img']}.png").as_uri()
        shot = (f'<div class="shot"><div class="v" style="aspect-ratio:{f["cam"]["w"]}/{f["cam"]["h"]}">'
                f'<img src="{src_img}" alt="" style="width:{im["width"]:.3f}%;left:{im["left"]:.3f}%;top:{im["top"]:.3f}%">'
                f'</div></div>')
        html = (f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><style>{SW_CSS}</style></head>'
                f'<body style="--prog:{p["color"]}"><div class="t"><p class="lbl">Своя программа</p>'
                f'<h1>{esc(p["title"])}</h1><p class="pr">{esc(plain(p["promise"]))}</p></div>{shot}'
                f'<div class="url">egorprotasov.ru/projects/{p["slug"]}/</div></body></html>')
        src = tmp / f"{p['slug']}.html"
        src.write_text(html, encoding="utf-8")
        _render(src, out / f"{p['slug']}.png", 1200, 630)
        subprocess.run(["sips", "-s", "format", "png", str(out / f"{p['slug']}.png")], capture_output=True, check=True)
        print(f"  превью: assets/og/{p['slug']}.png")
    shutil.rmtree(tmp, ignore_errors=True)


def build(root, site, projects, traces):
    root = pathlib.Path(root)
    out = root / "assets" / "og"
    out.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="og-src-"))

    pages = [("home", "Егор Протасов", "Свои проекты и клиентские кейсы на данных Search Console и Яндекс.Метрики",
              traces.get("home"), "egorprotasov.ru")]
    for p in projects:
        pages.append((p["slug"], plain(p["title"]), plain(p["row"]).capitalize(), traces.get(p["slug"]),
                      f"egorprotasov.ru/projects/{p['slug']}/"))

    for slug, title, sub, tr, url in pages:
        top = ('<div class="top">' + LOGO_SVG + '<span><b>Егор Протасов</b>'
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
    icon_html.write_text('<!doctype html><html><body style="margin:0;background:#000">'
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
