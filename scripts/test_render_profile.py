from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from render_profile import render,NS

class RenderTests(unittest.TestCase):
    def test_readme_edit_updates_both_visible_cards(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);shutil.copytree(Path(__file__).resolve().parents[1]/'assets',root/'assets')
            for intro in ['I do machine learning and C#/.NET development.', 'Обучаю модели &amp; проверяю качество.']:
                (root/'README.md').write_text(f'<picture><source srcset="assets/profile-motion-mobile.svg"><img src="assets/profile-motion.svg" alt="{intro}"></picture>')
                expected=render(root)
                for name in ['profile-motion.svg','profile-motion-mobile.svg']:
                    svg=ET.fromstring((root/'assets'/name).read_text())
                    visible=' '.join(''.join(el.itertext()) for el in svg.findall(f'{{{NS}}}text') if el.find(f'{{{NS}}}tspan') is not None)
                    self.assertEqual(visible,expected)
                    self.assertGreater(len(svg.findall(f'.//{{{NS}}}rect')),300)
                self.assertIn('?v=',(root/'README.md').read_text())
                before={p:p.read_bytes() for p in [root/'README.md',root/'assets/profile-motion.svg',root/'assets/profile-motion-mobile.svg']}
                render(root)
                self.assertTrue(all(p.read_bytes()==data for p,data in before.items()))

if __name__=='__main__': unittest.main()
