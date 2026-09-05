---
version: 1.0
name: Bar Ledger
slot: stats
description: >
  Comparison you can measure with your eye. Three or four labeled
  horizontal bars, widths in true proportion to their values, the
  highlighted bar in accent and the rest muted — the humblest chart
  in the pack; richer data shapes live in the `chart` slot.
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

# Bar Ledger — stats layout

## Intent

When the story is "this one versus those", numbers alone make the
audience do arithmetic. A horizontal bar row does the arithmetic for
them — and stays elegant precisely because it refuses every chart
convention beyond length: no axis, no gridlines, no legend, no
tooltips. Label left, bar middle, value right; the accent bar is the
sentence's subject.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       13 / 14  │
│  WHERE THE HOURS WENT       ← headline                         │
│                                                                │
│  Site rollout      ████████████████████████████████  1,240 h  │
│  Edge models       ████████████████████░░           760 h     │
│  Console           ██████████░░                     420 h     │
│  Incidents         ███░░  ← accent (the story)      118 h     │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  SOURCE / PERIOD                                       CINDER  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line | `--lp-font-display`, 84px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Rows | x:96 → 1824, first row top y:400, row pitch 130px; grid: label 380px / bar track 1fr / value 180px right-aligned; all vertically centered per row | — | — |
| · label | | `--lp-font-body`, 22px | `--lp-fg` |
| · bar | height 20px; width = value ÷ max × track width, **true proportion, no minimums** | — | highlighted bar `--lp-accent`; others `--lp-fg-muted` at 45% |
| · value | | `--lp-font-mono`, 20px, ls 0.04em | `--lp-fg`; highlighted row's value `--lp-accent` |
| Footer hairline + source | x:96 → 1824, y:962 / y:984 | mono 14px | `--lp-line` / `--lp-fg-muted` |

## Content constraints (hard limits)

- **3–4 bars,** one unit, sorted by value (descending) unless the
  labels have a fixed natural order. Five+ values → this is a chart's
  job; link a dashboard instead.
- **Proportions are sacred:** bar widths must be computed from the
  real values against the same maximum. No log scales, no truncated
  bars, no minimum widths for legibility — if the smallest bar is a
  sliver, the sliver is the story.
- **Exactly one highlighted bar** — the row the talk track is about.
  If all bars matter equally, none takes the accent.
- **Labels:** ≤ 24 characters. **Values:** ≤ 8 glyphs with unit.

## Image variant

**With images:** each row's label may carry a 96×96 image chip left
of it (grid gains a 120px chip column; labels shorten to ≤ 18
characters). All rows or none. **Recommended size / placeholder:**
`https://placehold.co/192x192` (2× for sharpness at 96px).
**Dimension fallback:** fixed 96×96 frames, `object-cover`,
token CSS fill behind each `<img>`. Chips are optional.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.40s` — rows arrive top-to-bottom, 0.14s stagger: label and
   value fade 0.4s, then the bar grows to its true width via
   `transform: scaleX(0→1)` (origin left) over 0.7s — the growth IS
   the reading moment.
3. The highlighted bar lands last regardless of its row position
   (+0.2s), and its value pops with it.
4. `1.30s` — footer fades, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
bars render at full width immediately.

## Skin points

- **Bars** → the system's fill vocabulary (solid, its pattern at high
  density); square ends unless the system rounds everything.
- **Track** → invisible by default; a system may show it as a 1px
  baseline hairline under each bar.
- **Highlight** → the system's accent; if the system is monochrome,
  highlight by full `--lp-fg` against 30% others.

## Failure modes to avoid

- Any distortion of proportion — the moment a bar lies, the deck lies.
- Gridlines, axes, percentage ticks; the values column already
  answers "how much exactly".
- Vertical bars — at slide distance horizontal bars with left labels
  read twice as fast.
