---
version: 1.0
name: Poster Stack
slot: opening
description: >
  The title as the entire slide. The deck title breaks into four stacked
  rows of display type — solid, outline, solid, accent — filling the
  stage like a gig poster. Chrome hides in the margins. With an image,
  one outline row becomes a letterbox image band: a picture used as a
  word.
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

# Poster Stack — opening layout

## Intent

For decks that can carry personality: no field, no lead, no hierarchy
except texture. Four rows of the same enormous size, differentiated only
by rendering — solid, outline, solid, accent — turn the title into a
pattern. The eye reads the texture first and the words second, which is
exactly the poster effect.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                    08 JUL 2026 │
│  STATE                       ← solid                           │
│  OF THE                      ← outline (or image band)         │
│  PLATFORM                    ← solid                           │
│  2026                        ← accent solid                    │
│  ──────────────────────────────────────────────────────────    │
│  PRESENTER — ORG                                      01 / 12  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:64 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Top meta (top-right) | right-aligned x:1824, y:64 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Stack | x:96, rows from y:150 to ≈ y:900; 4 rows, font-size 170px, line-height 1.09 (row pitch ≈ 185px) | `--lp-font-display`, weight 800, letter-spacing −0.02em, uppercase | row pattern top→bottom: 1 solid `--lp-fg` · 2 outline (2px text-stroke `--lp-fg` at ~55%, transparent fill) · 3 solid `--lp-fg` · 4 solid `--lp-accent` |
| Footer hairline | x:96 → 1824, y:940, 1px | — | `--lp-line` |
| Footer left / right | x:96 / right-aligned x:1824, y:962 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 4 rows.** The title must break into 4 fragments of ≤ 14
  characters each at 170px (uppercase, full 1728px width). Natural
  breaks: "STATE / OF THE / PLATFORM / 2026". Three-fragment titles get
  the year, org, or event as row 4.
- **Row pattern is fixed** (solid / outline / solid / accent). The
  accent row should be the fragment with the most meaning — usually the
  last.
- **No lead sentence.** Poster Stack refuses prose; context lives in
  the kicker and footer.

## Image variant

**With an image:** row 2 (the outline row) is replaced by a letterbox
image band — full row footprint (x:96 → 1824, height ≈ 165px), image
`object-cover`, no border. The image reads as one word in the
stack. Choose a crop with a strong horizontal (skyline, hands on a
table, hardware rack). The row's text fragment moves into the caption
position at the band's right edge (mono 13px on a scrim chip) so no
words are lost.

**Without an image:** the pure four-row type stack above.

**Recommended size / placeholder:** `https://placehold.co/1728x165`.
**Dimension fallback:** the band is a fixed 1728×165 frame with
`object-cover` (tall images simply crop to the letterbox); keep a
token CSS fill behind the `<img>`. The image is optional — the outline
text row is the default.

## Choreography

1. `0.00s` — rows rise in sequence: `translateY(60px→0)` + fade, 0.65s
   each, 0.11s stagger top→bottom (image band, if present, uses a
   `scaleY(0.6→1)` unfold instead).
2. `0.60s` — accent row's color arrives last: it enters as `--lp-fg`
   and crossfades to `--lp-accent` at `0.9s`, 0.4s.
3. `0.95s` — kicker, meta, footer fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms, accent color applied immediately.

## Skin points

- **Outline row** → the system's second texture (halftone fill, its
  faint tone solid, striped fill) — anything clearly lighter than the
  solid rows.
- **Accent row** → the system's emphasis treatment (its accent color,
  or italic serif if that is the system's voice).
- **Row casing** → uppercase is default; a serif system may set the
  stack in mixed case if its display face carries scale better that way.

## Failure modes to avoid

- Unequal row sizes or centering some rows — one size, all left-aligned,
  is the pattern.
- Fragments that read as nonsense in sequence. Read the stack aloud
  top to bottom before committing.
- Adding a lead, logos, or ghosts. The stack is everything.
- More than one image band.
