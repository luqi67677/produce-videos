---
version: 1.0
name: Wings
slot: chart
description: >
  Butterfly chart: two populations compared across the same 4–6
  categories, bars opening left and right from a center label gutter
  on ONE mirrored scale, every bar end value-labeled. The row where
  the two sides diverge most carries the accent — the asymmetry is
  the finding. Fulcrum weighs numbers; Wings shows their shape.
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

# Wings — chart layout

## Intent

Some comparisons are not about a winner but about **a different
shape**: the day shift's alert mix is not the night shift's, the
new cohort doesn't buy what the old one did. Wings spreads the two
populations from a shared spine so their profiles face each other —
symmetry reads instantly as "same world," and any long wing on one
side is the story. Use it for two groups over the same categories
where the MIX is the argument. For a two-option decision, use
Fulcrum or Ledger Versus.

## The chart contract (inherited refusals)

No gridlines, no axes. One linear scale, identical on both sides
(one pixel-per-unit, mirrored) — asymmetric scaling is the
butterfly chart's classic fraud and the first thing to refuse.
Every bar prints its value at its tip; group names sit once above
their wings; no legend. Exactly one accent element (the most
divergent row: its label, both bars, both values).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Two different cities after dark          ← headline           │
│  ALERTS PER 1,000 STREAMS · SAME SCALE BOTH WINGS              │
│                                                                │
│        Day shift        │category│        Night shift          │
│  342 ████████████████ Traffic incident ████ 121                │
│  187 █████████        Crowd density    ███ 64                  │
│   45 ██           Perimeter breach     ██████████ 210 ← accent │
│   76 ████             Flood sensor     ████ 82                 │
│   21 █               Camera tamper     █████ 96                │
│                                                                │
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
| Center gutter | x:820 → 1100 (280px), category labels centered in it | `--lp-font-display`, 24px, weight 700, centered, ≤ 2 lines | `--lp-fg`; accent row `--lp-accent` |
| Group headers | y:308; left name right-aligned to x:820, right name left-aligned at x:1100 | `--lp-font-display`, 28px, weight 700 | `--lp-fg` |
| Rows (×5) | bar centers at y:372, 492, 612, 732, 852 (120px pitch) | — | — |
| Left bars | right edge fixed at x:820, opening leftward; 40px tall | — | `--lp-fg` at 30%; accent row `--lp-accent` |
| Right bars | left edge fixed at x:1100, opening rightward; 40px tall | — | `--lp-fg` at 30%; accent row `--lp-accent` |
| Scale | one px-per-unit both sides; longest bar ≤ 700px | — | — |
| Values | mono 18px, 16px outside each bar tip, vertically centered | `--lp-font-mono` | `--lp-fg-muted`; accent row `--lp-accent` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 2 groups, 4–6 shared categories.** Three groups is a
  Quartet-shaped problem or a table.
- **One scale, mirrored exactly** — if one group's max dwarfs the
  other's, the small wing stays small; compressing either side is
  refused. Normalize BOTH sides to the same rate basis (per 1,000,
  per capita) before charting, and say so in the reading line.
- **Category labels:** ≤ 18 characters (they live in a 280px
  gutter), same order top-to-bottom for both wings by definition.
- **Values:** ≤ 5 characters; unit and basis live in the reading
  line.
- **Accent row:** exactly one — the largest divergence or the row
  the deck argues about. Both its bars accent together; never one
  wing only (that reads as team colors).
- **Sort rows** by the left group's magnitude or a stated fixed
  order — never to sculpt a prettier butterfly.

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

The wings open from the spine, total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — group headers + category labels fade in, 0.5s.
4. `0.50s` — rows open top to bottom, 0.14s apart: both bars wipe
   outward simultaneously (left bar `scaleX` origin RIGHT, right
   bar `scaleX` origin LEFT, 0.6s), values fading at each tip 0.15s
   later.
5. `1.40s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Bar mass** → the system's ink mixed toward the surface at ~30%
  perceived contrast; both wings the SAME ink (the sides are not
  teams).
- **Accent row** → the system's one hot color on both bars.
- **Center gutter** → may gain the system's faint vertical rules at
  x:820 and x:1100 if it frames columns; ≤ `--lp-fg-faint`.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Different scales per wing — the one unforgivable butterfly sin.
- Coloring the wings differently (left blue / right orange imports
  team semantics; the geometry already separates them).
- Raw counts from different-sized populations — rate-normalize or
  refuse.
- Category labels pushed to one side (the shared spine IS the
  comparison).
- Six-plus rows or paragraph-length category names.
- Branding larger than 40px tall or anywhere but the reserved corner.
