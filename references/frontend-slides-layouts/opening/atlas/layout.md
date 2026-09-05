---
version: 1.0
name: Atlas
slot: opening
description: >
  Map-plate opening. A faint coordinate grid covers the stage like a
  survey sheet, mono grid references hold the corners, and a small
  crosshair with a place tag marks the deck's subject in the upper
  field. The title anchors lower-left like a chart's legend block.
  For infrastructure, logistics, and territory decks — anything with
  a "where."
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

# Atlas — opening layout

## Intent

Decks about territory — rollouts, networks, coverage — usually open
with a literal map that's too busy to read and instantly wrong.
Atlas borrows the map's **instruments instead of its geography**:
the survey grid, the corner references, the crosshair. The audience
feels cartography without a single coastline, and the one marked
point says "this deck knows exactly where it's operating." The
empty gridded field doubles as breathing room the title never has
to fight.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│ 06°S ·······┆·········┆·········┆·········┆······· 106°E      │
│      ┆      ┆         ┆         ┆         ┆      ┆             │
│ ·····┆······┆·········┆······ ⊕ SECTOR 7 — JAKARTA UTARA       │
│      ┆      ┆         ┆      (crosshair + tag, accent)         │
│ ·····┆······┆·········┆·········┆·········┆·······             │
│      ┆      ┆         ┆         ┆         ┆      ┆             │
│  Coverage is a map            ← title block, lower-left        │
│  before it is a number                                         │
│                                                                │
│  Lead sentence, one or two lines.       [BRAND] ←──────────────┼─ optional
│ 6°12′S ································· PLATE 01 / 12         │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px** left/right
margins, **72px** top/bottom margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Survey grid | verticals every 240px from x:240, horizontals every 216px from y:216, full bleed, 1px | — | `--lp-fg-faint` |
| Corner references (×4) | 24px inside each stage corner (x:36/y:36 anchors), reading as grid coordinates | `--lp-font-mono`, 15px, letter-spacing 0.12em | `--lp-fg-muted` |
| Crosshair | centered at (1180, 330): two 56px hairline strokes crossing, 18px open ring at center | — | `--lp-accent` |
| Crosshair tag | 20px right of the crosshair, single line | `--lp-font-mono`, 17px, uppercase, letter-spacing 0.14em | `--lp-accent` |
| Title | x:96, baseline of last line ≈ y:760, max-width 1250px, ≤ 2 lines | `--lp-font-display`, 124px, weight 800, line-height 1.0, letter-spacing −0.02em | `--lp-fg` |
| Lead | x:96, 36px under the title, max-width 780px, ≤ 2 lines | `--lp-font-body`, 25px, line-height 1.5 | `--lp-fg-muted` |
| Branding slot (optional) | right-aligned to x:1824, y:880, ≤ 40px tall, ≤ 260px wide | wordmark in `--lp-font-display` 700 or an image logo | `--lp-fg` |
| Plate line (bottom-left) | x:96, y:956 (clear of the corner references) | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Plate counter (bottom-right) | right-aligned to x:1824, y:956 | same | `--lp-fg-muted` |

No chrome hairline and no boxed footer — the grid IS the chrome,
and the plate line sits directly on the field like a map margin.

## Content constraints (hard limits)

- **Corner references:** plausible survey notation for the deck's
  actual territory (real coordinates rounded, or honest zone names
  like "GRID N-4"). Random numbers read as random to anyone who
  knows the place.
- **One crosshair.** It marks the deck's operational subject (the
  city, the site, the corridor) and its tag names it, ≤ 30
  characters. A second marker turns the opening into a data slide.
- **Title:** ≤ 2 lines, ≤ 14 characters per line at 124px; wrap each
  line in its own span. Territorial voice welcome; puns about maps
  not required.
- **Lead:** ≤ 130 characters, ≤ 2 lines. Optional.
- **Plate line:** "PLATE 01 / 12"-style — the counter wears the
  map's costume.

## Branding / logo slot (optional)

The lower-right field (right-aligned to x:1824, y:880) is the
reserved **optional** branding slot — kept off the gridded upper
field so the mark never competes with the crosshair:

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

**With aerial imagery:** the grid may overlay a full-bleed muted
aerial photograph (opacity ≤ 20%, under the grid, over `--lp-bg`),
turning the survey sheet into a plate. Text zones stay identical;
the image must stay quiet enough that the title needs no scrim.

**Recommended size / placeholder:** `https://placehold.co/1920x1080`.
**Dimension fallback:** full-bleed frame, `object-fit: cover`, token
CSS fill behind. Optional — the bare grid is the default and reads
cleaner.

## Choreography

The sheet is surveyed, then titled — total ≤ 1.6s:

1. `0.00s` — the grid fades in as one plane, 0.8s.
2. `0.20s` — corner references fade, 0.5s, 0.06s stagger.
3. `0.45s` — the crosshair draws (strokes wipe from center, ring
   pops) with its tag fading 0.15s later, 0.5s.
4. `0.70s` — title lines rise `translateY(48px→0)` + fade, 0.7s,
   0.12s stagger.
5. `1.05s` — lead fades up, 0.5s.
6. `1.20s` — branding + plate lines fade, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Grid** → the system's texture fingerprint at the same faintness
  (dots at intersections, dashed rules); pitch may match the
  system's own grid module.
- **Crosshair** → the system's marker vocabulary (registration
  mark, target ring) ≤ 72px, accent ink.
- **Corner references** → the system's caps/label face.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; dark systems make this a night
  chart — grid at low-opacity light ink.

## Failure modes to avoid

- An actual detailed map (roads, boundaries) behind the grid — the
  abstraction IS the design; geography invites fact-checking.
- Grid strong enough to fight the title (stay ≤ `--lp-fg-faint`).
- Multiple crosshairs, route lines, or region shading — that's a
  data slide; the opening marks ONE subject.
- Corner references in display type or accent color (they are
  furniture, not content).
- Centering the title. The legend block belongs lower-left.
- Branding on the upper gridded field or larger than 40px tall.
