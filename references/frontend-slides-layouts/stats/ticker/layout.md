---
version: 1.0
name: Ticker
slot: stats
description: >
  A dense ruled band of four figures. Between two full-width hairlines,
  four stats share one row — value, label — divided by vertical
  hairlines, under an editorial headline. For the dashboard moment
  handled with restraint: more numbers than Stat Strip, no charts,
  no tiles.
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

# Ticker — stats layout

## Intent

Sometimes the slide honestly needs four numbers. Stat Strip's three
generous tiles won't hold them, and a dashboard grid would betray the
deck's register — so Ticker compresses the figures into one banded
row, like the market strip across a broadsheet's front page. The band
structure keeps density from becoming clutter: everything aligns to
one baseline, one rhythm, one rule above and below.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       12 / 14  │
│  THE OPERATION, AT A GLANCE     ← headline                     │
│                                                                │
├────────────────────────────────────────────────────────────────┤ y:520
│  214        │  38ms       │  99.98%     │  12                  │
│  DEPLOYS    │  P99        │  UPTIME     │  REGIONS             │
├────────────────────────────────────────────────────────────────┤ y:760
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  SOURCE / PERIOD                                       BEACON  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1–2 lines, max-width 1200px | `--lp-font-display`, 84px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Band rules | x:0 → 1920 (full bleed), y:520 and y:760, 1px | — | `--lp-line` |
| Cells | 4 equal columns between x:96 → 1824; vertical 1px hairlines between cells spanning the band's height; cells 2–4 padded 56px left | — | dividers `--lp-line` |
| Cell value | top-aligned y:576 | `--lp-font-display`, 104px, weight 800, line-height 0.95, ls −0.02em | `--lp-fg`; unit glyphs → `--lp-accent` |
| Cell label | 20px below value | `--lp-font-mono`, 14px, uppercase, ls 0.16em | `--lp-fg-muted` |
| Footer hairline + source | x:96 → 1824, y:962 / y:984 | mono 14px | `--lp-line` / `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 4 cells.** Three → Stat Strip; five → cut the weakest
  (a five-cell ticker's values shrink past legibility).
- **Values:** ≤ 6 glyphs, one shared precision register. **Labels:**
  1 line ≤ 14 characters — ticker labels are terse by genre.
- **No notes, deltas, or trends inside cells** — the band holds
  values and names only; anything needing context belongs on a Stat
  Strip or Keynote Figure slide.
- **Footer source is required**, as with all stats presets.

## Image variant

**With an image:** a 1200×260 image band sits above the ticker at
x:96 → 1296, y:220 (headline then 1 line, max-width 1200px is
unaffected; the image band right-aligns with the ticker's third
divider). Use for the operation's setting. **Recommended size /
placeholder:** `https://placehold.co/1200x260`. **Dimension
fallback:** fixed letterbox frame, `object-cover`, token CSS
fill behind the `<img>`. The image is optional.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.40s` — band rules wipe `scaleX(0→1)` (top from left, bottom
   from right), 0.8s.
3. `0.65s` — cells arrive left-to-right, 0.14s stagger: divider
   draws `scaleY(0→1)` 0.35s, value fades up `translateY(28px→0)`
   0.5s, label fades 0.4s at `+0.1s`.
4. `1.20s` — footer fades, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Counting animations allowed on
values (≤ 1s). Under `prefers-reduced-motion`, no transforms.

## Skin points

- **Band rules** → the system's strongest hairline pair; full bleed
  always.
- **Band fill** → the system may tint the band with its alternate
  surface at ≤ 6% contrast.
- **Cell dividers** → the system's divider vocabulary.

## Failure modes to avoid

- Mixed magnitudes that force tiny values ("2,147,483 / 3") — rescale
  units until all four sit at ≤ 6 glyphs.
- Sneaking sparklines or arrows into cells.
- Using Ticker as the deck's only stats slide when one number matters
  most — density flattens hierarchy; that number deserves Keynote
  Figure.
