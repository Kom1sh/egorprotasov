"""Разметка страниц: главная, страница проекта, переадресация, 404."""
import datetime as dt
import re

from .images import picture
from .text import esc, inline, num, plain

STATUS = {"up": "растёт", "hold": "держится", "down": "упал", "wip": "в работе"}
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


def status_badge(key):
    return f'<span class="st {key}">{STATUS[key]}</span>'


# ——— главная ———

def _project_rows(projects, sparks):
    rows = []
    own = projects[0]["kind"] == "own"
    for p in projects:
        sp = f'<td class="sp">{sparks.get(p["slug"], "")}</td>' if own else ""
        what = f'<td class="what">{inline(p["what"])}</td>' if own else ""
        rows.append(f'<tr><td class="name"><a href="/projects/{p["slug"]}/">{inline(p["title"])}</a></td>{what}{sp}'
                    f'<td class="res num">{inline(p["row"])}</td><td class="stc">{status_badge(p["status"])}</td></tr>')
    head = ('<tr><th scope="col">Проект</th><th scope="col">Что это</th><th scope="col" colspan="2">Результат</th>'
            '<th scope="col"><span class="sr-only">Состояние</span></th></tr>') if own else \
           ('<tr><th scope="col">Проект</th><th scope="col">Результат</th>'
            '<th scope="col"><span class="sr-only">Состояние</span></th></tr>')
    return f'<table class="ptable"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'


def home(site, own, client, img, chart_html, sparks, age):
    person = site["person"]
    lead = inline(person["lead"]).replace("{age}", f'<span data-born="{person["born"]}">{age}</span>')

    path_items, prev_year = [], None
    for item in site["path"]:
        year = item["year"] if item["year"] != prev_year else ""
        prev_year = item["year"]
        photo = ""
        if item.get("photo"):
            photo = (f'<figure>{picture(img, item["photo"], item["photo_alt"], display_w=520)}'
                     f'<figcaption class="cap">{inline(item["caption"])}</figcaption></figure>')
        year_html = f'<span class="year">{year}</span>' if year else '<span class="year" aria-hidden="true"></span>'
        path_items.append(f'<li>{year_html}<div><p>{inline(item["text"])}</p>{photo}</div></li>')

    life = site["life"]
    ideas = "".join(f"<li>{inline(t)}</li>" for t in life["items"])

    return f"""<header class="hero"><div class="wrap">
  <div class="who">
    {picture(img, "egor", "Егор Протасов", display_w=96, cls="ava", eager=True)}
    <div class="text">
      <h1>{esc(person["name"])}</h1>
      <p class="lead">{lead}</p>
      <p class="about">{inline(person["about"])}</p>
    </div>
  </div>
  {chart_html}
</div></header>

<section class="sec tone" aria-labelledby="path-h"><div class="wrap">
  <h2 id="path-h">Путь</h2>
  <ol class="path">{"".join(path_items)}</ol>
</div></section>

<section class="sec" id="projects" aria-labelledby="projects-h"><div class="wrap">
  <h2 id="projects-h">Проекты</h2>
  <h3>Свои</h3>
  {_project_rows(own, sparks)}
  <h3>Клиентские</h3>
  <p class="note">Названия не указываю по договорённости с клиентами.</p>
  {_project_rows(client, sparks)}
</div></section>

<section class="sec tone" aria-labelledby="life-h"><div class="wrap">
  <h2 id="life-h">Вне работы</h2>
  <div class="life-row">
    {picture(img, life["photo"], life["photo_alt"], display_w=620)}
    <div><p class="life-lead">{inline(life["lead"])}</p><ul class="ideas">{ideas}</ul></div>
  </div>
</div></section>"""


# ——— страница проекта ———

def _facts(p):
    f = p["facts"]
    items = [("Роль", f["role"]), ("Период", f["period"]), ("Команда", f["team"])]
    if p["kind"] == "own":
        items.append(("Стек", f["stack"]))
    else:
        items.append(("Ниша", f["niche"]))
    if p.get("site"):
        items[-1:] = [items[-1]]
    dl = "".join(f"<div><dt>{esc(k)}</dt><dd>{inline(v)}</dd></div>" for k, v in items)
    return f'<dl class="facts">{dl}</dl>'


def bars(sources, total_label):
    total = sum(s["value"] for s in sources)
    mx = max(s["value"] for s in sources)
    rows = "".join(
        f'<li><span>{esc(s["label"])}</span><span class="bar{"" if s.get("accent") else " muted"}" '
        f'style="width:{100 * s["value"] / mx:.1f}%"></span><span class="v">{num(s["value"])}</span></li>'
        for s in sources)
    return (f'<figure class="chart"><figcaption class="chart-head"><span class="chart-title">{esc(total_label)}</span>'
            f'</figcaption><ul class="bars" aria-label="{esc(total_label)}">{rows}</ul>'
            f'<p class="chart-src">Всего {num(total)} визитов. Яндекс.Метрика, 29 августа — 18 сентября 2026.</p></figure>')


def ultracker_scheme():
    """Схема: наша дорожка и дорожка клиента, задача привязана к спринту клиента, трекер считает окно передачи."""
    sprints = "".join(
        f'<rect x="{130 + i * 180}" y="96" width="172" height="34" rx="6" class="sch-box"/>'
        f'<text x="{130 + i * 180 + 12}" y="118" class="sch-t">Спринт {i + 1}</text>' for i in range(4))
    return f"""<figure class="scheme">
<svg viewBox="0 0 860 190" role="img" aria-label="Как Ultracker считает окно передачи: задача на моей дорожке привязана ко второму спринту клиента, трекер считает крайний момент передачи — начало второго спринта — и подсвечивает риск, если задача не успевает.">
<style>.sch-box{{fill:#f5f5f7;stroke:#d2d2d7}}.sch-t{{font:13px var(--font);fill:#1d1d1f}}.sch-l{{font:600 13px var(--font);fill:#6e6e73}}.sch-a{{font:13px var(--font);fill:#0a6ee0}}.sch-line{{stroke:#ececef}}</style>
<text x="0" y="52" class="sch-l">Моя дорожка</text>
<line x1="120" x2="860" y1="47" y2="47" class="sch-line"/>
<rect x="190" y="30" width="96" height="34" rx="6" style="fill:#e8f0fb;stroke:#0a6ee0"/>
<text x="202" y="52" class="sch-t">Задача</text>
<text x="0" y="118" class="sch-l">Клиент</text>
<line x1="120" x2="860" y1="113" y2="113" class="sch-line"/>
{sprints}
<line x1="310" y1="30" x2="310" y2="150" style="stroke:#0a6ee0;stroke-width:1.5"/>
<path d="M286,47 L306,47" style="stroke:#0a6ee0;stroke-width:1.5;fill:none"/>
<text x="318" y="168" class="sch-a">окно передачи: крайний момент,</text>
<text x="318" y="184" class="sch-a">чтобы задача попала во второй спринт</text>
</svg></figure>"""


def quarter_table(rows, caption, note):
    body = "".join(f"<tr><td>{esc(q)}</td><td>{num(c)}</td><td>{num(i)}</td><td>{esc(s)}</td></tr>"
                   for q, c, i, s in rows)
    return (f'<table class="dtable"><caption>{esc(caption)}</caption><thead><tr><th scope="col">Квартал</th>'
            f'<th scope="col">Клики</th><th scope="col">Показы</th><th scope="col">Небрендовые показы</th></tr></thead>'
            f'<tbody>{body}</tbody><tfoot><tr><td colspan="4">{esc(note)}</td></tr></tfoot></table>')


def project(p, *, result_extra, next_p, asof):
    kind_label = "Свой проект" if p["kind"] == "own" else "Клиентский проект, без названия по договорённости"
    site_link = ""
    if p.get("site"):
        site_link = f' <a href="{esc(p["site"])}" rel="noopener">{esc(p["site_label"])}</a>'
    done = "".join(f'<li><time datetime="{iso(d["date"])}">{esc(fmt_date(d["date"]))}</time>'
                   f'<p>{inline(d["text"])}</p></li>' for d in p["done"])
    task = "".join(f"<p>{inline(t)}</p>" for t in p["task"])
    result = "".join(f"<p>{inline(t)}</p>" for t in p.get("result", []))
    failed = "".join(f"<li>{inline(t)}</li>" for t in p.get("failed", []))
    failed_blk = (f'<section class="blk" aria-labelledby="f-h"><h2 id="f-h">Что не сработало</h2>'
                  f'<ol class="failed">{failed}</ol></section>') if failed else ""
    nxt = ""
    if next_p:
        nxt = (f'<nav class="next" aria-label="Другие проекты"><div><span class="lbl">Следующий проект</span>'
               f'<a class="title" href="/projects/{next_p["slug"]}/">{inline(next_p["title"])}</a></div>'
               f'<div><span class="lbl">Все проекты</span><a href="/#projects">на главной</a></div></nav>')
    return f"""<article class="wrap">
<header class="ph">
  <p class="kind">{status_badge(p["status"])}<span>{kind_label}.{site_link}</span></p>
  <h1>{inline(p["title"])}</h1>
  <p class="lead">{inline(p["lead"])}</p>
  {_facts(p)}
</header>

<section class="blk" aria-labelledby="t-h"><h2 id="t-h">Задача</h2><div class="prose">{task}</div></section>

<section class="blk" aria-labelledby="d-h"><h2 id="d-h">Что сделал</h2><ol class="done">{done}</ol></section>

<section class="blk" aria-labelledby="r-h"><h2 id="r-h">Результат</h2><div class="prose">{result}</div>{result_extra}</section>

{failed_blk}

<section class="blk" aria-labelledby="n-h"><h2 id="n-h">Сейчас</h2>
  <div class="now"><p class="asof">На {esc(asof)}</p><p>{inline(p["now"])}</p></div>
</section>
{nxt}
</article>"""


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
    return """<section class="sec"><div class="wrap">
  <h1 style="font-size:clamp(32px,4vw,48px);letter-spacing:-.02em;margin-bottom:16px">Такой страницы нет</h1>
  <p class="lead" style="margin-bottom:24px">Возможно, адрес изменился после переделки сайта.</p>
  <p><a href="/">На главную</a></p>
</div></section>"""


def sitemap(urls, updated):
    items = "".join(f"<url><loc>https://egorprotasov.ru{u}</loc><lastmod>{updated}</lastmod></url>" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>\n')


def age_on(born, today):
    b = dt.date.fromisoformat(born)
    return today.year - b.year - ((today.month, today.day) < (b.month, b.day))


__all__ = ["home", "project", "redirect", "not_found", "sitemap", "bars", "quarter_table",
           "ultracker_scheme", "age_on", "plain", "fmt_date"]
