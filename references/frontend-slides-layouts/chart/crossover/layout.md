---
version: 1.0
name: Crossover
slot: chart
description: >
  Two moments, every mover. A slope chart strings 3–5 series between
  a "then" pole and a "now" pole; the accent line is the one that
  crossed the field, and both of its endpoints carry numbers. The
  steepness IS the story — no axis, no grid, just slopes.
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

# Crossover — chart layout

## Intent

"X overtook Y" is a two-point story; a full time series buries it in
wobble. The slope chart strips change to its geometry: two vertical
hairline poles, one line per series, labels at both ends doing the
axis's job. Rank at a glance on each pole, change as steepness in
between — and when the accent line crosses another, the crossing
point is the slide's whole argument. A left text column narrates
while the chart stays uncluttered.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       12 / 18  │
│                          │                    │                │
│  HEADLINE     Vision API · 44% ●──────╲       │                │
│  (3 lines,               │             ╲──────● 31%            │
│   left col)              │        ╱────────── ● 38% +16 pts    │
│                Edge suite · 22% ●╱  ← accent  │                │
│  reading       Console · 19% ●────────────────● 17%            │
│  (muted)     Services · 15% ●──────────────────● 14%           │
│                          │                    │                │
│                        FY24                  FY26              │
│  SOURCE / PERIOD                                     BRAND     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px, uppercase, ls 0.18em / 0.12em | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:150, w:380, ≤ 3 lines | `--lp-font-display`, 56px, weight 800, lh 1.05, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Reading block | x:96, top y:430, w:360, 3–6 lines | `--lp-font-body`, 18px, lh 1.55 | `--lp-fg-muted` |
| Poles | vertical 1px hairlines at x:760 and x:1560, y:280 → 900 | — | `--lp-line` |
| Pole captions | centered under each pole, y:916 | mono 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Slopes | straight lines pole to pole; **y positions from ONE shared linear scale** (map the value range into y:300–880 with headroom) | — | accent series `--lp-accent` 4px; others `--lp-fg-muted` at 60%, 2.5px |
| Endpoint dots | 12px on each pole (accent series 16px) | — | match their line |
| Left labels | right-aligned ending x:736, one per series, vertically centered on its start dot: `Name · value` | body 20px; value in mono | `--lp-fg` (name), `--lp-fg` (value); accent series fully `--lp-accent` |
| Right labels | left-aligned from x:1584, centered on end dots: value only; accent series adds a delta line under its value | mono 24px / accent: mono 30px weight 500 + delta mono 14px | `--lp-fg`; accent series `--lp-accent` |
| Footer hairline + source | x:96 → 1824, y:962 / y:984 | mono 14px, uppercase, ls 0.12em | `--lp-line` / `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly two time points.** A middle moment matters → Skyline or
  Tideline instead.
- **3–5 series, one unit,** all on the same linear scale — a slope
  chart with per-series scales is a lie with hairlines.
- **Exactly one accent series** — the mover the headline is about.
  Only the accent series gets a delta; others get end values only.
- **Labels are the axis:** every series is value-labeled at both
  ends. Names ≤ 14 chars; values ≤ 5 glyphs.
- **Label collisions:** minimum 26px between label centers on a
  pole; if two collide, nudge each ≤ 10px vertically (dots stay at
  true positions) — if that can't resolve it, drop to 4 series.
- Slope direction must be visually honest: the scale includes both
  ends of every series with ≥ 6% headroom, never clipped.

## Image variant

**With image:** the reading block may be replaced by a 360×240 image
plate (x:96, top y:430, hairline border in `--lp-line`).
**Recommended size / placeholder:** `https://placehold.co/720x480`
(2× for sharpness). **Dimension fallback:** fixed 360×240 frame,
`object-cover`. **Load fallback:** token CSS fill behind the `<img>`.
Without either, the headline may grow to 64px / 4 lines.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.30s` — poles draw downward (`scaleY 0→1`, origin top), 0.6s;
   captions fade at `0.5s`.
3. `0.60s` — left labels and start dots fade in top-to-bottom,
   0.08s stagger.
4. `0.90s` — non-accent lines draw left→right
   (`pathLength`-normalized dash), 0.7s each, 0.1s stagger; each end
   dot and right label pops as its line lands.
5. `1.50s` — the accent line draws last and slowest (0.9s); its end
   dot, value, and delta pop at `2.30s` — the crossing is the finale.
6. `2.50s` — reading block and footer fade, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
all slopes render immediately.

## Skin points

- **Lines** → the system's stroke vocabulary; non-accent lines may
  take its secondary line style (fine dashes allowed if the system
  uses them), the accent line always solid.
- **Poles** → the system's hairline/divider treatment.
- **Dots** → the system's marker glyph (square, tick) at the same
  sizes.
- Monochrome systems: accent series = full `--lp-fg` at 4px against
  others at 30%.

## Failure modes to avoid

- More than two poles — that's a line chart pretending to be simple.
- Per-series scales or a clipped range that manufactures drama.
- Deltas on every series; one delta, on the accent, is the argument.
- Left labels drifting from their dots — the label centerline must
  sit on the dot (± the documented 10px collision nudge).
- Arrowheads, gradients along the line, or curved "slopes".
