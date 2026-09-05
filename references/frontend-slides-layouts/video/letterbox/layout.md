---
version: 1.0
name: Letterbox
slot: video
description: >
  Cinemascope band. A full-bleed-width video band crosses the middle of
  the stage in a wide crop, title above it, caption and runtime below —
  the slide reads like a frame from an anamorphic print with its
  margins intact.
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

# Letterbox — video layout

## Intent

Screening Room frames the video as an object; Letterbox lets it behave
like architecture — edge to edge, but held between typographic margins
so the slide never becomes a raw fullscreen embed. The wide crop is
the drama: even ordinary 16:9 footage reads as cinematic when the band
shows only its middle. Best for footage with strong horizontals —
skylines, conveyor lines, dashboards panning.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       10 / 14  │
│  THE LINE, END TO END        ← title                           │
├────────────────────────────────────────────────────────────────┤ y:300
│                                                                │
│                video band (full-bleed width, ▶)                │
│                                                                │
├────────────────────────────────────────────────────────────────┤ y:860
│  SUKABUMI CORRIDOR — SINGLE TAKE                       02:41   │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Title | x:96, top y:150, 1 line, max-width 1728px | `--lp-font-display`, 88–96px (default 96), weight 800, line-height 1, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Video band | x:0 → 1920 (full bleed), y:300 → 860 (1920×560, ≈3.4:1) ; 1px hairlines along its top and bottom edges | — | hairlines `--lp-line` |
| Play glyph | centered on the band, 96px circle | — | as Screening Room |
| Caption (below band, left) | x:96, y:896 | `--lp-font-mono`, 14px, uppercase, ls 0.14em | `--lp-fg-muted` |
| Runtime (below band, right) | right-aligned x:1824, y:896 | `--lp-font-mono`, 14px, ls 0.1em | `--lp-accent` |

## Content constraints (hard limits)

- **Title:** 1 line, ≤ 24 characters uppercase at 96px. Two-line
  titles crowd the band — shorten or use Screening Room.
- **Caption:** 1 line ≤ 60 characters. **Runtime:** `MM:SS`.
- **Footage:** must survive a center crop — the band shows roughly the
  middle 52% of a 16:9 source. Key action in the top or bottom third
  will be cut; prefer native wide exports when available.

## Video embed & fallbacks

- **Embed:** local `<video controls preload="metadata" poster="...">`
  filling the band with `object-cover` (this produces the
  cinemascope crop from a 16:9 source). Hosted `<iframe>` embeds
  cannot crop — with an iframe, letterbox it at 996×560 centered in
  the band and let the band's token fill show at the sides. Never
  autoplay with sound.
- **Poster / placeholder:** `https://placehold.co/1920x560` (the
  band's own ratio, so drafting shows the true crop).
- **Dimension fallback:** fixed 1920×560 band, media `object-cover`;
  token CSS fill behind for load failures.
- **No-video variant:** the poster as a still — the band becomes a
  panoramic image slide, caption and runtime replaced by a plain
  caption. The video is optional.
- **Reduced motion:** no autoplay anywhere in this preset.

## Choreography

1. `0.00s` — kicker, counter fade, 0.5s.
2. `0.10s` — title rises `translateY(36px→0)` + fade, 0.7s.
3. `0.35s` — band unfolds: `scaleY(0.85→1)` + fade (transform-origin
   center), 0.9s; edge hairlines wipe `scaleX(0→1)` at `0.5s`.
4. `0.95s` — play glyph scales in, 0.5s; caption and runtime fade up
   at `1.05s`.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Band edge hairlines** → the system's divider vocabulary (doubled,
  dashed); they are what keep the band architectural rather than a
  browser embed.
- **Runtime** → the system's tag treatment.
- **Band matting (iframe case)** → the system's darkest surface, not
  pure black, unless the system is black.

## Failure modes to avoid

- Vertical or square footage in the band — the crop destroys it; use
  Screening Room or Side Reel instead.
- Dropping the top/bottom hairlines and margins so it reads as a
  fullscreen video with stuff on it — the margins are the design.
- Titles above two lines, or moving the title onto the band.
