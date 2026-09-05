---
version: 1.0
name: Threshold
slot: section
description: >
  A gate band divider. Two full-width hairlines fence off a horizontal
  band across the stage's middle; the section title stands inside it
  with the part numeral at the band's far right. Above the band, a
  small inline part index; below it, one framing line. Crossing the
  band is crossing into the chapter.
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

# Threshold — section layout

## Intent

The horizontal sibling of Spine's vertical rule: two lines turn the
middle of the stage into a doorway, and the title stands in it like a
name carved on a lintel. Quieter than Countdown Plate, more formal
than Chapter Gate — the register of a report that takes its own
structure seriously. Works especially well in decks that use Horizon
as the opening (the band rhymes with the horizon line).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  DECK TITLE                                           06 / 14  │
│                                                                │
│                                       01 · 02 · [03] · 04 · 05 │
├────────────────────────────────────────────────────────────────┤ y:420
│                                                                │
│  EXECUTION                                              03     │
│  ← title inside the band              band numeral →           │
│                                                                │
├────────────────────────────────────────────────────────────────┤ y:660
│  One-line framing sentence, muted.                             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Deck title (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Counter (top-right) | right-aligned x:1824, y:72 | same | `--lp-fg-muted` |
| Part index | right-aligned x:1824, y:372; inline numbers separated by " · " | `--lp-font-mono`, 15px, ls 0.14em | past `--lp-fg-muted`, current `--lp-accent` (weight 500), future `--lp-fg-muted` at 50%; separators `--lp-fg-muted` |
| Band rules | x:0 → 1920 (full bleed), y:420 and y:660, 1px each | — | `--lp-line` |
| Title | x:96, vertically centered in the band (center y:540), 1 line | `--lp-font-display`, 112–128px (default 120), weight 700–800, line-height 1, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Band numeral | right-aligned x:1824, vertically centered in the band | `--lp-font-mono`, 48px, weight 500, ls 0.06em | `--lp-accent` |
| Framing line | x:96, y:708, max-width 800px | `--lp-font-body`, 22px, line-height 1.5 | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** exactly 1 line, ≤ 20 characters uppercase at 120px
  (the band numeral needs its right margin).
- **Part index:** 3–6 numbers, exactly one current. Numbers only — the
  labels live in the band.
- **Framing line:** 1 line ≤ 90 characters. Optional.
- The band is fixed at 240px tall (y:420 → 660); do not resize it to
  fit a longer title — shorten the title.

## Image variant

**With an image:** the band itself becomes an image band — a 1920×240
strip between the rules under a scrim of `--lp-bg` at ~78% so the
title stays legible on it. The doorway gains a view. **Recommended
size / placeholder:** `https://placehold.co/1920x240`. **Dimension
fallback:** fixed 1920×240 letterbox frame, `object-cover` (a
16:9 source shows its center strip), token CSS fill behind the
`<img>`. The image is optional.

## Choreography

1. `0.00s` — top band rule wipes `scaleX(0→1)` from the left, 0.8s;
   bottom rule mirrors from the right (`transform-origin: right`) at
   `0.15s` — the gate closes around the title's space.
2. `0.45s` — title rises `translateY(36px→0)` + fade, 0.7s; band
   numeral fades at `0.7s`.
3. `0.85s` — part index and framing line fade in, 0.5s.
4. `0.95s` — deck title and counter fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Band rules** → the system's strongest hairline treatment; always
  full-bleed.
- **Band fill** → the system may tint the band with its alternate
  surface at ≤ 8% contrast (a whisper of the Inversion move).
- **Part index separators** → the system's marker glyph.

## Failure modes to avoid

- Content wandering into the band beyond the title and numeral.
- Rules stopping at the margins — the doorway must span the stage.
- Using the band as a header bar with body text below; the space
  below holds one line, nothing more.
