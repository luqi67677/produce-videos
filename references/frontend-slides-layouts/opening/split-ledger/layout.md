---
version: 1.0
name: Split Ledger
slot: opening
description: >
  Hard vertical split. The left ~37% is an inverted full-height panel
  carrying the deck's metadata; the right field holds the title and lead.
  A giant numeral straddles the seam, stitching the two surfaces together.
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

# Split Ledger — opening layout

## Intent

A two-surface opening: the inverted panel gives the deck an immediate
sense of structure (metadata lives *there*, content lives *here*), and the
numeral breaking across the seam is the one flamboyant move that makes the
split read as designed rather than divided. Asymmetric like Offset
Marquee, but the energy is architectural instead of editorial.

## Region map (1920×1080 stage)

```
┌──────────────────────┬─────────────────────────────────────────┐
│ inverted panel       │                                         │
│  KICKER · LABEL   ▓0▓1                                         │
│                   ▓▓▓│▓▓   ← numeral straddles the seam        │
│                      │                                         │
│                      │   SIGNAL                                │
│                      │   OVER                                  │
│                      │   NOISE        ← title, right field     │
│                      │                                         │
│                      │   Lead sentence, max-width 560px.       │
│  EVENT               │                                         │
│  DATE                │   ─────────────────────────────────     │
│  ORG                 │                                 01 / 12 │
└──────────────────────┴─────────────────────────────────────────┘
        x:0→720                      x:816→1824
```

## Geometry

All values are stage pixels at 1920×1080.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Panel | x:0 → 720, full height, solid fill | — | fill `--lp-fg`, text `--lp-bg` (inverted region) |
| Panel kicker | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Panel meta stack | x:96, bottom-anchored at y:1008, one item per line, line-height 2.2 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-bg` at 70% opacity |
| Seam numeral | horizontally centered on x:720, top y:96, font-size 300px, line-height 1 | `--lp-font-display`, weight 800 | `--lp-accent` |
| Title | x:816, top y:380 for a 3-line title / y:450 for 2 lines, max-width 1000px; title + lead must end above y:930 | `--lp-font-display`, 136–150px (default 150), weight 700–800, line-height 0.95, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Lead | x:816, 36px below title, max-width 560px | `--lp-font-body`, 22px, line-height 1.55 | `--lp-fg-muted` |
| Footer hairline | x:816 → 1824, y:962, 1px | — | `--lp-line` |
| Counter | right-aligned to x:1824, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 2–3 lines in a 1000px column — roughly **8–9 characters
  uppercase** or **10–11 mixed case** per line at 150px. Short punchy
  fragments only; wrap each line in its own span. Step down to 136px at
  most before rewriting the title instead.
- **Lead:** 1–3 lines, ≤ 130 characters. Optional.
- **Panel meta stack:** 2–4 single-line items (event, date, org,
  version). The stack is bottom-anchored; it must not climb past y:700.
- **Seam numeral:** 2 characters ("01"). It must visibly cross the seam —
  centered on x:720 — and may be the deck monogram instead.

## Image variant

**With an image:** the inverted panel becomes an image panel — the
image fills the 720×1080 panel (`object-cover`) under a scrim
strong enough for the panel's kicker and meta stack to stay legible
(top and bottom gradients of the panel surface color at ~75%). The
seam numeral stays astride the seam.

**Recommended size / placeholder:** `https://placehold.co/720x1080`.
**Dimension fallback:** fixed 720×1080 frame, `object-cover`,
the solid inverted surface behind the `<img>` doubles as the load
fallback. The image is optional — the solid panel is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.4s:

1. `0.00s` — panel wipes in via `transform: scaleX(0→1)`,
   `transform-origin: left`, 0.6s.
2. `0.30s` — seam numeral drops in: `translateY(-40px→0)` + fade, 0.7s.
3. `0.45s` — title lines rise: `translateY(48px→0)` + fade, 0.7s,
   0.12s stagger per line.
4. `0.85s` — lead fades up, 0.6s.
5. `1.00s` — panel kicker, panel meta, footer hairline, counter fade
   in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Panel fill** → dual-surface design systems map the panel to their
  alternate surface (e.g., navy panel on cream field) instead of a raw
  bg/fg swap; single-surface systems keep the inversion. Panel text
  colors follow the chosen surface.
- **Seam numeral** → the system's display treatment (outline, stamp,
  monogram); it stays on `--lp-accent` or the panel's accent equivalent,
  and it stays astride the seam.
- **Footer hairline** → the system's divider vocabulary.
- **Panel texture** → the system's atmospheric treatment may fill the
  panel (gradient, grain, pattern) as long as panel text stays legible.

## Failure modes to avoid

- Moving the seam. 720px (37.5%) is the composition; a 50/50 split reads
  as a template, not a design.
- Putting the title on the panel or metadata in the right field — the
  surface-role separation is the layout.
- Shrinking the numeral so it fits inside one surface. If it doesn't
  cross the seam, delete it rather than shrink it.
- Long title lines in the narrow right column — rewrite, don't reflow.
