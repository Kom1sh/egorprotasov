"""Посадочная программы: первый экран с иконкой и настоящим кадром, «как работает» на читаемых
вырезках с подписями словами, зачем, что умеет, в работе, другие программы, связь.
И полоса «Программы» для главной.

Кадры — вырезки из настоящей программы, где всё закрытое закрыто ещё в ней самой. Каждая вырезка —
один понятный элемент, к нему рамка и короткая подпись: что здесь видно.
"""
from .hero import ICON_SET
from .pages import _work_list
from .text import esc, inline

WRAP_W = 1160    # ширина колонки сайта
ZOOM = 1.35      # во сколько раз вырезка может быть крупнее себя в программе: текст читается, но не мылится
ICON_W = 96

TG_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21.5 4.3 2.9 11.4c-.9.3-.9 1.6 0 1.9l4.7 1.5 1.8 5.6c.3.8 '
           '1.3 1 1.9.4l2.6-2.5 4.7 3.5c.7.5 1.7.1 1.9-.7l3.1-15c.2-1-.7-1.8-1.6-1.4Z" fill="currentColor" stroke="none"/></svg>')


def url(p):
    return f"/projects/{p['slug']}/"


def _pct(v):
    return f"{v:.3f}".rstrip("0").rstrip(".") + "%"


def display_w(f):
    return min(WRAP_W, round(f["w"] * ZOOM))


def _picture(f, alt, eager=False):
    name, w, h = f["img"], f["w"], f["h"]
    dw = display_w(f)
    sizes = f"(max-width: 960px) calc(100vw - 40px), {dw}px"
    webp = f"/assets/img/{name}-{w}.webp {w}w, /assets/img/{name}-{w * 2}.webp {w * 2}w"
    jpg = f"/assets/img/{name}-{w}.jpg {w}w, /assets/img/{name}-{w * 2}.jpg {w * 2}w"
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture class="sf-img"><source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="/assets/img/{name}-{w * 2}.jpg" srcset="{jpg}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{esc(alt)}" {load} decoding="async"></picture>')


def tag_place(f):
    """Подпись стоит над кадром, чтобы не закрывать текст программы; ножка идёт вниз к рамке.
    Если рамка у правого края, подпись прижата вправо."""
    m, w, h = f["mark"], f["w"], f["h"]
    right = (m["x"] + m["w"] / 2) / w > 0.6
    anchor = (m["x"] + m["w"] - 22) / w * 100 if right else (m["x"] + 22) / w * 100
    horiz = f"right:{_pct(100 - (m['x'] + m['w']) / w * 100)}" if right else f"left:{_pct(m['x'] / w * 100)}"
    stem = f"left:{_pct(anchor)};height:calc({_pct(m['y'] / h * 100)} + 7px)"
    return (" r" if right else ""), horiz, stem


def frame(p, f, caption, eager=False):
    """Вырезка из программы с рамкой и подписью словами."""
    m, w, h = f["mark"], f["w"], f["h"]
    side, pos, stem = tag_place(f)
    alt = f"{p['title']}, настоящий кадр: {f['tag']}. Цифры методики и найденные адреса закрыты в самой программе"
    return f"""<figure class="sf" style="max-width:{display_w(f)}px">
      <div class="sf-box" style="aspect-ratio:{w}/{h}">
        {_picture(f, alt, eager)}
        <span class="sf-mark" style="left:{_pct(m['x'] / w * 100)};top:{_pct(m['y'] / h * 100)};width:{_pct(m['w'] / w * 100)};height:{_pct(m['h'] / h * 100)}" aria-hidden="true"></span>
        <span class="sf-stem" style="{stem}" aria-hidden="true"></span>
        <span class="sf-tag{side}" style="{pos}"><i aria-hidden="true"></i>{esc(f['tag'])}</span>
      </div>
      <figcaption>{inline(caption)}</figcaption>
    </figure>"""


def icon(p, size=ICON_W, eager=False):
    s = p["slug"]
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture class="app-icon"><source type="image/webp" srcset="/assets/img/icon-{s}-{size}.webp 1x, '
            f'/assets/img/icon-{s}-{size * 2}.webp 2x"><img src="/assets/img/icon-{s}-{size * 2}.jpg" '
            f'srcset="/assets/img/icon-{s}-{size}.jpg 1x, /assets/img/icon-{s}-{size * 2}.jpg 2x" '
            f'width="{size}" height="{size}" alt="Иконка {esc(p["title"])}" {load} decoding="async"></picture>')


def _apps(sheets, skip=None):
    cells = []
    for s in sheets:
        if skip and s["slug"] == skip["slug"]:
            continue
        cells.append(f'<a class="app" href="{url(s)}" style="--prog:{s["color"]}">{icon(s)}'
                     f'<p class="app-t">{esc(s["title"])}</p><p class="app-w">{inline(s["what"].capitalize())}</p></a>')
    return f'<div class="apps n{len(cells)}">{"".join(cells)}</div>'


def page(p, *, img, sheets):
    """img — метаданные картинок из images.build: здесь не нужны, оставлены для единообразия с pages.project."""
    steps = "".join(
        f"""<li class="st">
    <div class="st-head"><div><p class="step-n">Шаг {i + 1}</p><h3>{inline(f['title'])}</h3></div><p class="st-p">{inline(f['text'])}</p></div>
    {frame(p, f, f"Настоящий кадр, {p['run_date']}.")}
  </li>""" for i, f in enumerate(p["steps"]))
    abilities = "".join(f'<li><span class="can-n">0{i + 1}</span><h3>{inline(a)}</h3><p>{inline(b)}</p></li>'
                        for i, (a, b) in enumerate(p["abilities"]))
    facts = "".join(f"<p>{inline(t)}</p>" for t in p["facts"])
    done = _work_list([{"date": d["date"], "text": d["text"]} for d in p["done"]])
    lead, punch = p["manifesto"][0], p["manifesto"][1]
    return f"""<div class="sw-page" style="--prog:{p['color']}">
<section class="sw-hero" id="top">
  <div class="wrap hero-text">
    <a class="sw-back" href="/#programs">{ICON_SET['back']}<span>Все программы</span></a>
    <div class="hero-id">{icon(p, eager=True)}<div><p class="lbl">Своя программа</p><h1>{esc(p['title'])}</h1></div></div>
    <div class="hero-side"><p class="hero-promise">{inline(p['promise'])}</p><p class="hero-meta">{inline(p['in_use'])}</p></div>
  </div>
  <div class="wrap hero-shot">{frame(p, p['hero'], p['hero']['caption'], eager=True)}</div>
</section>

<section class="sw-how" id="how"><div class="wrap">
  <p class="lbl">Как работает</p>
  <ol class="st-list">
  {steps}
  </ol>
</div></section>

<section class="sw-why"><div class="wrap">
  <p class="lbl">Зачем</p>
  <p class="why-lead">{inline(lead)}</p>
  <p class="why-punch">{inline(punch)}</p>
</div></section>

<section class="sw-can"><div class="wrap">
  <p class="lbl">Что умеет</p>
  <ol class="can-list">{abilities}</ol>
</div></section>

<section class="sw-work"><div class="wrap two">
  <p class="lbl">В работе</p>
  <div><div class="work-facts">{facts}</div>{done}</div>
</div></section>

<section class="sw-more"><div class="wrap">
  <p class="lbl">Другие программы</p>
  {_apps(sheets, skip=p)}
</div></section>

<section class="sw-talk"><div class="wrap">
  <p class="lbl">Связаться</p>
  <h2 class="cap"><b>Расскажите о своём проекте.</b> Покажу, что из рутины можно отдать программе, а что лучше делать руками.</h2>
  <p class="talk-act"><a class="btn-contact" href="https://t.me/Kom1sh">{TG_ICON}<span>Написать в Telegram</span></a></p>
  <p class="talk-note">Программа Егора Протасова, SEO Lead и проектного менеджера из Ростова-на-Дону. Кадры сняты с настоящей программы,
  цифры методики, найденные домены и названия источников данных закрыты в ней самой до съёмки.
  <a href="/" rel="author">Другие проекты и контакты</a>.</p>
</div></section>
</div>"""


def home_band(sheets):
    return f"""<section class="sw-band" id="programs"><div class="wrap">
  <p class="lbl">Программы</p>
  <h2 class="cap"><b>Три программы,</b> которые я написал для своей работы: от поиска ниши до проверки готового сайта</h2>
  {_apps(sheets)}
</div></section>"""


def image_widths(programs):
    """Ширины картинок для images.build: вырезки в 1x и 2x, иконки под вёрстку."""
    out = {f"icon-{p['slug']}": [ICON_W, ICON_W * 2] for p in programs}
    for p in programs:
        for f in [p["hero"]] + p["steps"]:
            out[f["img"]] = [f["w"], f["w"] * 2]
    return out


__all__ = ["page", "home_band", "frame", "icon", "image_widths", "url"]
