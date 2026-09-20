"""Разметка страниц: главная, страница проекта, переадресация, 404."""
import datetime as dt
import re

from .hero import ICON_SET, hero, lap_backdrop, path_section, project_backdrop
from .images import picture
from .text import esc, inline, num, plain

MONTHS_GEN = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
              "сентября", "октября", "ноября", "декабря"]
MONTHS_NOM = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август",
              "сентябрь", "октябрь", "ноябрь", "декабрь"]


def fmt_date(s):
    """«2026-07-23» → «23 июля 2026», «2026-09» → «сентябрь 2026», «2026-08-18/2026-08-20» → «18–20 августа 2026»."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})/(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y1, m1, d1, y2, m2, d2 = map(int, m.groups())
        if (y1, m1) == (y2, m2):
            return f"{d1}–{d2} {MONTHS_GEN[m1 - 1]} {y1}"
        return f"{d1} {MONTHS_GEN[m1 - 1]} — {d2} {MONTHS_GEN[m2 - 1]} {y2}"
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mo, d = map(int, m.groups())
        return f"{d} {MONTHS_GEN[mo - 1]} {y}"
    m = re.fullmatch(r"(\d{4})-(\d{2})", s)
    if m:
        y, mo = map(int, m.groups())
        return f"{MONTHS_NOM[mo - 1]} {y}"
    return s


def iso(s):
    m = re.match(r"(\d{4}-\d{2}(?:-\d{2})?)", s)
    return m.group(1) if m else ""


def url(p):
    return f"/projects/{p['slug']}/"


# ——— главная ———

def _own_section(p, img):
    """Блок своего проекта: его цвет, спецификация, снимок и вертикальный знак."""
    spec = "".join(f"<div><dt>{esc(k)}</dt><dd>{inline(v)}</dd></div>" for k, v in p["spec"])
    if p.get("shot"):
        media = (f'<figure class="shot">{picture(img, p["shot"], p["shot_alt"], display_w=1240)}</figure>')
    else:
        media = ultracker_scheme()
    return f"""<section class="proj" id="{p['slug']}" style="--bg:{p['color']};--fg:{p['fg']};--fg2:{p['fg2']}">
  <div class="proj-head"><dl class="spec">{spec}</dl></div>
  <div class="proj-media">{media}<div class="vert" style="font-size:{p['vert_size']}px" aria-hidden="true">{esc(p['vert'])}</div></div>
  <div class="proj-cap">
    <h3><b>{inline(p['title'])}</b> — {inline(p['what'])}</h3>
    <div class="proj-meta"><p>{inline(p['home_meta'])}</p>
      <a class="btn btn-{p['slug']}" href="{url(p)}">{ICON_SET[p['icon']]}<span>{esc(p['btn_label'])}</span></a></div>
  </div>
</section>"""


def _client_list(client):
    rows = "".join(
        f'<li><a href="{url(p)}"><span class="c-idx" aria-hidden="true">0{i + 1}</span>'
        f'<span class="c-name">{inline(p["title"])}</span><span class="c-res">{inline(p["row"])}</span>'
        f'<span class="c-when">{esc(p["home_when"])}</span></a></li>' for i, p in enumerate(client))
    return f'<ul class="c-list">{rows}</ul>'


def home(site, own, client, img, chart_html, traces, age, nav):
    person = site["person"]
    q = site["quote"]
    age_html = '<b data-born="' + person["born"] + f'">{age}</b>'
    bio = "".join("<p>" + inline(t).replace("{age}", age_html) + "</p>" for t in site["bio"])
    life = site["life"]
    ideas = "".join(f"<li>{inline(t)}</li>" for t in life["items"])
    path_items = [(it["year"] if i == 0 or site["path"][i - 1]["year"] != it["year"] else "", inline(it["text"]),
                   (it["photo"], it["photo_alt"], it.get("fig", ""), it.get("caption", "")) if it.get("photo") else None)
                  for i, it in enumerate(site["path"])]

    return f"""{hero(quote_lines=[(c, esc(t)) for c, t in q["lines"]], quote_author=esc(q["author"]),
                     name_line=esc(person["name"]), role=esc(person["role_line"]),
                     now_text=inline(person["now"]), traces=traces, nav=nav)}
  <div class="bio">
    <div class="bio-text">{bio}</div>
    <div class="rule" aria-hidden="true"><i></i></div>
    <figure class="portrait">{picture(img, "egor", "Егор Протасов", display_w=380, eager=True)}
      <figcaption><span class="nm">{esc(person["name"])}</span><span class="rl">{esc(person["role_line"])}</span></figcaption></figure>
  </div>
</header>

<section class="tele" id="telemetry">
  <div class="wrap">
    <p class="lbl">Телеметрия</p>
    <h2 class="cap">{inline(site["chart"]["caption"])}</h2>
    {chart_html}
  </div>
</section>

{''.join(_own_section(p, img) for p in own)}

<section class="clients" id="clients">
  <div class="wrap">
    <p class="lbl">Клиентские проекты</p>
    <h2 class="cap">{inline(site["clients_caption"])}</h2>
    {_client_list(client)}
  </div>
</section>

{path_section(path_items, img)}

<section class="life" id="life">
  <div class="wrap life-row">
    <figure class="life-photo"><span class="fr" aria-hidden="true"></span>{picture(img, life["photo"], life["photo_alt"], display_w=800)}</figure>
    <div>
      <p class="lbl">Вне работы</p>
      <p class="life-lead">{inline(life["lead"])}</p>
      <ul class="ideas">{ideas}</ul>
    </div>
  </div>
</section>"""


# ——— страница проекта ———

def _spec_strip(spec):
    items = "".join(f"<div><dt>{esc(k)}</dt><dd>{inline(v)}</dd></div>" for k, v in spec)
    return f'<div class="spec-strip"><div class="wrap"><dl class="spec">{items}</dl></div></div>'


def _block(label, inner, cls=""):
    return (f'<section class="blk {cls}"><div class="wrap two"><p class="lbl">{esc(label)}</p>'
            f'<div>{inner}</div></div></section>')


def _work_list(done):
    li = "".join(f'<li><span class="p-year"><time datetime="{iso(d["date"])}">{esc(fmt_date(d["date"]))}</time></span>'
                 f'<span class="p-node" aria-hidden="true"></span><div><p>{inline(d["text"])}</p></div></li>'
                 for d in done)
    return f'<ol class="p-list small">{li}</ol>'


def project(p, *, img, result_extra, next_p, asof, trace=""):
    kind = "Свой проект" if p["kind"] == "own" else "Клиентский проект"
    backdrop = project_backdrop(trace) if trace else lap_backdrop()
    site_link = ""
    if p.get("site"):
        site_link = (f'<a class="ph-site" href="{esc(p["site"])}" rel="noopener">{ICON_SET["link"]}'
                     f'<span>{esc(p["site_label"])}</span></a>')
    note = f'<p class="ph-note">{inline(p["note"])}</p>' if p.get("note") else ""
    media = ""
    if p.get("shot"):
        media = (f'<div class="wrap"><figure class="shot ph-shot">'
                 f'{picture(img, p["shot"], p["shot_alt"], display_w=1240)}</figure></div>')
    elif p.get("scheme"):
        media = f'<div class="wrap">{ultracker_scheme(cls="shot ui ph-shot")}</div>'

    failed = ""
    if p.get("failed"):
        failed = _block("Что не сработало",
                        '<ol class="failed">' + "".join(f"<li>{inline(t)}</li>" for t in p["failed"]) + "</ol>")
    result = "".join(f"<p>{inline(t)}</p>" for t in p["result"])

    style = (f"--bg:{p['color']};--fg:{p['fg']};--fg2:{p['fg2']};"
             f"--run:{p.get('run', '#bfe828')}")
    return f"""<header class="ph{'' if media else ' no-media'}" id="top" style="{style}">
  {backdrop}
  <div class="wrap">
    <a class="ph-back" href="/#projects">{ICON_SET["back"]}<span>Все проекты</span></a>
    <p class="ph-kind">{kind}</p>
    <h1>{inline(p["title"])}</h1>
    <div class="ph-sub">
      <div><p class="ph-lead">{inline(p["lead"])}</p>{note}</div>
      <div>{site_link}</div>
    </div>
  </div>
  {media}
</header>

<main id="main">
{_spec_strip(p["spec"])}
{_block("Задача", "".join(f"<p>{inline(t)}</p>" for t in p["task"]), cls="task")}
{_block("Что сделал", _work_list(p["done"]))}
<section class="blk res"><div class="wrap">
  <p class="lbl">Результат</p>
  <h2 class="cap">{inline(p["cap"])}</h2>
  <div class="prose">{result}</div>
  {result_extra}
</div></section>
{failed}
<section class="blk"><div class="wrap">
  <div class="now-card">
    <div class="now-head"><p class="lbl">Сейчас</p><p class="asof">на {esc(asof)}</p></div>
    <p class="now-text">{inline(p["now"])}</p>
  </div>
</div></section>
</main>

<nav class="nextp" style="--bg:{next_p['color']};--fg:{next_p['fg']};--fg2:{next_p['fg2']}" aria-label="Следующий проект">
  <a href="{url(next_p)}"><span class="np-lbl">Следующий проект</span>
    <span class="np-title">{inline(next_p["title"])}</span><span class="np-what">{inline(next_p["what"])}</span>
    {ICON_SET["next"]}</a>
</nav>"""


# ——— данные внутри страниц ———

def bars(sources, total_label):
    """Одна величина, прямые подписи: класс dbar, потому что .bar — это липкая шапка."""
    total = sum(s["value"] for s in sources)
    mx = max(s["value"] for s in sources)
    rows = "".join(
        f'<li><span>{esc(s["label"])}</span><span class="dbar{"" if s.get("accent") else " muted"}" '
        f'style="width:{100 * s["value"] / mx:.1f}%"></span><span class="v">{num(s["value"])}</span></li>'
        for s in sources)
    return (f'<figure class="chart"><figcaption class="chart-head"><span class="chart-title">{esc(total_label)}</span>'
            f'</figcaption><ul class="bars" aria-label="{esc(total_label)}">{rows}</ul>'
            f'<p class="chart-src">Всего {num(total)} визитов. Яндекс.Метрика, 29 августа — 18 сентября 2026.</p></figure>')


def quarter_table(rows, caption, note):
    body = "".join(f"<tr><td>{esc(q)}</td><td>{num(c)}</td><td>{num(i)}</td><td>{esc(s)}</td></tr>"
                   for q, c, i, s in rows)
    return (f'<table class="dtable"><caption>{esc(caption)}</caption><thead><tr><th scope="col">Квартал</th>'
            f'<th scope="col">Клики</th><th scope="col">Показы</th><th scope="col">Небрендовые показы</th></tr></thead>'
            f'<tbody>{body}</tbody><tfoot><tr><td colspan="4">{esc(note)}</td></tr></tfoot></table>')


def ultracker_scheme(cls="shot ui"):
    """Схема: моя дорожка и спринты клиента, задача привязана ко второму спринту, трекер считает окно передачи."""
    sprints = "".join(
        f'<rect x="{300 + i * 312}" y="450" width="296" height="80" rx="12" fill="#fff" stroke="#cfd6e0" stroke-width="2"/>'
        f'<text x="{324 + i * 312}" y="498">Спринт {i + 1}</text>' for i in range(4))
    return f"""<figure class="{cls}"><svg viewBox="0 0 1600 1000" role="img" aria-label="Схема Ultracker: моя дорожка и спринты клиента, задача привязана ко второму спринту, трекер считает окно передачи">
<rect width="1600" height="1000" fill="#f2f4f8"/><rect width="250" height="1000" fill="#0f1b2d"/>
<rect x="36" y="44" width="120" height="16" rx="4" fill="#e8edf5"/>
<g fill="#223352"><rect x="36" y="110" width="178" height="34" rx="8"/><rect x="36" y="160" width="150" height="14" rx="4" fill="#182740"/><rect x="36" y="192" width="130" height="14" rx="4" fill="#182740"/><rect x="36" y="224" width="160" height="14" rx="4" fill="#182740"/></g>
<rect x="300" y="60" width="420" height="30" rx="6" fill="#0f1b2d"/><rect x="300" y="104" width="260" height="16" rx="4" fill="#98a2b3"/>
<g font-family="system-ui, sans-serif" font-size="22" fill="#6b7788"><text x="300" y="224">Моя дорожка</text><text x="300" y="424">Спринты клиента</text></g>
<line x1="300" x2="1540" y1="250" y2="250" stroke="#e4e8ef" stroke-width="2"/>
<rect x="420" y="262" width="300" height="70" rx="12" fill="#e6eeff" stroke="#2f6bff" stroke-width="2"/>
<text x="446" y="306" font-family="system-ui, sans-serif" font-size="24" fill="#1d4ed8" font-weight="600">Батч текстов</text>
<g font-family="system-ui, sans-serif" font-size="22" fill="#3d4a5c">{sprints}</g>
<line x1="612" x2="612" y1="240" y2="620" stroke="#f5a623" stroke-width="4"/>
<path d="M720 297 C 680 297, 650 297, 616 297" stroke="#2f6bff" stroke-width="3" fill="none"/>
<rect x="628" y="590" width="360" height="56" rx="28" fill="#fff1d6"/>
<text x="652" y="626" font-family="system-ui, sans-serif" font-size="22" fill="#8a4b00" font-weight="600">окно передачи: вт, 20:00</text>
<g fill="#dfe4ec"><rect x="300" y="720" width="1240" height="16" rx="4"/><rect x="300" y="760" width="980" height="16" rx="4"/><rect x="300" y="800" width="1120" height="16" rx="4"/><rect x="300" y="840" width="760" height="16" rx="4"/></g>
</svg></figure>"""


# ——— служебные страницы ———

def redirect(to):
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><title>Страница переехала</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="https://egorprotasov.ru{to}">
<meta http-equiv="refresh" content="0; url={to}">
<script>location.replace({to!r})</script></head>
<body><p>Страница переехала: <a href="{to}">egorprotasov.ru{to}</a></p></body></html>
"""


def not_found():
    return """<main id="main"><section class="blk nf"><div class="wrap">
  <p class="lbl">404</p>
  <h1 class="cap"><b>Такой страницы нет.</b> Возможно, адрес изменился после переделки сайта</h1>
  <p class="nf-links"><a class="ph-site" href="/"><span>На главную</span></a></p>
</div></section></main>"""


def sitemap(urls, updated):
    items = "".join(f"<url><loc>https://egorprotasov.ru{u}</loc><lastmod>{updated}</lastmod></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>\n')


def age_on(born, today):
    b = dt.date.fromisoformat(born)
    return today.year - b.year - ((today.month, today.day) < (b.month, b.day))


__all__ = ["home", "project", "redirect", "not_found", "sitemap", "bars", "quarter_table",
           "ultracker_scheme", "age_on", "plain", "fmt_date", "iso", "url"]
