"""Посадочная программы: лист с чертежом, «как работает» на настоящих кадрах, зачем, что умеет,
в работе, комплект листов, связь. И полоса «Программы» для главной.

Камера по кадру считается здесь, в процентах: без скриптов и на телефоне каждая фигура уже стоит
на месте своего шага, скрипт только переключает шаги и запускает переходы.
"""
from .drawings import DRAWINGS, thumb
from .hero import ICON_SET
from .pages import _work_list
from .text import esc, inline

ENTER = 1.18     # фигура входит чуть шире, чем стоит камера
DISPLAY_W = 720  # ширина окна фигуры в вёрстке, CSS-пиксели

TG_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21.5 4.3 2.9 11.4c-.9.3-.9 1.6 0 1.9l4.7 1.5 1.8 5.6c.3.8 '
           '1.3 1 1.9.4l2.6-2.5 4.7 3.5c.7.5 1.7.1 1.9-.7l3.1-15c.2-1-.7-1.8-1.6-1.4Z" fill="currentColor" stroke="none"/></svg>')


def url(p):
    return f"/projects/{p['slug']}/"


def _pct(v):
    return f"{v:.3f}".rstrip("0").rstrip(".") + "%"


def _wider(c, W, H, f=ENTER):
    w, h = min(W, c["w"] * f), min(H, c["h"] * f)
    x = max(0, min(W - w, c["x"] - (w - c["w"]) / 2))
    y = max(0, min(H - h, c["y"] - (h - c["h"]) / 2))
    return {"x": x, "y": y, "w": w, "h": h}


def figure_geometry(f):
    """Всё, что нужно вёрстке фигуры, в процентах окна: где лежит картинка, откуда въезжает камера,
    где рамка выноски и с какой стороны номер."""
    W, H, c, m = f["w"], f["h"], f["cam"], f["mark"]
    R = {"x": 0, "y": 0, "w": W, "h": H} if f.get("wide") else _wider(c, W, H)
    s = c["w"] / R["w"]
    mx, my = (m["x"] - c["x"]) / c["w"] * 100, (m["y"] - c["y"]) / c["h"] * 100
    mw, mh = m["w"] / c["w"] * 100, m["h"] / c["h"] * 100
    return {
        "img": {"width": W / c["w"] * 100, "left": -c["x"] / c["w"] * 100, "top": -c["y"] / c["h"] * 100},
        "enter": {"tx": (c["x"] - R["x"] * s) / W * 100, "ty": (c["y"] - R["y"] * s) / H * 100, "s": s},
        "mark": {"left": mx, "top": my, "width": mw, "height": mh},
        "right": (m["x"] + m["w"] / 2) > (c["x"] + c["w"] / 2),
        "cy": my + mh / 2,
    }


def _picture(f, alt):
    name, w, h = f["img"], f["w"], f["h"]
    sizes = f"(max-width: 960px) {round(100 * w / f['cam']['w'])}vw, {round(DISPLAY_W * w / f['cam']['w'])}px"
    webp = f"/assets/img/{name}-{w}.webp {w}w, /assets/img/{name}-{w * 2}.webp {w * 2}w"
    jpg = f"/assets/img/{name}-{w}.jpg {w}w, /assets/img/{name}-{w * 2}.jpg {w * 2}w"
    return (f'<source type="image/webp" srcset="{webp}" sizes="{sizes}">'
            f'<img src="/assets/img/{name}-{w * 2}.jpg" srcset="{jpg}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{esc(alt)}" loading="lazy" decoding="async">')


def _fig(p, i, f):
    g = figure_geometry(f)
    n = i + 2
    im, en, mk = g["img"], g["enter"], g["mark"]
    side = " r" if g["right"] else ""
    inner = (f'style="top:{_pct(g["cy"])};left:{_pct(mk["left"] + mk["width"])};right:0"' if g["right"]
             else f'style="top:{_pct(g["cy"])};left:0;width:{_pct(mk["left"])}"')
    alt = f"{p['title']}, настоящий кадр: {f['cap']}. Цифры методики и найденные адреса закрыты в самой программе"
    return f"""<figure class="how-fig{' wide' if f.get('wide') else ''}" style="--tx:{_pct(en['tx'])};--ty:{_pct(en['ty'])};--s:{en['s']:.4f}">
      <div class="how-box" style="aspect-ratio:{f['cam']['w']}/{f['cam']['h']}">
        <div class="how-vp">
          <picture class="how-img" style="width:{_pct(im['width'])};left:{_pct(im['left'])};top:{_pct(im['top'])}">{_picture(f, alt)}</picture>
          <span class="how-mark" style="left:{_pct(mk['left'])};top:{_pct(mk['top'])};width:{_pct(mk['width'])};height:{_pct(mk['height'])}" aria-hidden="true"></span>
          <span class="how-lead in{side}" {inner} aria-hidden="true"></span>
        </div>
        <span class="how-lead out{side}" style="top:{_pct(g['cy'])}" aria-hidden="true"></span>
        <span class="how-ball{side}" style="top:{_pct(g['cy'])}" aria-hidden="true">{n}</span>
      </div>
      <figcaption><span><b>Фиг. {n}.</b> {esc(f['cap'])}</span><span>{esc(p['run_date'])}</span></figcaption>
    </figure>"""


def _legend(p):
    return "".join(f'<li class="lg" style="--d:{i}"><i>{i + 1}</i><span><b>{esc(a)}.</b> {inline(b)}</span></li>'
                   for i, (a, b) in enumerate(p["legend"]))


def _sheet_cells(sheets, current=None):
    cells = []
    for s in sheets:
        body = (f'<div class="set-draw" style="--prog:{s["color"]}">{thumb(s["slug"])}</div>'
                f'<p class="set-n">Лист {s["sheet"]}</p><p class="set-t">{esc(s["title"])}</p>'
                f'<p class="set-w">{inline(s["what"].capitalize())}</p>')
        if current and s["slug"] == current["slug"]:
            cells.append(f'<div class="set-sheet here" aria-current="page">{body}<span class="set-here">Этот лист</span></div>')
        else:
            cells.append(f'<a class="set-sheet" href="{url(s)}">{body}</a>')
    return f'<div class="set-row">{"".join(cells)}</div>'


def page(p, *, img, sheets):
    """img — метаданные картинок из images.build: здесь не нужны, оставлены для единообразия с pages.project."""
    total = len(sheets)
    figs = "".join(
        f"""<li class="how-item" data-i="{i}">
    <div class="how-text"><p class="fig-n">Фиг. {i + 2}</p><h3>{inline(f['title'])}</h3><p class="how-p">{inline(f['text'])}</p></div>
    {_fig(p, i, f)}
  </li>""" for i, f in enumerate(p["figs"]))
    abilities = "".join(f'<li><span class="can-n">0{i + 1}</span><h3>{inline(a)}</h3><p>{inline(b)}</p></li>'
                        for i, (a, b) in enumerate(p["abilities"]))
    facts = "".join(f"<p>{inline(t)}</p>" for t in p["facts"])
    done = _work_list([{"date": d["date"], "text": d["text"]} for d in p["done"]])
    lead, punch = p["manifesto"][0], p["manifesto"][1]
    return f"""<div class="sw-page" style="--prog:{p['color']}">
<section class="sw-sheet" id="top" data-tone="paper">
  <div class="sw-wrap sheet-grid">
    <div class="sheet-text">
      <a class="sw-back" href="/#programs">{ICON_SET['back']}<span>Все программы</span></a>
      <p class="sw-lbl">Своя программа, лист {p['sheet']} из {total}</p>
      <h1>{esc(p['title'])}</h1>
      <p class="sw-promise">{inline(p['promise'])}</p>
      <ol class="legend">{_legend(p)}</ol>
    </div>
    <figure class="sheet-fig">{DRAWINGS[p['slug']]()}</figure>
  </div>
  <div class="sw-wrap stamp-row"><dl class="stamp">
    <div class="st-name"><dt>Наименование</dt><dd>{esc(p['title'])}</dd></div>
    <div><dt>Лист</dt><dd>{p['sheet']}</dd></div><div><dt>Листов</dt><dd>{total}</dd></div>
    <div class="st-name"><dt>Назначение</dt><dd>{esc(p['purpose'])}</dd></div>
    <div><dt>Разраб.</dt><dd>Протасов</dd></div><div><dt>Год</dt><dd>{p['since'][:4]}</dd></div>
  </dl></div>
</section>

<section class="sw-how" id="how" data-tone="paper">
  <div class="how-track" style="--n:{len(p['figs'])}">
    <div class="how-stick">
      <div class="sw-wrap">
        <div class="how-head"><p class="sw-lbl">Как работает</p><p class="how-src">{esc(p['title'])}, настоящий прогон</p></div>
        <ol class="how-list">
  {figs}
        </ol>
      </div>
    </div>
  </div>
</section>

<section class="sw-why" data-tone="dark"><div class="wrap">
  <p class="lbl">Зачем</p>
  <p class="why-lead">{inline(lead)}</p>
  <p class="why-punch">{inline(punch)}</p>
</div></section>

<section class="sw-can" data-tone="dark"><div class="wrap">
  <p class="lbl">Что умеет</p>
  <ol class="can-list">{abilities}</ol>
</div></section>

<section class="sw-work" data-tone="dark"><div class="wrap two">
  <p class="lbl">В работе</p>
  <div><div class="work-facts">{facts}</div>{done}</div>
</div></section>

<section class="sw-set" data-tone="paper"><div class="sw-wrap">
  <div class="set-head"><p class="sw-lbl">Комплект</p><p class="set-cap">Три программы, которые я написал для своей работы</p></div>
  {_sheet_cells(sheets, current=p)}
</div></section>

<section class="sw-talk" data-tone="dark"><div class="wrap">
  <p class="lbl">Связаться</p>
  <h2 class="cap"><b>Расскажите о своём проекте.</b> Покажу, что из рутины можно отдать программе, а что лучше делать руками.</h2>
  <p class="talk-act"><a class="btn-contact" href="https://t.me/Kom1sh">{TG_ICON}<span>Написать в Telegram</span></a></p>
  <p class="talk-note">Программа Егора Протасова, SEO Lead и проектного менеджера из Ростова-на-Дону. Кадры сняты с настоящей программы,
  цифры методики, найденные домены и названия источников данных закрыты в ней самой до съёмки.
  <a href="/" rel="author">Другие проекты и контакты</a>.</p>
</div></section>
</div>"""


def home_band(sheets):
    return f"""<section class="sw-band" id="programs" data-tone="paper"><div class="sw-wrap">
  <div class="set-head"><p class="sw-lbl">Программы</p>
    <h2 class="band-cap"><b>Три программы,</b> которые я написал для своей работы: от поиска ниши до проверки готового сайта</h2></div>
  {_sheet_cells(sheets)}
</div></section>"""


__all__ = ["page", "home_band", "figure_geometry", "url"]
