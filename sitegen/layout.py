"""Каркас страницы: <head> с мета-тегами и JSON-LD, липкая шапка, подвал."""
import json
import pathlib

from .hero import LOGO, sticky_header
from .text import esc, inline

SITE = "https://egorprotasov.ru"
ICONS = pathlib.Path(__file__).resolve().parent.parent / "src" / "icons"

# Возраст пересчитывается в браузере от даты рождения, чтобы «Мне 19» не устарело.
AGE_JS = ("document.querySelectorAll('[data-born]').forEach(function(e){var b=new Date(e.dataset.born),n=new Date(),"
          "a=n.getFullYear()-b.getFullYear();if(n.getMonth()<b.getMonth()||(n.getMonth()==b.getMonth()&&n.getDate()<b.getDate()))a--;"
          "e.textContent=a})")

MAIL_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2.5" fill="none" '
             'stroke="currentColor" stroke-width="1.8"/><path d="m4 7 8 6 8-6" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>')


def head(*, title, description, path, og_image, og_type, jsonld, css_v, noindex=False,
         image_alt="", modified="", author="Егор Протасов"):
    url = SITE + path
    robots = ('<meta name="robots" content="noindex, follow">' if noindex else
              '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">')
    ld = json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")) if jsonld else ""
    extra = [f'<meta property="og:image:alt" content="{esc(image_alt or title)}">',
             f'<meta name="author" content="{esc(author)}">']
    if og_type == "article" and modified:
        extra += [f'<meta property="article:modified_time" content="{modified}">',
                  f'<meta property="article:published_time" content="{modified}">',
                  f'<meta property="article:author" content="{SITE}/">']
    if og_type == "profile":
        extra += ['<meta property="profile:first_name" content="Егор">',
                  '<meta property="profile:last_name" content="Протасов">',
                  '<meta property="profile:username" content="Kom1sh">']
    extra_html = "\n".join(extra)
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
{robots}
<meta name="theme-color" content="#000000">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/site.css?v={css_v}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Егор Протасов">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
{extra_html}
<link rel="alternate" type="text/plain" href="{SITE}/llms.txt" title="Версия сайта для языковых моделей">
{f'<script type="application/ld+json">{ld}</script>' if ld else ''}
</head>"""


def _icon(name):
    svg = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
    if "<title>" in svg:
        svg = svg[:svg.index("<title>")] + svg[svg.index("</title>") + 8:]
    return svg.strip()


def socials(site):
    out = []
    for c in site["contacts"]:
        icon = MAIL_ICON if c["icon"] == "mail" else _icon(c["icon"])
        out.append(f'<a class="soc" href="{esc(c["href"])}" aria-label="{esc(c["label"])}"'
                   f'{" rel=\"me noopener\"" if c["href"].startswith("http") else ""}>{icon}</a>')
    return "".join(out)


def nav(own, client):
    """Разделы в шапке: свои проекты, клиентские, обо мне."""
    return [("Своё", [(p["nav_label"], f"/projects/{p['slug']}/") for p in own]),
            ("Клиенты", [(p["nav_label"], f"/projects/{p['slug']}/") for p in client]),
            ("Обо мне", [("путь", "/#path"), ("вне работы", "/#life"), ("контакты", "/#contacts")])]


def footer(site, own, client):
    own_links = "".join(f'<a href="/projects/{p["slug"]}/">{inline(p["nav_label"])}</a>' for p in own)
    cl_links = "".join(f'<a href="/projects/{p["slug"]}/">{inline(p["nav_label"])}</a>' for p in client)
    contacts = "".join(f'<a href="{esc(c["href"])}">{esc(c["foot_label"])}</a>'
                       for c in site["contacts"] if c.get("foot_label"))
    return f"""<footer class="foot" id="contacts">
  <div class="wrap">
    <div class="f-top">
      <div class="f-id"><a class="logo big" href="/" aria-label="Егор Протасов, на главную">{LOGO}</a>
        <p><b>{esc(site["person"]["name"])}</b><br>{esc(site["person"]["role_line"])}</p></div>
      <div class="f-soc">{socials(site)}</div>
    </div>
    <div class="f-nav">
      <div><p class="lbl">Своё</p>{own_links}</div>
      <div><p class="lbl">Клиенты</p>{cl_links}</div>
      <div><p class="lbl">Обо мне</p><a href="/#path">Путь</a><a href="/#life">Вне работы</a>
        <a href="https://kom1sh.github.io/seo-course/">Факультатив по SEO и GEO</a></div>
      <div><p class="lbl">Связаться</p>{contacts}</div>
    </div>
    <div class="f-bottom"><span>© {site["meta"]["updated"][:4]} {esc(site["person"]["name"])}</span>
      <span>Данные на сайте обновлены {esc(site["meta"]["updated_label"])}</span>
      <span>{inline(site["footer_note"])}</span></div>
  </div>
</footer>"""


def metrika(counter):
    """Счётчик Яндекс.Метрики: нужен, чтобы видеть переходы из поиска и из ответов ИИ."""
    if not counter:
        return ""
    return f"""<script>
(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};
m[i].l=1*new Date();for(var j=0;j<document.scripts.length;j++){{if(document.scripts[j].src===r){{return}}}}
k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})
(window,document,'script','https://mc.yandex.ru/metrika/tag.js?id={counter}','ym');
ym({counter},'init',{{ssr:true,webvisor:true,clickmap:true,accurateTrackBounce:true,trackLinks:true}});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/{counter}" style="position:absolute;left:-9999px" alt=""></div></noscript>"""


def page(*, head_html, body, site, own, client, nav_data, chart_js_v=None, sticky=False):
    """sticky — липкая шапка отдельно: на главной она уже внутри первого экрана."""
    bar = sticky_header(nav_data, home="/") if sticky else ""
    scripts = f'<script src="/assets/chart.js?v={chart_js_v}" defer></script>' if chart_js_v else ""
    return f"""{head_html}
<body>
<a class="skip" href="#main">Перейти к содержимому</a>
{bar}
{body}
{footer(site, own, client)}
{scripts}<script src="/assets/motion.js" defer></script><script src="/assets/menu.js" defer></script>
<script>{AGE_JS}</script>
{metrika(site.get("analytics", {}).get("metrika"))}
</body>
</html>
"""
