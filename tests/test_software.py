"""Проверки посадочных программ: страница, вырезки, стоп-слова.

    python3 -m unittest discover -s tests
"""
import pathlib
import sys
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _programs():
    ps = [tomllib.loads(f.read_text(encoding="utf-8")) for f in sorted((ROOT / "src" / "projects").glob("*.toml"))]
    return sorted((p for p in ps if p["kind"] == "software"), key=lambda p: p["sheet"])


class Page(unittest.TestCase):
    def setUp(self):
        from sitegen import software
        self.software = software
        self.programs = _programs()

    def page(self, p):
        return self.software.page(p, img={}, sheets=self.programs)

    def test_three_programs_in_order(self):
        self.assertEqual([p["slug"] for p in self.programs], ["emd-finder", "strata", "site-audit"])

    def test_page_has_every_block(self):
        for p in self.programs:
            with self.subTest(slug=p["slug"]):
                html = self.page(p)
                for marker in ('class="sw-hero"', 'class="sw-how"', 'class="sw-why"', 'class="sw-can"',
                               'class="sw-work"', 'class="sw-more"', 'class="sw-talk"'):
                    self.assertIn(marker, html)
                self.assertEqual(html.count('<li class="st"'), 3)
                self.assertNotIn("how-fig", html)

    def test_hero_has_icon_real_frame_and_words(self):
        for p in self.programs:
            with self.subTest(slug=p["slug"]):
                html = self.page(p)
                hero = html[html.index('class="sw-hero"'):html.index('class="sw-how"')]
                self.assertIn(f'/assets/img/icon-{p["slug"]}-', hero)
                self.assertIn(f'/assets/img/{p["hero"]["img"]}-', hero)
                self.assertIn(p["hero"]["tag"], hero)
                self.assertIn("<h1>", hero)

    def test_every_tag_sits_inside_its_crop(self):
        for p in self.programs:
            for f in [p["hero"]] + p["steps"]:
                with self.subTest(slug=p["slug"], img=f["img"]):
                    m = f["mark"]
                    self.assertGreaterEqual(m["x"], -1)
                    self.assertGreaterEqual(m["y"], -1)
                    self.assertLessEqual(m["x"] + m["w"], f["w"] + 1)
                    self.assertLessEqual(m["y"] + m["h"], f["h"] + 1)

    def test_other_programs_are_icons_and_not_a_link_to_itself(self):
        for p in self.programs:
            with self.subTest(slug=p["slug"]):
                s = self.page(p)
                s = s[s.index('class="sw-more"'):]
                self.assertNotIn(f'href="/projects/{p["slug"]}/"', s)
                for other in self.programs:
                    if other is not p:
                        self.assertIn(f'href="/projects/{other["slug"]}/"', s)
                        self.assertIn(f'/assets/img/icon-{other["slug"]}-', s)

    def test_home_band_shows_every_program_icon(self):
        html = self.software.home_band(self.programs)
        for p in self.programs:
            self.assertIn(f'href="/projects/{p["slug"]}/"', html)
            self.assertIn(f'/assets/img/icon-{p["slug"]}-', html)


class StopWords(unittest.TestCase):
    def test_sources_and_stack_are_caught(self):
        from sitegen import guard
        self.assertTrue(guard.software_stop_hits("данные из Ahrefs и веб-архива"))
        self.assertTrue(guard.software_stop_hits("ссылка get.egorprotasov.ru/d/x"))
        self.assertFalse(guard.software_stop_hits("Находит нишу и свободный домен"))

    def test_program_pages_are_clean(self):
        from sitegen import guard, software
        programs = _programs()
        for p in programs:
            with self.subTest(slug=p["slug"]):
                self.assertEqual(guard.software_stop_hits(software.page(p, img={}, sheets=programs)), [])


if __name__ == "__main__":
    unittest.main()
