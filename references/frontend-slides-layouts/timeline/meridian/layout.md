---
version: 1.0
name: Meridian
slot: timeline
description: >
  Horizontal timeline content slide. A full-width track carries 3–5
  dated entries alternating above and below the line, each tethered by
  a short vertical tick — date in mono accent, title in display, one
  line of description. Optional thumbnail per entry on its outward side.
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

# Meridian — timeline layout

## Intent

Timelines die by crowding: every event stacked on one side, arrows,
boxes. Meridian alternates entries above and below the track so each
gets its own air, and the tick — a plain vertical hairline — replaces
every arrow and connector. Chronology reads left to right, hierarchy
reads by distance from the line. Unlike the section-slot rails
(Waypoint, Recap Rail), this is a *content* slide: real dates, real
events.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       05 / 14  │
│  HOW WE GOT HERE          ← headline                           │
│                                                                │
│      MAR 2025                        JAN 2026                  │
│      First pilot                     Series B                  │
│      One camera, one dock.           Fuel for the fleet.       │
│         │                               │                      │
│  ───────●───────────●───────────●───────●──────────●────────   │
│                     │           │                  │           │
│              SEP 2025      NOV 2025           JUL 2026         │
│              12 sites      Edge launch        Today            │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line | `--lp-font-display`, 84px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Track | x:96 → 1824, y:640, 1px | — | `--lp-line` |
| Nodes | on the track at each entry's x; 10px filled circles; the final ("today") node 14px | — | `--lp-fg-muted`; final node `--lp-accent` |
| Ticks | vertical 1px, 40px long, from node upward (above-entries) or downward (below-entries) | — | `--lp-line` |
| Entries | max-width 300px each, anchored at the tick's far end (above entries sit bottom-anchored 56px above the track; below entries top-anchored 56px below) | date: `--lp-font-mono` 14px uppercase ls 0.16em; title: `--lp-font-display` 30px weight 700, 8px below date; desc: `--lp-font-body` 17px lh 1.45, 8px below title | date `--lp-accent`, title `--lp-fg`, desc `--lp-fg-muted` |

Entry x-positions: distribute nodes across x:180 → 1740 with roughly
equal spacing, alternating above/below starting above.

## Content constraints (hard limits)

- **3–5 entries** in strict chronological order. Six or more → split
  the timeline across two slides at a natural era break.
- **Date:** ≤ 12 characters. **Title:** 1 line ≤ 20 characters.
  **Description:** 1–2 lines ≤ 70 characters.
- **The final entry may be "today"** — accent node, and its description
  may point forward. Only the final node takes accent.
- Entries must not overlap horizontally: with 5 entries keep titles
  short; with wordy entries drop to 4.

## Image variant

**With images:** each entry may carry a 280×158 thumbnail on its
outward side (above the text for above-entries, below the text for
below-entries, 20px gap). All entries get thumbnails or none — the
alternating rhythm must stay symmetric.

**Recommended size / placeholder:** `https://placehold.co/280x158`
(16:9). **Dimension fallback:** fixed 280×158 frames, `object-cover`,
token CSS fill behind each `<img>`. Thumbnails are optional —
with them, headline drops to 72px and the track moves to y:660.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.40s` — track wipes `scaleX(0→1)`, origin left, 0.9s.
3. `0.60s` — per entry, left to right (0.15s stagger): node pops
   `scale(0→1)` 0.3s → tick draws `scaleY(0→1)` from the node 0.3s →
   entry text fades up 0.45s.
4. Final accent node pops last with a slightly larger overshoot.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Nodes/ticks** → the system's marker vocabulary (its timeline dots,
  dashes); tick length may run 32–56px.
- **Dates** → the system's label treatment; keep them the only mono
  element in each entry.
- **Track** → the system's hairline style.

## Failure modes to avoid

- All entries on one side "for alignment" — the alternation is the
  breathing room.
- Arrows, chevrons, or curved connectors. The tick is the connector.
- Paragraph-length descriptions; this is a spine, not a history essay.
- Using Meridian for deck structure (that is Waypoint / Recap Rail).
