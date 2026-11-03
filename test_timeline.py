"""Static regression checks, including exact preservation against approved base."""
import re, subprocess, unittest
from pathlib import Path

class TimelineTests(unittest.TestCase):
    def test_overviews_present_in_static_html(self):
        s=Path('index.html').read_text()
        days=re.findall(r'<section class="card-day".*?</section>',s,re.S)
        self.assertTrue(days)
        for day in days:
            if 'data-wday="Вс"' not in day:
                self.assertIn('class="day-overview"',day)
                self.assertIn('class="day-scale"',day)
                self.assertNotRegex(day,r'class="day-segment break"[^>]*>[^<]+')
    def test_original_data_unchanged(self):
        old=subprocess.check_output(['git','show','76a5e2b:index.html'],text=True)
        new=Path('index.html').read_text()
        for pattern in [r'<li class="tl-item.*?</li>',r'<table.*?</table>',r'var LISTS = .*?;',r'var BELLS = .*?;']:
            self.assertEqual(re.findall(pattern,old,re.S),re.findall(pattern,new,re.S))
    def test_idempotent(self):
        from overview_timeline import enhance
        s=Path('index.html').read_text()
        self.assertEqual(enhance(s),s)

if __name__=='__main__': unittest.main()
