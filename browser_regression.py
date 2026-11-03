"""Real-browser regression, run with python3 browser_regression.py [URL]."""
from pathlib import Path
import json, sys
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else Path('index.html').resolve().as_uri()
OUT=Path('/Users/konstantinmorylev/.hermes/cache/scratch/kitis-v7');OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch()
    for width in [1440,390]:
        page=browser.new_page(viewport={'width':width,'height':1000},device_scale_factor=1)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.clock.install(time=datetime(2026,11,2,7,20,tzinfo=timezone.utc))
        page.goto(URL);page.wait_for_timeout(300)
        if width<1025:page.locator('.tab[data-tab="t"]').click()
        page.locator('#tlist .li').filter(has_text='Морылёв').click()
        entity=page.locator('.ent:not([hidden])')
        assert entity.locator('.card-day').count()==7
        button=entity.locator('[data-view=res]');button.click()
        results=entity.locator('[data-pane=res]')
        assert results.is_visible() and results.locator('table tr').count()>1
        assert results.locator('.loadsum').is_visible()
        results.screenshot(path=str(OUT/f'results-{width}.png'))
        entity.locator('[data-view=sch]').click()
        monday=entity.locator('.card-day[data-wday="Пн"]')
        monday.scroll_into_view_if_needed()
        for card in monday.locator('.bell-card').all():
            assert card.is_visible()
            assert card.locator('time').inner_text()
            assert card.evaluate('(e)=>e.scrollWidth<=e.clientWidth')
        assert monday.locator('.bell-card').count()==13
        cursor=monday.locator('.day-cursor')
        assert cursor.is_visible()
        before=cursor.evaluate('(e)=>parseFloat(e.style.left)')
        page.clock.run_for(60000)
        assert cursor.evaluate('(e)=>parseFloat(e.style.left)')>before
        monday.screenshot(path=str(OUT/f'overview-{width}.png'))
        page.evaluate('scrollTo(0,0)')
        page.screenshot(path=str(OUT/f'page-{width}.png'))
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        # Toggle free lessons must not hide any exact break card or actual break row.
        entity.locator('.toggle-free').click()
        assert all(x.is_visible() for x in monday.locator('.break-card,.tl-break').all())
        entity.locator('.toggle-free').click()
        assert not errors,errors
        print(json.dumps({'width':width,'results_rows':results.locator('table tr').count(),'days':7,'bell_cards':13,'errors':errors,'screenshots':str(OUT)}))
        page.close()
    browser.close()
