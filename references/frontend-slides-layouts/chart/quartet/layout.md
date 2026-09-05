---
version: 1.0
name: Quartet
slot: chart
description: >
  Small multiples: four mini area charts in a 2×2 grid, every panel on
  the SAME y-scale and time span, each with its own baseline, name,
  and endpoint value. One panel — the story's protagonist — renders
  its silhouette in accent. For series that would tangle into
  spaghetti if overlaid.
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

# Quartet — chart layout

## Intent

Four trend lines on one chart cross, tangle, and force a legend.
Quartet gives **each series its own small stage with identical
rules** — same scale, same span, same geometry — so shapes compare
honestly panel to panel while every line stays readable. The eye does
what legends can't: pattern-matches four silhouettes at once. Use it
for 4 comparable series over the same period; for one series use
Tideline, for exactly-two-moment comparisons use Crossover.

## The chart contract (inherited refusals)

No gridlines. No y-axes — each panel prints its endpoint value, and
the reading line states the shared scale covenant. No legend — every
panel is named directly. True proportions: all four panels share one
y-scale from a real zero baseline (each panel's bottom hairline).
Exactly one accent element (the protagonist panel's silhouette +
endpoint).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Four cities, one scale                   ← headline           │
│  WEEKLY CONFIRMED ALERTS · SAME Y-SCALE EVERY PANEL            │
│                                                                │
│  Jakarta        740 │  Bandung          690                    │
│      ▄▄▄▀▀▀▀        │      ▄▄▄▄▀▀▀                             │
│  ▄▀▀▀▀▀▀▀▀▀▀▀       │  ▀▀▀▀▀▀▀▀▀▀▀                             │
│  ─────────────      │  ─────────────      ← baselines          │
│                     │                                          │
│  Surabaya       610 │  Medan            940  ← accent panel    │
│  ▀▄▄▄▄▄▀▀▀▀         │        ▄▄▄▀▀█                            │
│  ▀▀▀▀▀▀▀▀▀▀▀        │  ▄▄▀▀▀▀▀▀▀▀▀                             │
│  ─────────────      │  ─────────────                           │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / SPAN                                     07 / 12     │
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
| Panels (×4) | 816×250 at (96,330), (1008,330), (96,630), (1008,630); 96px column gutter, 50px row gutter | — | — |
| Panel names | panel top-left, single line | `--lp-font-display`, 26px, weight 700 | `--lp-fg`; accent panel `--lp-accent` |
| Endpoint values | panel top-right, aligned with the name | `--lp-font-mono`, 22px | `--lp-fg`; accent panel `--lp-accent` |
| Chart areas | y:+64 → y:+234 inside each panel (170px tall), full 816px width | area silhouette via straight segments (honest polyline, no smoothing) | neutral panels `--lp-fg-faint` fill; accent panel `--lp-accent` fill |
| Baselines | each panel's bottom edge (y:+234), full width, 1px — this is 0 | — | `--lp-line` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source/span) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 4 series.** Three leaves a hole in the grid (use a 3×1
  row variant: panels 528×420 at x:96/672/1248 — only when all three
  matter equally); five means dropping the least important.
- **One shared y-scale, stated in the reading line.** The tallest
  panel's peak sets the scale for all four; a panel may look "empty"
  — that emptiness is information.
- **Same time span** in every panel, 8–36 points each, straight
  segments only.
- **Endpoint values:** ≤ 5 characters; the unit lives in the reading
  line. The endpoint is the ONLY number per panel.
- **Panel names:** ≤ 14 characters.
- **Accent panel:** exactly one — the series the deck argues about
  (fastest riser, the anomaly). All other silhouettes stay faint.

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

The four stages rise together, total ≤ 1.6s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — panel names, endpoint values, and baselines fade in,
   0.5s, 0.1s stagger in reading order.
4. `0.50s` — silhouettes grow `scaleY(0→1)` from their baselines
   (`transform-origin: bottom`), 0.8s, 0.12s stagger in reading
   order — the accent panel last, landing the beat.
5. `1.30s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Neutral silhouettes** → the system's ink mixed toward the
  surface at ≤ 20% perceived contrast; may gain a 1–2px top stroke
  in the same ink.
- **Accent silhouette** → the system's one hot color, solid or with
  its sanctioned fill treatment.
- **Baselines** → the system's axis-line treatment.
- **Endpoint values** → may gain the system's endpoint dot (≤ 12px)
  at the series' last point, same ink as the silhouette.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Per-panel y-scales ("to show detail") — the single scale IS the
  chart; rescaling any panel is the lie this layout exists to avoid.
- Overlaying a comparison line inside any panel.
- Smoothed/bezier silhouettes — straight segments between honest
  points.
- More than one number per panel (start values, peaks, deltas — the
  shapes carry those).
- Ranking panels by size or giving the accent panel more area.
- Branding larger than 40px tall or anywhere but the reserved corner.
