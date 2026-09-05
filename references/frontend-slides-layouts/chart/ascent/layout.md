---
version: 1.0
name: Ascent
slot: chart
description: >
  Pace chart: cumulative delivery as an accent area climbing across
  the program's full time field, measured against one straight plan
  line running from start to the committed target. A dashed "today"
  vertical crosses both, and the gap between plan and actual is
  printed where it stands. Answers exactly one question: are we on
  pace?
tokens:
  - --lp-bg
  - --lp-fg
  - --lp-fg-muted
  - --lp-fg-faint
  - --lp-accent
  - --lp-line
  - --lp-font-display
  - --lp-font-body
  - --lp-font-mono
---

# Ascent — chart layout

## Intent

Program reviews hide the only number that matters — the gap between
where the plan said we'd be and where we are — inside burndown
dashboards. Ascent draws it as **terrain against a rope line**: the
plan is the straight rope from start to summit, the actual is the
ground climbed, and today's vertical shows daylight between them.
The layout works equally when ahead or behind; what it refuses is
not knowing. Use it for one cumulative metric with a dated,
committed target. For a trend without a target, Tideline.

## The chart contract (inherited refusals)

No gridlines, no y-axis. The plan line is data (the commitment),
not chrome; the today line is dashed and labeled. True proportions:
y runs from a real zero baseline to the target with the plan line
connecting (start, 0) to (deadline, target); the actual area uses
straight segments between honest points. All four values printed
(target, plan-at-today, actual-at-today, gap). Exactly one accent
element (the actual area + endpoint + its value).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  The road to ten thousand                 ← headline           │
│  CUMULATIVE CAMERAS · PLAN = CONTRACT TRAJECTORY               │
│                      today                    10,000 target ─┐ │
│                        ┊                        ____________ ● │
│                        ┊          plan line ___/               │
│                        ○ 5,800 ___/                            │
│               gap −900 ┊___/▒▒▒                                │
│                    ____┊▒▒▒▒▒▒▒ ← actual area (accent)         │
│              _____/▒▒▒▒● 4,900                                 │
│  0 ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁ baseline       │
│  JAN 26                                        DEC 26          │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / BASIS                                    09 / 12     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px** left/right
margins, **72px** top/bottom margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72, single line | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Branding slot (top-right, optional) | right-aligned to x:1824, y:66, ≤ 40px tall, ≤ 260px wide | wordmark in `--lp-font-display` 700 or an image logo | `--lp-fg` |
| Chrome hairline | x:96 → 1824, y:118, 1px | — | `--lp-line` |
| Headline | x:96, y:164, max-width 1400px, 1 line | `--lp-font-display`, 60px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Reading line | x:96, y:242, single line | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` |
| Field | x:460 (= program start) → x:1760 (= deadline); y:850 (= 0) → y:330 (= target) | — | — |
| Baseline | x:460 → 1760, y:850, 1px; date labels at both ends beneath (y:874) | dates `--lp-font-mono` 17px | `--lp-line`; dates `--lp-fg-muted` |
| Plan line | straight 2px line from (460, 850) to (1760, 330) — rendered as a rotated rule | — | `--lp-fg` |
| Target marker | 12px open square at (1760, 330); label "TARGET n" right-aligned above at y:296 | label `--lp-font-mono` 18px | `--lp-fg` |
| Today line | dashed 1px vertical at today's x, y:330 → 850; "TODAY" tag above at y:302 | tag `--lp-font-mono` 15px | `--lp-line`; tag `--lp-fg-muted` |
| Plan-at-today marker | 12px open square where the plan line crosses today; value beside it | value `--lp-font-mono` 20px | `--lp-fg-muted` |
| Actual area | from x:460 to today's x, straight segments, filled to the baseline | — | `--lp-accent` |
| Actual endpoint | 16px filled square at (today, actual); value beside it | value `--lp-font-mono` 22px, weight 500 | `--lp-accent` |
| Gap label | on the today line, midway between plan and actual markers, offset right | `--lp-font-mono`, 19px, signed ("−900" / "+400") | `--lp-fg` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (basis) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **One metric, cumulative, with a real committed target and
  deadline** (contract, board filing). Self-set stretch goals get a
  Tideline, not a rope line.
- **The four printed values must reconcile:** plan-at-today −
  actual-at-today = the printed gap, exactly.
- **Today's position is honest** on the time axis (58% of the
  program elapsed = 58% across the field).
- **Actual curve:** 8–24 straight segments; no smoothing, no
  projection beyond today — the area STOPS at the today line.
  Forecast bands are refused (draw next quarter's slide next
  quarter).
- **Works both ways:** when ahead of plan, the same geometry holds
  and the gap label goes positive — never restyle the chart to
  celebrate or mourn.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

None — chart presets carry data, not imagery.

## Choreography

The rope is fixed before the climb is shown, total ≤ 1.9s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — baseline wipes `scaleX(0→1)` origin left, 0.5s; date
   labels fade.
4. `0.50s` — the plan line draws from start to target (`scaleX(0→1)`
   along its own axis, origin left), 0.7s; target marker + label
   land at 1.1s.
5. `0.90s` — the actual area grows `scaleX(0→1)` origin left, 0.8s —
   the climb replays; its endpoint + value land at 1.55s.
6. `1.55s` — the today line draws `scaleY(0→1)` origin top with its
   tag, 0.4s; plan-at-today marker and the gap label fade at 1.75s —
   the verdict is the last thing to appear.
7. `1.80s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Actual area** → the system's one hot color, solid or its
  sanctioned area treatment; may gain a 2px top stroke in the same
  ink.
- **Plan line** → the system's emphatic rule; solid always (the
  commitment is not tentative) — only the today line dashes.
- **Markers** → the system's point vocabulary; plan markers stay
  open, actual stays filled.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Projecting the actual area past today (dotted "we'll catch up"
  tails are the genre's signature lie).
- Re-baselining the plan line to a revised target without saying
  so — if the target moved, BOTH lines show (old plan at
  `--lp-fg-faint`), or the slide is propaganda.
- A y-scale that doesn't reach the target (a summit off-frame).
- Coloring the gap red/green.
- Two metrics on one field ("cameras AND operators") — one rope,
  one climb.
- Branding larger than 40px tall or anywhere but the reserved corner.
