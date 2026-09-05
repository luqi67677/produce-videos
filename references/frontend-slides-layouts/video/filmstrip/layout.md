---
version: 1.0
name: Filmstrip
slot: video
description: >
  Playlist grammar. A main 960×540 player under an editorial header,
  with an "up next" rail of 2–3 thumbnail rows (poster, title,
  duration) on the right — for the slide that carries a small library
  of clips, one of which leads.
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

# Filmstrip — video layout

## Intent

When there are several clips (three regional demos, before/during/after
footage), cramming them into equal tiles buries the lead. Filmstrip
ranks them: one clip earns the player, the rest wait in a labeled rail
with honest durations. In a live talk the presenter plays the main
clip and gestures at the rail; in an exported deck the rail documents
what footage exists and how long each piece runs.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       09 / 14  │
│  THREE SITES ON TAPE      ← headline                           │
│                                                                │
│  ┌──────────────────────────────┐   UP NEXT ── rail label      │
│  │                              │   ┌─────┐ Harbor east        │
│  │        main player           │   └─────┘ 01:42              │
│  │        (poster + ▶)          │   ┌─────┐ Metro hub          │
│  │                              │   └─────┘ 02:10              │
│  └──────────────────────────────┘   ┌─────┐ Airport apron      │
│  JAKARTA NORTH — 02:56 ← caption    └─────┘ 01:18              │
└────────────────────────────────────────────────────────────────┘
      x:96→1056                          x:1152→1824
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line, max-width 1200px | `--lp-font-display`, 84px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Main player | x:96 → 1056 (960×540), y:320 → 860; 1px border | — | border `--lp-line` |
| Play glyph | centered on main player, 88px circle | — | as Screening Room |
| Main caption | x:96, y:884, single line | `--lp-font-mono`, 13px, uppercase, ls 0.14em | `--lp-fg-muted` |
| Rail label | x:1152, y:320 | `--lp-font-mono`, 14px, uppercase, ls 0.2em | `--lp-accent` |
| Rail rows | x:1152 → 1824, first row top y:370; each row: 240×135 thumb left + text right (24px gap), 1px hairline above rows 2+, rows 40px apart | row title: `--lp-font-display` 24px weight 700; duration: `--lp-font-mono` 13px, 8px below title | title `--lp-fg`, duration `--lp-fg-muted`, hairlines `--lp-line` |

## Content constraints (hard limits)

- **Exactly one main player.** The lead clip is a decision, not a
  layout accident — make it the one you would keep if only one
  survived.
- **Rail:** 2–3 rows. One row is a footnote (drop the rail, use
  Screening Room); four rows is an archive, not a slide.
- **Row titles:** 1 line ≤ 22 characters. **Durations:** `MM:SS`,
  required — a rail without durations is a mystery-meat menu.
- **Headline:** 1 line ≤ 30 characters.

## Video embed & fallbacks

- **Main player embed:** local `<video controls preload="metadata"
  poster="...">` preferred; hosted `<iframe>` at the same geometry.
  Never autoplay. Rail thumbs are posters (images), optionally click-
  swapping into the main player in presenter decks — an enhancement,
  never required.
- **Poster / placeholders:** main `https://placehold.co/960x540`;
  rail thumbs `https://placehold.co/480x270` (2× for sharpness at
  240×135).
- **Dimension fallback:** fixed frames throughout, posters
  `object-cover`, token CSS fill behind every poster.
- **No-video variant:** posters as stills turn this into a gallery
  slide — acceptable for exported decks; keep durations only if the
  clips exist somewhere reachable.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.35s` — main player settles (1.02→1 + fade), 0.9s; play glyph at
   `0.85s`; caption at `1.0s`.
3. `0.55s` — rail label fades; rows fade up top-to-bottom, 0.5s each,
   0.12s stagger.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Thumb chrome** → the system's image chrome; thumbs and main player
  must share it.
- **Durations** → the system's tag treatment (chips, brackets).
- **Rail hairlines** → the system's divider vocabulary.

## Failure modes to avoid

- Equal-sizing the clips into a grid — ranking is the layout's point.
- Rail rows without durations, or titles that wrap.
- Playing rail clips inline at thumb size; they swap into the main
  player or they wait.
