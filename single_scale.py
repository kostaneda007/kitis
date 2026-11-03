"""Presentation-only, idempotent single-scale migration. No timetable data changes."""
import re
from pathlib import Path


def migrate(s):
    if 'kitis-single-scale-v9' in s:
        return s
    a=s.index('<section class="day-overview" id="globalOverview"'); b=s.index('<section class="live" id="liveCard">',a)
    s=s[:a]+'''<section class="day-overview" id="globalOverview" aria-label="Обзор дня: пары и перемены"><h2>Обзор дня · сегодня</h2><p class="day-status"></p><div class="day-scale" role="group" aria-label="Пары и перемены по времени"></div><div class="day-scale-labels" aria-hidden="true"></div><div class="day-legend"><span class="legend-lesson">Пары · номера на шкале</span><span class="legend-break">Перемены · узкие интервалы</span><span class="legend-now">Сейчас · линия и подсветка</span></div><div class="scale-detail"><p id="intervalDetail" aria-live="polite"></p><div class="scale-controls"><label for="intervalSelect">Интервал</label><select id="intervalSelect" aria-describedby="intervalDetail"><option>Сейчас</option></select><button type="button" id="scaleReset">К текущему</button></div></div></section>'''+s[b:]
    a=s.index('function paintGlobalOverview(');b=s.index('function paintDayOverview(',a)
    s=s[:a]+JS+'\n'+s[b:]
    return s.replace('</style>',CSS+'\n</style>')

JS=r'''function paintGlobalOverview(now){
  var host=$('#globalOverview'),arr=now.wday===1?BELLS['Понедельник']:BELLS['Вт-Сб'];
  var scale=$('.day-scale',host),select=$('#intervalSelect'),reset=$('#scaleReset');
  if(host.dataset.day!==String(now.wday)){
    host.dataset.day=now.wday;host._selected=null;host._intervals=[];
    scale.innerHTML='';select.innerHTML='<option value="">Сейчас · автоматически</option>';
    $('.day-scale-labels',host).innerHTML='';
    if(now.wday!==0){
      var start=toMin(arr[0][0]),end=toMin(arr[arr.length-1][1]);
      function add(a,b,label,kind,n){
        var x=toMin(a),y=toMin(b),i=host._intervals.length;
        var item={s:x,e:y,a:a,b:b,label:label,kind:kind};host._intervals.push(item);
        var button=document.createElement('button');button.type='button';button.className='day-segment '+kind;
        if(y-x<65)button.classList.add('short');
        button.dataset.s=x;button.dataset.e=y;button.dataset.index=i;
        button.style.left=100*(x-start)/(end-start)+'%';button.style.width=100*(y-x)/(end-start)+'%';
        button.setAttribute('aria-label',label+' · '+a+'–'+b+' · '+(y-x)+' мин');
        button.innerHTML=kind==='lesson'?'<span class="scale-number"><span class="wide-label">Пара </span>'+n+'</span><span class="scale-time">'+a+'–'+b+'</span>':'';
        function choose(){host._selected=i;paintGlobalOverview(host._now);}
        button.addEventListener('click',choose);button.addEventListener('focus',choose);
        button.addEventListener('keydown',function(e){if(e.key==='Escape'){host._selected=null;select.focus();paintGlobalOverview(host._now);}if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();var buttons=$$('.day-segment',host);buttons[(i+(e.key==='ArrowRight'?1:-1)+buttons.length)%buttons.length].focus();}});
        scale.appendChild(button);var option=document.createElement('option');option.value=i;option.textContent=label+' · '+a+'–'+b;select.appendChild(option);
      }
      arr.forEach(function(t,i){if(i)add(arr[i-1][1],t[0],'Перемена '+i+'–'+(i+1),'break');add(t[0],t[1],'Пара '+(i+1),'lesson',i+1);});
      scale.insertAdjacentHTML('beforeend','<span class="day-cursor" hidden aria-label="Текущее время"></span>');
      var ticks=[{m:start,t:arr[0][0]}];
      for(var h=Math.ceil(start/60);h*60<end;h++)if(h*60-start>=40&&end-h*60>=40)ticks.push({m:h*60,t:('0'+h).slice(-2)+':00'});
      ticks.push({m:end,t:arr[arr.length-1][1]});
      $('.day-scale-labels',host).innerHTML=ticks.map(function(t,i){return '<span class="scale-tick '+(i===0?'first':i===ticks.length-1?'last':'middle')+'" style="left:'+100*(t.m-start)/(end-start)+'%">'+t.t+'</span>';}).join('');
    }
    select.onchange=function(){host._selected=this.value===''?null:+this.value;paintGlobalOverview(host._now);};
    reset.onclick=function(){host._selected=null;paintGlobalOverview(host._now);};
  }
  host._now=now;
  var sunday=now.wday===0,active=-1;
  host._intervals.forEach(function(t,i){if(now.mins>=t.s&&now.mins<t.e)active=i;});
  var selected=host._selected,shown=selected===null?active:selected,t=host._intervals[shown];
  $('.day-status',host).textContent=sunday?'Воскресенье · занятий нет':(now.wday===1?'Понедельник':'Вторник–суббота')+' · '+arr[0][0]+'–'+arr[arr.length-1][1]+' · длина интервала = длительность';
  $('#intervalDetail').textContent=t?((shown===active?'Сейчас · ':'')+t.label+' · '+t.a+'–'+t.b+' · '+(shown===active?'осталось '+(t.e-now.mins)+' мин':(t.e-t.s)+' мин')):(sunday?'Сегодня можно отдохнуть':now.mins<toMin(arr[0][0])?'Занятия начнутся в '+arr[0][0]:'Занятия закончились');
  select.value=selected===null?'':String(selected);reset.disabled=selected===null;
  $$('.day-segment',host).forEach(function(el,i){el.classList.toggle('now',i===active);el.classList.toggle('selected',selected===i);el.setAttribute('aria-pressed',String(shown===i));if(i===active)el.setAttribute('aria-current','time');else el.removeAttribute('aria-current');});
  [scale,$('.day-scale-labels',host),$('.day-legend',host),$('.scale-controls',host)].forEach(function(el){el.hidden=sunday;});
  var cursor=$('.day-cursor',host);if(cursor){var start=toMin(arr[0][0]),end=toMin(arr[arr.length-1][1]);cursor.hidden=active<0;if(!cursor.hidden)cursor.style.left=100*(now.mins+new Date().getSeconds()/60-start)/(end-start)+'%';}
}'''
CSS='''/* kitis-single-scale-v9: overview first, exact details on demand */
#globalOverview .day-scale{height:64px;margin-top:20px;border-radius:8px;isolation:isolate}
#globalOverview .day-segment{height:64px;border:0;border-right:1px solid var(--md-surface-container);border-radius:0;padding:0;cursor:pointer;display:flex;flex-direction:column;gap:5px;overflow:hidden;font:inherit;min-width:0}
#globalOverview .day-segment:first-child{border-radius:8px 0 0 8px}
#globalOverview .day-segment.lesson{background:var(--md-surface-highest);color:var(--md-on-surface)}
#globalOverview .day-segment.break{background:var(--md-primary);color:var(--md-on-primary)}
#globalOverview .day-segment.now{background:var(--st-ok);color:var(--st-on-ok);outline:none}
#globalOverview .day-segment.selected{box-shadow:inset 0 0 0 3px var(--md-on-surface)}
#globalOverview .day-segment:focus-visible{outline:3px solid var(--md-on-surface);outline-offset:3px;z-index:3}
.short .scale-time,.short .wide-label{display:none}
.scale-number{font-size:14px;font-weight:650}.scale-time{font-size:11px;white-space:nowrap;font-variant-numeric:tabular-nums}
#globalOverview .day-cursor{top:-10px;bottom:-8px;pointer-events:none;background:var(--md-on-surface);box-shadow:0 0 0 1px var(--md-surface-low)}
#globalOverview .day-cursor::before{background:var(--st-ok);border:1px solid var(--md-surface-low)}
#globalOverview .day-scale-labels{position:relative;height:20px;margin-top:12px;display:block;font-variant-numeric:tabular-nums}
.scale-tick{position:absolute;transform:translateX(-50%);font-size:11px}.scale-tick.first{transform:none}.scale-tick.last{transform:translateX(-100%)}
#globalOverview .day-legend{margin:12px 0;gap:8px 16px}
#globalOverview .day-legend span::before{content:'';display:inline-block;width:10px;height:10px;margin-right:6px;border-radius:2px;background:var(--md-surface-highest);border:1px solid var(--md-outline)}
#globalOverview .day-legend .legend-break::before{background:var(--md-primary)}
#globalOverview .day-legend .legend-now::before{background:var(--st-ok)}
.scale-detail{border-top:1px solid var(--md-outline-variant);padding-top:12px;display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;justify-content:space-between}
#intervalDetail{font-size:14px;font-weight:550;line-height:22px;margin:0;min-width:0}
.scale-controls{display:flex;align-items:center;gap:8px;max-width:100%}.scale-controls label{font-size:12px;color:var(--md-on-surface-variant)}
.scale-controls select,.scale-controls button{min-height:44px;border:1px solid var(--md-outline);border-radius:8px;background:var(--md-surface-high);color:var(--md-on-surface);padding:8px;font:inherit;font-size:12px;min-width:0}
.scale-controls select{max-width:260px;flex:1}.scale-controls button{white-space:nowrap;cursor:pointer}.scale-controls button:disabled{opacity:.5;cursor:default}
#globalOverview [hidden]{display:none!important}
@media(max-width:1250px){.scale-time{display:none}.wide-label{display:none}}
@media(max-width:600px){#globalOverview .day-scale,#globalOverview .day-segment{height:52px}.scale-number{font-size:12px}.scale-tick.middle{display:none}.scale-controls{width:100%;flex-wrap:wrap}.scale-controls label{width:100%}.scale-controls select{max-width:none}#globalOverview h2{font-size:18px}.scale-detail{gap:12px}#globalOverview .day-legend{font-size:10px;gap:6px 10px}}
'''
if __name__=='__main__':
    p=Path(__file__).with_name('index.html');p.write_text(migrate(p.read_text()))
