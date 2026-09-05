---
version: 1.0
name: Gamut
slot: chart
description: >
  Range chart for spread stories. Four category rows, each a light
  p5–p95 band on one shared zero-poled scale with a solid median
  tick inside it; band ends and medians value-labeled directly. The
  row whose spread is the problem carries the accent. For when the
  average is fine and the variance is the finding.
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

# Gamut — chart layout

## Intent

Averages are where variance goes to hide. A site can boast a fine
median while its worst hour is a catastrophe — and Bar Ledger,
plotting one value per row, would never show it. Gamut plots **the
whole honest range**: the band is what actually happens, the tick is
the typical case, and a wide band reads as instability at a glance.
Use it when the deck's argument is about consistency (SLAs, spread,
worst-case exposure). If only the typical values matter, Bar Ledger.

## The chart contract (inherited refusals)

No gridlines, no y-axis. A single zero pole anchors the shared
scale; every band end and median is value-labeled directly, so no
legend is needed — the reading line defines the band (e.g. "p5–p95")
once. True proportions on one linear scale. Exactly one accent
element (the argued row's band, tick, and labels).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Same median, different weather           ← headline           │
│  RESPONSE MINUTES · P5–P95 BAND, MEDIAN TICK · ZERO AT POLE    │
│         │                                                      │
│  Jakarta│      4 ░░░░▌░░░░ 9        ← band + median tick       │
│  Bandung│        5 ░░░░▌░░░░░░ 11                              │
│ Surabaya│      4 ░░░▌░░░ 8                                     │
│    Medan│         6 ░░░▌░░░░░░░░░░░░░░░░░░ 21   ← accent       │
│         │                                                      │
│       0 MIN                                                    │
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
| Zero pole | vertical 1px at x:560, y:320 → 856; label centered under it at y:872 | pole label `--lp-font-mono` 15px | `--lp-line`; label `--lp-fg-muted` |
| Field | x:560 (= 0) → x:1760 (= scale max + ~10%), linear | — | — |
| Category rows (×4) | row centers at y:372, 500, 628, 756 (128px pitch) | — | — |
| Category labels | right-aligned to x:520, on row center | `--lp-font-display`, 28px, weight 700 | `--lp-fg`; accent row `--lp-accent` |
| Bands | from min to max value, 20px tall, centered on row center | — | `--lp-line` fill; accent row `--lp-accent` at 35% opacity |
| Median ticks | 6×36px, centered on the median value and row center | — | `--lp-fg`; accent row `--lp-accent` |
| Band-end values | mono 17px, 16px outside each band end, vertically centered | `--lp-font-mono` | `--lp-fg-muted`; accent row `--lp-accent` |
| Median values | mono 19px, centered 26px above the tick | `--lp-font-mono` | `--lp-fg`; accent row `--lp-accent` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **3–5 categories, one unit, one shared zero-poled scale.** With 3
  rows use 170px pitch; with 5, 105px.
- **The band definition is fixed and stated once** in the reading
  line (p5–p95, min–max, or IQR — pick one and hold it for every
  row). Mixing definitions across rows is fraud.
- **Three numbers per row, no more:** band-min, median, band-max.
  Means, p99s, and footnote statistics go in the source line or
  nowhere.
- **Accent row:** exactly one — the row whose SPREAD is the story
  (usually the widest band). Its band, tick, and all three labels
  take the accent.
- **Values:** ≤ 4 characters; unit lives in the reading line.
- **Sort rows** by a stated logic (magnitude of median, fixed site
  order) — never by how flattering the bands look.

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

Bands stretch open from their medians, total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — zero pole grows `scaleY(0→1)` origin top, 0.6s.
4. `0.50s` — rows open top to bottom, 0.16s apart: the median tick
   pops `scale(0→1)` (0.3s), then the band stretches from the tick
   outward (`scaleX(0→1)`, transform-origin at the median's position
   within the band, 0.6s), then the three value labels fade.
5. `1.35s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Bands** → the system's ink mixed toward the surface (or its
  faint texture) at ≤ 35% perceived contrast; may round ends ≤ 10px.
- **Median ticks** → the system's marker vocabulary (diamond, circle,
  3px rule), ≤ 36px tall.
- **Zero pole** → the system's axis-line treatment.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Whiskers, boxes, and outlier dots — the full box-plot costume
  needs a stats audience; a band and a tick need nobody's training.
- Bands without printed ends (unlabeled ranges read as decoration).
- Truncating the field to start above zero.
- Accenting the narrowest band to brag — Gamut argues about
  problems; bragging about consistency is a Bar Ledger of p95s.
- A second tick per row (mean AND median) — pick the honest one.
- Branding larger than 40px tall or anywhere but the reserved corner.
