---
version: 1.0
name: Rule Columns
slot: list
description: >
  Three open columns for exactly three items, each opened by a short
  accent tick and a mono numeral — no borders, no cards, just three
  parallel reading paths under one headline. The columnar sibling of
  Stat Strip.
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

# Rule Columns — list layout

## Intent

Counter Cards boxes four items; Rule Columns un-boxes three. Each
column is opened by the smallest possible chrome — a 48×4 accent tick
and a numeral — and then runs as free text, so the slide reads as
three short essays sharing a stage rather than a widget row. The
natural home for triads: three pillars, three phases, three teams.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       08 / 14  │
│  HOW WE RUN IT            ← headline                           │
│                                                                │
│  ▮▮▮▮            ▮▮▮▮            ▮▮▮▮        ← accent ticks    │
│  01              02              03          ← mono numerals   │
│                                                                │
│  Plan weekly     Ship daily      Audit always                  │
│  Body text in    Body text …     Body text …                   │
│  its own column                                                │
│  of 4–6 lines.                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line, max-width 1200px | `--lp-font-display`, 84px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Columns | 3 equal, x:96 → 1824, 96px gaps (columns ≈ 512px), top y:380 | — | — |
| · accent tick | 48×4px | — | `--lp-accent` |
| · numeral | 20px below tick | `--lp-font-mono`, 18px, weight 500, ls 0.12em | `--lp-fg-muted` |
| · column title | 28px below numeral | `--lp-font-display`, 36px, weight 700, line-height 1.15 | `--lp-fg` |
| · column body | 18px below title | `--lp-font-body`, 19px, line-height 1.6 | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 columns.** Four → Counter Cards; two → Ledger Versus.
- **Column titles:** 1–2 lines ≤ 24 characters. **Bodies:** 3–6 lines
  ≤ 260 characters, within one line of each other across columns.
- **No vertical dividers, borders, or fills** — the gap is the
  divider; adding lines turns this into a table.

## Image variant

**With images:** each column opens with a 512×200 image band directly
above its accent tick (y:380, content shifting down 232px; bodies then
cap at 4 lines). All three columns get bands or none. **Recommended
size / placeholder:** `https://placehold.co/512x200`. **Dimension
fallback:** fixed letterbox frames, `object-cover`, token CSS
fill behind each `<img>`. Bands are optional.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.40s` — columns enter left-to-right, 0.15s stagger: tick wipes
   `scaleX(0→1)` 0.4s → numeral fades → title and body fade up
   `translateY(24px→0)` 0.55s at `+0.15s`.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Accent tick** → the system's marker device (its rule, a glyph,
  a tag) ≤ 80×24px; identical across columns.
- **Numerals** → the system's label treatment; may be dropped entirely
  when the triad has no order.
- **Column rhythm** → gaps may open to 120px in airy systems.

## Failure modes to avoid

- Unequal column lengths — the ragged bottom is fine, a one-line
  column beside a six-line column is not.
- Boxes, tints, or vertical hairlines between columns.
- Center-aligning column content; each column is left-set prose.
