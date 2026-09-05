---
version: 1.0
name: Half Plate
slot: opening
description: >
  Image-led 50/50 opening. The left half is a full-bleed media plate with
  a small caption chip; the right half carries kicker, title, lead, and a
  presenter footer. Without an image, the plate inverts to the alternate
  surface and carries an oversized outline monogram.
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

# Half Plate — opening layout

## Intent

The opening for decks that have one strong photograph: give it half the
stage, uncropped by decoration, and let the typography answer it from
the other half. The hard 50/50 seam is the design — neither side leaks
into the other except the caption chip, which belongs to the image.

## Region map (1920×1080 stage)

```
┌──────────────────────────┬─────────────────────────────────────┐
│                          │  KICKER · LABEL                     │
│                          │                                     │
│      media plate         │  ▮▮▮▮                               │
│      (full bleed,        │  FIELD                              │
│       object-cover)      │  NOTES          ← title             │
│                          │                                     │
│                          │  Lead sentence, max-width 620px.    │
│  ┌caption chip┐          │                                     │
│  └────────────┘          │  ─────────────────────────────      │
│                          │  PRESENTER — ORG           01 / 12  │
└──────────────────────────┴─────────────────────────────────────┘
        x:0→960                       x:1056→1824
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Media plate | x:0 → 960, full height; image `object-cover` | — | — |
| Caption chip | inside plate: x:48, bottom:48; padding 10×16 | `--lp-font-mono`, 13px, uppercase, letter-spacing 0.14em | text `--lp-fg-muted` on a chip of `--lp-bg` at ~82% opacity |
| Kicker | x:1056, y:96 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Accent bar | x:1056, 44px above title, 72×8px | — | `--lp-accent` |
| Title | x:1056, top y:340, max-width 720px | `--lp-font-display`, 108–120px (default 120), weight 700–800, line-height 0.97, letter-spacing −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Lead | x:1056, 36px below title, max-width 620px | `--lp-font-body`, 22px, line-height 1.55 | `--lp-fg-muted` |
| Footer hairline | x:1056 → 1824, y:940, 1px | — | `--lp-line` |
| Footer left / right | x:1056 / right-aligned x:1824, y:962 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 2–3 lines, ≤ 8 characters uppercase (≤ 10 mixed) per line
  at 120px in the 720px column. Step down to 108px at most.
- **Lead:** 1–3 lines, ≤ 140 characters. Optional.
- **Caption chip:** 1 line, ≤ 48 characters — what/where/when of the
  image. Required whenever a real photo is shown.
- **Image:** portrait-leaning or square crops work best; the plate is
  960×1080. Never letterbox inside the plate.

## Image variant

This preset is image-first; the case above is the image case.

**Recommended size / placeholder:** `https://placehold.co/960x1080` —
use this URL during drafting so the crop is honest, then swap for the
real photo. **Dimension fallback:** the plate is a fixed 960×1080 frame
with `object-cover`, so any delivered aspect ratio fills it; keep
a token-built CSS fill behind the `<img>` so a missing or failed image
degrades to a designed surface, not a hole.

**Without an image:** fill the plate with the inverted surface
(`--lp-fg`, or the design system's alternate surface) and center an
oversized outline monogram or deck numeral (≈ 480px, 2px text-stroke in
the plate's faint tone). Drop the caption chip. Everything on the right
half is unchanged.

## Choreography

1. `0.00s` — media plate fades in with a slow 1.03→1 scale settle, 1.1s.
2. `0.20s` — kicker fades, 0.5s; accent bar wipes `scaleX(0→1)` at
   `0.30s`, 0.5s.
3. `0.40s` — title lines rise `translateY(44px→0)` + fade, 0.7s, 0.12s
   stagger; lead follows at `0.80s`.
4. `0.95s` — caption chip and footer fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Caption chip** → the system's tag/label treatment.
- **Seam** → a 1px hairline or the system's divider may sit on x:960 if
  the image and field tones blur together.
- **Plate treatment** → the system may apply its duotone/grain treatment
  to the image, but no frames, borders, or rounded corners on the plate.

## Failure modes to avoid

- Shrinking the plate to less than half. 50/50 or use a different preset.
- Text or logos over the image beyond the caption chip.
- A skinny title squeezed by long words — hyphenate nothing; rewrite.
