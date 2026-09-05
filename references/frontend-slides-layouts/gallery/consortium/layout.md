---
version: 1.0
name: Consortium
slot: gallery
description: >
  Logo wall as a ruled specimen sheet. Under an editorial header, a
  4×2 grid of partner/customer marks divided by interior hairlines —
  every logo the same maximum footprint, monochrome, centered in its
  cell. A mono footnote row admits how many are not shown. No logo
  soup, no size hierarchy.
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

# Consortium — gallery layout

## Intent

Logo slides fail by crowding: forty marks at postage-stamp size prove
volume but read as noise. Consortium shows **exactly eight, ruled like
a type specimen** — the grid's discipline transfers to the brands and
back. Eight is enough to prove adoption; the footnote carries the rest
of the count honestly. Use it for customers, partners, or member
institutions; never mix categories on one wall.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Twelve cities run on it                  ← headline           │
│                                                                │
│     [logo]     │    [logo]     │    [logo]     │    [logo]     │
│  ──────────────┼───────────────┼───────────────┼────────────   │
│     [logo]     │    [logo]     │    [logo]     │    [logo]     │
│                                                                │
│  AND 14 MORE ACROSS 6 PROVINCES        ← footnote row          │
│  ─────────────────────────────────────────────────────────     │
│  BASIS / DATE                                      06 / 12     │
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
| Headline | x:96, y:164, max-width 1400px, 1 line | `--lp-font-display`, 64px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Grid | x:96 → 1824, y:300 → 776; 4 columns × 2 rows, cells 432×238 | — | — |
| Interior hairlines | 3 vertical (x:528, 960, 1392, y:300→776), 1 horizontal (y:538, x:96→1824), 1px; no outer border | — | `--lp-line` |
| Logo slots (×8) | centered in each cell, max 240×96 | image `object-fit: contain` | rendered monochrome |
| Footnote row | x:96, y:836, single line | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.14em | `--lp-fg-muted`; the count may be `--lp-accent` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (basis) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 8 marks.** With only 6, run 3×2 (cells 576×238, verticals
  at x:672, 1248). Fewer than 6 marks means each deserves naming —
  use Ledger List with org names instead. More than 8 goes in the
  footnote, period.
- **One category per wall** (all customers, or all partners — the
  kicker names which). Mixing reads as padding.
- **Monochrome only:** every mark rendered in `--lp-fg` tones (CSS
  `filter: grayscale(1)` at minimum; true one-color versions
  preferred). One full-color logo breaks the sheet.
- **Equal footprint:** every mark fits the same 240×96 box, centered.
  No "anchor client" enlargement — the footnote can name the flagship.
- **Footnote:** ≤ 60 characters, honest arithmetic ("AND 14 MORE…").
  Drop it only if the wall IS the complete set — silence implies
  completeness.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot for the PRESENTING org's mark (the wall
below belongs to the partners, never to the presenter):

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image slots

**Recommended size / placeholder:** `https://placehold.co/240x96` per
mark (or 480×192 supplied at 2×). **Dimension fallback:** each mark
renders inside a fixed 240×96 box with `object-fit: contain`, so any
delivered logo proportions center without stretching. **Load
fallback:** the cell shows nothing but the grid — an empty cell reads
as designed space, so no CSS fill is required behind logo slots.

Every mark is optional/substitutable: a partner without a usable logo
file takes a text wordmark in `--lp-font-display` weight 700 at 28px,
centered in the same box (2–3 text cells among image cells is fine —
specimen sheets mix).

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline rises `translateY(32px→0)` + fade, 0.6s.
3. `0.30s` — interior hairlines wipe in (verticals `scaleY(0→1)`
   origin top, horizontal `scaleX(0→1)` origin left), 0.6s together.
4. `0.50s` — marks fade in cell by cell in reading order, 0.4s each,
   0.08s stagger.
5. `1.15s` — footnote + footer fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Interior hairlines** → the system's divider vocabulary; may
  become surface-gap gutters (12px, like Triptych) in borderless
  systems.
- **Mark treatment** → the system's image filter (duotone toward
  `--lp-fg`) applied uniformly.
- **Footnote count** → the system's emphasis move on the numeral.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg` only; texture behind logos muddies
  small marks.

## Failure modes to avoid

- Nine-plus marks, shrunken cells, or a third row — the footnote
  exists so the wall doesn't have to prove volume.
- Full-color logos, or one mark at "hero" size.
- Captions under each mark (name, city, contract value) — that's a
  table; use Ledger List.
- Borders around the outer grid edge (the sheet bleeds into the
  slide's whitespace by design).
- The presenter's own logo inside the wall.
- Branding larger than 40px tall or anywhere but the reserved corner.
