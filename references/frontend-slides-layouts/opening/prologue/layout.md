---
version: 1.0
name: Prologue
slot: opening
description: >
  Epigraph-led opening. A short italic quotation sits centered in the
  upper field with a mono attribution, separated from the title block
  by a small centered rule — book front-matter grammar. The title
  anchors lower-left at display scale. For narrative and mission
  decks that earn a literary register.
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

# Prologue — opening layout

## Intent

Books open with someone else's words because borrowed gravity is
real: an epigraph tells the reader what tradition the work claims.
Prologue gives a deck that move — **quotation first, title second** —
and the pairing does the framing before slide two exists. The
epigraph may be a real external quotation (cited honestly) or the
deck's own thesis dressed as one (attributed to the team). Use it
for mission decks, annual letters, and keynotes; never for a rate
review.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · SERIES                         [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│         A city that can see itself                             │
│         can govern itself.            ← epigraph, italic       │
│                                                                │
│         — GOV. INFRASTRUCTURE REVIEW, 2024  ← attribution      │
│                                                                │
│                        ───                                     │
│                                                                │
│  The seeing city             ← title, lower-left               │
│  Annual letter, 2026         ← subtitle                        │
│  ─────────────────────────────────────────────────────────     │
│  PRESENTER — ROLE                                  01 / 12     │
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
| Epigraph | centered on x:960, block starting y:236, max-width 1100px, ≤ 3 lines | `--lp-font-display`, 46px, weight 400, italic, line-height 1.35, centered | `--lp-fg` |
| Attribution | centered, 36px under the epigraph | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.16em, prefixed with an em dash | `--lp-fg-muted` |
| Divider | centered 80×2px rule, y:560 | — | `--lp-accent` |
| Title | x:96, top y:660, max-width 1400px, ≤ 2 lines | `--lp-font-display`, 104px, weight 800, line-height 1.0, letter-spacing −0.02em | `--lp-fg` |
| Subtitle | x:96, 28px under the title, single line | `--lp-font-body`, 26px | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (presenter) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Epigraph:** ≤ 120 characters, ≤ 3 lines, set italic without
  quotation marks (the register carries it). It must EARN the
  gravity — a platitude in italics is a platitude in italics.
- **Attribution:** ≤ 50 characters, honest. Real quotes cite their
  real source and year; self-authored epigraphs attribute to the
  team or the document ("— THE 2026 LETTER"), never to an invented
  sage.
- **Title:** ≤ 2 lines, ≤ 18 characters per line at 104px, distinct
  in voice from the epigraph (the epigraph sings, the title names).
- **Subtitle:** ≤ 60 characters, single line. Optional.
- **The centered upper field / left-anchored lower field contrast
  is the composition** — the epigraph floats, the title stands.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

None by default — front matter is typographic. The tolerated
substitution: the divider may become a small emblem or press mark
≤ 96×96px (the design system's seal), placeholder
`https://placehold.co/192x192` rendered 96×96, `object-fit: contain`.

## Choreography

The quotation is read before the book is named — total ≤ 1.6s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.15s` — epigraph fades in as one block (it is read, not
   watched), 0.9s.
3. `0.55s` — attribution fades, 0.5s.
4. `0.75s` — divider wipes `scaleX(0→1)` from center, 0.4s.
5. `0.90s` — title lines rise `translateY(40px→0)` + fade, 0.7s,
   0.12s stagger; subtitle trails 0.15s.
6. `1.25s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Epigraph face** → serif systems set it in their text italic —
  this layout is where a serif system earns its keep.
- **Divider** → the system's ornament vocabulary (fleuron, seal,
  short doubled rule), ≤ 96px wide, accent ink.
- **Attribution** → the system's caps/label face.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; a paper tint suits the register.

## Failure modes to avoid

- An epigraph longer than the title is tall — three lines is the
  ceiling; the quotation is a doorway, not a hall.
- Quotation marks plus italics plus an accent color — pick the
  italics and stop.
- Fake attributions ("— ANCIENT PROVERB"). The credibility spent
  there never comes back.
- Centering the title too (all-centered reads as a certificate).
- Epigraph and title in the same voice — if they interchange, cut
  one.
- Branding larger than 40px tall or anywhere but the reserved corner.
