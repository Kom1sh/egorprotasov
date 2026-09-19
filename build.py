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
S1, S2 = "#0a6ee0", "#1f9d62"
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
    own_dates = days(D(2026, 6, 15), D(2026, 9, 18))
    tk = C.moving_average(series("techkio-organic", "visits", own_dates, D(2026, 7, 17)))
    mp = C.moving_average(series("mapka-organic", "visits", own_dates))
    src_own = site["chart"]["source"]
    out = {}

    out["home"] = C.line_chart(
        "growth", title=site["chart"]["title"], dates=own_dates, source=src_own,
        series=[{"name": "techkio.ru", "color": S1, "values": tk}, {"name": "мапка.рф", "color": S2, "values": mp}],
        annotations=[{"date": D(2026, 7, 20), "label": ["запуск techkio.ru", "и движка мапки"], "mobile": "запуск"}],
        mobile_from=D(2026, 7, 10),
        summary=f"Визиты из поиска в день: techkio.ru вырос с нуля до {round(tk[-1])}, мапка.рф — с 2 до {round(mp[-1])}.")
    out["spark"] = {"techkio": C.sparkline(tk, S1, "Рост визитов techkio.ru из поиска"),
                    "mapka": C.sparkline(mp, S2, "Рост визитов мапка.рф из поиска")}

    out["mapka"] = C.line_chart(
        "mapka-growth", title="Визиты из поиска в день", dates=own_dates, source=src_own,
        series=[{"name": "мапка.рф", "color": S2, "values": mp}],
        annotations=[{"date": D(2026, 7, 23), "label": ["фасетный движок", "в проде"], "mobile": "движок"}],
        mobile_from=D(2026, 7, 1),
        summary=f"Визиты мапка.рф из поиска выросли с 2 до {round(mp[-1])} в день после запуска фасетного движка 23 июля 2026.")

    tk_dates = days(D(2026, 7, 17), D(2026, 9, 18))
    tk2 = C.moving_average(series("techkio-organic", "visits", tk_dates))
    out["techkio"] = C.line_chart(
        "techkio-growth", title="Визиты из поиска в день", dates=tk_dates, source=src_own,
        series=[{"name": "techkio.ru", "color": S1, "values": tk2}],
        annotations=[{"date": D(2026, 8, 1), "label": ["посадочные под", "кластеры запросов"], "mobile": "посадочные"},
                     {"date": D(2026, 9, 1), "label": ["переезд", "после вайпа"], "mobile": "переезд"}],
        summary=f"Визиты techkio.ru из поиска выросли с нуля до {round(tk2[-1])} в день за два месяца.")

    ad_dates = days(D(2025, 5, 8), D(2026, 9, 16))
    spike = (D(2026, 5, 23), D(2026, 5, 31), ["спамный всплеск", "исключён"])
    gsc_src = "Скользящее среднее за 7 дней. Google Search Console, 8 мая 2025 — 16 сентября 2026."
    clicks = series("ad-network", "clicks_7d", ad_dates)
    pos = series("ad-network", "position_7d", ad_dates)
    out["ad-network"] = C.line_chart(
        "ad-clicks", title="Клики из Google в день", dates=ad_dates, source=gsc_src,
        series=[{"name": "клики", "color": S1, "values": clicks}], bands=[spike],
        annotations=[{"date": D(2026, 8, 29), "label": ["обвал", "29–30 августа"], "mobile": "обвал"}],
        summary="Клики из Google выросли примерно с 23 до 91 в день к маю 2026 года; спамный всплеск 23–31 мая исключён; 29–30 августа начался обвал.") + \
        C.line_chart(
            "ad-position", title="Средняя позиция в Google, выше — ближе к первой строке", dates=ad_dates, source=gsc_src,
            series=[{"name": "позиция", "color": S2, "values": pos}], kind="pos", invert=True, bands=[spike],
            summary="Средняя позиция в Google улучшилась примерно с 52 до 10 к маю 2026 года.")

    cx_dates = days(D(2025, 5, 8), D(2026, 9, 16))
    impr = series("crypto-exchange", "impressions_7d", cx_dates)
    out["crypto-exchange"] = C.line_chart(
        "cx-impressions", title="Показы в Google в день", dates=cx_dates,
        source="Скользящее среднее за 7 дней. Google Search Console, 8 мая 2025 — 16 сентября 2026.",
        series=[{"name": "показы", "color": S1, "values": impr}],
        annotations=[{"date": D(2026, 1, 17), "label": ["первая волна", "страниц пар"], "mobile": "1-я волна"},
                     {"date": D(2026, 5, 19), "label": ["вторая", "волна"], "mobile": "2-я волна"}],
        summary="Показы криптобиржи в Google выросли примерно в пять раз за год.") + \
        pages.quarter_table(
            [("III квартал 2025", 15714, 52242, "12,9%"), ("IV квартал 2025", 16470, 53717, "17,5%"),
             ("I квартал 2026", 12306, 65160, "36,2%"), ("II квартал 2026", 18904, 135088, "38,9%")],
            "По кварталам",
            "Google Search Console. Доля небрендовых показов посчитана по запросам, которые Search Console раскрывает.")

    # ряды для линий на превью в соцсетях
    out["_traces"] = {
        "home": [{"color": S1, "values": tk}, {"color": S2, "values": mp}],
        "mapka": [{"color": S2, "values": mp}],
        "techkio": [{"color": S1, "values": tk2}],
        "ad-network": [{"color": S1, "values": clicks}],
        "crypto-exchange": [{"color": S1, "values": impr}],
    }
    return out


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
    written = []

    meta = site["meta"]
    head = layout.head(title=meta["title"], description=meta["description"], path="/", og_image="/assets/og/home.png",
                       og_type="profile", jsonld=home_ld(site, img), css_v=css_v)
    body = pages.home(site, own, client, img, ch["home"], ch["spark"], age)
    written.append(write("index.html", layout.page(head_html=head, body=body, site=site, chart_js_v=js_v)))

    ordered = own + client
    extras = {"mediachef": lambda p: pages.bars(p["sources"], "Откуда приходят на сайт"),
              "ultracker": lambda p: pages.ultracker_scheme()}
    for i, p in enumerate(ordered):
        slug = p["slug"]
        extra = ch.get(slug) or (extras[slug](p) if slug in extras else "")
        has_chart = slug in ch
        head = layout.head(title=f"{plain(p['title'])}. Егор Протасов", description=p["description"],
                           path=f"/projects/{slug}/", og_image=f"/assets/og/{slug}.png", og_type="article",
                           jsonld=project_ld(p, site), css_v=css_v)
        body = pages.project(p, result_extra=extra, next_p=ordered[(i + 1) % len(ordered)], asof=ASOF)
        top = layout.topbar([("Проекты", "/#projects")])
        written.append(write(f"projects/{slug}/index.html",
                             layout.page(head_html=head, body=body, site=site, top=top,
                                         chart_js_v=js_v if has_chart else None)))

    head = layout.head(title="Страница не найдена. Егор Протасов", description="Такой страницы нет.", path="/404.html",
                       og_image="/assets/og/home.png", og_type="website", jsonld=None, css_v=css_v, noindex=True)
    written.append(write("404.html", layout.page(head_html=head, body=pages.not_found(), site=site,
                                                 top=layout.topbar([]))))

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
