"""Targeted, idempotent enhancement of the original static KITIS page."""
from pathlib import Path
import re, datetime
p=Path(__file__).with_name('index.html')
s=p.read_text()
if 'kitis-timeline-v4' in s:
    raise SystemExit('Already patched')
original_lessons=re.findall(r'<li class="tl-item".*?</li>',s)
# Keep every original lesson and load table byte-for-byte; fill only absent days.
bells=[('08:30','09:00'),('09:10','10:30'),('10:40','12:00'),('12:20','13:40'),('13:50','15:10'),('16:00','17:20'),('17:30','18:50')]
main=[('08:30','10:00'),('10:10','11:40'),('12:10','13:40'),('13:50','15:20'),('15:30','17:00'),('17:10','18:40')]
def mins(t):
    h,m=map(int,t.split(':'));return h*60+m
def fill_entity(m):
    block=m.group(0)
    if 'id="panel-default"' in block:return block
    days=re.findall(r'<section class="card-day" data-date="([^"]+)" data-wday="([^"]+)"',block)
    anchor=datetime.datetime.strptime(days[0][0],'%d.%m.%Y').date() if days else datetime.date(2026,11,2)
    monday=anchor-datetime.timedelta(days=anchor.weekday())
    additions=''
    for i,dow in enumerate(['Пн','Вт','Ср','Чт','Пт','Сб','Вс']):
        if any(d[1]==dow for d in days):continue
        date=(monday+datetime.timedelta(days=i)).strftime('%d.%m.%Y')
        rows=''
        for n,(a,b) in enumerate(bells if i==0 else main if i<6 else [],1):
            if n>1:
                prev=(bells if i==0 else main)[n-2][1];gap=mins(a)-mins(prev)
                rows+=f'<li class="tl-break"><span class="tl-breaklabel">Перемена</span><span class="tl-breaktime">{prev}–{a} · {gap} мин</span></li>'
            rows+=f'<li class="tl-item tl-free" data-wday="{dow}" data-date="{date}" data-s="{mins(a)}" data-e="{mins(b)}" data-n="{n}"><span class="tl-node">{n}</span><div class="tl-body"><div class="tl-time">{a}–{b}</div><div class="tl-title free">Окно — пара свободна</div></div></li>'
        additions+=f'<section class="card-day" data-date="{date}" data-wday="{dow}"><div class="day-head"><span class="dow">{dow}</span><span class="date">{date}</span><span class="cnt">Нет занятий</span></div>'+('<ol class="tl">'+rows+'</ol>' if rows else '<p class="empty-day">Выходной — занятий нет</p>')+'</section>'
    # Schedule pane ends immediately before result pane (or entity end).
    end=block.find('</div><div class="pane" data-pane="res"')
    if end<0:end=block.rfind('</div></section>')
    if end<0:end=block.rfind('</section>')
    if end<0:raise ValueError(block[:150])
    block=block[:end]+additions+block[end:]
    cards=re.findall(r'<section class="card-day" data-date="[^\"]+" data-wday="[^\"]+".*?</section>',block,re.S)
    if cards:
        ordered=iter(sorted(cards,key=lambda c:['Пн','Вт','Ср','Чт','Пт','Сб','Вс'].index(re.search(r'data-wday="([^\"]+)"',c)[1])))
        block=re.sub(r'<section class="card-day" data-date="[^\"]+" data-wday="[^\"]+".*?</section>',lambda _:next(ordered),block,flags=re.S)
    return block
# Entity contains nested sections: next entity/main boundary is unambiguous.
s=re.sub(r'<section class="ent"(?:(?!<section class="ent"|</main>).)*',fill_entity,s,flags=re.S)
css='''
/* kitis-timeline-v4: true time geometry, full-width desktop chooser */
[hidden]{display:none!important}
.empty-day{padding:20px 24px;color:var(--md-on-surface-variant)}
.time-axis{position:relative;height:44px;margin:12px 24px 18px;background:var(--md-surface-low);border-radius:8px;overflow:hidden}
.axis-lesson,.axis-break{position:absolute;top:0;height:26px;font-size:11px;display:flex;align-items:center;justify-content:center;background:var(--md-surface-highest);border-right:1px solid var(--md-surface-low)}
.axis-break{background:var(--md-primary-container);color:var(--md-on-primary-container);font-size:9px}
.time-axis::after{content:'08:30';position:absolute;bottom:0;left:0;font-size:10px}
.axis-end{position:absolute;bottom:0;right:0;font-size:10px}
.time-cursor{position:absolute;top:0;bottom:0;width:2px;background:var(--st-ok);z-index:3;box-shadow:0 0 5px var(--st-ok)}
.track{position:relative;gap:0;height:36px}
.track .seg{position:absolute;top:0;height:32px;padding:0;border-radius:3px}
.track .track-break{background:rgba(0,0,0,.25);font-size:9px;color:var(--md-on-primary-container)}
@media(min-width:1025px){
 body.choosing .layout{display:block;max-width:none}
 body.choosing .side{position:relative;top:0;width:100%;height:calc(100dvh - 112px);max-height:none;border:0;padding:12px 24px;gap:8px}
 body.choosing .content{display:none}
 body.choosing .textfield{max-width:420px}
 body.choosing .textfield input{height:36px}
 body.choosing .count{padding-bottom:0}
 body.choosing .list{display:grid;grid-auto-flow:column;grid-template-rows:repeat(var(--chooser-rows,15),minmax(0,1fr));grid-auto-columns:minmax(0,1fr);gap:3px 8px;overflow:hidden}
 body.choosing .li{padding:3px 8px;gap:6px;font-size:12px;min-height:0}
 body.choosing .li .lead{display:none}
 body.choosing .li .txt{white-space:normal;overflow:visible}
 body.choosing .li .cnt{padding:2px 5px;font-size:10px}
}
@media(max-width:600px){.time-axis{margin:12px 16px}.tl-break{flex-wrap:wrap;gap:5px}.tl-break .tl-breaklabel{font-size:10px}}
'''
s=s.replace('</style>',css+'\n</style>')
s=s.replace('function currentBell(now){','function currentBell(now){\n  if(now.wday === 0) return null;')
s=s.replace('function select(target){','function select(target){\n  document.body.classList.remove("choosing");')
s=s.replace("if (FIRST) { FIRST = false; return; }","if (FIRST) { FIRST = false; return; }\n  document.body.classList.add('choosing');\n  $('#search').value = '';\n  fitChooser();\n  window.scrollTo(0,0);")
s=s.replace('function openSide(){','function openSide(){\n  if(window.innerWidth > 1024){document.body.classList.add("choosing");fitChooser();window.scrollTo(0,0);return;}')
s=s.replace('function closeSide(){','function closeSide(){\n  document.body.classList.remove("choosing");')
s=s.replace('setInterval(paint, 20000);','setInterval(paint, 1000);\n  window.addEventListener("resize",fitChooser);')
s=s.replace('  var now = mskNow();','  var now = mskNow();\n  paintTimeAxes(now);')
start=s.index("    var html = '';\n    arr.forEach")
end=s.index('    track.innerHTML = html;',start)+len('    track.innerHTML = html;')
s=s[:start]+'''    track.innerHTML = axisMarkup(arr, now, true);
'''+s[end:]
s=s.replace("          if (prev && prev.classList.contains('tl-break')) prev.hidden = hide;","          // Breaks are real bell intervals, independent of free lesson visibility.")
s=s.replace("        if (!hit) hit = fallback;","        // Never display another weekday as today's lesson.")
extra='''
function fitChooser(){
  var list=$('#tlist');if(!list)return;
  var height=window.innerHeight-list.getBoundingClientRect().top-24;
  var rows=Math.max(1,Math.floor(height/30));
  list.style.setProperty('--chooser-rows',rows);
}
function axisMarkup(arr,now,live){
  var start=toMin(arr[0][0]), end=toMin(arr[arr.length-1][1]), span=end-start, html='';
  function segment(a,b,label,br){
    var l=100*(a-start)/span,w=100*(b-a)/span;
    html+='<span class="'+(live?'seg '+(br?'track-break':''):(br?'axis-break':'axis-lesson'))+'" style="left:'+l+'%;width:'+w+'%" title="'+label+'">'+label+'</span>';
  }
  arr.forEach(function(b,i){
    if(i)segment(toMin(arr[i-1][1]),toMin(b[0]),String(toMin(b[0])-toMin(arr[i-1][1]))+'′',true);
    segment(toMin(b[0]),toMin(b[1]),String(i+1),false);
  });
  if(now && now.wday!==0 && now.mins>=start && now.mins<=end)html+='<span class="time-cursor" aria-label="Текущее время" style="left:'+Math.min(100,Math.max(0,100*(now.mins-start)/span))+'%"></span>';
  if(!live)html+='<span class="axis-end">'+arr[arr.length-1][1]+'</span>';
  return html;
}
function paintTimeAxes(now){
  $$('.ent:not([hidden]) .card-day[data-wday]').forEach(function(day){
    var dow=DOW[day.dataset.wday];if(dow===0)return;
    var arr=dow===1?BELLS['Понедельник']:BELLS['Вт-Сб'];
    var axis=$('.time-axis',day);
    if(!axis){axis=document.createElement('div');axis.className='time-axis';axis.setAttribute('aria-label','Пары и перемены по времени');$('.day-head',day).after(axis);}
    axis.innerHTML=axisMarkup(arr,dow===now.wday?now:null,false);
    $$('.tl-break',day).forEach(function(br){
      var next=br.nextElementSibling,prev=br.previousElementSibling;
      if(!next||!prev||!next.dataset.s||!prev.dataset.e)return;
      var gap=+next.dataset.s-(+prev.dataset.e);
      var label=$('.tl-breaktime',br);
      if(label)label.textContent=$('.tl-time',prev).textContent.split('–')[1]+'–'+$('.tl-time',next).textContent.split('–')[0]+' · '+gap+' мин';
    });
  });
}
'''
s=s.replace('/* ---------- init ---------- */',extra+'\n/* ---------- init ---------- */')
assert re.findall(r'<li class="tl-item".*?</li>',s)==original_lessons
p.write_text(s)
print('Preserved',len(original_lessons),'occupied lessons; enhanced',len(s),'characters')
