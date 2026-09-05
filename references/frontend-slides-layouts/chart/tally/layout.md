---
version: 1.0
name: Tally
slot: chart
description: >
  Waffle chart for one proportion made countable. A 10×10 grid of
  unit squares on the right — the share filled in accent, in reading
  order, the remainder faint — with the percentage at display scale
  and its plain-language reading on the left. One number, one hundred
  squares, no second series.
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

# Tally — chart layout

## Intent

Percentages abstract; squares count. Aperture shows how a whole
divides among several parts; Tally shows **one share of one whole so
concretely the audience could tally it by hand** — 37 filled squares
out of a hundred is a fact the eye verifies on the spot. Use it when
a single proportion is the slide's entire argument and its size
should feel physical ("37 of every 100 cameras"). Two proportions
need two slides or an Aperture.

## The chart contract (inherited refusals)

No gridlines beyond the squares themselves. No axes. No legend —
the reading line says what one square is. True proportion by count:
filled squares = round(share × 100), and the printed percentage
matches that count exactly. Exactly one accent element (the filled
squares and their number are one unit).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  The v4 model, one year in                ← headline           │
│  EACH SQUARE IS ONE CAMERA IN A HUNDRED   ← mono reading       │
│                                                                │
│   37%                          ▪▪▪▪▪▪▪▪▪▪                      │
│   ← 200px, accent              ▪▪▪▪▪▪▪▪▪▪                      │
│                                ▪▪▪▪▪▪▪▪▪▪                      │
│   of federation cameras        ▪▪▪▪▪▪▪□□□  ← fill stops        │
│   run v4 detection today       □□□□□□□□□□     mid-row          │
│                                □□□□□□□□□□                      │
│   MONO FOOTNOTE                □□□□□□□□□□  (10×10, reading     │
│                                □□□□□□□□□□   order fill)        │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / DATE                                     08 / 12     │
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
| Headline | x:96, y:164, max-width 1100px, 1 line | `--lp-font-display`, 60px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Reading line | x:96, y:242, single line | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` |
| Percentage | x:96, top ≈ y:380 | `--lp-font-display`, 200px, weight 800, letter-spacing −0.03em | `--lp-accent` |
| Reading sentence | x:96, 32px under the figure, max-width 620px, ≤ 3 lines | `--lp-font-body`, 30px, line-height 1.4 | `--lp-fg` |
| Footnote | x:96, y:856 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Waffle grid | x:1220 → 1728, y:330 → 838; 10×10 cells of 40px with 12px gaps (508px square) | — | filled `--lp-accent`, unfilled `--lp-fg-faint` |
| Fill order | reading order: top-left, row by row | — | — |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **One proportion only.** No second color, no stacked shares, no
  "last year" ghost fill. Comparing two shares is Ratio Split's or
  Aperture's job.
- **Count = percentage:** filled squares are exactly
  round(share × 100), and the display figure is that integer with a
  % sign. A share below 1% or above 99% makes the grid silly — use
  Denominator instead.
- **Percentage:** ≤ 4 characters including the sign.
- **Reading sentence:** ≤ 90 characters, ≤ 3 lines. It must name the
  whole ("of federation cameras…") — a share without its whole is
  decoration.
- **Reading line** states the unit-square meaning ("each square is
  one camera in a hundred").

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

The tally counts itself, total ≤ 1.8s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — the grid's unfilled squares fade in as rows, top to
   bottom, 0.06s per row (the empty frame arrives first).
4. `0.70s` — filled squares sweep in, in reading order, by row:
   each filled row fades+scales in (`scale(0.6→1)`), 0.08s per row
   — the count visibly accumulates.
5. `1.10s` — the percentage rises `translateY(32px→0)` + fade, 0.7s
   (the number lands after its squares justify it).
6. `1.30s` — reading sentence + footnote fade, 0.5s.
7. `1.40s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Squares** → the system's cell vocabulary: rounded ≤ 8px, circles,
  or its pictogram unit if it has one — same 10×10 metric grid.
- **Unfilled cells** → the system's faint texture or outline cells;
  must stay ≤ `--lp-fg-faint` contrast.
- **Percentage** → the system's display numerals; stays the same ink
  as the filled cells (they are one accent unit).
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Two shares in one grid, or a legend explaining fill colors — one
  proportion, one ink, no legend.
- A fill count that disagrees with the printed percentage (the
  audience counts — that's the point).
- Icon-of-the-week pictograms (people, cameras) unless the design
  system owns a unit pictogram — novelty units cheapen the count.
- Scattering the fill decoratively instead of reading order.
- Shrinking the grid below 40px cells to make room for prose — cut
  prose instead.
- Branding larger than 40px tall or anywhere but the reserved corner.
