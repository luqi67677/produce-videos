---
version: 1.0
name: Triptych
slot: image
description: >
  Three-panel image wall. An editorial header band holds kicker,
  headline, and the optional brand mark; below it, three equal
  portrait-orientation image panels run full bleed to the bottom
  edge, separated by thin surface gaps, each carrying a mono
  figure-caption chip at its lower-left corner. One panel may be
  declared the key panel and gets the accent caption.
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

# Triptych — image layout

## Intent

Plate Caption studies ONE image like a museum exhibit; Triptych shows
**three images as one argument** — three sites, three states, three
moments of the same system. The equal panel widths refuse to rank the
images; only the accent caption chip may nominate a key panel. Use it
when the evidence is plural and parallel (before/during/after,
site A/B/C), never for three unrelated pictures.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  One system, three cities        ← headline                    │
├────────────────────┬────────────────────┬──────────────────────┤
│                    │                    │                      │
│    image panel     │    image panel     │     image panel      │
│     632 × 820      │     632 × 820      │      632 × 820       │
│                    │                    │                      │
│                    │                    │                      │
│  FIG 01 — CAPTION  │  FIG 02 — CAPTION  │  FIG 03 — CAPTION    │
└────────────────────┴────────────────────┴──────────────────────┘
                        ↑ panels run full bleed to the bottom edge
```

## Geometry

All values are stage pixels at 1920×1080.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72, single line | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Branding slot (top-right, optional) | right-aligned to x:1824, y:66, ≤ 40px tall, ≤ 260px wide | wordmark in `--lp-font-display` 700 or an image logo | `--lp-fg` |
| Headline | x:96, y:128, max-width 1500px, 1 line | `--lp-font-display`, 60px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Panel band | y:260 → 1080 (full bleed bottom) | — | — |
| Panels (×3) | x:0→632, x:644→1276, x:1288→1920; each 632×820 | image `object-fit: cover` over a token CSS fill | fill: `--lp-fg-faint` over `--lp-bg` |
| Panel gaps (×2) | 12px, showing the slide surface | — | `--lp-bg` |
| Caption chips | inside each panel, bottom-left, x:+24 y:−24 from corner, padding 10×16px | `--lp-font-mono`, 14px, uppercase, letter-spacing 0.14em, on a `--lp-bg` chip | text `--lp-fg`; key panel's chip text `--lp-accent` |

No footer — the panels own the bottom edge. The slide counter, if the
deck uses one, moves into the header line next to the branding slot.

## Content constraints (hard limits)

- **Exactly 3 images**, same orientation, thematically parallel. For a
  pair, use two 950px panels (x:0→950, x:970→1920); for one image, use
  Plate Caption instead.
- **Headline:** ≤ 42 characters, one line. Optional — without it the
  panel band rises to y:200 (panels 632×880) and the kicker alone
  heads the slide.
- **Captions:** ≤ 38 characters, one line, pattern "FIG NN — subject,
  place". Every panel gets one; a panel without a caption is a hole in
  the record.
- **Key panel:** at most one; marked ONLY by its chip text going
  accent. No borders, scaling, or other favoritism.

## Branding / logo slot (optional)

The top-right corner of the header (right-aligned to x:1824, y:66) is
a reserved **optional** branding slot: the presenting org's wordmark
or logo, ≤ 40px tall and ≤ 260px wide.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image slots

**Recommended size / placeholder:** `https://placehold.co/632x820` per
panel (portrait). **Dimension fallback:** fixed 632×820 frames,
`object-fit: cover`, so any delivered aspect ratio fills without
moving the layout. **Load fallback:** a token CSS fill
(`--lp-fg-faint` wash over `--lp-bg`) behind every `<img>`.

All three images are optional as a set: with no imagery available,
each panel keeps its fill and caption and the slide degrades to a
designed three-plate specimen sheet — acceptable for drafts, weak for
finals; prefer real photographs.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — header (kicker, branding) fades in, 0.5s.
2. `0.10s` — headline rises `translateY(32px→0)` + fade, 0.6s.
3. `0.30s` — panels rise `translateY(48px→0)` + fade, 0.7s each,
   0.15s stagger left → right.
4. `0.90s` — caption chips fade in, 0.5s, 0.1s stagger.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Caption chips** → the system's label vocabulary (outlined chip,
  underlined tag, stamp); same corner, footprint ≤ 420×44px.
- **Panel gaps** → may widen to 16px or carry the system's hairline
  instead of raw surface; never disappear (panels must not touch).
- **Panel fills** → the system's texture fingerprint at
  `--lp-fg-faint` contrast (visible only while images load or when
  imagery is dropped).
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Header background** → flat `--lp-bg`; a hairline under the header
  band (y:252) is the sanctioned extra if the system rules everything.

## Failure modes to avoid

- Unequal panel widths or a "hero" middle panel — that hierarchy
  belongs to other layouts. Equality is the point.
- Mixed orientations or wildly different subjects/exposures across
  the three images; the wall must read as one series.
- Captions floating outside the panels or centered under them —
  museum-outside captioning is Plate Caption's grammar.
- Text overlaid on the images beyond the caption chips.
- Branding larger than 40px tall or anywhere but the header slot.
