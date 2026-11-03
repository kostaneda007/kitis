from pathlib import Path
from datetime import datetime,timezone
import sys,json
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else Path('index.html').resolve().as_uri()
OUT=Path('/Users/konstantinmorylev/.hermes/cache/scratch/kitis-v8');OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch()
 for width in [1440,390]:
  page=b.new_page(viewport={'width':width,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.clock.install(time=datetime(2026,11,2,7,20,tzinfo=timezone.utc));page.goto(URL);page.wait_for_timeout(300)
  assert page.locator('.day-overview').count()==1
  assert page.locator('.card-day .day-overview').count()==0
  page.screenshot(path=str(OUT/f'chooser-{width}.png'))
  if width<1025:page.locator('.tab[data-tab=t]').click()
  page.locator('#tlist .li').filter(has_text='Морылёв').click()
  entity=page.locator('.ent:not([hidden])');assert entity.locator('.card-day').count()==7
  entity.locator('[data-view=res]').click();assert entity.locator('[data-pane=res]').is_visible()
  assert entity.locator('[data-pane=res] table tr').count()>1
  page.screenshot(path=str(OUT/f'results-{width}.png'))
  entity.locator('[data-view=sch]').click()
  assert page.locator('#globalOverview .bell-card').count()==13
  assert 'Пара 2'==page.locator('#globalOverview .bell-card.now b').inner_text()
  assert entity.locator('.card-day[data-wday="Пн"] .tl-item.now').count()==1
  before=page.locator('.day-cursor').evaluate('(e)=>parseFloat(e.style.left)');page.clock.run_for(60000)
  assert page.locator('.day-cursor').evaluate('(e)=>parseFloat(e.style.left)')>before
  page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/f'lesson-{width}.png'))
  page.clock.set_system_time(datetime(2026,11,2,8,31,tzinfo=timezone.utc));page.evaluate('paint()')
  assert page.locator('#globalOverview .break-card.now').count()==1
  assert page.locator('#globalOverview .day-segment.break.now').count()==1
  assert entity.locator('.card-day[data-wday="Пн"] .tl-break.now').count()==1
  page.screenshot(path=str(OUT/f'break-{width}.png'))
  entity.locator('.toggle-free').click();assert entity.locator('.tl-free:visible').count()==0
  entity.locator('.toggle-free').click()
  page.clock.set_system_time(datetime(2026,11,3,8,31,tzinfo=timezone.utc));page.evaluate('paint()')
  assert page.locator('#globalOverview .bell-card').count()==11
  assert page.locator('#globalOverview .lesson-card.now b').inner_text()=='Пара 2'
  page.clock.set_system_time(datetime(2026,11,8,7,31,tzinfo=timezone.utc));page.evaluate('paint()')
  assert 'Воскресенье' in page.locator('#globalOverview').inner_text()
  assert page.locator('#globalOverview .bell-card').count()==0
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors
  print(json.dumps({'width':width,'passed':True,'errors':errors,'screenshots':str(OUT)}));page.close()
 b.close()
