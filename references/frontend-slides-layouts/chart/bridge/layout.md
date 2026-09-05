---
version: 1.0
name: Bridge
slot: chart
description: >
  Waterfall chart for one decomposed change. A grounded start bar, 2–4
  floating signed steps linked by dashed running-level connectors, and
  a grounded end bar in accent — the only chart in the pack allowed to
  float bars, and only because the arithmetic is printed on every one
  of them and sums exactly.
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

# Bridge — chart layout

## Intent

"We went from 4,200 to 6,500" hides the story; the story is what was
added, what was built, and what was honestly retired along the way.
Bridge walks the audience across that arithmetic **one signed step at
a time**, each step's value printed on it, the running level carried
by dashed connectors, and the destination bar earning the accent.
Use it when one total changed for 2–4 nameable reasons. If the
reasons don't sum exactly to the change, the slide is not ready.

## The chart contract (inherited refusals)

No gridlines. No y-axis — the printed values ARE the axis. No
floating legend. True proportions from a real zero baseline for the
grounded bars; floating steps are proportionally true and sum
exactly. Exactly one accent element (the end bar).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  How the fleet reached 6,500              ← headline           │
│  CAMERA COUNT FY25 → FY26 · STEPS SUM EXACTLY                  │
│                        +900 ┌──┐                               │
│              +1,800 ┌──┐----│  │---- ┐ −400                    │
│             ┌──┐----│  │    └──┘     ▼┌──┐----┌────┐           │
│   4,200     │  │    └──┘              └──┘    │    │ 6,500     │
│  ┌────┐-----│  │                              │▒▒▒▒│ ← accent  │
│  │    │     └──┘                              │▒▒▒▒│           │
│  ┴────┴───────────────────────────────────────┴────┴─ baseline │
│  FY25 BASE  NEW SITES   DENSIFY     RETIRED   FY26 TOTAL       │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / PERIOD                                   10 / 12     │
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
| Field | y:360 (= scale max + headroom) → y:820 (= 0), linear | — | — |
| Baseline | x:96 → 1824, y:820, 1px | — | `--lp-line` |
| Columns (×5 for start + 3 steps + end) | 200px wide; x:96, 478, 860, 1242, 1624 (equal gaps). With 2 steps: 4 columns 220px at x:96, 566, 1036, 1506 | — | — |
| Start bar | grounded on the baseline, height = value | — | `--lp-fg` |
| Positive step bars | floating: bottom at the incoming running level, height = step | — | `--lp-fg-muted` |
| Negative step bars | floating: TOP at the incoming running level, height = |step|, outlined (2px stroke, no fill) | — | stroke `--lp-fg-muted` |
| End bar | grounded, height = final value | — | `--lp-accent` |
| Connectors | dashed 1px horizontal at each outgoing running level, spanning the gap to the next column | — | `--lp-line` |
| Value labels | 14px above each bar's top edge (below the bottom edge for negative steps), centered on the column; steps signed ("+1,800", "−400") | `--lp-font-mono`, 20px | matches its bar's ink; end value `--lp-accent` |
| Column labels | y:848, centered under each column, single line | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.10em | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Start + 2–4 steps + end.** One step is a Ratio Split; five steps
  is an accounting appendix.
- **The arithmetic must close:** start + Σsteps = end, exactly, in
  the printed figures. Rounding that breaks the sum disqualifies the
  data for this preset.
- **Scale:** y:820 is 0; y:360 is the running maximum plus ~5%
  headroom. Grounded bars rise from the baseline — never truncated.
- **Signs:** every step label signed; start and end unsigned. At
  most ONE negative step — more means the story is decline, and a
  decline deserves its own slide, not a dip in a victory bridge.
- **Column labels:** ≤ 12 characters, real nouns ("NEW SITES", not
  "GROWTH 1").
- **Values:** ≤ 7 characters. Units live in the reading line.

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

The bridge builds itself left to right, total ≤ 2.0s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — baseline wipes `scaleX(0→1)` origin left, 0.6s.
4. `0.50s` — start bar grows `scaleY(0→1)` origin bottom, 0.5s; its
   value + column label fade 0.15s later.
5. `0.75s` — steps play 0.28s apart: connector wipes across the gap
   (origin left, 0.25s), then the step bar grows (positive: origin
   bottom; negative: origin TOP — it hangs downward), then its label.
6. `1.60s` — end bar grows origin bottom, 0.6s — the arrival beat;
   its accent value fades at 1.85s.
7. `1.90s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Step fills** → the system's ink mixed toward the surface;
  positive steps one mix step lighter than grounded bars, negative
  steps outlined or hatched in the same ink. Never red/green — the
  signs and the hang direction already encode it.
- **Connectors** → the system's dashed-line vocabulary.
- **End bar** → the system's one hot color; if the system is
  monochrome, the end bar goes full `--lp-fg` and the start bar
  drops one mix step.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Steps that don't sum — the audience WILL do the arithmetic.
- Red/green step coloring (imports P&L semantics the pack refuses).
- Truncating the baseline or letting grounded bars start above zero.
- Connectors as arrows, or slopes between levels — the level carries
  flat; only bars carry magnitude.
- Accenting the biggest step instead of the end bar (the destination
  is the story; the steps are the route).
- Branding larger than 40px tall or anywhere but the reserved corner.
