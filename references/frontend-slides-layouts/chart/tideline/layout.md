---
version: 1.0
name: Tideline
slot: chart
description: >
  One trend as landscape. A single-series area chart rises across the
  full stage width like a tide against the bottom of the slide, drawn
  with honest straight segments, its endpoint capped by an accent dot
  and the only big number on the slide.
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

# Tideline — chart layout

## Intent

A trend told in numbers ("we went from 2,180 to 9,640") asks the
audience to imagine the shape; Tideline shows the shape and labels
only its two ends. The area runs from the left bleed to the right
margin, filled faint under a firm line — a horizon the headline
stands above. Straight point-to-point segments keep the wobble
honest: the dips are real, and surviving them is part of the story.
The accent endpoint dot carries the destination value; everything
else is atmosphere.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       09 / 18  │
│  HEADLINE WITH ONE EM                     reading block        │
│                                           (2–4 muted lines)    │
│                                                    9,640 ← em  │
│                                                  ●             │
│                                          ┌──────╱              │
│  2,180 · start label        ┌────╲──────╱                      │
│  ─────────┌──────╲───┌─────╱      ╲────╱   ← faint fill        │
│ ╱━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ← baseline      │
│    DEC '24      JUN '25      DEC '25          MAY '26          │
│  SOURCE / PERIOD                                     BRAND     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px, uppercase, ls 0.18em / 0.12em | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line, ≤ 34 chars | `--lp-font-display`, 76px, weight 800, lh 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Reading block | right x:1824, w:360, top y:128, 2–4 lines | `--lp-font-body`, 18px, lh 1.55 | `--lp-fg-muted` |
| Plot region | SVG x:0 → 1920, top y:440, baseline y:960 (520px tall); **data starts at x:0 (left bleed) and ends at x:1824** | — | — |
| · line | 3px stroke, straight point-to-point segments, 12–36 points | — | `--lp-fg` |
| · fill | area under the line, closed to the baseline | — | `--lp-fg-faint` |
| · endpoint | 14px dot on the final point; value above-right of it, right-aligned to x:1824, date line under the value | display 44px weight 800 / mono 13px | `--lp-accent` / `--lp-fg-muted` |
| · start label | x:96, ~28px above the area's left edge, one line | mono 15px, ls 0.04em | `--lp-fg-muted` |
| Baseline | x:0 → 1920 (full bleed), y:960, 1px | — | `--lp-line` |
| Time ticks | 3–5 under the baseline, y:978, at true data x-positions; the endpoint's date line stands in for the final tick (never duplicate it) | mono 13px, uppercase, ls 0.08em | `--lp-fg-muted` |
| Source / Brand | x:96 / right x:1824, y:1020 | mono 14px, uppercase, ls 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **One series.** Two trends → Crossover (if two points carry it) or
  two Tidelines on consecutive slides; never two areas stacked on
  one another here.
- **Zero baseline, always.** y:960 is zero; heights are value ÷
  y-max × 520 with y-max chosen just above the peak (peak lands in
  the top ~10% of the plot). No truncated ranges.
- **Straight segments only** — never smoothed splines; interpolation
  invents data. 12–36 real points; fewer than 12 → Skyline.
- **Two values on the whole slide:** the start label and the endpoint
  value. Intermediate peaks stay unlabeled — the shape is the point.
- **3–5 time ticks** at true positions. No y-axis, no gridlines.
- Trend must be genuinely monotonic-ish; if the line ends below where
  it started, say so in the headline — the chart may not spin.

## Image variant

**With image:** the slide may run over a full-bleed backdrop
photograph (`absolute inset-0`, `object-cover`) under a scrim that
deepens toward the bottom so the fill and baseline stay legible;
tokens then map to the design system's on-image roles.
**Recommended size / placeholder:** `https://placehold.co/1920x1080`.
**Dimension fallback:** full-stage frame, `object-cover`. **Load
fallback:** the plain `--lp-bg` slide IS the no-image variant —
first-class, not a degradation.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.30s` — baseline fades in, 0.5s.
3. `0.45s` — the line draws left→right over 1.4s
   (`pathLength`-normalized `stroke-dashoffset 1→0`); the fill fades
   in beneath it from `0.9s`, 0.8s.
4. `1.70s` — endpoint dot pops (scale 0→1) and the endpoint value
   rises with it; start label and time ticks fade at `1.2s`.
5. `2.00s` — reading block and source line fade, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
the full area renders immediately.

## Skin points

- **Fill** → the system's quiet surface treatment: flat faint ink by
  default; may become the system's texture (halftone, grid) clipped
  to the area, or a vertical fade of the accent at ≤ 12% opacity.
- **Line** → the system's rule weight (2–4px); terminal dot may
  become the system's marker glyph.
- **Baseline** → may adopt the system's signature divider.

## Failure modes to avoid

- Smoothing the line — bezier "beautification" is data invention.
- A truncated y-range that exaggerates the climb.
- Labeling every peak and dip; two numbers bracket the story.
- Gridlines or a y-axis — the endpoint value is the axis.
- A second series sharing the plot; ambiguity kills the landscape.
