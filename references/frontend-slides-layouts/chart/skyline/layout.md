---
version: 1.0
name: Skyline
slot: chart
description: >
  Time made visible. Six to ten vertical columns march chronologically
  across the lower stage in true proportion, the latest (or pivotal)
  column in accent — a city skyline of quarters where growth is read
  as height, with no axis and no gridlines to slow the eye.
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

# Skyline — chart layout

## Intent

When the story is "how far we've come", a table of quarters makes the
audience do the plotting. A column row does it for them: chronology
runs left to right, magnitude is height, and the accent column is the
sentence's subject. Like Bar Ledger, it stays elegant by refusing
chart chrome — no y-axis, no gridlines, no legend. Two selectively
placed value labels (the first column and the accent column) are the
only numbers; they bracket the journey and make every other column
readable by interpolation.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       07 / 18  │
│  HEADLINE WITH ONE EM                     reading block        │
│                                           (2–4 muted lines)    │
│   34M                                              128M ←accent│
│    █                                          █    ██          │
│    █     █     █     █      █      █     █    ██   ██          │
│    █     █     █     █      █      █     ██   ██   ██          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ← baseline          │
│  Q3'24  Q4'24  Q1'25  Q2'25  Q3'25  Q4'25  Q1'26  Q2'26        │
│  SOURCE / PERIOD                                     BRAND     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px, uppercase, ls 0.18em / 0.12em | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line, ≤ 34 chars | `--lp-font-display`, 76px, weight 800, lh 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Reading block | right x:1824, w:360, top y:128, 2–4 lines | `--lp-font-body`, 18px, lh 1.55 | `--lp-fg-muted` |
| Plot region | x:96 → 1824, top y:340, baseline y:920 (580px tall) | — | — |
| · columns | width 120px, distributed `justify-between`; **height = value ÷ max × 580, true proportion, zero baseline, no minimums** | — | accent column `--lp-accent`; others `--lp-fg-muted` at 45% |
| · value labels | centered above column top, gap 12px; **first column and accent column only** | mono 18px muted / mono 24px weight 500 accent | see left |
| Baseline | x:96 → 1824, y:920, 2px | — | `--lp-line` |
| Period labels | one per column, centered under it, y:938 | mono 13px, uppercase, ls 0.08em | `--lp-fg-muted` |
| Source / Brand | x:96 / right x:1824, y:1008 | mono 14px, uppercase, ls 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **6–10 columns,** one unit, one series, strictly chronological —
  never sorted by value. Fewer than 6 periods → Bar Ledger (stats)
  or Ratio Split; more than 10 → aggregate periods.
- **Proportions are sacred:** heights computed from real values
  against the same maximum, from a zero baseline. No truncated axes,
  no minimum heights — a flat early years is the story's setup.
- **Exactly one accent column** — usually the latest, always the one
  the talk track lands on. Its value label is mandatory; the first
  column's label is mandatory; **no other columns carry numbers.**
- **Period labels ≤ 7 chars** (`Q3 '24`, `2019`, `MAR`). **Values
  ≤ 6 glyphs with unit.**
- One series only. Two series → two Skylines on consecutive slides,
  or Crossover if the story is the gap.

## Image variant

**With image:** the reading block may be replaced by a 360×200 image
plate (top y:128, hairline border in `--lp-line`).
**Recommended size / placeholder:** `https://placehold.co/720x400`
(2× for sharpness). **Dimension fallback:** fixed 360×200 frame,
`object-cover`. **Load fallback:** token CSS fill (faint gradient in
`--lp-fg-faint`) behind the `<img>`. Without image or reading, the
headline may take a second line instead.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.30s` — baseline draws left→right via `scaleX(0→1)`, 0.6s.
3. `0.45s` — columns grow from the baseline via `scaleY(0→1)`
   (origin bottom), 0.6s each, 0.08s stagger left→right; each
   column's period label fades with it.
4. The accent column lands last (+0.2s after its slot) and its value
   label pops with it; the first column's label fades at `0.5s`.
5. `1.60s` — reading block and source line fade, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
columns render at full height immediately.

## Skin points

- **Columns** → the system's fill vocabulary (solid, or its pattern
  at high density); square tops unless the system rounds everything
  (then ≤ 4px, top corners only, anchored to the baseline).
- **Baseline** → the system's rule weight; may become its signature
  divider.
- **Muted columns** → when remapping, derive from ONE ink (mix
  `--lp-fg-muted` toward `--lp-bg`), never a second hue — identity
  here is time, not category, so color must not suggest categories.

## Failure modes to avoid

- Any distortion of proportion — truncated baselines flatter growth
  and the audience can tell.
- A y-axis, gridlines, or a number on every column; two labels
  bracket the range, the shape does the rest.
- Sorting columns by value — chronology is the x-axis's one job.
- Rainbow or per-column hues; only the accent column separates.
