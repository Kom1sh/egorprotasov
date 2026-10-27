"""CV в PDF: одна страница A4 из данных сайта, печать через Google Chrome без интерфейса.

Проекты, результаты и сроки — из src/projects/*.toml, имя и контакты — из src/site.toml,
остальное — из src/cv.toml. Одна колонка: так резюме читают и люди, и парсеры у рекрутёров.
HTML кладётся в .cache/cv/ (в .gitignore); PDF печатается заново, только если HTML изменился.
Без Chrome сборка не падает: остаётся прошлый PDF и предупреждение.
"""
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import time

from .hero import LOGO
from .text import esc, inline

CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SITE = "https://egorprotasov.ru"

CSS = """@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
/* не системный SF Pro: у него кириллическая «е» — тот же глиф, что латинская, и Chrome рвёт текст PDF
   на кусочки (копирование и парсеры резюме получают «про / е / ктный»). Helvetica Neue даёт цельный текст */
body { margin: 0; font-family: "Helvetica Neue", Arial, sans-serif;
  font-size: 8.9pt; line-height: 1.38; color: #141414; -webkit-font-smoothing: antialiased; }
/* без обрезки по краю листа: лишнее уходит на вторую страницу, и сборка это видит */
.page { width: 210mm; min-height: 296mm; padding: 10mm 15mm 7mm; display: flex; flex-direction: column; }
a { color: inherit; text-decoration: none; }
b { font-weight: 650; }
.nw { white-space: nowrap; }
.top { display: flex; justify-content: space-between; align-items: flex-end; gap: 8mm; padding-bottom: 4mm;
  border-bottom: 1.2pt solid #141414; }
.id { display: flex; align-items: center; gap: 4mm; }
.id .mark { flex: none; width: 13mm; height: 13mm; color: #141414; }
h1 { margin: 0; font-size: 22pt; line-height: 1.05; letter-spacing: -.02em; font-weight: 700; }
.role { margin: 1.4mm 0 0; font-size: 10pt; color: #555; }
.contacts { list-style: none; margin: 0; padding: 0; text-align: right; font-size: 8.6pt; line-height: 1.6; }
.contacts a { border-bottom: .4pt solid #c9c9c9; }
section { display: grid; grid-template-columns: 29mm minmax(0, 1fr); gap: 0 5mm; padding: 2.5mm 0;
  border-bottom: .5pt solid #e3e3e3; }
section:last-of-type { border-bottom: 0; }
h2 { margin: .5mm 0 0; font-size: 7.1pt; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: #5b6b08; }
p { margin: 0 0 1.5mm; } p:last-child { margin-bottom: 0; }
ul { margin: 0; padding: 0; list-style: none; }
.job { display: flex; justify-content: space-between; gap: 4mm; margin-bottom: 1.2mm; }
.muted { color: #777; }
.when { color: #777; font-size: 8.2pt; white-space: nowrap; font-variant-numeric: tabular-nums; }
.cases { margin: 1.2mm 0 1.6mm; }
.cases li { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 0 4mm; margin-bottom: .8mm; }
.cases a b { border-bottom: .4pt solid #c9c9c9; }
.dots li { position: relative; padding-left: 4mm; margin-bottom: .6mm; }
.dots li::before { content: ""; position: absolute; left: .3mm; top: .55em; width: 1.5mm; height: 1.5mm;
  background: #bfe828; border: .4pt solid #5b6b08; transform: rotate(45deg); }
.foot { margin-top: auto; padding-top: 2mm; display: flex; justify-content: space-between; font-size: 7.6pt; color: #8a8a8a; }"""


def _contacts(site):
    """Почта, Telegram, ВКонтакте и сайт; телефон не публикуем."""
    keep = ("Почта", "Telegram", "ВКонтакте")
    items = [(c["href"], re.sub(r"^(mailto:|https?://)", "", c["href"])) for c in site["contacts"] if c["label"] in keep]
    items.append((SITE + "/", "egorprotasov.ru"))
    return "".join(f'<li><a href="{esc(h)}">{esc(t)}</a></li>' for h, t in items)


def _case(p, text, when=""):
    link = f'<a href="{SITE}/projects/{p["slug"]}/"><b>{inline(p["title"])}</b></a>'
    return f'<li><span>{link} — {text}</span><span class="when">{esc(when)}</span></li>'


def html(site, cv, own, client, programs, asof):
    person, job, edu, sk = site["person"], cv["job"], cv["education"], cv["skills"]
    about = "".join(f"<p>{inline(t)}</p>" for t in cv["about"])
    cases = "".join(_case(p, inline(p["row"]), p["home_when"]) for p in client)
    duties = "".join(f"<li>{inline(t)}</li>" for t in job["duties"])
    mine = "".join(_case(p, f'{inline(p["what"])}; {inline(p["row"])}') for p in own)
    progs = "".join(_case(p, inline(p["what"])) for p in programs)
    extra = "".join(f"<li>{inline(t)}</li>" for t in edu["extra"])
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><title>{esc(person["name"])} — CV</title><style>{CSS}</style></head>
<body><div class="page">
<header class="top">
  <div class="id">{LOGO}<div><h1>{esc(person["name"])}</h1><p class="role">{inline(person["role_line"])}</p></div></div>
  <ul class="contacts">{_contacts(site)}</ul>
</header>
<section><h2>О себе</h2><div>{about}</div></section>
<section><h2>Опыт</h2><div>
  <p class="job"><span><b>{inline(job["role"])}</b>, {inline(job["place"])} <span class="muted">— {inline(job["note"])}</span></span>
    <span class="when">{esc(job["when"])}</span></p>
  <p>{inline(job["intro"])}</p>
  <ul class="cases">{cases}</ul>
  <ul class="dots">{duties}</ul>
</div></section>
<section><h2>Свои проекты</h2><div><ul class="cases">{mine}</ul></div></section>
<section><h2>Свои программы</h2><div><ul class="cases">{progs}</ul></div></section>
<section><h2>Образование</h2><div><p><b>{inline(edu["place"])}</b><br>{inline(edu["what"])}</p><ul class="dots">{extra}</ul></div></section>
<section><h2>Навыки</h2><div><p><b>Инструменты:</b> {inline(sk["tools"])}</p><p><b>Языки:</b> {inline(sk["languages"])}</p></div></section>
<div class="foot"><span>Кейсы с данными из Search Console и Яндекс.Метрики — egorprotasov.ru</span><span>данные на {esc(asof)}</span></div>
</div></body></html>
"""


def pages(pdf_bytes):
    """Число страниц: словари страниц в PDF от Chrome не сжаты."""
    return len(re.findall(rb"/Type\s*/Page\b", pdf_bytes))


def print_pdf(html_path, pdf_path):
    """Chrome печатает и не всегда сам выходит: ждём, пока файл перестанет расти, и завершаем процесс."""
    tmp = pdf_path.with_name(pdf_path.stem + ".printing.pdf")
    tmp.unlink(missing_ok=True)
    profile = tempfile.mkdtemp(prefix="cv-chrome-")
    proc = subprocess.Popen([CHROME, "--headless", "--disable-gpu", "--no-first-run", f"--user-data-dir={profile}",
                             "--no-pdf-header-footer", f"--print-to-pdf={tmp}", html_path.as_uri()],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0, last = time.time(), -1
    while time.time() - t0 < 60:
        size = tmp.stat().st_size if tmp.exists() else 0
        if size and size == last:
            break
        last = size
        time.sleep(0.6)
    proc.kill()
    shutil.rmtree(profile, ignore_errors=True)
    if not tmp.exists() or not tmp.stat().st_size:
        raise RuntimeError(f"Chrome не напечатал {pdf_path.name}")
    tmp.replace(pdf_path)


def build(root, site, cv, own, client, programs, asof):
    """HTML в .cache/cv/, PDF — по cv["file"]. Возвращает (путь к HTML, список предупреждений)."""
    root = pathlib.Path(root)
    cache = root / ".cache" / "cv"
    cache.mkdir(parents=True, exist_ok=True)
    src = html(site, cv, own, client, programs, asof)
    page = cache / "cv-ru.html"
    pdf = root / cv["file"]
    pdf.parent.mkdir(parents=True, exist_ok=True)
    stale = not pdf.exists() or not page.exists() or page.read_text(encoding="utf-8") != src
    page.write_text(src, encoding="utf-8")
    warns = []
    if stale:
        if not pathlib.Path(CHROME).exists():
            return page, [f"нет Google Chrome — {cv['file']} не обновлён"]
        print_pdf(page, pdf)
        print(f"  CV: {cv['file']}")
    n = pages(pdf.read_bytes())
    if n != 1:
        warns.append(f"{cv['file']}: страниц {n}, а должна быть одна — сократите src/cv.toml")
    return page, warns
