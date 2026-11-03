"""Idempotent presentation patch: retain all data, expose bell times and results."""
from pathlib import Path
import re
from overview_timeline import MON, MAIN, minute


def improve(s):
    if 'kitis-readable-v7' in s:
        return s
    def overview(m):
        block=m[0]
        times=re.findall(r'aria-label="Пара (\d+) · (\d\d:\d\d)–(\d\d:\d\d)"',block)
        if not times:
            raise ValueError('Overview without source lesson intervals')
        cards='<div class="bell-guide" aria-label="Все пары и перемены: точное время">'
        for i,(n,a,b) in enumerate(times):
            cards+=f'<div class="bell-card lesson-card"><b>Пара {n}</b><time>{a}–{b}</time><small>{minute(b)-minute(a)} мин</small></div>'
            if i<len(times)-1:
                end=times[i+1][1];duration=minute(end)-minute(b)
                cards+=f'<div class="bell-card break-card"><b>Перемена {n}–{int(n)+1}</b><time>{b}–{end}</time><small>{duration} мин</small></div>'
        cards+='</div>'
        return block.replace('<span>Интервалы и длительности — ниже</span>','<span>Номера на шкале соответствуют карточкам</span>').replace('</div></div>', '</div>'+cards+'</div>')
    s=re.sub(r'<div class="day-overview">.*?<div class="day-legend">.*?</div></div>',overview,s,flags=re.S)
    s=s.replace('<button class="stab active" data-view="sch">Расписание</button>', '<button type="button" class="stab active" data-view="sch" aria-pressed="true">Расписание</button>')
    s=s.replace('<button class="stab" data-view="res">Итоги</button>', '<button type="button" class="stab" data-view="res" aria-pressed="false">Итоги нагрузки</button>')
    s=s.replace("b.classList.toggle('active', b === btn);", "b.classList.toggle('active', b === btn);\n      b.setAttribute('aria-pressed', String(b === btn));")
    # Give each results region a clear visible title, including its owner.
    def results(m):
        block=m[0]
        name=re.search(r'<h2 class="ent-name">(.*?)</h2>',block)
        if 'data-pane="res"' not in block or not name:return block
        return block.replace('<div class="pane" data-pane="res" hidden>', '<div class="pane" data-pane="res" hidden><h3 class="results-title">Итоги нагрузки · '+name[1]+'</h3><p class="results-note">По группам и дисциплинам: всего часов, план, факт и остаток. Таблицу на телефоне можно прокручивать вправо.</p>')
    # Entity sections contain day sections, so bound by next entity rather than first closing section.
    s=re.sub(r'<section class="ent".*?(?=<section class="ent"|</main>)',results,s,flags=re.S)
    css='''
/* kitis-readable-v7: explicit time cards; never encode time by color alone */
.bell-guide{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:6px;margin-top:12px}
.bell-card{min-width:0;padding:9px 8px;border-radius:8px;background:var(--md-surface-highest);display:flex;flex-direction:column;gap:4px;font-variant-numeric:tabular-nums}
.bell-card b{font-size:12px;line-height:18px;font-weight:600}
.bell-card time{font-size:12px;line-height:18px;white-space:nowrap;color:var(--md-on-surface)}
.bell-card small{font-size:11px;line-height:16px;color:var(--md-on-surface-variant)}
.lesson-card{grid-row:1}
.break-card{grid-row:2;border-left:3px solid var(--md-primary);background:var(--md-surface-low)}
.break-card b{color:var(--md-primary)}
.subtabs .stab[data-view]{min-height:44px;border:1px solid var(--md-outline);padding:10px 18px;border-radius:12px;color:var(--md-on-surface);background:var(--md-surface-highest);font-weight:600}
.subtabs .stab[data-view].active{background:var(--md-primary);color:var(--md-on-primary);border-color:var(--md-primary)}
.stab:focus-visible{outline:3px solid var(--md-primary);outline-offset:3px}
.results-title{font-size:20px;line-height:28px;margin:0 0 8px}
.results-note{font-size:13px;line-height:20px;color:var(--md-on-surface-variant);margin:0 0 16px}
@media(min-width:1025px) and (max-width:1350px){.bell-guide{grid-template-columns:repeat(4,minmax(0,1fr))}.lesson-card,.break-card{grid-row:auto}}
@media(max-width:1024px){.bell-guide{grid-template-columns:repeat(4,minmax(0,1fr))}.lesson-card,.break-card{grid-row:auto}}
@media(max-width:600px){.bell-guide{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px}.bell-card{padding:8px 10px}.bell-card time{font-size:13px}.bell-card small{font-size:12px}.subtabs{gap:8px}.subtabs .stab[data-view]{padding:10px 12px}}
'''
    return s.replace('</style>',css+'\n</style>')

if __name__=='__main__':
    p=Path(__file__).with_name('index.html')
    p.write_text(improve(p.read_text()))
