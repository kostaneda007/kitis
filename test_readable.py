"""User regression: visible results and explicit bell information, not tooltips."""
import re
import subprocess
import unittest
from pathlib import Path
from overview_timeline import MON, MAIN, minute

class ReadableTests(unittest.TestCase):
    def test_every_interval_static(self):
        days=re.findall(r'<section class="card-day".*?</section>',Path('index.html').read_text(),re.S)
        for day in days:
            if 'data-wday="Вс"' in day:continue
            arr=MON if 'data-wday="Пн"' in day else MAIN
            cards=re.findall(r'<div class="bell-card .*?</div>',day,re.S)
            cards=[re.sub('<[^>]+>','',c) for c in cards]
            self.assertEqual(len(cards),len(arr)*2-1)
            for i,(a,b) in enumerate(arr):
                self.assertIn(a+'–'+b,cards[i*2])
                self.assertIn(str(minute(b)-minute(a))+' мин',cards[i*2])
                if i<len(arr)-1:
                    end=arr[i+1][0]
                    self.assertIn(b+'–'+end,cards[i*2+1])
                    self.assertIn(str(minute(end)-minute(b))+' мин',cards[i*2+1])
    def test_originals_preserved(self):
        old=subprocess.check_output(['git','show','8992b72:index.html'],text=True)
        s=Path('index.html').read_text()
        for pat in [r'<li class="tl-item.*?</li>',r'<table.*?</table>',r'var LISTS = .*?;',r'var BELLS = .*?;']:
            self.assertEqual(re.findall(pat,old,re.S),re.findall(pat,s,re.S))
    def test_idempotent(self):
        from readable_overview import improve
        s=Path('index.html').read_text();self.assertEqual(improve(s),s)

if __name__=='__main__':unittest.main()
