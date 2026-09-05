---
version: 1.0
name: Horizon
slot: opening
description: >
  A single full-width rule crosses the stage at y:560 — the horizon —
  and the title stands directly on it like a skyline. Above the line:
  air and a kicker. Below it: lead left, event meta right. With an
  image, everything above the horizon becomes sky.
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

# Horizon — opening layout

## Intent

One line, drawn all the way across, changes a blank stage into a
landscape. The title's baseline sits exactly on that line, so the type
reads as built on the ground rather than floating — an architectural
opening with almost nothing on it. The accent segment over the rule at
the left margin is the sunrise: the single warm point.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       01 / 12  │
│                                                                │
│                        (open sky)                              │
│                                                                │
│  ON SOLID GROUND                ← title standing on the line   │
│ ▮▮▮▮▮───────────────────────────────────────────────────────── │ ← horizon y:560
│  Lead sentence sits below                    EVENT NAME        │
│  the line, max-width 640px.                  08 JUL 2026       │
│                                              JAKARTA           │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Horizon rule | x:0 → 1920 (full bleed), y:560, 1px | — | `--lp-line` |
| Accent segment | x:96, y:557, 240×7px — overlays the rule | — | `--lp-accent` |
| Title | x:96, bottom edge flush to y:552 (8px above the rule), max-width 1728px, 1–2 lines | `--lp-font-display`, 128–150px (default 140), weight 700–800, line-height 0.95, letter-spacing −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Lead | x:96, y:608, max-width 640px | `--lp-font-body`, 23px, line-height 1.55 | `--lp-fg-muted` |
| Meta block | right-aligned x:1824, y:608, one item per line, line-height 2 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 1 line strongly preferred (≤ 18 characters uppercase at
  140px), 2 lines maximum. With 2 lines only the last line touches the
  horizon.
- **Lead:** 1–3 lines, ≤ 150 characters.
- **Meta block:** 2–4 single-line items (event, date, city, org).
- Below-line content ends above y:860 — the lower field keeps at least
  200px of ground.

## Image variant

**With an image:** the region above the horizon (y:0 → 560) becomes a
full-bleed image band. A bottom-up scrim (linear gradient from
`--lp-bg` at 95% to transparent over the band's lower 220px) keeps the
title legible where it stands on the line. Kicker and counter sit on
the image — give them a scrim chip if the crop is busy. Landscape
crops only; this is literally the horizon.

**Without an image:** flat `--lp-bg` sky, as specified above.

**Recommended size / placeholder:** `https://placehold.co/1920x560`.
**Dimension fallback:** the band is a fixed 1920×560 frame with
`object-cover`; keep a token CSS fill behind the `<img>` so a
failed load degrades to the no-image sky. The image is optional.

## Choreography

1. `0.00s` — horizon rule wipes full width via `scaleX(0→1)`, origin
   left, 0.9s; accent segment follows at `0.45s`, 0.5s.
2. `0.30s` — title rises from below the line: `translateY(56px→0)` +
   fade, 0.8s (with an image band, it rises out of the scrim).
3. `0.75s` — lead fades up; meta block fades in, 0.6s.
4. `0.95s` — kicker and counter fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Accent segment** → the system's marker (thicker stub, tag, dot
  cluster) overlapping the rule at the left margin, ≤ 280×16px.
- **Horizon rule** → the system's strongest hairline treatment; it must
  stay full-bleed edge to edge.
- **Sky** → the system's atmospheric gradient may fill the above-line
  region even without an image, fading to quiet before the rule.

## Failure modes to avoid

- Floating the title above the line — the baseline contact IS the
  concept. Zero to 12px gap, no more.
- Putting content in the sky other than kicker/counter (or the image).
- A second rule anywhere. One horizon.
