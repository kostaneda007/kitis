from pathlib import Path
from datetime import datetime,timezone
import sys,json,re,subprocess
from playwright.sync_api import sync_playwright
from single_scale import migrate
URL=sys.argv[1] if len(sys.argv)>1 else Path('index.html').resolve().as_uri()
OUT=Path('/Users/konstantinmorylev/.hermes/cache/scratch/kitis-v9');OUT.mkdir(parents=True,exist_ok=True)
source=Path('index.html').read_text();assert migrate(source)==source
old=subprocess.check_output(['git','show','d419066:index.html'],text=True)
# Every normal schedule and results pane is byte-identical.
for pattern in [r'<section class="card-day".*?</section>',r'<div class="pane" data-pane="res".*?(?=</section>)']:
 assert re.findall(pattern,old,re.S)==re.findall(pattern,source,re.S)
with sync_playwright() as p:
 b=p.chromium.launch()
 for width in [1440,390,320]:
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
  assert page.locator('#globalOverview .bell-card').count()==0
  assert page.locator('#globalOverview .day-segment').count()==13
  assert 'Пара 2' in page.locator('#globalOverview .day-segment.now').get_attribute('aria-label')
  assert 'осталось' in page.locator('#intervalDetail').inner_text()
  before=page.locator('.day-cursor').evaluate('(e)=>parseFloat(e.style.left)');page.clock.run_for(60000)
  assert page.locator('.day-cursor').evaluate('(e)=>parseFloat(e.style.left)')>before
  segments=page.locator('#globalOverview .day-segment')
  for i in range(segments.count()):
   segments.nth(i).click();label=segments.nth(i).get_attribute('aria-label').split(' · ')
   assert label[0] in page.locator('#intervalDetail').inner_text() and label[1] in page.locator('#intervalDetail').inner_text()
  page.locator('#intervalSelect').select_option('1');assert '09:00–09:10' in page.locator('#intervalDetail').inner_text()
  page.locator('#scaleReset').click();assert 'Пара 2' in page.locator('#intervalDetail').inner_text()
  segments.nth(0).focus();page.keyboard.press('ArrowRight');assert '09:00–09:10' in page.locator('#intervalDetail').inner_text()
  page.keyboard.press('Escape');assert page.locator('#scaleReset').is_disabled()
  page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/f'lesson-{width}.png'))
  page.clock.set_system_time(datetime(2026,11,2,8,31,tzinfo=timezone.utc));page.evaluate('paint()')
  active=page.locator('#globalOverview .day-segment.break.now');assert active.count()==1
  assert active.evaluate('(e)=>getComputedStyle(e).backgroundColor')==page.evaluate('getComputedStyle(document.documentElement).getPropertyValue("--st-ok").trim()') or active.evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(123, 224, 160)'
  assert 'Перемена' in page.locator('#intervalDetail').inner_text()
  assert entity.locator('.card-day[data-wday="Пн"] .tl-break.now').count()==1
  page.screenshot(path=str(OUT/f'break-{width}.png'))
  entity.locator('.toggle-free').click();assert entity.locator('.tl-free:visible').count()==0
  entity.locator('.toggle-free').click()
  page.clock.set_system_time(datetime(2026,11,3,8,31,tzinfo=timezone.utc));page.evaluate('paint()')
  assert segments.count()==11
  assert 'Пара 2' in page.locator('#intervalDetail').inner_text()
  page.screenshot(path=str(OUT/f'tuesday-{width}.png'))
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.clock.set_system_time(datetime(2026,11,8,7,31,tzinfo=timezone.utc));page.evaluate('paint()')
  assert 'Воскресенье' in page.locator('#globalOverview').inner_text()
  assert segments.count()==0
  assert not errors,errors
  print(json.dumps({'width':width,'passed':True,'errors':errors,'screenshots':str(OUT)}));page.close()
 b.close()
