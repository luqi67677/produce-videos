---
version: 1.0
name: Caliper
slot: chart
description: >
  Dumbbell chart for per-category change. Four category rows, each
  holding a horizontal span from an open "then" marker to a filled
  "now" marker on one shared, zero-poled scale; both endpoints carry
  their values directly. The row with the biggest movement is the one
  accent element. Change measured like a machinist would — jaw to jaw.
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

# Caliper — chart layout

## Intent

Crossover shows change by slope between two shared poles; Caliper
shows it **as distance closed (or opened) per category**. Each row is
one measurement: where the category stood, where it stands, and the
gap between — no time axis, no slope illusion, just the honest span.
Use it when 3–5 categories each have a then/now pair and the story is
"look how far each one moved." If all categories share the same two
dates and the crossing pattern matters, use Crossover.

## The chart contract (inherited refusals)

No gridlines. No y-axis. No floating legend — the first row's
endpoints are labeled with their period names directly. True
proportions on one shared scale with an explicit zero pole. Exactly
one accent element (the biggest mover's entire dumbbell).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Response time, then and now              ← headline           │
│  MEDIAN MINUTES, ALERT → ON SCENE         ← mono reading       │
│         │                2026   2024                           │
│  Jakarta│         6 ■━━━━━━━━━━━━□ 14                          │
│  Bandung│          7 ■━━━━━━━━━━━━━━━━□ 18                     │
│ Surabaya│         6 ■━━━━━━━━□ 11                              │
│    Medan│           9 ■━━━━━━━━━━━━━━━━━━━□ 22    ← accent     │
│         │                                                      │
│       0 MIN (zero pole)                                        │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / PERIOD                                   09 / 12     │
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
| Zero pole | vertical 1px line at x:560, y:320 → 856 | — | `--lp-line` |
| Zero pole label | x:560 centered, y:872 | `--lp-font-mono`, 15px, uppercase | `--lp-fg-muted` |
| Field | x:560 (=0) → x:1760 (=scale max), linear | — | — |
| Category rows (×4) | row centers at y:372, 500, 628, 756 (128px pitch) | — | — |
| Category labels | right-aligned to x:520, on row center | `--lp-font-display`, 28px, weight 700 | `--lp-fg`; accent row `--lp-accent` |
| Connectors | 3px horizontal bar between the two markers, on row center | — | `--lp-fg-muted`; accent row `--lp-accent` |
| "Then" markers | open 16×16px square (2px stroke, transparent fill) at the then-value | — | stroke `--lp-fg-muted`; accent row `--lp-accent` |
| "Now" markers | filled 16×16px square at the now-value | — | `--lp-fg`; accent row `--lp-accent` |
| Value labels | mono 19px, 12px outward of each marker (now-value on the inner/left side, then-value outer/right when values fall; mirrored when they rise) | `--lp-font-mono` | `--lp-fg`; accent row `--lp-accent` |
| Period tags | above the FIRST row's two markers only, 30px up | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **3–5 categories** (4 is the sweet spot; with 3 use 170px pitch,
  with 5 use 105px). Same unit across all rows, one shared scale.
- **The zero pole is real:** x:560 is 0 in data units and the scale
  runs linear to the max value with ~5% headroom. Never clip the
  field to "zoom the story."
- **Values:** ≤ 4 characters plus unit; the unit appears in the
  reading line, not per label.
- **Period tags** (e.g. "2024", "2026") label the first row's
  markers only — the marker shapes carry it for the rest.
- **Accent row:** exactly one — the biggest absolute mover, or the
  row the deck argues about. Its label, connector, both markers, and
  values all take the accent; everything else stays neutral.
- **Mixed directions are allowed** (some rows improving, some
  worsening) — that tension is a legitimate story; the marker fill
  (open=then, filled=now) keeps it readable.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

None — chart presets carry data, not imagery. The sole graphic
liberty is the design system's texture fingerprint OUTSIDE the field
(left of the zero pole), at ≤ `--lp-fg-faint`.

## Choreography

Measurement made visible, total ≤ 1.8s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — zero pole grows `scaleY(0→1)` origin top, 0.6s.
4. `0.50s` — rows measure themselves top to bottom, 0.18s apart:
   the "then" marker pops `scale(0→1)` (0.3s), the connector wipes
   from then toward now (`scaleX(0→1)`, origin at the then end,
   0.5s), the "now" marker pops as it lands, value labels fade 0.1s
   later. Category labels fade with their row.
5. `1.35s` — period tags + footer fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Markers** → the system's point vocabulary (circles, diamonds)
  keeping the open-vs-filled distinction and ≤ 18px size.
- **Connectors** → may thicken to 4px or take the system's dash; the
  accent row keeps a solid stroke.
- **Zero pole** → the system's axis-line treatment (doubled, dashed).
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **When remapping to color systems:** neutral rows take the system's
  ink mixed toward the surface; the accent row takes the one hot
  color. Never one hue per row.

## Failure modes to avoid

- Truncating the scale to start above zero — the pole IS the honesty.
- Arrowheads on connectors (the open/filled markers already encode
  direction); gradients or glows on the accent row.
- Sorting rows by "impressiveness" — sort by size of now-value,
  alphabetical, or a stated logic.
- A legend box. Period tags on the first row, once.
- Two accent rows, or accenting values but not their row.
- Branding larger than 40px tall or anywhere but the reserved corner.
