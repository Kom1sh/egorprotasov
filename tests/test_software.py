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


if __name__ == "__main__":
    unittest.main()
