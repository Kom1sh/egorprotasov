"""Проверки посадочных программ: страница, геометрия кадров, стоп-слова.

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


def _img_meta(programs):
    return {f["img"]: {"ratio": f["h"] / f["w"], "widths": [f["w"], f["w"] * 2]} for p in programs for f in p["figs"]}


class Page(unittest.TestCase):
    def setUp(self):
        from sitegen import software
        self.software = software
        self.programs = _programs()
        self.img = _img_meta(self.programs)

    def test_three_programs_in_order(self):
        self.assertEqual([p["slug"] for p in self.programs], ["emd-finder", "strata", "site-audit"])

    def test_page_has_every_block_and_no_drawing(self):
        for p in self.programs:
            with self.subTest(slug=p["slug"]):
                html = self.software.page(p, img=self.img, sheets=self.programs)
                for marker in ('class="sw-hero"', 'class="sw-how"', 'class="sw-why"', 'class="sw-can"',
                               'class="sw-work"', 'class="sw-more"', 'class="sw-talk"'):
                    self.assertIn(marker, html)
                self.assertEqual(html.count('class="how-item'), 3)
                self.assertNotIn('class="machine', html)
                self.assertNotIn("Фиг.", html)

    def test_hero_shows_a_real_frame_of_this_program(self):
        for p in self.programs:
            with self.subTest(slug=p["slug"]):
                html = self.software.page(p, img=self.img, sheets=self.programs)
                hero = html[html.index('class="sw-hero"'):html.index('class="sw-how"')]
                self.assertIn(f'/assets/img/{p["figs"][p["hero"]]["img"]}-', hero)
                self.assertIn("<h1>", hero)

    def test_other_programs_link_out_but_not_to_itself(self):
        for p in self.programs:
            with self.subTest(slug=p["slug"]):
                html = self.software.page(p, img=self.img, sheets=self.programs)
                s = html[html.index('class="sw-more"'):]
                self.assertNotIn(f'href="/projects/{p["slug"]}/"', s)
                for other in self.programs:
                    if other is not p:
                        self.assertIn(f'href="/projects/{other["slug"]}/"', s)

    def test_camera_inside_crop_and_mark_inside_camera(self):
        for p in self.programs:
            for f in p["figs"]:
                with self.subTest(slug=p["slug"], img=f["img"], cap=f["cap"]):
                    c, m = f["cam"], f["mark"]
                    self.assertGreaterEqual(c["x"], 0)
                    self.assertGreaterEqual(c["y"], 0)
                    self.assertLessEqual(c["x"] + c["w"], f["w"] + 1)
                    self.assertLessEqual(c["y"] + c["h"], f["h"] + 1)
                    self.assertGreaterEqual(m["x"], c["x"] - 1)
                    self.assertGreaterEqual(m["y"], c["y"] - 1)
                    self.assertLessEqual(m["x"] + m["w"], c["x"] + c["w"] + 1)
                    self.assertLessEqual(m["y"] + m["h"], c["y"] + c["h"] + 1)

    def test_home_band_links_every_program(self):
        html = self.software.home_band(self.programs)
        for p in self.programs:
            self.assertIn(f'href="/projects/{p["slug"]}/"', html)


class StopWords(unittest.TestCase):
    def test_sources_and_stack_are_caught(self):
        from sitegen import guard
        self.assertTrue(guard.software_stop_hits("данные из Ahrefs и веб-архива"))
        self.assertTrue(guard.software_stop_hits("ссылка get.egorprotasov.ru/d/x"))
        self.assertFalse(guard.software_stop_hits("Находит нишу и свободный домен"))

    def test_program_pages_are_clean(self):
        from sitegen import guard, software
        programs = _programs()
        img = _img_meta(programs)
        for p in programs:
            with self.subTest(slug=p["slug"]):
                self.assertEqual(guard.software_stop_hits(software.page(p, img=img, sheets=programs)), [])


if __name__ == "__main__":
    unittest.main()
