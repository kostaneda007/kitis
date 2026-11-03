"""Consolidate live context into the sole overview; preserve all schedule data."""
from pathlib import Path
import re

def migrate(s):
    if 'kitis-sticky-overview-v10' in s:
        return s
    a=s.index('<section class="live" id="liveCard">');b=s.index('</section>',a)+len('</section>')
    s=s[:a]+s[b:]
    s=s.replace('<h2>Обзор дня · сегодня</h2>', '<div class="overview-heading"><h2>Обзор дня · сегодня</h2><div class="overview-live" aria-live="polite"><span class="live-pair" id="livePair"></span><span class="live-time" id="liveTime"></span><span class="live-left" id="liveLeft"></span></div></div><div class="live-sub" id="liveSub"></div>')
    s=s.replace("  var track = $('#liveTrack');\n",'')
    s=s.replace("    var arr = bell.mon ? BELLS['Понедельник'] : BELLS['Вт-Сб'];\n    track.innerHTML = axisMarkup(arr, now, true);",'')
    s=s.replace("    track.innerHTML = '';",'')
    # Keep the live subject context, but label the actual interval consistently,
    # including the pre-day state (currentBell historically calls this a break).
    end="    sub.textContent = 'Нет занятий';\n\n  }\n}"
    assert end in s
    s=s.replace(end,"""    sub.textContent = 'Нет занятий';

  }
  var overview = $('#globalOverview'), intervals = overview._intervals || [];
  var active = intervals.find(function(t){return now.mins >= t.s && now.mins < t.e;});
  if(active){
    pair.textContent = active.label;
    time.textContent = active.a + '–' + active.b;
    left.textContent = (active.kind === 'lesson' ? 'Идёт · до конца ' : 'Перемена · до конца ') + (active.e - now.mins) + ' мин';
  } else if(now.wday !== 0 && intervals.length){
    var before = now.mins < intervals[0].s;
    pair.textContent = before ? 'До начала занятий' : 'Занятия закончились';
    time.textContent = before ? 'Первая пара · ' + intervals[0].a : 'Последняя пара · до ' + intervals[intervals.length-1].b;
    left.textContent = before ? 'До начала ' + (intervals[0].s - now.mins) + ' мин' : '';
  }
}
""")
    css='''/* kitis-sticky-overview-v10 */
/* Clip without creating a non-scrolling ancestor that disables sticky. */
html,body{overflow-x:clip}
.overview-heading{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px 20px}
#globalOverview .overview-heading h2{margin:0}
.overview-live{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;min-width:0}
#globalOverview .live-pair{font-size:16px;color:var(--st-ok)}
#globalOverview .live-left{margin-left:0;font-size:13px}
#globalOverview .live-sub{margin:8px 0 0;line-height:1.5}
@media(min-width:1025px){
 #globalOverview{position:sticky;top:var(--overview-top,112px);z-index:30;box-shadow:var(--el2);scroll-margin-top:var(--overview-top,112px)}
 html{scroll-padding-top:calc(var(--overview-top,112px) + var(--overview-height,320px) + 16px)}
}
@media(max-width:1024px){#globalOverview{position:static}.overview-live{width:100%}}
'''
    s=s.replace('</style>',css+'\n</style>')
    script='''// Measure rather than assume header height (fonts, zoom, wrapping).
function sizeOverview(){
 var header=document.querySelector('.appbar'),overview=document.getElementById('globalOverview');
 document.documentElement.style.setProperty('--overview-top',header.getBoundingClientRect().height+'px');
 document.documentElement.style.setProperty('--overview-height',overview.getBoundingClientRect().height+'px');
}
new ResizeObserver(sizeOverview).observe(document.querySelector('.appbar'));
new ResizeObserver(sizeOverview).observe(document.getElementById('globalOverview'));
sizeOverview();
'''
    s=s.replace('</script>',script+'\n</script>')
    return s

if __name__=='__main__':
    p=Path(__file__).with_name('index.html');p.write_text(migrate(p.read_text()))
