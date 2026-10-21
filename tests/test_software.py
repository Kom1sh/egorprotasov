"""Проверки посадочных программ: чертежи, страница, стоп-слова.

    python3 -m unittest discover -s tests
"""
import pathlib
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sitegen import drawings  # noqa: E402

SLUGS = ("emd-finder", "strata", "site-audit")


class Drawings(unittest.TestCase):
    def test_each_drawing_is_valid_svg_with_six_callouts(self):
        for slug in SLUGS:
            with self.subTest(slug=slug):
                svg = drawings.DRAWINGS[slug]()
                root = ET.fromstring(svg)
                self.assertTrue(root.tag.endswith("svg"))
                calls = [g for g in root.iter() if g.get("class") == "call"]
                self.assertEqual(sorted(int(g.get("data-n")) for g in calls), [1, 2, 3, 4, 5, 6])

    def test_lines_are_normalised_for_drawing_in(self):
        for slug in SLUGS:
            with self.subTest(slug=slug):
                root = ET.fromstring(drawings.DRAWINGS[slug]())
                lines = [e for e in root.iter() if "ln" in (e.get("class") or "").split()]
                self.assertGreater(len(lines), 20)
                self.assertTrue(all(e.get("pathLength") == "1" for e in lines))

    def test_thumb_has_no_callouts_and_no_motion(self):
        for slug in SLUGS:
            with self.subTest(slug=slug):
                svg = drawings.thumb(slug)
                ET.fromstring(svg)
                self.assertNotIn('class="call"', svg)
                self.assertNotIn("jig", svg)
                self.assertNotIn("fall", svg)


def _programs():
    import tomllib
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

    def test_three_programs_in_sheet_order(self):
        self.assertEqual([p["slug"] for p in self.programs], ["emd-finder", "strata", "site-audit"])

    def test_page_has_every_block(self):
        for p in self.programs:
            with self.subTest(slug=p["slug"]):
                html = self.software.page(p, img=self.img, sheets=self.programs)
                for marker in ('class="sw-sheet"', 'class="sw-how"', 'class="sw-why"', 'class="sw-can"',
                               'class="sw-work"', 'class="sw-set"', 'class="sw-talk"'):
                    self.assertIn(marker, html)
                self.assertEqual(html.count('class="how-item'), 3)
                self.assertEqual(html.count('<li class="lg"'), 6)
                self.assertIn(f"лист {p['sheet']} из 3", html)

    def test_current_sheet_is_not_a_link_to_itself(self):
        for p in self.programs:
            with self.subTest(slug=p["slug"]):
                html = self.software.page(p, img=self.img, sheets=self.programs)
                s = html[html.index('class="sw-set"'):]
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
