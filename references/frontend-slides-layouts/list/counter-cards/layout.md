---
version: 1.0
name: Counter Cards
slot: list
description: >
  Asymmetric list for exactly 4 items. A headline column holds the left
  third; the right two-thirds is a 2×2 grid of hairline-bordered cards,
  each led by an oversized index numeral. Flat, ruled, and rhythmic —
  cards without card-chrome clichés.
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

# Counter Cards — list layout

## Intent

The counterpart to Ledger List for when items deserve equal visual
weight rather than a reading order. The headline column gives the slide
a stable anchor and a place for framing prose, while the four cards get
identical real estate — no hierarchy games. Elegance rules: 1px borders
instead of shadows, numerals instead of icons, and generous padding so
each card reads as a small composed page.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER               ┌──────────────┐ ┌──────────────┐        │
│                       │ 01           │ │ 02           │        │
│  WHAT                 │ Card title   │ │ Card title   │        │
│  CHANGES              │ Body text …  │ │ Body text …  │        │
│  NOW                  └──────────────┘ └──────────────┘        │
│                       ┌──────────────┐ ┌──────────────┐        │
│  Framing lead,        │ 03           │ │ 04           │        │
│  muted, 3 lines.      │ Card title   │ │ Card title   │        │
│                       │ Body text …  │ │ Body text …  │        │
│                       └──────────────┘ └──────────────┘        │
└────────────────────────────────────────────────────────────────┘
     x:96→640                x:736→1824
```

## Geometry

All values are stage pixels at 1920×1080.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker | x:96, y:120 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Headline | x:96, top y:170, max-width 544px | `--lp-font-display`, 96px, weight 700–800, line-height 1.0, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Framing lead | x:96, 40px below headline, max-width 460px | `--lp-font-body`, 21px, line-height 1.6 | `--lp-fg-muted` |
| Card grid | x:736 → 1824, y:120 → 960; 2×2, 24px gap | — | — |
| Card | 1px border, no fill, no radius, no shadow; padding 44px | — | border `--lp-line` |
| Card numeral | top of card | `--lp-font-display`, 64px, weight 800, line-height 1 | `--lp-accent` |
| Card title | 28px below numeral | `--lp-font-display`, 34px, weight 700, line-height 1.15 | `--lp-fg` |
| Card body | 16px below title | `--lp-font-body`, 19px, line-height 1.55 | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 4 items.** Three items → Ledger List or a wider 1×3 variant
  of your own; five → split the slide. The 2×2 symmetry is the layout.
- **Card title:** 1–2 lines, ≤ 40 characters.
- **Card body:** 2–4 lines, ≤ 190 characters. Keep the four bodies
  within one line of each other in length — even card "weight" is what
  makes the grid elegant.
- **Headline:** 1–3 short lines, ≤ 12 characters uppercase per line at
  96px (max-width 544px).
- **Framing lead:** 2–4 lines, ≤ 180 characters. Optional.

## Image variant

**With images:** each card gains a 100×100 image chip in its top-right
corner (44px from the card's top and right edges), the numeral staying
top-left — numeral and chip share the card's header zone. All four
cards get chips or none. Chips are content (product shots, site
photos), never decorative icons.

**Recommended size / placeholder:** `https://placehold.co/200x200`
(2× for sharpness at 100px). **Dimension fallback:** fixed 100×100
frames, `object-cover`, token CSS fill behind each `<img>`.
Chips are optional — numeral-only cards are the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.4s:

1. `0.00s` — kicker fades in, 0.5s.
2. `0.10s` — headline rises: `translateY(40px→0)` + fade, 0.7s.
3. `0.45s` — framing lead fades up, 0.6s.
4. `0.40s` — cards enter in reading order (01→04):
   `translateY(32px→0)` + fade, 0.6s, 0.12s stagger; each card's
   numeral fades in 0.15s after its card.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Card border** → the system's edge vocabulary (thicker top rule only,
  corner ticks, dashed) — flat always; shadows and fills are off-limits
  unless the system is explicitly card-based, in which case its card
  surface may be used at the same geometry.
- **Card numeral** → the system's figure style or a small glyph/icon
  slot ≤ 64px, in `--lp-accent`.
- **Grid gap** → may open to 32px if the system's rhythm is airier;
  never below 16px.
- **One card may be emphasized** (inverted fill or accent border) when
  the content genuinely leads with one item — at most one.

## Failure modes to avoid

- Shadowed, rounded, or filled cards by default — that is the generic
  dashboard look this preset exists to avoid.
- Uneven card content: one card with 5 lines while another has 1 breaks
  the grid's calm.
- Icons in place of numerals "for visual interest" — the numeral column
  is the visual interest.
- Squeezing the headline column below 500px to give cards more room —
  shorten card copy instead.
