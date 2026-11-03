# Daily overview: one proportional scale

Decision: retain a single full-day horizontal scale above all entity schedules. Lessons are graphite with numbers, breaks orange, the active interval green with a moving time cursor. Exact selected/current interval and remaining minutes appear below; desktop lesson times only appear where space allows. Full day fits narrow screens without horizontal scrolling.

Why: overview first, details on demand; avoid repeating every interval as a card. A vertical list and a multi-row card grid duplicate the existing schedule and cannot express one continuous timespan.

Research:
- Nielsen Norman Group, Progressive Disclosure: expose primary information first, make secondary details easy and obvious to access. https://www.nngroup.com/articles/progressive-disclosure
- Continuum: full timespan and detail access. https://eprints.soton.ac.uk/263818/1/continuum-rev.pdf
- Timeline legibility/clutter guidance: https://blog.tomsawyer.com/timeline-graph-visualization

Interaction: click, focus, or arrow through segments; use the explicitly labelled native interval chooser for narrow breaks (44px control, no overlapping tap regions). Selection persists until “К текущему” or Escape. The live interval remains green regardless of selection. Sunday is an explicit empty state. Time labels use endpoint labels on mobile, spaced hourly ticks on desktop. No hover-only dependency.

Reproduce: `python3 single_scale.py`; legacy migrations chain into this idempotent migration. It never regenerates or changes timetable data. `python3 test_single_scale.py [URL]` checks immutable schedule/results markup against d419066, Monday/main/Sunday, every interval, keyboard/select/reset, moving cursor, active lesson and break, Results, all seven days, mobile overflow, JavaScript errors, and screenshots at 1440/390/320px.
