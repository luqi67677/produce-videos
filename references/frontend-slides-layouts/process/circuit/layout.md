---
version: 1.0
name: Circuit
slot: process
description: >
  Cyclical process as a drawn loop. A rectangular hairline circuit
  dominates the stage with four numbered stations at its corners and
  small direction ticks on each edge; the process name sits at dead
  center inside the loop. The loop draws itself clockwise on entry.
  For processes that repeat — never for one-way pipelines.
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

# Circuit — process layout

## Intent

Staircase makes order spatial and Meridian makes time linear, but some
processes have **no end** — detect feeds verify feeds dispatch feeds
learning feeds detection. Circuit gives that its honest shape: a closed
loop the eye can travel forever. The rectangle (not a circle) keeps the
pack's ruled geometry and gives each stage a corner to own. Use it only
when stage 4 genuinely feeds stage 1; a one-way process on a loop is a
lie — use Staircase.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│   01 Detect                 ▸                    02 Verify     │
│    ●───────────────────────────────────────────────●           │
│    │                                               │           │
│  ▴ │              The detection loop               │ ▾         │
│    │              ← center title                   │           │
│    ●───────────────────────────────────────────────●           │
│   04 Learn                  ◂                   03 Dispatch    │
│                                                                │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / CADENCE                                  11 / 12     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px** left/right
margins, **72px** top/bottom margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72, single line | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Branding slot (top-right, optional) | right-aligned to x:1824, y:66, ≤ 40px tall, ≤ 260px wide | wordmark in `--lp-font-display` 700 or an image logo | `--lp-fg` |
| Chrome hairline | x:96 → 1824, y:118, 1px | — | `--lp-line` |
| Loop | rectangle x:420 → 1500, y:330 → 800, 1px edges | — | `--lp-line` |
| Corner nodes (×4) | centered on each corner, 14×14px; station 01's node 18×18px | — | `--lp-fg`; station 01 `--lp-accent` |
| Direction ticks (×4) | midpoint of each edge, pointing clockwise (top ▸, right ▾, bottom ◂, left ▴), ~20px glyphs | `--lp-font-mono` | `--lp-fg-muted` |
| Center title | dead center of the loop (960, 565), max-width 800px, ≤ 2 lines | `--lp-font-display`, 72px, weight 700, centered | `--lp-fg` |
| Station labels (×4) | anchored outside their corners: top corners label ABOVE the loop (baseline ≈ y:296), bottom corners BELOW (top ≈ y:836); left stations left-aligned at x:420, right stations right-aligned to x:1500 | number: `--lp-font-mono` 18px; title: `--lp-font-display` 36px weight 700 inline after number; note: `--lp-font-body` 20px on the next line | number `--lp-accent`; title `--lp-fg`; note `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

Station order is clockwise from top-left: 01 top-left, 02 top-right,
03 bottom-right, 04 bottom-left.

## Content constraints (hard limits)

- **Exactly 4 stations.** Three-stage loops center a triangle nobody
  can rule cleanly — re-cut the process or use Staircase. Five is a
  diagram, not a slide.
- **The loop must be real:** station 04's output feeds station 01.
  The slide asserts it; the speaker must be able to defend it.
- **Center title:** ≤ 24 characters per line, ≤ 2 lines. Name the
  loop, not the company.
- **Station titles:** ≤ 12 characters, one word ideally. Notes: ≤ 44
  characters, one line. Notes are optional as a set.
- **One accent station** (01, the entry point) — its node enlarges and
  its number is already accent; nothing else changes.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

**With a center image:** the center title may sit on a 480×270 still
(a monitor frame from the process) centered in the loop at y:430 → 700,
title dropping to 48px on a scrim band across the image's lower third.
Use only when the image genuinely shows the loop running.

**Recommended size / placeholder:** `https://placehold.co/480x270`.
**Dimension fallback:** fixed frame, `object-fit: cover`, token CSS
fill behind the `<img>`. Optional — the type-only center is the
default and the stronger form.

## Choreography

The loop draws itself clockwise, total ≤ 1.9s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — center title rises `translateY(28px→0)` + fade, 0.6s.
3. `0.30s` — edges draw sequentially, 0.28s each, clockwise: top edge
   `scaleX(0→1)` origin left; right edge `scaleY(0→1)` origin top;
   bottom edge `scaleX(0→1)` origin RIGHT; left edge `scaleY(0→1)`
   origin BOTTOM.
4. `0.42s` — corner nodes pop `scale(0→1)` 0.35s each as the drawing
   edge reaches them (02 at 0.58s, 03 at 0.86s, 04 at 1.14s, 01 last
   at 1.42s — the loop closes where it began).
5. `0.55s` — station labels fade up `translateY(16px→0)` 0.5s each,
   clockwise stagger 0.28s matching their nodes.
6. `1.45s` — direction ticks + footer fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Corner nodes** → the system's node vocabulary (rings, diamonds,
  ticks) ≤ 22px; station 01 keeps its accent and size lead.
- **Direction ticks** → the system's arrow/pointer glyph at the same
  midpoints; may be dropped entirely in minimal systems (the numbered
  clockwise order still reads).
- **Loop edges** → dashed or 2px in heavy systems; never gradients or
  glows.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; the loop interior may take a
  half-step tint (≤ `--lp-fg-faint`) if the system needs the center
  lifted.

## Failure modes to avoid

- Putting a one-way process on the loop. If the audience asks "then
  what?" and the answer is "done," this is the wrong preset.
- Rounding the rectangle into a circle or adding curved arrows —
  that's clip-art grammar; the pack draws with rules.
- Station labels drifting from their corners (each label belongs to
  exactly one corner, anchored outward, never overlapping an edge).
- More than one accent station, or accenting the ticks.
- Branding larger than 40px tall or anywhere but the reserved corner.
