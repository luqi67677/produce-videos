---
version: 1.0
name: Annals
slot: timeline
description: >
  Vertical chronicle. A headline sets the arc, then 4 dated entries
  descend the stage along a thin vertical spine: year in the mono
  gutter, node on the spine, event title beside it, and a quiet
  description column on the right. The final node — today — is
  enlarged and carries the accent. Reads like the annals page of an
  annual report.
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

# Annals — timeline layout

## Intent

Meridian walks a chronology left-to-right like a road; Annals stacks it
top-to-bottom like a **record**. The vertical spine gives history weight
and inevitability — each entry is a stratum laid on the last, and the
reading order is the date order. Use it when the entries deserve full
sentences (Meridian's alternating captions are terse) or when the deck's
grid language is already row-based. Four entries; the last one is now.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Seven years to the national grid        ← headline            │
│                                                                │
│   2019 ──●   First traffic pilot      Twelve intersections…    │
│          │                                                     │
│   2021 ──●   Provincial rollout       Four provinces adopted…  │
│          │                                                     │
│   2024 ──●   The 4,000-camera mark    Analytics moved to…      │
│          │                                                     │
│   2026 ──◉   National grid, phase 1   Eight ministries share…  │
│              ↑ accent "today" node                             │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / PROGRAM                                  09 / 12     │
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
| Headline | x:96, y:170, max-width 1300px, 1 line | `--lp-font-display`, 64px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Spine | vertical 1px line at x:360, from y:332 to y:806 | — | `--lp-line` |
| Nodes (×4) | centered on the spine at each row's title cap-height (y:332, 490, 648, 806), 12×12px; final node 18×18px | — | rows 1–3 `--lp-fg`; final `--lp-accent` |
| Years | right-aligned to x:312, aligned to node center | `--lp-font-mono`, 22px, letter-spacing 0.08em | `--lp-fg-muted`; final year `--lp-accent` |
| Entry titles | x:420, node-aligned, max-width 640px, 1 line | `--lp-font-display`, 40px, weight 700 | `--lp-fg` |
| Entry descriptions | x:1150 → 1824 (674px column), top-aligned with title | `--lp-font-body`, 22px, line-height 1.5, ≤ 2 lines | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

Row pitch is **158px** (node centers at y:332, 490, 648, 806).

## Content constraints (hard limits)

- **Exactly 4 entries**, oldest first, newest last. With only 3, grow
  the pitch to 210px (nodes at 332, 542, 752). Five entries do not fit
  with descriptions — cut an entry or use Meridian.
- **Years:** 4–7 characters (a year, "Q3 24", or "Mar 25"). Consistent
  format across all entries.
- **Titles:** ≤ 28 characters, one line, no wrapping.
- **Descriptions:** ≤ 110 characters, ≤ 2 lines. Optional as a set —
  dropping ALL descriptions widens titles to 1100px; never drop only
  some.
- **The final entry is the present** (or the nearest milestone) and is
  the only accent moment on the slide.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves — the
  chrome hairline terminates the header on its own.

## Image variant

**With era images:** the description column may be replaced by a single
480×640 portrait-orientation image at x:1344 → 1824, y:332 → 806 (the
span of the spine), captioned in mono at its lower-left corner. Titles
then widen to 820px and descriptions are dropped entirely.

**Recommended size / placeholder:** `https://placehold.co/480x640`.
**Dimension fallback:** fixed frame, `object-fit: cover`, token CSS
fill behind the `<img>` for load failures. The image is optional — the
three-column text form is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline rises `translateY(36px→0)` + fade, 0.6s.
3. `0.30s` — spine grows `scaleY(0→1)` from the top
   (`transform-origin: top`), 0.9s.
4. `0.45s` — nodes pop `scale(0→1)`, 0.4s each, 0.15s stagger downward
   (each node appears as the spine reaches it).
5. `0.55s` — rows (year, title, description) fade up
   `translateY(24px→0)`, 0.6s each, 0.15s stagger downward.
6. `1.20s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Nodes** → the system's node vocabulary (circles, diamonds, ticks);
  the final node may become an open accent ring ≤ 22px, echoing
  Recap Rail's "next" grammar.
- **Spine** → the system's line vocabulary (dashed, doubled); may
  thicken to 2px in heavy systems.
- **Years** → may sit in small outlined chips if the system frames
  labels; chip footprint ≤ 120×36px.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; a faint vertical grain echoing the
  spine is the sanctioned atmospheric upgrade.

## Failure modes to avoid

- Alternating entries left/right of the spine — that is Meridian's
  grammar rotated, and it wrecks the gutter alignment. Everything
  hangs right of the spine except the years.
- More than one accent node, or accenting a middle entry. History
  culminates; it doesn't flash.
- Descriptions of uneven presence (some rows with, some without).
- Curved, angled, or decorated spines. It is a record, not a river.
- Branding larger than 40px tall or anywhere but the reserved corner.
