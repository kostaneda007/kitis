from pathlib import Path
from datetime import datetime, timezone
import sys,json,re,subprocess
from playwright.sync_api import sync_playwright
from sticky_overview import migrate
URL=sys.argv[1] if len(sys.argv)>1 else Path('index.html').resolve().as_uri()
OUT=Path('/Users/konstantinmorylev/.hermes/cache/scratch/kitis-v10');OUT.mkdir(parents=True,exist_ok=True)
s=Path('index.html').read_text();assert migrate(s)==s
old=subprocess.check_output(['git','show','81cc5af:index.html'],text=True)
for pattern in [r'<section class="card-day".*?</section>',r'<div class="pane" data-pane="res".*?(?=</section>)']:
 assert re.findall(pattern,s,re.S)==re.findall(pattern,old,re.S)
with sync_playwright() as p:
 b=p.chromium.launch()
 for width in [1440,1050,390,320]:
  page=b.new_page(viewport={'width':width,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.clock.install(time=datetime(2026,11,2,7,20,tzinfo=timezone.utc));page.goto(URL);page.wait_for_timeout(300)
  assert page.locator('#globalOverview').count()==1
  assert page.locator('#liveCard,#liveTrack').count()==0
  if width<=1024:page.locator('.tab[data-tab=t]').click()
  page.locator('#tlist .li').filter(has_text='Морылёв').click();page.wait_for_timeout(300)
  entity=page.locator('.ent:not([hidden])');assert entity.locator('.card-day').count()==7
  header=page.locator('#globalOverview .overview-live')
  assert 'Пара 2' in header.inner_text() and 'до конца 70 мин' in header.inner_text()
  assert page.locator('#globalOverview #liveSub').count()==1
  page.locator('#intervalSelect').select_option('1')
  assert 'Перемена' in page.locator('#intervalDetail').inner_text() and 'Пара 2' in header.inner_text()
  page.locator('#scaleReset').click()
  cursor=page.locator('#globalOverview .day-cursor');x=cursor.evaluate('(e)=>parseFloat(e.style.left)')
  page.clock.run_for(60000);assert cursor.evaluate('(e)=>parseFloat(e.style.left)')>x
  page.evaluate('scrollTo(0,700)');page.wait_for_timeout(100)
  bounds=page.locator('#globalOverview').bounding_box();app=page.locator('.appbar').bounding_box()
  if width>1024:
   assert abs(bounds['y']-(app['y']+app['height']))<1,(bounds,app)
   page.evaluate('scrollBy(0,300)');page.wait_for_timeout(100)
   assert abs(page.locator('#globalOverview').bounding_box()['y']-bounds['y'])<1
   assert page.locator('#globalOverview').evaluate('(e)=>getComputedStyle(e).position')=='sticky'
  else:
   assert page.locator('#globalOverview').evaluate('(e)=>getComputedStyle(e).position')=='static'
  page.screenshot(path=str(OUT/f'scrolled-{width}.png'))
  entity.locator('[data-view=res]').click();assert entity.locator('[data-pane=res]').is_visible()
  assert entity.locator('[data-pane=res] table tr').count()>1
  entity.locator('[data-view=sch]').click()
  for day,hour,minute,text in [(2,8,31,'Перемена'),(3,8,31,'Пара 2'),(8,7,31,'Выходной'),(2,4,0,'До начала занятий'),(2,19,0,'Занятия закончились')]:
   page.clock.set_system_time(datetime(2026,11,day,hour,minute,tzinfo=timezone.utc));page.evaluate('paint()')
   assert text in header.inner_text(),header.inner_text()
   if text=='Перемена':
    assert 'до конца 9 мин' in header.inner_text()
    assert page.locator('#globalOverview .break.now').count()==1
    assert page.locator('#globalOverview .break.now').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(123, 224, 160)'
    page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/f'break-{width}.png'))
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  assert not errors,errors
  print(json.dumps({'width':width,'stickyTop':bounds['y'],'errors':errors,'passed':True,'screenshots':str(OUT)}));page.close()
 b.close()
