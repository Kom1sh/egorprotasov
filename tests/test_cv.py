"""Проверки CV: что попадает в PDF и как на него ведут кнопки сайта.

    python3 -m unittest discover -s tests
"""
import pathlib
import re
import sys
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _data():
    site = tomllib.loads((ROOT / "src" / "site.toml").read_text(encoding="utf-8"))
    site["cv"] = tomllib.loads((ROOT / "src" / "cv.toml").read_text(encoding="utf-8"))
    ps = [tomllib.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "src" / "projects").glob("*.toml"))]
    pick = lambda kind, key: sorted((p for p in ps if p["kind"] == kind), key=lambda p: p[key])
    return site, pick("own", "order"), pick("client", "order"), pick("software", "sheet")


class Cv(unittest.TestCase):
    def setUp(self):
        from sitegen import cv
        self.cv = cv
        self.site, self.own, self.client, self.programs = _data()
        self.html = cv.html(self.site, self.site["cv"], self.own, self.client, self.programs, "20 сентября 2026")

    def test_no_phone(self):
        self.assertNotRegex(self.html, r"\+7[\s\d()-]{9,}")
        self.assertNotIn("tel:", self.html)

    def test_contacts_are_full_links(self):
        for href in ("mailto:egorprotasov06@gmail.com", "https://t.me/Kom1sh", "https://vk.com/kom1sh",
                     "https://egorprotasov.ru/"):
            self.assertIn(f'href="{href}"', self.html)
        self.assertNotIn("github.com", self.html)

    def test_every_project_links_to_its_case(self):
        for p in self.own + self.client + self.programs:
            self.assertIn(f'href="https://egorprotasov.ru/projects/{p["slug"]}/"', self.html)

    def test_passes_forbidden_words_guard(self):
        from sitegen import guard
        self.assertEqual(guard.forbidden_hits(self.html), [])

    def test_font_keeps_cyrillic_text_whole(self):
        # системный SF Pro рвёт кириллицу в тексте PDF на кусочки
        self.assertNotIn("-apple-system", self.html)

    def test_page_count(self):
        one = b"<</Type /Pages /Count 1>> <</Type /Page /Parent 1 0 R>>"
        self.assertEqual(self.cv.pages(one), 1)
        self.assertEqual(self.cv.pages(one + b" <</Type /Page>>"), 2)


class Buttons(unittest.TestCase):
    def test_hero_and_sticky_header_link_the_pdf(self):
        from sitegen import hero
        site, *_ = _data()
        cv = site["cv"]
        html = hero.hero(quote_lines=[("l", "x")], quote_author="a", name_line="n", role="r", now_text="t",
                         traces="", nav=[], cv=cv)
        href = f'href="/{cv["file"]}" download="{cv["download_name"]}"'
        for cls in ("cv-link", "bar-cv", "ov-cv", "btn-cv"):
            self.assertRegex(html, rf'<a class="{cls}" {re.escape(href)}>')

    def test_no_cv_no_links(self):
        from sitegen import hero
        self.assertEqual(hero.cv_link(None, "cv-link"), "")


if __name__ == "__main__":
    unittest.main()
