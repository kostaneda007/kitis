"""Presentation-only migration; safe after patch_timeline.py, never regenerate data."""
from pathlib import Path
import re

def redesign(s):
    if 'kitis-timeline-v5' in s:
        return s
    css='''
/* kitis-timeline-v5: readable event cards, one event-relative live progress */
@media(min-width:1025px){body.choosing footer{display:none}}
.live{background:var(--md-surface-container);color:var(--md-on-surface);border:1px solid var(--md-outline-variant);border-left:3px solid var(--md-primary);border-radius:16px;padding:18px 20px;margin-bottom:24px;box-shadow:none}
.live-head{gap:8px 14px;line-height:24px;align-items:center}
.live-tag{padding:0;background:none;color:var(--md-on-surface-variant);font-size:11px}
.live-pair{color:var(--md-on-surface);font-size:24px;font-weight:600;line-height:30px}
.live-time{color:var(--md-on-surface-variant);font-size:15px}
.live-left{padding:5px 10px;line-height:20px}
.live-sub,.live-sub b,.live-sub .note{color:var(--md-on-surface-variant)}
.live-sub{margin-top:8px;font-size:13px}
.track{display:block;height:auto;margin-top:16px}
.progress-labels{display:flex;justify-content:space-between;gap:12px;color:var(--md-on-surface-variant);font-size:12px;font-variant-numeric:tabular-nums;margin-bottom:8px}
.progress-labels strong{color:var(--st-ok);font-weight:500}
.progress-rail{height:6px;position:relative;background:var(--md-surface-highest);border-radius:99px;margin:0 5px}
.progress-fill{position:absolute;inset:0 auto 0 0;background:var(--st-ok);border-radius:99px}
.progress-rail .time-cursor{top:-3px;bottom:auto;height:12px;width:12px;border-radius:50%;transform:translateX(-50%);box-shadow:0 0 0 3px var(--md-surface-container);background:var(--st-ok)}
.progress-legend{display:flex;gap:16px;flex-wrap:wrap;font-size:11px;color:var(--md-on-surface-variant);margin-top:10px}
.progress-legend span::before{content:'';display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--st-ok);margin-right:6px}
.progress-legend span+span::before{background:var(--md-outline)}
.tl-item{grid-template-columns:68px minmax(0,1fr);gap:14px}
.tl-node,.tl-item.tl-free .tl-node{width:auto;height:auto;min-height:28px;padding:4px 7px;border-radius:8px;font-size:12px;white-space:nowrap;font-weight:600}
.tl-time{font-variant-numeric:tabular-nums}
.tl-body{min-width:0}
.tl-break{justify-content:space-between;padding:8px 14px;background:transparent;gap:8px}
.tl-break .tl-gap{display:none}
.tl-break .tl-breaklabel{font-size:12px;font-weight:500;letter-spacing:0;text-transform:none;color:var(--md-on-surface-variant)}
.tl-break .tl-breaktime{font-size:12px;font-weight:400}
@media(max-width:600px){.live{padding:16px}.live-head{gap:6px 10px}.live-tag{width:100%}.live-pair{font-size:22px}.live-time{font-size:13px}.live-left{margin-left:0;font-size:12px}.progress-labels{font-size:11px;gap:6px}.tl-item{grid-template-columns:60px minmax(0,1fr);gap:10px}.tl-node{font-size:11px}.tl-break{padding:8px 4px}}
'''
    s=s.replace('</style>',css+'\n</style>')
    s=re.sub(r'(<span class="tl-node">)(\d+)(</span>)',r'\1Пара \2\3',s)
    start=s.index('function axisMarkup(')
    end=s.index('function paintTimeAxes(',start)
    s=s[:start]+'''function axisMarkup(arr,now,live){
  var bell=currentBell(now);if(!bell||bell.state==='done')return '';
  var start=bell.state==='now'?toMin(bell.start):bell.since;
  var end=bell.state==='now'?toMin(bell.end):toMin(bell.next.start);
  if(start===null)start=toMin(arr[0][0])-30;
  var precise=now.mins+(new Date().getSeconds()/60);
  var percent=Math.min(100,Math.max(0,100*(precise-start)/(end-start)));
  function clock(n){return ('0'+Math.floor(n/60)).slice(-2)+':'+('0'+n%60).slice(-2);}
  return '<div class="progress-labels"><span>'+clock(start)+' · '+(bell.state==='now'?'Начало':'Перерыв')+'</span><strong>Сейчас '+clock(now.mins)+'</strong><span>'+clock(end)+' · '+(bell.state==='now'?'Конец':'Начало пары')+'</span></div>'+
    '<div class="progress-rail" role="progressbar" aria-label="'+(bell.state==='now'?'Ход текущей пары':'До следующей пары')+'" aria-valuemin="0" aria-valuemax="100" aria-valuenow="'+Math.round(percent)+'"><span class="progress-fill" style="width:'+percent+'%"></span><span class="time-cursor" aria-label="Текущее время" style="left:'+percent+'%"></span></div><div class="progress-legend"><span>Прошло времени</span><span>Осталось до '+(bell.state==='now'?'конца пары':'следующей пары')+'</span></div>';
}
''' +s[end:]
    s=re.sub(r"    var axis=\$\('\.time-axis',day\);.*?    axis.innerHTML=axisMarkup\(arr,dow===now.wday\?now:null,false\);",'',s,flags=re.S)
    s=s.replace("left.textContent = 'до конца '","left.textContent = 'Идёт · до конца '")
    s=s.replace("pair.textContent = '—';","pair.textContent = 'Выходной';")
    s=s.replace("var gap=+next.dataset.s-(+prev.dataset.e);","var gap=+next.dataset.s-(+prev.dataset.e);\n      $('.tl-breaklabel',br).textContent='Перемена · '+gap+' мин';")
    s=s.replace("+' · '+gap+' мин';",";") if False else s
    s=s.replace(".split('–')[0]+' · '+gap+' мин';",".split('–')[0];")
    # Make every break readable before JS too.
    s=re.sub(r'(<span class="tl-breaklabel">)[^<]*(</span><span class="tl-breaktime">)([^<]*?) · (\d+) мин</span>',lambda m:m[1]+'Перемена · '+m[4]+' мин'+m[2]+m[3]+'</span>',s)
    return s

if __name__=='__main__':
    p=Path(__file__).with_name('index.html');p.write_text(redesign(p.read_text()))
