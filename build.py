#!/usr/bin/env python3
"""Сборка egorprotasov.ru.

    python3 build.py          # страницы, картинки, sitemap, проверки
    python3 build.py --og     # плюс превью для соцсетей и иконки (нужен Google Chrome)

Контент — src/site.toml и src/projects/*.toml, ряды для графиков — src/data/*.csv,
исходные фото — src/img. Результат пишется в корень репозитория, его отдаёт GitHub Pages.
"""
import csv
import datetime as dt
import hashlib
import json
import pathlib
import sys
import tomllib

from sitegen import chart as C
from sitegen import guard, images, layout, pages
from sitegen.text import plain

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
SITE = layout.SITE
S1, S2 = "#bd7f0f", "#4a8fe0"   # проверено на чёрном фоне: янтарь и синий
ASOF = "20 сентября 2026"


def load():
    site = tomllib.loads((SRC / "site.toml").read_text(encoding="utf-8"))
    projects = [tomllib.loads(p.read_text(encoding="utf-8")) for p in sorted((SRC / "projects").glob("*.toml"))]
    own = sorted((p for p in projects if p["kind"] == "own"), key=lambda p: p["order"])
    client = sorted((p for p in projects if p["kind"] == "client"), key=lambda p: p["order"])
    return site, own, client


def series(name, key, dates, start=None):
    rows = {dt.date.fromisoformat(r["date"]): r[key] for r in csv.DictReader(open(SRC / "data" / f"{name}.csv"))}
    out = []
    for d in dates:
        v = rows.get(d, "")
        out.append(None if v == "" or (start and d < start) or d not in rows else float(v))
    return out


def days(a, b):
    return [a + dt.timedelta(i) for i in range((b - a).days + 1)]


D = dt.date


# ——— графики ———

def charts(site):
    """Графики на главной и на страницах проектов. Цвета проверены на чёрном фоне."""
    end = D(2026, 9, 19)
    own_dates = days(D(2026, 6, 15), end)
    tk = series("techkio-organic", "visits", own_dates, D(2026, 7, 17))
    mp = series("mapka-organic", "visits", own_dates)
    src_own = site["chart"]["source"]
    out = {}

    out["home"] = C.line_chart(
        "growth", title=site["chart"]["title"], dates=own_dates, source=src_own,
        series=[{"name": "K.I.O", "color": S1, "values": tk}, {"name": "мапка.рф", "color": S2, "values": mp}],
        annotations=[{"date": D(2026, 7, 20), "label": ["запуск K.I.O", "и движка мапки"], "mobile": "запуск"}],
        mobile_from=D(2026, 7, 10),
        summary="Визиты из поиска по дням: K.I.O с нуля до 240 в среднем за неделю, пик 323, мапка.рф с двух до 97 в среднем за неделю.")

    out["mapka"] = C.line_chart(
        "mapka-visits", title="Визиты из поиска по дням", dates=own_dates, source=src_own,
        series=[{"name": "мапка.рф", "color": S2, "values": mp}],
        annotations=[{"date": D(2026, 7, 23), "label": ["запуск фасетного", "движка"], "mobile": "движок"}],
        mobile_from=D(2026, 7, 1),
        summary="Визиты мапки из поиска: 1–2 в день в июне, 97 в среднем за последнюю неделю, пик 125 пятнадцатого сентября.")

    tk_dates = days(D(2026, 7, 17), end)
    tk2 = series("techkio-organic", "visits", tk_dates)
    out["techkio"] = C.line_chart(
        "kio-visits", title="Визиты из поиска по дням", dates=tk_dates,
        source="Яндекс.Метрика, визиты из поисковых систем по дням, 17 июля — 19 сентября 2026.",
        series=[{"name": "techkio.ru", "color": S1, "values": tk2}],
        annotations=[{"date": D(2026, 8, 1), "label": ["посадочные под", "кластеры запросов"], "mobile": "посадочные"},
                     {"date": D(2026, 9, 1), "label": ["переезд", "после вайпа"], "mobile": "переезд"}],
        summary="Визиты techkio.ru из поиска: с нуля в июле до 240 в среднем за неделю, пик 323 девятнадцатого сентября.")

    ad_dates = days(D(2025, 5, 8), D(2026, 9, 16))
    spike = [(D(2026, 5, 23), D(2026, 5, 31), "спамный всплеск исключён")]
    gsc = "Google Search Console, скользящее среднее за 7 дней, 8 мая 2025 — 16 сентября 2026."
    clicks = series("ad-network", "clicks_7d", ad_dates)
    pos = series("ad-network", "position_7d", ad_dates)
    out["ad-network"] = C.line_chart(
        "ad-clicks", title="Клики из Google в день", dates=ad_dates, source=gsc, bands=spike,
        series=[{"name": "клики", "color": S1, "values": clicks}],
        annotations=[{"date": D(2026, 8, 29), "label": ["обвал на стороне", "сайта клиента"], "mobile": "обвал"}],
        summary="Клики из Google: около 23 в день летом 2025 года, 91 в мае 2026-го, после обвала в конце августа — около 28.") + \
        C.line_chart(
            "ad-position", title="Средняя позиция в Google, выше — ближе к первой строке", dates=ad_dates,
            source=gsc, kind="pos", invert=True, bands=spike,
            series=[{"name": "позиция", "color": S2, "values": pos}],
            summary="Средняя позиция поднялась с 52 весной 2025 года до 10 к маю 2026-го, сейчас около 20.")

    impr = series("crypto-exchange", "impressions_7d", ad_dates)
    out["crypto-exchange"] = C.line_chart(
        "cx-impressions", title="Показы в Google в день", dates=ad_dates, source=gsc,
        series=[{"name": "показы", "color": S1, "values": impr}],
        annotations=[{"date": D(2026, 1, 17), "label": ["первая волна", "страниц торговых пар"], "mobile": "1-я волна"},
                     {"date": D(2026, 5, 19), "label": ["вторая", "волна"], "mobile": "2-я волна"}],
        summary="Показы криптобиржи в Google выросли примерно в пять раз за год.") + \
        pages.quarter_table(
            [("III квартал 2025", 15714, 52242, "12,9%"), ("IV квартал 2025", 16470, 53717, "17,5%"),
             ("I квартал 2026", 12306, 65160, "36,2%"), ("II квартал 2026", 18904, 135088, "38,9%")],
            "По кварталам",
            "Google Search Console. Доля небрендовых показов посчитана по запросам, которые Search Console раскрывает.")

    # линии роста на фоне первого экрана и ряды для превью в соцсетях
    out["_traces"] = {
        "home": [{"color": S1, "values": C.moving_average(tk)}, {"color": S2, "values": C.moving_average(mp)}],
        "mapka": [{"color": S2, "values": C.moving_average(mp)}],
        "techkio": [{"color": S1, "values": C.moving_average(tk2)}],
        "ad-network": [{"color": S1, "values": clicks}],
        "crypto-exchange": [{"color": S1, "values": impr}],
    }
    return out


def trace_paths(rows, w=1440):
    """Две линии роста, вписанные в фон первого экрана."""
    out = []
    for i, r in enumerate(rows):
        vals, h, y0 = r["values"], (520 if i == 0 else 260), 1150
        n, mx = len(vals), max(x for x in vals if x is not None)
        pts, pen = [], False
        for j, x in enumerate(vals):
            if x is None:
                pen = False
                continue
            pts.append(f"{'L' if pen else 'M'}{w * j / (n - 1):.1f},{y0 - h * x / mx:.1f}")
            pen = True
        out.append(f'<path class="t{i + 1}" d="{" ".join(pts)}"/>')
    return "".join(out)


# ——— JSON-LD ———

def person_ld(site, img):
    p = site["person"]
    return {
        "@type": "Person", "@id": f"{SITE}/#person", "name": p["name"], "url": f"{SITE}/",
        "jobTitle": p["job_title"], "description": plain(p["about"]),
        "image": f"{SITE}/assets/img/egor-{img['egor']['widths'][-1]}.jpg",
        "address": {"@type": "PostalAddress", "addressLocality": p["city"], "addressCountry": "RU"},
        "affiliation": {"@type": "CollegeOrUniversity", "name": "Донской государственный технический университет"},
        "knowsAbout": ["SEO", "GEO", "программное SEO", "управление проектами"],
        "sameAs": [c["href"] for c in site["contacts"] if c["href"].startswith("https://")],
    }


def home_ld(site, img):
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "ProfilePage", "@id": f"{SITE}/#page", "url": f"{SITE}/", "name": site["meta"]["title"],
         "dateModified": site["meta"]["updated"], "inLanguage": "ru", "mainEntity": {"@id": f"{SITE}/#person"}},
        person_ld(site, img),
        {"@type": "WebSite", "@id": f"{SITE}/#site", "url": f"{SITE}/", "name": "Егор Протасов", "inLanguage": "ru"},
    ]}


def project_ld(p, site):
    url = f"{SITE}/projects/{p['slug']}/"
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "@id": f"{url}#article", "url": url, "headline": plain(p["title"]),
         "description": p["description"], "inLanguage": "ru", "dateModified": site["meta"]["updated"],
         "author": {"@type": "Person", "@id": f"{SITE}/#person", "name": site["person"]["name"]},
         "image": f"{SITE}/assets/og/{p['slug']}.png"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Егор Протасов", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Проекты", "item": f"{SITE}/#projects"},
            {"@type": "ListItem", "position": 3, "name": plain(p["title"]), "item": url}]},
    ]}


# ——— сборка ———

def ver(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def llms_txt(site, own, client):
    lines = [f"# {site['person']['name']}", "",
             f"> {plain(site['person']['lead']).replace('{age}', str(pages.age_on(site['person']['born'], dt.date.today())))}", "",
             plain(site["person"]["about"]), "", "## Свои проекты", ""]
    lines += [f"- [{plain(p['title'])}]({SITE}/projects/{p['slug']}/): {plain(p['what'])}, {plain(p['row'])}" for p in own]
    lines += ["", "## Клиентские проекты (без названий по договорённости с клиентами)", ""]
    lines += [f"- [{plain(p['title'])}]({SITE}/projects/{p['slug']}/): {plain(p['row'])}" for p in client]
    lines += ["", "## Контакты", ""] + [f"- {c['label']}: {c['href']}" for c in site["contacts"]]
    return "\n".join(lines) + "\n"


def main():
    site, own, client = load()
    img = images.build(SRC / "img", ROOT / "assets" / "img")
    ch = charts(site)
    css_v, js_v = ver(ROOT / "assets" / "site.css"), ver(ROOT / "assets" / "chart.js")
    age = pages.age_on(site["person"]["born"], dt.date.today())
    nav = layout.nav(own, client)
    written = []

    meta = site["meta"]
    head = layout.head(title=meta["title"], description=meta["description"], path="/", og_image="/assets/og/home.png",
                       og_type="profile", jsonld=home_ld(site, img), css_v=css_v)
    body = pages.home(site, own, client, img, ch["home"], trace_paths(ch["_traces"]["home"]), age, nav)
    written.append(write("index.html", layout.page(head_html=head, body=body, site=site, own=own, client=client,
                                                   nav_data=nav, chart_js_v=js_v)))

    ordered = own + client
    extras = {"mediachef": lambda p: pages.bars(p["sources"], "Откуда приходят на сайт")}
    for i, p in enumerate(ordered):
        slug = p["slug"]
        extra = ch.get(slug) or (extras[slug](p) if slug in extras else "")
        head = layout.head(title=f"{plain(p['title'])}. Егор Протасов", description=p["description"],
                           path=f"/projects/{slug}/", og_image=f"/assets/og/{slug}.png", og_type="article",
                           jsonld=project_ld(p, site), css_v=css_v)
        body = pages.project(p, img=img, result_extra=extra, next_p=ordered[(i + 1) % len(ordered)], asof=ASOF)
        written.append(write(f"projects/{slug}/index.html",
                             layout.page(head_html=head, body=body, site=site, own=own, client=client, nav_data=nav,
                                         chart_js_v=js_v if slug in ch else None, sticky=True)))

    head = layout.head(title="Страница не найдена. Егор Протасов", description="Такой страницы нет.", path="/404.html",
                       og_image="/assets/og/home.png", og_type="website", jsonld=None, css_v=css_v, noindex=True)
    written.append(write("404.html", layout.page(head_html=head, body=pages.not_found(), site=site, own=own,
                                                 client=client, nav_data=nav, sticky=True)))

    # старые адреса кейсов
    for old, new in (("cases/adtech", "/projects/ad-network/"), ("cases/crypto", "/projects/crypto-exchange/"),
                     ("cases/p2p-lending", "/")):
        written.append(write(f"{old}/index.html", pages.redirect(new)))

    urls = ["/"] + [f"/projects/{p['slug']}/" for p in ordered]
    written.append(write("sitemap.xml", pages.sitemap(urls, meta["updated"])))
    written.append(write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"))
    written.append(write("llms.txt", llms_txt(site, own, client)))

    # проверки: запрещённые слова во всём, что уходит в публичный репозиторий
    to_check = written + list(SRC.rglob("*.toml")) + list(SRC.rglob("*.csv"))
    bad = {str(p.relative_to(ROOT)): h for p in to_check if (h := guard.forbidden_hits(p.read_text(encoding="utf-8")))}
    if bad:
        print("СБОРКА ОСТАНОВЛЕНА: на страницах запрещённые слова (названия клиентов или агентства):")
        for f in bad:
            print(f"  {f}: {len(bad[f])} совпадений")
        sys.exit(1)
    warnings = [(str(p.relative_to(ROOT)), w) for p in written if p.suffix == ".html"
                for w in guard.style_warnings(p.read_text(encoding="utf-8"))]
    for f, w in warnings:
        print(f"  предупреждение {f}: {w}")

    if "--og" in sys.argv:
        from sitegen import og
        og.build(ROOT, site, own + client, ch["_traces"])

    print(f"готово: {len(written)} файлов, предупреждений по тексту {len(warnings)}")


if __name__ == "__main__":
    main()
