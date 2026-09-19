"""Каркас страницы: <head> с мета-тегами и JSON-LD, шапка внутренних страниц, подвал."""
import json

from .text import esc, inline

SITE = "https://egorprotasov.ru"

# Возраст пересчитывается в браузере от даты рождения, чтобы «Мне 19» не устарело.
AGE_JS = ("document.querySelectorAll('[data-born]').forEach(function(e){var b=new Date(e.dataset.born),n=new Date(),"
          "a=n.getFullYear()-b.getFullYear();if(n.getMonth()<b.getMonth()||(n.getMonth()==b.getMonth()&&n.getDate()<b.getDate()))a--;"
          "e.textContent=a})")


def head(*, title, description, path, og_image, og_type, jsonld, css_v, noindex=False):
    url = SITE + path
    robots = '<meta name="robots" content="noindex, follow">' if noindex else ""
    ld = json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")) if jsonld else ""
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{url}">
{robots}<meta name="theme-color" content="#ffffff">
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
{f'<script type="application/ld+json">{ld}</script>' if ld else ''}
</head>"""


def topbar(crumbs):
    """crumbs: [(подпись, адрес)] после имени."""
    rest = "".join(f'<span class="sep" aria-hidden="true">/</span><a href="{esc(h)}">{esc(t)}</a>' for t, h in crumbs)
    return (f'<header class="topbar"><nav class="wrap" aria-label="Навигация">'
            f'<a class="home" href="/">Егор Протасов</a>{rest}</nav></header>')


def footer(site):
    links = "".join(f'<a href="{esc(c["href"])}"{" rel=\"me noopener\"" if c["href"].startswith("http") else ""}>'
                    f'{esc(c["label"])}</a>' for c in site["contacts"])
    return (f'<footer class="site-foot"><div class="wrap"><div class="contacts">{links}</div>'
            f'<p class="made">{inline(site["footer_note"])}</p></div></footer>')


def page(*, head_html, body, site, chart_js_v=None, top=None):
    scripts = f'<script src="/assets/chart.js?v={chart_js_v}" defer></script>' if chart_js_v else ""
    return f"""{head_html}
<body>
<a class="skip" href="#main">Перейти к содержимому</a>
{top or ''}
<main id="main">
{body}
</main>
{footer(site)}
{scripts}<script>{AGE_JS}</script>
</body>
</html>
"""
