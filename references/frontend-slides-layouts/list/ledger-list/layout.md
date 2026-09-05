---
version: 1.0
name: Ledger List
slot: list
description: >
  Editorial index for 3–5 list items. A kicker-and-headline block sits
  top-left; below it, each item is a full-width hairline row — accent
  numeral, item title, and a right-hand description column — like the
  contents page of a well-set journal. Elegance through alignment, not
  decoration.
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

# Ledger List — list layout

## Intent

Bullet slides fail when every item floats in a card or hangs off a dot.
Ledger List treats the list as a **table of contents**: ruled rows, a
numeral gutter, titles in display type, and descriptions quietly
right-set in their own column. The eye scans down the numeral column,
across each rule — the structure does the guiding, so no boxes, icons,
or bullets are needed.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       07 / 14  │
│  WHAT SHIPS NEXT           ← headline                          │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  01   Edge inference          Description text sits in its     │
│                               own right-hand column, 2 lines.  │
│  ──────────────────────────────────────────────────────────    │
│  02   Unified console         Description …                    │
│  ──────────────────────────────────────────────────────────    │
│  03   Latency budgets         Description …                    │
│  ──────────────────────────────────────────────────────────    │
│  04   Partner APIs            Description …                    │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px**
left/right margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned to x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Headline | x:96, top y:118, max-width 1200px | `--lp-font-display`, 84px, weight 700–800, line-height 1.02, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Rows block | x:96 → 1824, first rule at y:360 | — | — |
| Row rule | full content width, 1px, above each row | — | `--lp-line` |
| Row grid | columns: numeral 120px / title 1fr / description 640px; vertical padding 34px top & bottom | — | — |
| Row numeral | left column, top-aligned with title | `--lp-font-mono`, 20px, weight 500, letter-spacing 0.1em | `--lp-accent` |
| Row title | middle column | `--lp-font-display`, 44px, weight 700, line-height 1.1 | `--lp-fg` |
| Row description | right column, 640px | `--lp-font-body`, 20px, line-height 1.55 | `--lp-fg-muted` |

Row height derives from content: with 2-line descriptions a row runs
≈ 130px, so 4 rows ≈ 520px (y:360 → 880), leaving breathing room below.
The block must end above y:1000.

## Content constraints (hard limits)

- **Items:** 3–5. Two items is a comparison (different slot); six
  overflows — split into two slides.
- **Row title:** 1 line, ≤ 32 characters. Titles are noun phrases, not
  sentences.
- **Row description:** 1–2 lines, ≤ 130 characters. All rows should have
  descriptions or none — mixing ruins the column rhythm.
- **Headline:** 1 line, ≤ 30 characters at 84px.
- **Numbering:** zero-padded ("01"), sequential. If the items are
  unordered in spirit, keep the numerals anyway — they are wayfinding,
  not ranking.

## Image variant

**With images:** each row gains a 96×96 thumbnail column between the
numeral and the title — the row grid becomes
`120px / 120px / 1fr / 640px` (numeral / thumb / title / description),
thumbs vertically centered per row, 1px `--lp-line` border. All rows
get thumbs or none — a gap in the thumb column breaks the ledger.

**Recommended size / placeholder:** `https://placehold.co/192x192`
(2× for sharpness at 96px). **Dimension fallback:** fixed 96×96
frames, `object-cover`, token CSS fill behind each `<img>`.
Thumbnails are optional — the type-only ledger is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.10s` — headline rises: `translateY(36px→0)` + fade, 0.7s.
3. `0.40s` — rows enter top-to-bottom: each row's rule wipes via
   `scaleX(0→1)` (origin left, 0.5s) while its content fades up
   `translateY(24px→0)` (0.55s), 0.12s stagger between rows.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Row rules** → the system's divider vocabulary (dashed, doubled,
  colored) at the same positions.
- **Numerals** → the system's figure style (serif figures, outlined,
  inside a small tag/pill ≤ 56px wide), in `--lp-accent`.
- **Row hover/build** → in presenter decks, rows may build one-by-one on
  key-press using the same rise animation.
- **Background** → flat or quiet texture; the ruled rows need visual
  silence around them.

## Failure modes to avoid

- Wrapping row titles to two lines — shorten the title instead; the
  single-line title column is the design.
- Boxing the rows into cards or zebra-striping them. Rules only.
- Letting descriptions exceed two lines or differ wildly in length —
  ragged rhythm reads as neglect.
- Centering anything. The three-column left-set grid is the layout.
