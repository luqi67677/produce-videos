---
version: 1.0
name: Loom
slot: chart
description: >
  Rhythm heatmap. A 7×12 matrix — days as rows, two-hour blocks as
  columns — woven in five depths of ONE ink, darker meaning more. Day
  labels in the left gutter, hour marks under the columns, and the
  single peak cell ringed in accent with its value printed inside.
  For when-does-it-happen stories, never for magnitudes over time.
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

# Loom — chart layout

## Intent

Skyline and Tideline answer "how much over time"; Loom answers
**"when"** — the weekly weave of a phenomenon, rush hours reading as
dark wefts, quiet nights as pale ones. The pattern is the finding: a
control room sees its own staffing problem in one glance. Use it for
cyclical intensity (alerts by hour×day, traffic, logins). If the
question is a trend, not a rhythm, this is the wrong chart.

## The chart contract (inherited refusals)

No gridlines (the cell gaps are the grid). No axes beyond direct day
and hour labels. No legend — the reading line states "darker = more,"
and the five depths are steps of ONE ink toward the surface, never a
second hue. One accent element: the peak cell's ring and printed
value. Depth steps must be perceptually wide (in the grayscale demo:
6%, 15%, 30%, 50%, 78% ink).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  The week has a shape                     ← headline           │
│  CONFIRMED ALERTS BY 2-HOUR BLOCK · DARKER = MORE              │
│                                                                │
│      MON  ░░▒▒▓▓▒▒▒▒▓▓█▓▒░                                     │
│      TUE  ░░▒▒▓▓▒▒▒▒▓▓▓▓▒░                                     │
│      WED  ░░▒▒█▓▒▒▒▒▓▓█▓▒░                                     │
│      THU  ░░▒▒▓▓▒▒▒▓▓▓█▓▒░                                     │
│      FRI  ░░▒▒▓▓▒▒▒▓█[212]▓▒  ← peak cell ringed, value inside │
│      SAT  ░░░▒▒▒▓▓▓▓██▓▓                                       │
│      SUN  ░░░░▒▒▒▒▓▓▓▒▒                                        │
│           00    06    12    18    24                           │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / SPAN                                     12 / 14     │
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
| Matrix | 7 rows × 12 columns; cells 108×56, gaps 12; x:250 → 1678, y:330 → 770 (row pitch 64) | — | cells: `--lp-fg` at 6 / 15 / 30 / 50 / 78% by intensity |
| Day labels | right-aligned to x:230, vertically centered per row | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.10em | `--lp-fg-muted` |
| Hour marks | y:794, at block boundaries 00 / 06 / 12 / 18 / 24 (x:250, 610, 970, 1330, left-aligned; 24 right-aligned to x:1678) | `--lp-font-mono`, 15px | `--lp-fg-muted` |
| Peak ring | 3px accent outline around the single peak cell, offset −3px | — | `--lp-accent` |
| Peak value | centered inside the peak cell | `--lp-font-mono`, 18px, weight 500 | `--lp-bg` (on the dark cell) |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source/span) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **7 day-rows × 12 two-hour columns.** Hour-level (24-column) grids
  are dashboard granularity — aggregate to blocks; the slide is read
  from meters away. Other weaves (weeks × months) keep ≤ 14 columns.
- **Exactly 5 intensity depths**, binned honestly (quantiles or
  equal-width, stated in the footer if not obvious). More depths
  read as noise at distance.
- **One ink.** Depths are opacity/mix steps of `--lp-fg` (or the
  system's ink); a hue ramp is a refusal.
- **One peak cell** ringed, with its raw value printed inside. If
  two cells tie, ring the one the story is about — never two rings.
- **Every row and column real:** no dropping quiet days to compress
  the matrix; the empty cells are the contrast that makes dark ones
  legible.

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

The loom weaves row by row, total ≤ 1.6s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — day labels fade in together, 0.5s.
4. `0.40s` — rows weave in top to bottom: each row fades +
   drifts from the left (`translateX(-24px→0)`), 0.5s, 0.09s stagger.
5. `1.10s` — hour marks fade, 0.4s.
6. `1.20s` — the peak ring pops `scale(0.6→1)` + fade with its
   value, 0.4s — the finding lands last.
7. `1.30s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Cells** → rounded ≤ 8px if the system rounds; gaps may narrow
  to 8px in dense systems.
- **Ink ramp** → the system's single sequential ramp (its ink mixed
  toward its surface) at five stops; never a multi-hue ramp.
- **Peak ring** → the system's focus/highlight vocabulary (corner
  ticks, an underline bracket) touching only the one cell.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- A color-scale legend bar — the reading line plus five honest
  depths make it redundant; if five depths need a legend, the
  binning is wrong.
- Hue ramps (blue→red) or diverging scales — rhythm has no
  "negative."
- Printing values in every cell — the weave is the message; one
  value, at the peak, is the exception that proves it.
- 24 hourly columns on a projected slide.
- Interpolated/smoothed cells or heat "glow" bleeding across gaps.
- Branding larger than 40px tall or anywhere but the reserved corner.
