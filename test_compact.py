from pathlib import Path
import json, subprocess
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright
OUT=Path('/Users/konstantinmorylev/.hermes/cache/scratch/kitis-v11');OUT.mkdir(exist_ok=True,parents=True)
with sync_playwright() as p:
 b=p.chromium.launch()
 for width in [1440,1050,390,320]:
  page=b.new_page(viewport={'width':width,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.clock.install(time=datetime(2026,11,3,7,20,tzinfo=timezone.utc))
  page.goto(Path('index.html').resolve().as_uri());page.wait_for_timeout(300)
  if width<1025:page.locator('.tab[data-tab=t]').click()
  page.locator('#tlist .li').filter(has_text='Морылёв').click()
  ent=page.locator('.ent:not([hidden])');assert ent.locator('.card-day').count()==7
  ent.locator('[data-view=res]').click();assert ent.locator('[data-pane=res] table tr').count()>1
  rows=ent.locator('[data-pane=res] table tr').count();ent.locator('[data-view=sch]').click()
  page.evaluate('scrollTo(0,0)');page.wait_for_timeout(300)
  assert not page.locator('.appbar').evaluate('(e)=>e.classList.contains("overview-pinned")')
  page.screenshot(path=str(OUT/f'top-{width}.png'))
  page.evaluate('scrollTo(0,650)');page.wait_for_timeout(300)
  assert page.locator('.appbar.overview-pinned #globalOverview').count()==1
  assert page.locator('#globalOverview').count()==1
  geometry=page.evaluate('''()=>{let a=document.querySelector('.appbar').getBoundingClientRect(),o=document.querySelector('#globalOverview').getBoundingClientRect(),t=document.querySelector('.tabs').getBoundingClientRect();return {header:a.height,overviewTop:o.top,overviewBottom:o.bottom,tabsTop:t.top,overflow:document.documentElement.scrollWidth>innerWidth}}''')
  assert not geometry['overflow'],geometry
  assert geometry['overviewBottom']<=geometry['tabsTop']+1,geometry
  assert page.locator('#liveTime').is_visible() and page.locator('#liveLeft').is_visible()
  assert '10:00' in page.locator('#liveTime').inner_text()
  page.screenshot(path=str(OUT/f'pinned-{width}.png'))
  page.locator('#overviewExpand').click();assert page.locator('#intervalSelect').is_visible()
  page.locator('#intervalSelect').select_option(index=2)
  assert page.locator('#intervalDetail').inner_text()
  page.locator('#overviewExpand').focus();page.keyboard.press('Escape');print(page.evaluate('({y:scrollY,head:document.querySelector(".appbar").className,cls:document.querySelector("#globalOverview").className,expanded:document.querySelector("#overviewExpand").getAttribute("aria-expanded")})'));assert not page.locator('#intervalSelect').is_visible()
  page.clock.run_for(60000);assert '39 мин' in page.locator('#liveLeft').inner_text(),page.locator('#liveLeft').inner_text()
  page.clock.fast_forward(40*60000);assert 'Перемена' in page.locator('#liveLeft').inner_text()
  assert '10:10' in page.locator('#liveTime').inner_text()
  page.evaluate('scrollTo(0,0)');page.wait_for_timeout(300)
  assert page.locator('.overview-home>#globalOverview').count()==1
  assert page.locator('#intervalSelect').is_visible()
  assert not errors,errors
  print(json.dumps({'width':width,'geometry':geometry,'days':7,'results_rows':rows,'errors':errors,'lesson_break_countdown':'passed'}))
  page.close()
 b.close()
# Every original schedule panel is byte-identical (only the preceding overview changed).
s=Path('index.html').read_text();old=subprocess.check_output(['git','show','99b018f:index.html'],text=True)
a='<section class="ent" id="panel-default"';end='<script>'
assert s[s.index(a):s.index(end)]==old[old.index(a):old.index(end)]
print('ALL STATIC SCHEDULE PANELS BYTE-IDENTICAL; screenshots',OUT)
