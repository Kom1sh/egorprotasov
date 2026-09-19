"""Первый экран: контур круга, цитата вместо имени, липкая шапка. И «Путь» с осью."""

LIME = "#bfe828"

# Знак с живого сайта: буква «Е» из прямоугольников плюс акцентная точка. Перекрашен под тёмную тему.
LOGO = ('<svg class="mark" viewBox="0 0 64 64" aria-hidden="true">'
        '<g fill="currentColor">'
        '<rect x="10" y="13" width="11" height="38"/><rect x="10" y="13" width="31" height="10"/>'
        '<rect x="10" y="27" width="25" height="9"/><rect x="10" y="41" width="31" height="10"/></g>'
        f'<circle cx="51" cy="46" r="6.5" fill="{LIME}"/></svg>')

# Иконки внутренней страницы: ссылка на сайт проекта, возврат к списку, переход к следующему.
ICON_SET = {
    "link": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1.6 1.6 0 0 1-1.6 1.6H5.6A1.6 1.6 0 0 1 4 19V8.2A1.6 1.6 0 0 1 5.6 6.6H11"/></svg>',
    "back": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 5 3.5 12 10 19M3.5 12H21"/></svg>',
    "next": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 5l7 7-7 7M21 12H3"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.6" fill="currentColor" stroke="none"/></svg>',
    "cube": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2 3 7v10l9 5 9-5V7z"/><path d="M3 7l9 5 9-5M12 12v10"/></svg>',
    "wave": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 12h2M7 8v8M11 4v16M15 7v10M19 10v4M21 12h0"/></svg>',
    "board": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16M15 4v16"/></svg>',
}

# Контур гоночного круга: по нему идёт светящийся сегмент.
LAP = ("M260 880 L900 880 C 1040 880, 1120 820, 1120 750 C 1120 690, 1060 650, 990 644 "
       "C 930 638, 900 600, 918 562 C 936 524, 1000 512, 1058 532 C 1120 554, 1180 536, 1196 488 "
       "C 1214 434, 1160 386, 1090 386 L520 386 C 420 386, 360 420, 330 480 "
       "C 300 540, 300 620, 268 680 C 236 740, 200 800, 260 880 Z")


def blueprint(traces):
    """Фон: тонкая сетка чертежа, контур круга и линии роста проектов."""
    grid = "".join(f'<line class="g-v" x1="{x}" x2="{x}" y1="0" y2="1200"/>' for x in range(60, 1440, 60))
    grid += "".join(f'<line class="g-h" x1="0" x2="1440" y1="{y}" y2="{y}"/>' for y in range(60, 1200, 60))
    lap = (f'<g class="lap">'
           f'<path class="lap-base" d="{LAP}"/>'
           f'<path class="lap-run" d="{LAP}"/>'
           f'<g class="lap-start"><line x1="400" y1="860" x2="400" y2="900"/>'
           f'<text x="400" y="924" text-anchor="middle">старт</text></g></g>')
    return (f'<svg class="bp" viewBox="0 0 1440 1200" preserveAspectRatio="xMidYMin slice" aria-hidden="true">'
            f'<g class="grid">{grid}</g>{lap}<g class="traces">{traces}</g></svg>')


def sticky_header(nav, home="#top"):
    cols = "".join(
        f'<div><p class="lbl">{title}</p><ul>'
        + "".join(f'<li><a href="{href}"><i aria-hidden="true"></i>{label}</a></li>' for label, href in items)
        + "</ul></div>" for title, items in nav)
    return f"""<header class="bar" id="bar">
  <a class="plate" href="{home}" aria-label="Егор Протасов, на главную">{LOGO}<span>Протасов</span></a>
  <button class="index" type="button" aria-expanded="false" aria-controls="index-menu">
    <span class="dots" aria-hidden="true"><i></i><i></i><i></i><i></i></span><span class="index-lbl">Разделы</span>
  </button>
</header>
<div class="overlay" id="index-menu" hidden>
  <div class="ov-inner"><nav class="menu" aria-label="Разделы">{cols}</nav>
    <div class="ov-foot"><a class="btn-contact" href="https://t.me/Kom1sh"><span>Написать в Telegram</span></a></div>
  </div>
</div>"""


def hero(*, quote_lines, quote_author, name_line, role, now_text, traces, nav):
    cols = "".join(
        f'<div><p class="lbl">{title}</p><ul>'
        + "".join(f'<li><a href="{href}"><i aria-hidden="true"></i>{label}</a></li>' for label, href in items)
        + "</ul></div>" for title, items in nav)
    q = "".join(f'<span class="{cls}">{text}</span>' for cls, text in quote_lines)
    return f"""{sticky_header(nav)}
<header class="hero" id="top">
  {blueprint(traces)}
  <div class="hero-top">
    <a class="logo" href="#top" aria-label="Егор Протасов">{LOGO}<span>Протасов</span></a>
    <nav class="menu top" aria-label="Разделы">{cols}</nav>
  </div>
  <div class="hero-mid">
    <blockquote class="quote"><p>{q}</p><footer>{quote_author}</footer></blockquote>
    <h1 class="who-line">{name_line}<span>{role}</span></h1>
    <div class="hero-act">
      <a class="btn-contact" href="https://t.me/Kom1sh">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21.5 4.3 2.9 11.4c-.9.3-.9 1.6 0 1.9l4.7 1.5 1.8 5.6c.3.8 1.3 1 1.9.4l2.6-2.5 4.7 3.5c.7.5 1.7.1 1.9-.7l3.1-15c.2-1-.7-1.8-1.6-1.4Z" fill="currentColor" stroke="none"/></svg>
        <span>Связаться</span></a>
      <p class="now"><span class="badge">Сейчас</span>{now_text}</p>
    </div>
  </div>"""


def path_section(items, img=None):
    from .images import picture
    rows = []
    for year, text, photo in items:
        ph = ""
        if photo:
            cap = f'<figcaption><b>рис. {photo[2]}</b> {photo[3]}</figcaption>' if photo[3] else ""
            ph = (f'<figure class="p-photo"><span class="fr" aria-hidden="true"></span>'
                  f'{picture(img, photo[0], photo[1], display_w=520)}{cap}</figure>')
        rows.append(f'<li{" class=cont" if not year else ""}><span class="p-year">{year}</span>'
                    f'<span class="p-node" aria-hidden="true"></span><div><p>{text}</p>{ph}</div></li>')
    return f"""<section class="path-sec" id="path">
  <div class="wrap">
    <p class="lbl">Путь</p>
    <h2 class="cap"><b>Два года</b> от первого курса до своего факультатива</h2>
    <ol class="p-list">{''.join(rows)}</ol>
  </div>
</section>"""
