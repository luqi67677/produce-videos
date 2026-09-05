---
version: 1.0
name: Tiers
slot: pricing
description: >
  Three open pricing columns under an editorial header. Each column:
  mono tier name, display-scale price with cadence note, a hairline,
  then a short feature ledger. The recommended tier is marked by a
  thick accent bar above its column and an accent tier name — no
  boxes, no buttons, no "most popular" ribbons.
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

# Tiers — pricing layout

## Intent

Pricing slides usually import SaaS-website grammar — cards, shadows,
CTA buttons — which reads as advertising inside a presentation. Tiers
keeps the pack's ledger voice: **three priced columns, stated flatly,
like a rate card**. The price is the display moment; everything else
is quiet. One tier may be recommended (accent bar + name), and the
speaker argues the recommendation — the slide only marks it.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Three ways to start                      ← headline           │
│                                                                │
│              ▮▮▮▮▮▮▮▮▮▮ ← accent bar (recommended)             │
│  PILOT           METRO             NATIONAL                    │
│  $1,900          $6,400            Custom                      │
│  PER MONTH       PER MONTH         ANNUAL CONTRACT             │
│  ───────         ───────           ───────                     │
│  120 streams     1,000 streams     Unlimited streams           │
│  One site        Five sites        Unlimited sites             │
│  Email support   24/7 desk         Dedicated team              │
│  Monthly models  Weekly models     Custom models               │
│  ─────────────────────────────────────────────────────────     │
│  TERMS / NOTE                                      11 / 12     │
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
| Columns (×3) | x:96, 672, 1248; each 480px wide, 96px gutters | — | — |
| Accent bar (recommended tier only) | full column width × 8px at y:312 | — | `--lp-accent` |
| Tier names | y:348 | `--lp-font-mono`, 17px, uppercase, letter-spacing 0.18em | `--lp-fg-muted`; recommended `--lp-accent` |
| Prices | y:392 | `--lp-font-display`, 96px, weight 800, letter-spacing −0.02em | `--lp-fg` |
| Cadence notes | 12px under the price | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Column hairlines | full column width, y:576, 1px | — | `--lp-line` |
| Feature ledgers | from y:608, 4 lines, 46px pitch | `--lp-font-body`, 22px, line-height 1 | `--lp-fg`; the differentiating word may be weight 700 |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (terms) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 tiers.** Two tiers is a Ledger Versus / Fulcrum decision;
  four is a website, not a slide.
- **Prices:** ≤ 8 characters ("$1,900", "Rp 95M", "Custom"). Real
  figures or an honest "Custom" — never "Contact us!" marketing copy.
  All three at the same y; if one tier is "Custom", it still sits at
  price scale.
- **Cadence notes:** ≤ 22 characters ("PER MONTH", "ANNUAL CONTRACT").
- **Features:** exactly 4 lines per column, ≤ 26 characters each,
  row-aligned across columns so equivalent features share a line.
  Parallel phrasing ("120 streams / 1,000 streams / Unlimited
  streams"), never checkmark lists.
- **Recommended tier:** at most one, marked ONLY by the accent bar and
  accent name. No size changes, no "popular" labels.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

This layout takes no imagery — prices are the picture. If the deck
needs a product visual beside pricing, split the story across two
slides (Plate Caption, then Tiers). The only sanctioned graphic
addition is the design system's texture fingerprint behind the
header band at ≤ `--lp-fg-faint` contrast.

## Choreography

Staggered entrance on slide activation, total ≤ 1.6s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline rises `translateY(32px→0)` + fade, 0.6s.
3. `0.30s` — accent bar wipes `scaleX(0→1)` origin left, 0.5s.
4. `0.35s` — tier names fade, 0.4s, 0.1s stagger left → right.
5. `0.45s` — prices rise `translateY(40px→0)` + fade, 0.7s, 0.12s
   stagger left → right; cadence notes trail each by 0.1s.
6. `0.80s` — column hairlines wipe `scaleX(0→1)` origin left, 0.5s,
   0.1s stagger.
7. `0.95s` — feature lines fade up, 0.4s each, 0.06s stagger within
   a column, columns offset 0.1s.
8. `1.30s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Accent bar** → the system's signature marker (rule, tab, stamp)
  at the same position, footprint ≤ 480×24px.
- **Column hairlines** → the system's divider vocabulary.
- **Tier names** → outlined chips if the system frames labels; chip
  footprint ≤ 200×36px.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Currency styling** → the currency symbol may drop to 50% size and
  superscript if the system's numerals suit it; the figure stays 96px.

## Failure modes to avoid

- Card borders, background fills, or shadows around tiers — the open
  columns ARE the design.
- CTA buttons ("Get started"). Decks are spoken; the ask lives in the
  closing slide.
- Feature lists of uneven length or non-parallel phrasing across
  columns.
- Strikethrough "was" prices, percent-off badges, or urgency copy.
- More than one accent tier, or accenting via size instead of the bar.
- Branding larger than 40px tall or anywhere but the reserved corner.
