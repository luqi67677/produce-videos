---
version: 1.0
name: Datum
slot: chart
description: >
  Bullet chart for delivered-versus-committed. Three KPI rows, each a
  horizontal bar of actual delivery expressed as percent of its
  target, all measured against ONE vertical datum line at 100%. Bars
  that cross the line beat their promise; the row the deck must argue
  about carries the accent. Absolute figures printed at every bar end.
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

# Datum — chart layout

## Intent

"Did you do what you said?" is the only question status meetings ask.
Datum answers it in one geometry: **a fixed line where the promises
stand, and bars that either reach it or don't**. Normalizing every
KPI to percent-of-target lets uptime, counts, and hours share one
honest field — and the printed absolute figures keep the
normalization auditable. Use it for 3 committed targets under review;
for magnitudes without targets, Bar Ledger.

## The chart contract (inherited refusals)

No gridlines. No axis beyond the single datum line, which is data
(the commitment), not chrome. No legend — the reading line states
the encoding once. True proportions: bars scale linearly from a real
zero at the field's left edge; the datum sits at 100% of each row's
own target, and each row prints actual/target absolutes. Exactly one
accent element (the argued row).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Promised vs delivered                    ← headline           │
│  BARS = DELIVERED AS % OF TARGET · LINE = THE PROMISE          │
│                                       TARGET │                 │
│  Cameras live      ████████████████████████████▌ 6,500 / 6,250 │
│  TARGET 6,250                                 │                │
│                                               │                │
│  Operator certs    █████████████████████▌     │ 1,740 / 2,000  │ ← accent
│  TARGET 2,000                                 │     (the miss) │
│                                               │                │
│  Uptime, fleet     ████████████████████████████│ 99.95 / 99.9  │
│  TARGET 99.9%                                 │                │
│  0 ───────────────────────────────────────────┴─────────       │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / PERIOD                                   11 / 12     │
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
| Field | x:500 (= 0%) → x:1700 (= 120%), 10px per percent | — | — |
| Datum line | vertical 2px at x:1500 (= 100%), y:330 → 850 | — | `--lp-fg` |
| Datum tag | centered on x:1500, y:300 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| KPI rows (×3) | bar centers at y:400, 570, 740 (170px pitch) | — | — |
| KPI labels | x:96, aligned to bar top, max-width 380px | `--lp-font-display`, 28px, weight 700 | `--lp-fg`; accent row `--lp-accent` |
| Target sublabels | under each KPI label | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.10em | `--lp-fg-muted` |
| Tracks | x:500 → 1700, 44px tall, centered on bar center | — | `--lp-fg-faint` |
| Bars | from x:500, width = percent × 10px, 44px tall | — | `--lp-fg`; accent row `--lp-accent` |
| Value labels | 20px right of each bar end, "actual / target" | `--lp-font-mono`, 20px | `--lp-fg-muted`; accent row `--lp-accent` |
| Zero label | x:500 centered, y:872 | `--lp-font-mono`, 15px | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 KPIs** (with 2, use 220px pitch at y:430/650; four
  targets under review is a spreadsheet — split the slide).
- **Targets must be real prior commitments** (from the last board,
  the contract, the SLA) and the sublabel names each one. Inventing
  targets after the fact is the dishonesty this layout makes visible.
- **Bars cap at 120%** (the field edge); overdelivery beyond that
  prints in the value label but the bar stops — the field never
  rescales to flatter a hero row.
- **Value labels:** "actual / target" in the KPI's own unit, ≤ 16
  characters total.
- **Accent row:** exactly one — the row the meeting will argue about
  (usually the miss). Beating rows stay `--lp-fg`; the accent is
  attention, not shame-coloring. Never red.
- **KPI labels:** ≤ 20 characters. Target sublabels: ≤ 18.

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

The promises stand first; delivery measures against them. Total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — the datum line grows `scaleY(0→1)` origin top, 0.6s,
   with its tag — the promise exists before the results.
4. `0.55s` — tracks fade in, 0.4s, 0.1s stagger.
5. `0.70s` — bars grow `scaleX(0→1)` origin left, 0.7s each, 0.15s
   stagger top to bottom; each row's labels fade as its bar lands.
6. `1.40s` — value labels + zero label + footer fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Datum line** → the system's emphatic rule (doubled, 3px) — it
  outranks hairlines; never dashed (promises are not tentative).
- **Tracks** → the system's faint fill or may be dropped in minimal
  systems (bars against whitespace).
- **Bars** → the system's ink; the accent row its one hot color.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Per-row datum positions — ONE line at 100% is the geometry; rows
  normalize to it, never it to rows.
- Red/green pass-fail coloring, checkmarks, or "on track" chips.
- Bars starting anywhere but 0%, or a field zoomed to 80–110% "for
  detail" — the drama of nearly-reaching lives in the full run-up.
- Hiding the absolute figures (percent-only bullet charts let
  normalization lie).
- Accenting the best row by default — accent the one that needs the
  meeting's attention.
- Branding larger than 40px tall or anywhere but the reserved corner.
