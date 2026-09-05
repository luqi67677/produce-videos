---
version: 1.0
name: Masthead
slot: opening
description: >
  Newspaper-nameplate opening. A single-line title spans the full content
  width at the very top, closed by a thick-thin double rule and a
  three-part meta row. The lower field stays open, balanced by a lead
  block bottom-right and a giant ghost drop-cap cropped by the
  bottom-left corner.
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

# Masthead — opening layout

## Intent

Top-anchored where the other opening presets are center- or
bottom-anchored. The title behaves like a publication's nameplate: it
runs the full width, gets ruled off like a front page, and then the rest
of the slide is deliberately quiet — one lead block low-right, one ghost
drop-cap low-left, acres of field between. Reads as "issue one of
something serious."

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  THE YEAR AHEAD                              ← nameplate, 1 line│
│  ══════════════════════════════════════════════════════════    │ ← 4px rule
│  KICKER          VOLUME / DESCRIPTOR                DATE        │ ← meta row
│  ──────────────────────────────────────────────────────────    │ ← 1px rule
│                                                                │
│                    (deliberate open field)                     │
│                                                                │
│   ┌────┐                            Lead paragraph block,      │
│   │ gho│st drop-cap                 max-width 640px, anchored  │
│   │ cro│pped bottom-left            bottom-right               │
│  ─┴────┴────────────────────────────────────────────────────  │
│  PRESENTER — ORG                                      01 / 14  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px**
left/right margins, **72px** top/bottom margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Nameplate | x:96 → 1824, top y:96, single line, no wrap | `--lp-font-display`, 150–176px (default 170), weight 700–800, line-height 1, letter-spacing −0.02em | `--lp-fg`; `<em>` word → `--lp-accent` |
| Thick rule | x:96 → 1824, y:312, 4px | — | `--lp-fg` |
| Meta row | x:96 → 1824, y:344, flex: left / center / right | `--lp-font-mono`, 15px, uppercase; left item letter-spacing 0.18em, others 0.12em | left `--lp-accent`, center+right `--lp-fg-muted` |
| Thin rule | x:96 → 1824, y:396, 1px | — | `--lp-line` |
| Ghost drop-cap | left:48, bottom:−140 (cropped by bottom edge), font-size 520px, line-height 0.8 | `--lp-font-display`, weight 800, outline (2px text-stroke, transparent fill) | `--lp-fg-faint` |
| Lead block | right-aligned block: right:96, bottom edge ≈ y:880, max-width 640px, text-align left | `--lp-font-body`, 26px, line-height 1.55; 48×6px accent bar above, 28px gap | `--lp-fg-muted`, bar `--lp-accent` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left / right | x:96 / right-aligned x:1824, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Nameplate:** exactly 1 line, must fit 1728px without wrapping — at
  170px roughly **12–13 characters uppercase** or **14–16 mixed case**.
  Step down to 150px at most; below that, pick a shorter title or a
  different preset. At most one `<em>` word.
- **Meta row:** exactly 3 single-line items (kicker / volume-descriptor /
  date). If only 2 exist, the center slot holds the org name.
- **Lead:** 2–4 lines, ≤ 220 characters. This preset expects a lead — the
  bottom-right block is half the composition.
- **Ghost drop-cap:** exactly 1 character — the nameplate's first letter,
  or the org's initial. Must be cropped by the bottom edge. Prefer letters
  with diagonals or curves (A, N, R, S…) — outline-rendered straight-edged
  glyphs like T, I, or L read as stray rectangles when cropped.

## Image variant

**With an image:** the ghost drop-cap is replaced by a 520×360 image
plate (1px `--lp-line` border) anchored bottom-left at x:96, its
bottom edge at y:920 (above the footer), with a mono caption line
beneath — a front-page lead photo. The bottom-right lead block is
unchanged; the two anchors now mirror as photo vs. prose.

**Recommended size / placeholder:** `https://placehold.co/520x360`.
**Dimension fallback:** fixed 520×360 frame, `object-cover`,
token CSS fill behind the `<img>`. The image is optional — the ghost
drop-cap is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — nameplate rises into view: `translateY(60px→0)` + fade,
   0.8s.
2. `0.35s` — thick rule wipes via `scaleX(0→1)`, origin left, 0.6s;
   thin rule follows at `0.5s`.
3. `0.55s` — meta row items fade in left-to-right, 0.5s, 0.08s stagger.
4. `0.70s` — ghost drop-cap drifts up: `translateY(60px→0)` + fade, 0.9s.
5. `0.90s` — accent bar wipes, then lead fades up, 0.6s.
6. `1.10s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Thick-thin rule pair** → the system's strongest divider vocabulary
  (double hairline, dotted+solid, colored band ≤ 8px). The pair rhythm —
  heavy then light — is structural.
- **Ghost drop-cap** → the system's signature glyph or texture
  fingerprint at `--lp-fg-faint` contrast, cropped bottom-left.
- **Accent bar on lead** → the system's marker device, footprint ≤
  120×24px.
- **`<em>` treatment** → the system's emphasis move, colored `--lp-accent`.
- **Background** → flat `--lp-bg` or a paper-like atmospheric treatment;
  heavy directional gradients fight the front-page register.

## Failure modes to avoid

- Wrapping the nameplate to two lines — one line IS the nameplate. Two
  lines means this is the wrong preset (use Offset Marquee).
- Filling the open field with content. The emptiness between the ruled
  header and the bottom anchors is the design.
- Centering the lead block or moving it left — it counterweights the
  ghost drop-cap; both anchors are needed.
- Rendering the ghost drop-cap fully inside the frame — uncropped it
  reads as a logo, not atmosphere.
