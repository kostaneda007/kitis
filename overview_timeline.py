"""Idempotent two-level presentation migration; never rebuild schedule data."""
from pathlib import Path
import re
MON=[('08:30','09:00'),('09:10','10:30'),('10:40','12:00'),('12:20','13:40'),('13:50','15:10'),('16:00','17:20'),('17:30','18:50')]
MAIN=[('08:30','10:00'),('10:10','11:40'),('12:10','13:40'),('13:50','15:20'),('15:30','17:00'),('17:10','18:40')]
def minute(t):
    h,m=map(int,t.split(':'));return h*60+m

def enhance(s):
    if 'kitis-overview-v6' in s:return s
    def day(m):
        block=m[0]
        dow=re.search(r'data-wday="([^"]+)"',block)[1]
        if dow=='Вс':return block
        arr=MON if dow=='Пн' else MAIN
        start,end=minute(arr[0][0]),minute(arr[-1][1]); span=end-start
        segments=''
        for i,(a,b) in enumerate(arr):
            if i:
                p=arr[i-1][1];label=f'Перемена {p}–{a}, {minute(a)-minute(p)} мин'
                segments+=f'<span class="day-segment break" style="left:{100*(minute(p)-start)/span:.6f}%;width:{100*(minute(a)-minute(p))/span:.6f}%" role="img" aria-label="{label}" title="{label}"></span>'
            label=f'Пара {i+1} · {a}–{b}'
            segments+=f'<span class="day-segment lesson" style="left:{100*(minute(a)-start)/span:.6f}%;width:{100*(minute(b)-minute(a))/span:.6f}%" role="img" aria-label="{label}" title="{label}">{i+1}</span>'
        overview='<div class="day-overview"><p class="day-status">Обзор дня · '+arr[0][0]+'–'+arr[-1][1]+'</p><div class="day-scale" aria-label="Пропорциональная шкала пар и перемен">'+segments+'<span class="day-cursor" hidden aria-label="Текущее время"></span></div><div class="day-scale-labels"><span>'+arr[0][0]+'</span><span>'+arr[-1][1]+'</span></div><div class="day-legend"><span class="legend-lesson">Пары 1–'+str(len(arr))+'</span><span class="legend-break">Перемены</span><span class="legend-now">Сейчас</span><span>Интервалы и длительности — ниже</span></div></div>'
        block=block.replace('<ol class="tl">',overview+'<ol class="tl">',1)
        index=iter(range(1,len(arr)))
        def br(m):
            i=next(index);a,b=arr[i-1][1],arr[i][0]
            return '<li class="tl-break"><span class="tl-breaklabel">Перемена · '+str(minute(b)-minute(a))+' мин</span><span class="tl-breaktime">'+a+'–'+b+'</span></li>'
        return re.sub(r'<li class="tl-break[^\"]*">.*?</li>',br,block,flags=re.S)
    s=re.sub(r'<section class="card-day".*?</section>',day,s,flags=re.S)
    css='''
/* kitis-overview-v6: full-day geometry above readable event rows */
.day-overview{margin:14px 24px 12px}
.day-status{font-size:13px;line-height:20px;margin-bottom:10px;color:var(--md-on-surface-variant)}
.day-status.is-current{color:var(--st-ok)}
.day-scale{position:relative;height:32px;background:var(--md-surface-low);border-radius:6px}
.day-segment{position:absolute;top:0;height:32px;display:flex;align-items:center;justify-content:center;font-size:12px;line-height:16px;font-weight:600;border-right:1px solid var(--md-surface-container)}
.day-segment.lesson{background:var(--md-surface-highest);color:var(--md-on-surface)}
.day-segment.break{background:var(--md-primary)}
.day-cursor{position:absolute;top:-5px;bottom:-5px;width:3px;transform:translateX(-50%);background:var(--st-ok);box-shadow:0 0 0 1px var(--md-surface-low);z-index:2}
.day-cursor::before{content:'';position:absolute;top:-2px;left:-3px;border-radius:50%;width:9px;height:9px;background:var(--st-ok)}
.day-scale-labels{display:flex;justify-content:space-between;font-size:11px;color:var(--md-on-surface-variant);margin-top:7px}
.day-legend{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:8px;font-size:11px;line-height:16px;color:var(--md-on-surface-variant)}
.day-legend span:not(:last-child)::before{content:'';display:inline-block;width:8px;height:8px;margin-right:5px;background:var(--md-surface-highest);border:1px solid var(--md-outline);border-radius:2px}
.day-legend span.legend-break::before{background:var(--md-primary);border-color:var(--md-primary)}
.day-legend span.legend-now::before{background:var(--st-ok);border-color:var(--st-ok)}
.tl-break.now{background:var(--st-ok-container);border:1px solid var(--st-ok)}
.tl-break.now .tl-breaklabel,.tl-break.now .tl-breaktime{color:var(--st-on-ok-container)}
.tl-item.tl-free.now{background:var(--st-ok-container);border-color:var(--st-ok)}
@media(min-width:1025px){
.tl{gap:4px;padding:4px 16px 16px}
.tl-item{padding:9px 12px;grid-template-columns:64px minmax(0,1fr);gap:12px;border-radius:8px}
.tl-body{display:grid;grid-template-columns:108px minmax(0,1fr);gap:2px 12px;align-items:start}
.tl-title{font-size:14px;line-height:20px;margin:0}
.tl-time{font-size:12px;line-height:20px}
.tl-meta{grid-column:2;margin-top:2px;gap:4px 10px}
.tl-meta .mt{padding:0;background:transparent;font-size:11px;line-height:18px}
.tl-break{padding:4px 12px;min-height:26px}
}
@media(max-width:600px){.day-overview{margin:14px 16px 12px}.tl-item{padding:12px}.tl-title{font-size:14px;line-height:21px}.tl-meta{gap:4px}.tl-meta .mt{padding:4px 6px}.day-legend{gap:4px 12px}}
'''
    s=s.replace('</style>',css+'\n</style>')
    js='''function paintDayOverview(day,arr,dow,now){
  var overview=$('.day-overview',day);if(!overview)return;
  var current=dow===now.wday,bell=current?currentBell(now):null;
  var status=$('.day-status',overview),cursor=$('.day-cursor',overview);
  var start=toMin(arr[0][0]),end=toMin(arr[arr.length-1][1]);
  var text='Обзор дня · '+arr[0][0]+'–'+arr[arr.length-1][1];
  if(current){
    if(bell.state==='now')text='Сейчас: пара '+bell.n+' · '+bell.start+'–'+bell.end;
    else if(bell.state==='break'&&bell.since!==null){var prev=arr[bell.next.n-2];text='Сейчас: перемена · '+prev[1]+'–'+bell.next.start+' · '+(toMin(bell.next.start)-bell.since)+' мин';}
    else text=bell.state==='done'?'Сейчас: занятия закончились':'Сейчас: до начала занятий · '+arr[0][0];
  }
  status.textContent=text;status.classList.toggle('is-current',current);
  cursor.hidden=!(current&&now.mins>=start&&now.mins<end);
  if(!cursor.hidden){var precise=now.mins+new Date().getSeconds()/60;cursor.style.left=Math.min(100,Math.max(0,100*(precise-start)/(end-start)))+'%';cursor.setAttribute('aria-label','Сейчас '+('0'+now.hour).slice(-2)+':'+('0'+now.minute).slice(-2));}
  $$('.tl-break',day).forEach(function(br){var prev=br.previousElementSibling,next=br.nextElementSibling;br.classList.toggle('now',!!(current&&prev&&next&&now.mins>=+prev.dataset.e&&now.mins<+next.dataset.s));});
}
'''
    s=s.replace('function paintTimeAxes(now){',js+'function paintTimeAxes(now){')
    needle="var arr=dow===1?BELLS['Понедельник']:BELLS['Вт-Сб'];"
    s=s.replace(needle,needle+'\n    paintDayOverview(day,arr,dow,now);')
    s=s.replace("el.classList.toggle('now', isNow && mode !== 'done');","el.classList.toggle('now', isNow && mode === 'now');")
    return s

if __name__=='__main__':
    p=Path(__file__).with_name('index.html');p.write_text(enhance(p.read_text()))
