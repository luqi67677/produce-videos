---
version: 1.0
name: Chapter Gate
slot: section
description: >
  Asymmetric section divider. An enormous chapter numeral, solid but
  faint, bleeds off the right edge while the section title anchors the
  lower-left behind an accent rule. A chapter rail along the bottom shows
  where the deck is. The pause between movements, not a new cover.
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

# Chapter Gate — section layout

## Intent

A section divider must do two jobs in three seconds: mark a clean break,
and tell the audience where they are in the journey. Chapter Gate does
the first with scale (the numeral owns the right half as pure atmosphere)
and the second with the chapter rail — a quiet bottom strip listing every
part with the current one lit. It deliberately echoes the deck's opening
asymmetry without repeating it: the numeral is a solid faint fill, not an
outline, so dividers and covers stay visually distinct.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  PART TWO                                            ┌─────────┼──
│                                                      │         │
│                                                      │ numeral │  ← "02"
│  ▮▮▮▮  ← accent bar 72×8                             │  solid  │    faint fill,
│  DEEPER, NOT                                         │  faint  │    cropped by
│  WIDER                 ← section title               │  640px  │    right edge
│                                                      └─────────┼──
│  One-line framing sentence, muted.                             │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  ● 01 INERTIA   ◉ 02 DEPTH   ○ 03 EXECUTION   ○ 04 PROOF      │ ← chapter rail
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Chapter numeral | right:−40 (cropped by right edge), vertically centered, font-size 640px, line-height 0.8 | `--lp-font-display`, weight 800, **solid fill** (not outline — outline ghosts belong to opening/closing slots) | `--lp-fg-faint` |
| Accent bar | x:96, 44px above title's first line, 72×8px | — | `--lp-accent` |
| Section title | x:96, baseline of last line ≈ y:640, max-width 1150px | `--lp-font-display`, 120–140px (default 132), weight 700–800, line-height 0.97, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Framing line | x:96, 36px below title, max-width 680px | `--lp-font-body`, 24px, line-height 1.5 | `--lp-fg-muted` |
| Rail hairline | x:96 → 1824, y:940, 1px | — | `--lp-line` |
| Chapter rail | x:96, y:966, single row, items spaced 64px apart; each item = 8px dot + mono label | `--lp-font-mono`, 14px, uppercase, letter-spacing 0.14em | past items `--lp-fg-muted` (filled dot), current `--lp-accent` (filled dot + label), future `--lp-fg-muted` at 50% (hollow dot) |

## Content constraints (hard limits)

- **Title:** 1–2 lines, ≤ 12 characters per line at 132px (uppercase;
  ~14 mixed case). Section titles are fragments, not sentences. At most
  one `<em>` phrase.
- **Framing line:** 1 line, ≤ 90 characters. Optional.
- **Numeral:** 2 characters ("02"). Always the current part number,
  zero-padded.
- **Chapter rail:** 3–6 items, each ≤ 14 characters (number + one word).
  More than 6 parts → drop labels, keep numbered dots only. Exactly one
  item is current.

## Image variant

**With an image:** the chapter numeral is replaced by a full-height
image panel at x:1280 → 1920, bleeding off the right edge, with a
left-edge fade (linear gradient from `--lp-bg` at 100% to transparent
over the panel's left 160px) so it dissolves into the slide instead of
cutting it. The chapter number moves into the kicker ("Part 02 —
Depth"). Title, framing line, and chapter rail are unchanged.

**Recommended size / placeholder:** `https://placehold.co/640x1080`.
**Dimension fallback:** fixed 640×1080 frame, `object-cover`,
token CSS fill behind the `<img>`. The image is optional — the faint
numeral is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.3s:

1. `0.00s` — numeral fades in (opacity only — it is centered with a
   transform, so animating transforms would break its position), 1.0s.
2. `0.15s` — kicker fades in, 0.5s.
3. `0.25s` — accent bar wipes via `scaleX(0→1)`, origin left, 0.5s.
4. `0.35s` — title lines rise: `translateY(44px→0)` + fade, 0.7s, 0.12s
   stagger.
5. `0.70s` — framing line fades up, 0.6s.
6. `0.85s` — rail hairline and chapter rail fade in; the current item's
   dot pops via `scale(0→1)` at `1.1s`, 0.4s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Numeral** → the system's display numerals or chapter-number
  treatment (e.g., serif figures), still solid-faint and cropped right.
- **Accent bar** → the system's signature rule/marker, footprint ≤
  120×24px.
- **Rail dots** → the system's marker glyphs (squares, ticks, em-dashes);
  the three states (past / current / future) must stay distinguishable.
- **Background** → the system's dark or light atmospheric treatment;
  the numeral must remain readable as a shape against it.

## Failure modes to avoid

- Rendering the numeral as an outline — that is the opening/closing
  ghost vocabulary; dividers use solid faint fill.
- Skipping the chapter rail. Without it this is a weak opening slide,
  not a divider.
- Adding content bullets or images. A divider is a breath, not a slide.
- Long titles. If the section name needs 3 lines, shorten the name.
