---
version: 1.0
name: Index Ledger
slot: section
description: >
  The deck's table of contents as the divider. Every part appears as a
  display-scale row; the current one sits at full contrast with an
  accent numeral and bar, the others recede to a whisper. The audience
  sees the whole book each time a chapter turns.
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

# Index Ledger — section layout

## Intent

Chapter Gate lights one stop, Waypoint draws the map — Index Ledger
reprints the whole contents page and highlights the line we've reached.
The repetition is the pleasure: the same slide returns at every
divider with the highlight one row lower, so the deck's progress is
felt as a page slowly being read. Best for decks of 4–6 named parts
whose titles are worth re-reading.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  PART THREE                                           06 / 14  │
│                                                                │
│  01  Inertia            ← 16% opacity                          │
│  02  Depth              ← 16%                                  │
│ ▮03  Execution          ← full contrast + accent bar & numeral │
│  04  Proof              ← 16%                                  │
│  05  Next               ← 16%                                  │
│                                                                │
│  One-line framing sentence, muted.                             │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Index rows | x:160, first row top y:220, row pitch 136px; each row: mono numeral (width 120px) + display title inline | numeral: `--lp-font-mono`, 26px, ls 0.1em; title: `--lp-font-display`, 96px, weight 700–800, line-height 1, ls −0.02em | current row: numeral `--lp-accent`, title `--lp-fg`; other rows: both at `--lp-fg` 16% opacity |
| Current-row bar | x:96, 12×96px, vertically centered on the current row | — | `--lp-accent` |
| Framing line | x:160, 64px below the last row, max-width 800px | `--lp-font-body`, 22px, line-height 1.5 | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Rows:** 4–6, the deck's actual parts in order, exactly one
  current. Three parts → Waypoint; seven+ → Chapter Gate's rail.
- **Row titles:** 1 line, ≤ 16 characters at 96px. Part names, not
  sentences.
- **Framing line:** 1 line ≤ 90 characters. Optional.
- Rows + framing must end above y:980; with 6 rows drop the row pitch
  to 124px and the title size to 88px.

## Image variant

**With an image:** a 480×640 image plate (1px `--lp-line` border)
occupies the right field at x:1344 → 1824, y:220, with a mono caption
beneath — the chapter's key visual; row titles then cap at 14
characters so no row approaches the plate. **Recommended size /
placeholder:** `https://placehold.co/480x640`. **Dimension fallback:**
fixed frame, `object-cover`, token CSS fill behind the `<img>`.
The image is optional.

## Choreography

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.15s` — rows fade in top-to-bottom *at their resting opacity*,
   0.45s each, 0.1s stagger (dim rows arrive dim — they never flash
   to full).
3. `0.70s` — the current row rises `translateY(20px→0)` to full
   contrast, 0.6s; its accent bar wipes `scaleY(0→1)` at `0.95s`.
4. `1.10s` — framing line fades up, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Current-row bar** → the system's marker (arrow glyph, index hand,
  its bullet) at the same anchor, ≤ 48px wide.
- **Dim rows** → systems with an outline vocabulary may render
  non-current rows as outline text at `--lp-fg-faint` instead of
  low opacity.
- **Numerals** → the system's figure style.

## Failure modes to avoid

- Editing row titles between dividers — the whole point is the exact
  reprint with the highlight moved.
- More than one row at full contrast, or dim rows above ~25% opacity
  (the contrast gap is the highlight).
- Turning rows into links/blurbs. This is a contents page, not a menu
  of summaries.
