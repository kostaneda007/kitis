"""Dock the existing interactive overview inside the menu, never clone it."""
from pathlib import Path

def migrate(s):
    if 'kitis-menu-overview-v11' in s:
        return s
    css='''/* kitis-menu-overview-v11 */
html{overflow-anchor:none}
.appbar{position:fixed;left:0;right:0;top:0}
body{padding-top:var(--menu-base-height,112px)}
.appbar.overview-pinned #globalOverview .day-segment{height:22px}
.appbar.overview-pinned .scale-number{font-size:11px;line-height:22px}
.appbar.overview-pinned .scale-range,.appbar.overview-pinned .scale-boundary{display:none}
#globalOverview{position:static;scroll-margin-top:var(--overview-top);box-shadow:none}
html{scroll-padding-top:calc(var(--overview-top,112px) + 16px)}
.overview-home{display:flow-root;position:relative}
.overview-sentinel{position:absolute;bottom:0;width:1px;height:1px;pointer-events:none}
.menu-overview{display:none;flex:1;min-width:0}
.appbar.overview-pinned .menu-overview{display:block}
.appbar.overview-pinned .appbar-row>div:not(.menu-overview){display:none}
#overviewExpand{display:none}
.appbar.overview-pinned #globalOverview{margin:0;padding:4px 0;border:0;border-radius:0;background:transparent;min-width:0;animation:overviewDock 180ms ease-out}
.appbar.overview-pinned .overview-heading{gap:4px;flex-wrap:nowrap}
.appbar.overview-pinned #globalOverview .overview-heading h2,.appbar.overview-pinned #globalOverview .live-sub,.appbar.overview-pinned #globalOverview .day-status,.appbar.overview-pinned #globalOverview .day-scale-labels,.appbar.overview-pinned #globalOverview .day-legend,.appbar.overview-pinned #globalOverview .scale-detail{display:none}
.appbar.overview-pinned #globalOverview .scale-time{display:none}
.appbar.overview-pinned #globalOverview .day-cursor{top:0;bottom:0}
.appbar.overview-pinned #globalOverview .day-cursor::before{display:none}
.appbar.overview-pinned .overview-live{width:auto;flex:1;gap:4px 10px;flex-wrap:wrap;line-height:1.25}
.appbar.overview-pinned #globalOverview .live-pair{font-size:12px}
.appbar.overview-pinned #globalOverview .live-time,.appbar.overview-pinned #globalOverview .live-left{font-size:12px}
.appbar.overview-pinned #globalOverview .day-scale{height:22px;margin:3px 0 0}
.appbar.overview-pinned #overviewExpand{display:block;flex:none;border:1px solid var(--md-outline-variant);border-radius:8px;padding:4px 8px;background:var(--md-surface-high);color:var(--md-on-surface);font:inherit;font-size:12px;min-height:32px;cursor:pointer}
.appbar.overview-pinned #globalOverview.overview-expanded .scale-detail{display:flex;position:absolute;left:12px;right:12px;top:100%;margin:0;padding:16px;background:var(--md-surface-container);box-shadow:var(--el3);border-radius:0 0 16px 16px;max-height:55vh;overflow:auto;z-index:2}
.appbar.overview-pinned .scale-detail p{overflow-wrap:anywhere}
#overviewExpand:focus-visible{outline:2px solid var(--md-primary);outline-offset:2px}
@keyframes overviewDock{from{opacity:.4;transform:translateY(6px)}to{opacity:1;transform:none}}
@media(max-width:600px){
 .appbar.overview-pinned .appbar-row{gap:6px;padding:0 8px;min-height:78px}
 .appbar.overview-pinned .overview-live{gap:2px 6px}
 .appbar.overview-pinned #globalOverview .live-left{flex-basis:100%}
 .appbar.overview-pinned #globalOverview .day-scale{height:22px}
 .appbar.overview-pinned #overviewExpand{padding:4px;font-size:11px}
 .appbar.overview-pinned #globalOverview.overview-expanded .scale-detail{flex-direction:column;align-items:stretch}
}
@media(prefers-reduced-motion:reduce){.appbar.overview-pinned #globalOverview{animation:none}}
'''
    s=s.replace('</style>',css+'\n</style>')
    a=s.index('// Measure rather than assume header height')
    b=s.index('</script>',a)
    s=s[:a]+'''// One live node moves between its natural home and the top menu.
(function(){
 var header=document.querySelector('.appbar'), row=header.querySelector('.appbar-row');
 var overview=document.getElementById('globalOverview');
 var home=document.createElement('div');home.className='overview-home';
 overview.before(home);home.append(overview);
 var sentinel=document.createElement('span');sentinel.className='overview-sentinel';sentinel.setAttribute('aria-hidden','true');home.append(sentinel);
 var slot=document.createElement('div');slot.className='menu-overview';row.append(slot);
 var expand=document.createElement('button');expand.id='overviewExpand';expand.type='button';expand.textContent='Подробнее';expand.setAttribute('aria-expanded','false');
 var detail=overview.querySelector('.scale-detail');detail.id='overviewDetails';expand.setAttribute('aria-controls',detail.id);overview.querySelector('.overview-heading').append(expand);
 var pinned=false,observer;
 function details(open){overview.classList.toggle('overview-expanded',open);expand.setAttribute('aria-expanded',String(open));expand.textContent=open?'Свернуть':'Подробнее';}
 expand.addEventListener('click',function(){details(expand.getAttribute('aria-expanded')!=='true');});
 overview.addEventListener('keydown',function(e){if(e.key==='Escape'){details(false);expand.focus();}});
 overview.querySelector('.day-scale').addEventListener('click',function(){if(pinned)details(true);});
 overview.querySelector('.day-scale').addEventListener('focusin',function(){if(pinned)details(true);});
 function dock(next){
  if(next===pinned)return;
  var focus=document.activeElement,focused=overview.contains(focus);
  if(next){home.style.height=home.getBoundingClientRect().height+'px';slot.append(overview);}
  else {home.prepend(overview);home.style.height='';details(false);}
  pinned=next;header.classList.toggle('overview-pinned',next);
  if(focused){if(next)details(true);focus.focus({preventScroll:true});}
  measure();
 }
 function measure(){var h=header.getBoundingClientRect().height;document.documentElement.style.setProperty('--overview-top',h+'px');if(!pinned)document.documentElement.style.setProperty('--menu-base-height',h+'px');}
 // A stable sentinel prevents the moved element from observing itself.
 function observe(){
  if(observer)observer.disconnect();
  var base=header.querySelector('.tabs').getBoundingClientRect().bottom;
  if(pinned && matchMedia('(max-width:600px)').matches)base-=22;
  observer=new IntersectionObserver(function(entries){var r=entries[0].boundingClientRect;dock(!entries[0].isIntersecting && r.top<base);},{rootMargin:'-'+base+'px 0px 0px 0px',threshold:0});observer.observe(sentinel);
 }
 new ResizeObserver(measure).observe(header);
 window.addEventListener('resize',function(){measure();observe();});
 measure();observe();
})();

'''+s[b:]
    return s

if __name__=='__main__':
    p=Path(__file__).with_name('index.html');p.write_text(migrate(p.read_text()))
