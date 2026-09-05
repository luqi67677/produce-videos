---
version: 1.0
name: Recap Rail
slot: closing
description: >
  The journey, completed. A closing statement sits above a full-width
  recap rail — every part of the deck as a filled node with its label,
  the final node ringed in accent — with a one-line coda and a contact
  footer. The structural bookend to Waypoint and Chapter Gate.
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

# Recap Rail — closing layout

## Intent

Decks that used Waypoint or Chapter Gate dividers made a promise: here
is the map, we will walk it. Recap Rail keeps that promise visibly —
the same track, now with every stop filled and labeled. The audience
sees the whole arc at the moment of goodbye, which is the strongest
comprehension aid a closing can offer.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  IN CLOSING                                           12 / 12  │
│                                                                │
│  THE WHOLE ARC.          ← statement                           │
│                                                                │
│  ●──────────●──────────●──────────●──────────◎                 │
│  INERTIA    DEPTH      EXECUTION  PROOF      NEXT   ← labels   │
│                                                                │
│  One line drawing the moral of the journey.   ← coda           │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  EMAIL · SITE · HANDLE                             NORTHBEAM   │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Statement | x:96, top y:150, max-width 1400px, 1–2 lines | `--lp-font-display`, 108–120px (default 116), weight 700–800, line-height 0.97, letter-spacing −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Recap rail track | x:96 → 1824, y:560, 1px | — | `--lp-line` |
| Nodes | evenly spaced, first at x:96, last at x:1824; filled 12px circles; final node: 16px ring (3px border, open center) | — | filled `--lp-fg-muted`; final ring `--lp-accent` |
| Node labels | centered under each node, 26px below track | `--lp-font-mono`, 14px, uppercase, ls 0.14em | past labels `--lp-fg-muted`; final label `--lp-accent` |
| Coda | x:96, y:700, max-width 1000px | `--lp-font-body`, 24px, line-height 1.55 | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:940, 1px | — | `--lp-line` |
| Footer left (contacts) / right (org) | x:96 / right-aligned x:1824, y:962 | `--lp-font-mono`, 15px, ls 0.08em / uppercase ls 0.12em | `--lp-fg-muted`, separators `--lp-accent` |

## Content constraints (hard limits)

- **Statement:** 1–2 lines, ≤ 18 characters uppercase per line at 116px.
- **Nodes:** 3–6, matching the deck's actual parts in order. The final
  node is not a past part — it is the next step ("Next", "Q3", "You"),
  which is why it is a ring, not a fill: open, not yet done.
- **Node labels:** ≤ 12 characters each. Every node is labeled — this
  is the recap; Waypoint's one-label discipline does not apply here.
- **Coda:** 1–2 lines, ≤ 140 characters. Optional.

## Image variant

**With images:** each *past* node's label may gain a 240×150 thumbnail
above the track (its bottom edge 24px above the track, centered on the
node) — a filmstrip of the deck's chapters. The final ring node never
gets a thumbnail; its future is the point. All past nodes get thumbs
or none.

**Recommended size / placeholder:** `https://placehold.co/240x150`.
**Dimension fallback:** fixed 240×150 frames, `object-cover`,
token CSS fill behind each `<img>`. Thumbnails are optional.

**Without images:** the pure rail above; statement may grow to 120px.

## Choreography

1. `0.00s` — kicker and counter fade, 0.5s; statement rises
   `translateY(44px→0)` + fade at `0.1s`, 0.7s.
2. `0.45s` — track wipes `scaleX(0→1)`, origin left, 0.8s.
3. `0.70s` — nodes and labels (and thumbs) pop/fade left-to-right,
   0.35s each, 0.1s stagger; the final ring pops last and its label
   fades at `+0.15s`.
4. `1.20s` — coda and footer fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Nodes** → the system's marker vocabulary; filled-vs-ring must stay
  legible as done-vs-open.
- **Thumbnails** → the system's image chrome (hairline border, corner
  ticks) at the same geometry.
- **Track** → the system's hairline style.

## Failure modes to avoid

- Inventing parts that weren't in the deck to fill the rail.
- A filled final node — the open ring is the message.
- Skipping node labels (that's Waypoint, a divider, not a recap).
- More than 6 nodes: collapse minor parts before crowding the rail.
