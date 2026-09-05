---
version: 1.0
name: Split Curtain
slot: closing
description: >
  Horizontal split closing. The statement sits in the open upper field;
  an inverted full-width band rises across the bottom like a curtain,
  carrying three contact columns. A short accent bar stitches the seam.
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

# Split Curtain — closing layout

## Intent

The curtain metaphor made literal: the deck ends when the inverted band
comes up over the bottom of the stage. The band does double duty — it is
the strongest possible "we're done" signal and the natural home for
practical exits (contacts), separated from the emotional statement above
it by a hard surface change instead of mere whitespace.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  BEFORE YOU GO                                        12 / 12  │
│                                                                │
│  BUILD IT                                                      │
│  WITH US.               ← statement, upper field               │
│                                                                │
│  One-line sub, muted.                                          │
│  ▮▮▮▮▮▮  ← accent stitch overlapping the seam                  │
├────────────────────────────────────────────────────────────────┤ y:680
│ inverted band (curtain)                                        │
│  EMAIL            │  DOCS              │  CHANNEL              │
│  CONTACT          │  example.com/road  │  #platform-roadmap    │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:96 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned to x:1824, y:96 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Statement | x:96, top y:230, max-width 1500px | `--lp-font-display`, 152–176px (default 168), weight 700–800, line-height 0.95, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Sub line | x:96, 32px below statement, max-width 720px | `--lp-font-body`, 24px, line-height 1.5 | `--lp-fg-muted` |
| Band (curtain) | x:0 → 1920, y:680 → 1080 (400px tall), solid fill | — | fill `--lp-fg`, text `--lp-bg` (inverted region) |
| Accent stitch | x:96, y:676, 160×8px — overlaps the seam, above both surfaces | — | `--lp-accent` |
| Contact grid | x:96 → 1824 inside band, top edge y:820; 3 equal columns; 1px vertical hairlines between; columns 2–3 padded 48px left | labels: `--lp-font-mono` 13px uppercase ls 0.16em; values: `--lp-font-body` 24px | labels `--lp-bg` at 60% opacity, values `--lp-bg`; hairlines `--lp-bg` at 25% opacity |

## Content constraints (hard limits)

- **Statement:** 1–2 lines, ≤ 15 characters per line at 168px (uppercase
  ≈ 12). At most one `<em>` phrase. Statement + sub must end above y:640.
- **Sub line:** 1 line, ≤ 90 characters. Optional.
- **Contact grid:** exactly 3 cells, single-line values, identifiers only.
  Natural fills: email / docs-or-repo / channel-or-handle. If only 2 real
  items exist, the third holds the org or deck title.
- **Kicker / counter:** one line each, real chrome only.

## Image variant

**With an image:** a 584×504 image plate (1px `--lp-line` border)
sits in the upper field at x:1240 → 1824, y:96 → 600; the statement's
max-width tightens to 1000px. The band and stitch are unchanged — the
photo rides above the curtain.

**Recommended size / placeholder:** `https://placehold.co/584x504`.
**Dimension fallback:** fixed 584×504 frame, `object-cover`,
token CSS fill behind the `<img>`. The image is optional.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.10s` — statement lines rise: `translateY(56px→0)` + fade, 0.7s,
   0.12s stagger.
3. `0.50s` — sub line fades up, 0.6s.
4. `0.45s` — band rises: `translateY(80px→0)` + fade, 0.8s.
5. `0.70s` — accent stitch wipes via `scaleX(0→1)`, origin left, 0.5s.
6. `0.85s` — contact cells rise with 0.1s stagger per column, 0.6s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Band fill** → dual-surface systems map the band to their alternate
  surface instead of a raw bg/fg swap; the band may also carry the
  system's atmospheric texture if contact text stays legible.
- **Accent stitch** → the system's marker device (tag, stamp, doubled
  rule ≤ 12px tall) — it must visibly overlap the seam at the left
  margin.
- **Contact hairlines** → the system's divider style at band-appropriate
  contrast; the tri-column rhythm is structural.
- **`<em>` treatment** → the system's emphasis move, colored `--lp-accent`.

## Failure modes to avoid

- Moving the seam above y:620 or below y:760 — the band must read as a
  band, not a half-slide or a footer.
- Putting the statement on the band or a paragraph in the upper field.
  Emotional register above the seam, practical register below it.
- Dropping the stitch — without it the two surfaces read as unrelated
  slides stacked together.
- Adding a fourth contact cell or wrapping values to two lines.
