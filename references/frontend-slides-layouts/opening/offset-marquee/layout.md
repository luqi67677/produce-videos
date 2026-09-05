---
version: 1.0
name: Offset Marquee
slot: opening
description: >
  Asymmetric opening slide. A left-anchored display title sits low on the
  stage against a giant ghost numeral cropped by the top-right edge. Mono
  chrome runs along the top, a presenter footer along the bottom, and a
  short accent bar punctuates the title. The composition reads as confident
  and editorial regardless of which design system skins it.
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

# Offset Marquee — opening layout

## Intent

The first slide has one job: establish authority and set the deck's voice.
Offset Marquee does it with **asymmetry and scale contrast** — a massive
title anchored to the lower-left, balanced by an oversized ghost numeral
bleeding off the upper-right. Nothing is centered. The empty space top-left
and mid-right is deliberate and must be preserved.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│ 96px margin                                          ┌─────────┼──
│  KICKER · LABEL                     EVENT / DATE ──▶ │  ghost  │  ← "01"
│  ──────────────────────────────────────────────────  │ numeral │    cropped
│                                                      │ 560px   │    by edge
│                (deliberate empty space)              └─────────┼──
│                                                                │
│  ▮▮▮▮  ← accent bar 72×8                                       │
│  WHERE WE                                                      │
│  GO NEXT                  ← display title, ≤3 lines            │
│                                                                │
│  Lead sentence, max-width 680px, 1–2 lines.                    │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  PRESENTER — ROLE — ORG                            01 / 12     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px** left/right
margins, **72px** top/bottom margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72, single line | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Top meta (top-right) | right-aligned to x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Chrome hairline | x:96 → 1824, y:118, 1px | — | `--lp-line` |
| Ghost numeral | right:-24, top:36, font-size 560px, line-height 0.8, cropped by stage edge | `--lp-font-display`, weight 700–800, rendered as outline (2px text-stroke, transparent fill) | `--lp-fg-faint` |
| Accent bar | x:96, sits 48px above title's first line, 72×8px | — | `--lp-accent` |
| Display title | x:96, baseline of last line ≈ y:780, max-width 1360px | `--lp-font-display`, 152–176px (default 168), weight 700–800, line-height 0.95, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Lead | x:96, 40px below title, max-width 680px | `--lp-font-body`, 26px, line-height 1.5 | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em; separate items with a spaced "—" | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 2–3 lines. Every line must fit the 1360px column without
  wrapping — at 168px that is roughly **11–12 characters uppercase** or
  **13–14 mixed case** in a wide grotesque; wrap each line in its own
  span so nothing reflows. If a line overflows, first break the lines
  differently or cut words, then step the size down — never below 152px,
  never to 4 lines. Title casing (uppercase vs mixed) is a skin decision;
  re-check the fit after applying the design system's display face.
  Exactly one `<em>` phrase is recommended (the accent moment); zero is
  acceptable, two is not.
- **Lead:** 1–2 lines, ≤ 120 characters total. Optional — the layout holds
  without it.
- **Kicker / meta / footer:** single line each, real deck chrome only
  (event, date, presenter, org). Never render internal labels.
- **Ghost numeral:** 2 characters max ("01"). May instead be a short
  glyph or the deck's monogram if the design system has one.

## Image variant

**With an image:** a full-height image panel occupies x:1360 → 1920,
bleeding off the right edge; the ghost numeral is dropped (the panel
takes its atmospheric role) and the title max-width tightens to
1150px. A mono caption chip sits at the panel's bottom-left corner.

**Recommended size / placeholder:** `https://placehold.co/560x1080`.
**Dimension fallback:** fixed 560×1080 frame, `object-fit: cover`,
token CSS fill behind the `<img>` for load failures. The image is
optional — the ghost numeral is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.4s:

1. `0.00s` — chrome (kicker, meta, hairline) fades in, 0.5s.
2. `0.15s` — ghost numeral drifts in from +40px right with fade, 0.9s.
3. `0.30s` — accent bar wipes in via `transform: scaleX(0→1)`,
   `transform-origin: left`, 0.5s.
4. `0.40s` — title lines rise: each line `translateY(48px→0)` + fade,
   0.7s, 0.12s stagger per line (wrap each line in a span).
5. `0.80s` — lead fades up, 0.6s.
6. `0.95s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Accent bar** → the system's signature rule/marker (e.g., Signal's 36px
  gold rule, a tag pill, a stamp). Same position; footprint ≤ 120×24px.
- **Ghost numeral** → the system's texture fingerprint or a large
  system-native decorative element, as long as it stays at `--lp-fg-faint`
  contrast and is cropped by the top-right edge.
- **Hairlines** → the system's divider vocabulary (dashed, doubled,
  colored) at the same coordinates.
- **`<em>` treatment** → the system's emphasis move (italic, color shift,
  outline text), colored `--lp-accent`.
- **Background** → flat `--lp-bg` by default; the system may apply its
  atmospheric background treatment as long as text contrast is preserved.

## Failure modes to avoid

- Centering the title or the whole composition. The lower-left anchor and
  the empty top-left quadrant ARE the layout.
- Letting the ghost numeral compete with the title: it must sit behind
  content (z-index below text) and stay faint.
- Filling the empty space with extra elements (logos, badges, imagery).
  One logo is permitted, only in the top-right meta position, ≤ 40px tall.
- Shrinking side margins to fit a longer title — shorten the title.
