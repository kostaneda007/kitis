"""Collapse repeated day infographics to one live global overview, preserving rows."""
from pathlib import Path
import re

def migrate(s):
    if 'kitis-global-v8' in s:return s
    s,n=re.subn(r'<div class="day-overview">.*?<div class="bell-guide".*?</div></div></div>', '', s, flags=re.S)
    if not n:raise ValueError('No old overviews removed')
    top='<section class="day-overview" id="globalOverview" aria-label="Сегодня: все пары и перемены"><h2>Обзор дня · сегодня</h2><p class="day-status"></p><div class="day-scale"></div><div class="day-scale-labels"></div><div class="day-legend"><span class="legend-lesson">Пары</span><span class="legend-break">Перемены</span><span class="legend-now">Сейчас</span></div><div class="bell-guide"></div></section>'
    s=s.replace('<section class="live" id="liveCard">',top+'<section class="live" id="liveCard">',1)
    a=s.index('function paintDayOverview(');b=s.index('function paintTimeAxes(',a)
    s=s[:a]+'''function paintGlobalOverview(now){
  var host=$('#globalOverview'), key=String(now.wday),arr=now.wday===1?BELLS['Понедельник']:BELLS['Вт-Сб'];
  if(host.dataset.day!==key){
    host.dataset.day=key;
    var scale=$('.day-scale',host),guide=$('.bell-guide',host),labels=$('.day-scale-labels',host);
    scale.innerHTML='';guide.innerHTML='';labels.innerHTML='';
    if(now.wday!==0){
      var start=toMin(arr[0][0]),end=toMin(arr[arr.length-1][1]);
      function interval(a,b,label,kind){
        var x=toMin(a),y=toMin(b),seg=document.createElement('span'),card=document.createElement('div');
        seg.className='day-segment '+kind;seg.dataset.s=x;seg.dataset.e=y;
        seg.style.left=100*(x-start)/(end-start)+'%';seg.style.width=100*(y-x)/(end-start)+'%';
        seg.textContent=kind==='lesson'?label.replace('Пара ',''):'';seg.title=label+' · '+a+'–'+b+' · '+(y-x)+' мин';seg.setAttribute('aria-label',seg.title);scale.appendChild(seg);
        card.className='bell-card '+kind+'-card';card.dataset.s=x;card.dataset.e=y;
        card.innerHTML='<b>'+label+'</b><time>'+a+'–'+b+'</time><small>'+(y-x)+' мин</small>';guide.appendChild(card);
      }
      arr.forEach(function(t,i){if(i)interval(arr[i-1][1],t[0],'Перемена '+i+'–'+(i+1),'break');interval(t[0],t[1],'Пара '+(i+1),'lesson');});
      scale.insertAdjacentHTML('beforeend','<span class="day-cursor" hidden aria-label="Текущее время"></span>');
      labels.innerHTML='<span>'+arr[0][0]+'</span><span>'+arr[arr.length-1][1]+'</span>';
    }
    scale.hidden=now.wday===0;$('.day-legend',host).hidden=now.wday===0;
  }
  var bell=currentBell(now),text='Воскресенье · занятий нет';
  if(bell){
    if(bell.state==='now')text='Сейчас: пара '+bell.n+' · '+bell.start+'–'+bell.end;
    else if(bell.state==='break'&&bell.since!==null)text='Сейчас: перемена · '+arr[bell.next.n-2][1]+'–'+bell.next.start+' · '+(toMin(bell.next.start)-bell.since)+' мин';
    else text=bell.state==='done'?'Занятия закончились':'До начала занятий · '+arr[0][0];
  }
  $('.day-status',host).textContent=text;
  $$('.day-segment,.bell-card',host).forEach(function(el){var active=now.wday!==0&&now.mins>=+el.dataset.s&&now.mins<+el.dataset.e;el.classList.toggle('now',active);if(active)el.setAttribute('aria-current','time');else el.removeAttribute('aria-current');});
  var cursor=$('.day-cursor',host);
  if(cursor){var start=toMin(arr[0][0]),end=toMin(arr[arr.length-1][1]);cursor.hidden=now.mins<start||now.mins>=end;if(!cursor.hidden)cursor.style.left=100*(now.mins+new Date().getSeconds()/60-start)/(end-start)+'%';}
}
function paintDayOverview(day,arr,dow,now){
  $$('.tl-break',day).forEach(function(br){var prev=br.previousElementSibling,next=br.nextElementSibling;br.classList.toggle('now',!!(dow===now.wday&&prev&&next&&now.mins>=+prev.dataset.e&&now.mins<+next.dataset.s));});
}
''' +s[b:]
    s=s.replace('paintTimeAxes(now);','paintGlobalOverview(now);\n  paintTimeAxes(now);')
    s=s.replace('</style>','''/* kitis-global-v8 */
#globalOverview{margin:0 0 16px;padding:20px;background:var(--md-surface-container);border-radius:16px}
#globalOverview h2{font-size:20px;margin:0 0 8px}
#globalOverview .bell-guide{grid-template-columns:repeat(4,minmax(0,1fr))}
#globalOverview .bell-card{grid-row:auto}
#globalOverview .bell-card.now,#globalOverview .day-segment.now{background:var(--st-ok);color:var(--st-on-ok);outline:2px solid var(--st-ok);outline-offset:1px}
#globalOverview .bell-card.now :is(b,time,small){color:var(--st-on-ok)}
#liveTrack{display:none}
@media(max-width:600px){#globalOverview{padding:16px}#globalOverview .bell-guide{grid-template-columns:repeat(2,minmax(0,1fr))}}
</style>''')
    return s
if __name__=='__main__':
    p=Path(__file__).with_name('index.html');p.write_text(migrate(p.read_text()))
