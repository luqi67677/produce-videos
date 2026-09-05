---
version: 1.0
name: Staircase
slot: list
description: >
  Sequence made spatial. Three or four items descend the stage in
  steps — each one lower and further right than the last — so the eye
  walks the list instead of scanning it. For lists where order IS the
  meaning: phases, escalations, funnels.
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

# Staircase — list layout

## Intent

Every other list preset arranges items in a stack or a row; Staircase
uses position itself as the connector. Step N+1 begins below and to
the right of step N, so progression reads without a single arrow. The
diagonal also solves the boring-slide problem for 3–4 short items —
the composition is dynamic while every element stays austere.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       09 / 14  │
│  ROLLOUT, IN ORDER          ← headline                         │
│                                                                │
│  01 Pilot site                                                 │
│     Description …                                              │
│           02 Corridor of five                                  │
│              Description …                                     │
│                     03 Regional fleet                          │
│                        Description …                          │
│                              04 Everything else                │
│                                 Description …                  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line | `--lp-font-display`, 84px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Steps | step N (1-based) at x:96 + (N−1)×220, y:340 + (N−1)×160 | — | — |
| · step numeral | inline before title, 24px gap | `--lp-font-mono`, 20px, weight 500, ls 0.1em | `--lp-accent` |
| · step title | | `--lp-font-display`, 40px, weight 700, line-height 1.1 | `--lp-fg` |
| · step description | 10px below title, indented to the title's x, max-width 560px | `--lp-font-body`, 19px, line-height 1.5 | `--lp-fg-muted` |
| Step riser (optional) | 1px vertical hairline, 56px tall, from each step's numeral down toward the next step's row | — | `--lp-line` |

## Content constraints (hard limits)

- **3–4 steps,** strictly ordered — if the items could be shuffled
  without loss, use Ledger List; the staircase asserts sequence.
- **Titles:** 1 line ≤ 24 characters. **Descriptions:** 1–2 lines
  ≤ 110 characters.
- With 4 steps the last begins at x:756 / y:820 — its description must
  stay ≤ 1 line to clear the bottom margin.
- The upper-right triangle stays empty; it is the staircase's sky.

## Image variant

**With images:** each step carries a 200×112 thumbnail left of its
numeral (its right edge 24px before the numeral; step 1's thumb is
therefore off-grid at x:96 and the steps shift right by 224px, so cap
at 3 steps). All steps get thumbs or none. **Recommended size /
placeholder:** `https://placehold.co/400x224` (2× for sharpness at
200×112). **Dimension fallback:** fixed frames, `object-cover`,
token CSS fill behind each `<img>`. Thumbnails are optional.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.40s` — steps descend in order, 0.18s stagger: each fades up
   `translateY(28px→0)` 0.55s, its riser drawing `scaleY(0→1)`
   0.3s after it lands.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Step numerals** → the system's label/tag treatment.
- **Risers** → the system's hairline style, or omitted entirely in
  very airy systems — the offsets alone carry the sequence.
- **Final step** → may take the accent on its numeral *and* title
  when the last step is the destination (funnel endings).

## Failure modes to avoid

- Equalizing the offsets into a grid "for neatness" — the diagonal is
  the information.
- Arrows or chevrons between steps; position already says it.
- Long descriptions that make lower steps collide with the right
  margin — the staircase narrows as it descends; write accordingly.
