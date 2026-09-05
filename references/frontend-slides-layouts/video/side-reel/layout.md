---
version: 1.0
name: Side Reel
slot: video
description: >
  Annotated player. The video sits right at 1088×612; the left column
  carries kicker, title, a short reading, and a timestamped chapter
  list in mono — so the presenter can jump, and the audience knows
  what they are about to watch before it plays.
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

# Side Reel — video layout

## Intent

Screening Room asks for full attention; Side Reel earns partial
attention honestly. The chapter list is the working device — mono
timestamps that tell the room what happens at 00:00, 01:24, 03:05 —
so a presenter can scrub to the beat that matters, and a reader of the
exported deck still learns the video's structure without pressing
play. Best for product demos and walkthroughs discussed while paused.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       08 / 14  │
│                                                                │
│  CONSOLE, IN          ┌──────────────────────────────────┐     │
│  MOTION   ← title     │                                  │     │
│                       │          16:9 player             │     │
│  Reading line.        │         (poster + ▶)             │     │
│                       │                                  │     │
│  00:00  Cold open     └──────────────────────────────────┘     │
│  01:24  Provisioning    CONSOLE V2.4 — RECORDED JUL 2026 ← cap │
│  03:05  Audit trail                                            │
└────────────────────────────────────────────────────────────────┘
     x:96→640                    x:736→1824
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Title | x:96, top y:170, max-width 544px, 2–3 lines | `--lp-font-display`, 64–72px (default 72), weight 700–800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Reading | x:96, 32px below title, max-width 500px | `--lp-font-body`, 20px, line-height 1.55 | `--lp-fg-muted` |
| Chapter list | x:96, top y:600, width 544px; 3–4 rows, 1px hairline above each, 22px padding top and bottom | timestamp: `--lp-font-mono` 15px ls 0.1em; beat: `--lp-font-body` 19px, 24px gap after timestamp | timestamp `--lp-accent`, beat `--lp-fg`, hairlines `--lp-line` |
| Player | x:736 → 1824 (1088×612), y:234 → 846, vertically centered; 1px border | — | border `--lp-line` |
| Play glyph | centered on the player, 88px circle | — | as Screening Room |
| Caption strip | x:736, y:870, single line | `--lp-font-mono`, 13px, uppercase, ls 0.14em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 2–3 lines, ≤ 12 characters uppercase per line at 72px.
- **Reading:** 1–3 lines, ≤ 140 characters. Optional.
- **Chapters:** 3–4 rows, chronological; timestamps `MM:SS`; beat text
  1 line ≤ 28 characters. Two chapters is a caption, five is a table
  of contents — wrong slide either way.
- **Caption strip:** 1 line ≤ 60 characters — artifact + record date.

## Video embed & fallbacks

- **Preferred embed:** local `<video controls preload="metadata"
  poster="...">` in the frame; hosted `<iframe>` at the same geometry
  otherwise. Never autoplay with sound.
- **Poster / placeholder:** `https://placehold.co/1088x612`.
- **Dimension fallback:** fixed 1088×612 frame; posters `object-cover`;
  non-16:9 video letterboxes natively inside the frame.
- **No-video variant:** keep the layout with the poster as a still
  (the chapter list becomes a step list) — or use Plate Caption if no
  chapter structure exists. The video is optional; the chapter list
  is not.

## Choreography

1. `0.00s` — kicker, counter fade, 0.5s.
2. `0.10s` — title lines rise `translateY(36px→0)` + fade, 0.65s,
   0.12s stagger; reading at `0.5s`.
3. `0.25s` — player settles in (1.02→1 + fade), 0.9s; play glyph at
   `0.75s`; caption at `0.9s`.
4. `0.65s` — chapter rows: hairline wipes + row fades up, 0.5s each,
   0.12s stagger.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Timestamps** → the system's label/tag treatment; may become
  outlined chips.
- **Player border / hairlines** → the system's chrome and divider
  vocabulary.
- **Chapter rows** → in presenter decks, rows may act as scrub links
  (`video.currentTime = t`) — an enhancement, never a requirement.

## Failure modes to avoid

- Chapter beats written as sentences — they are titles of moments.
- Moving the chapter list under the player; the left column is the
  reading order (what → why → when), the player is the payoff.
- A player so small the poster is illegible — 1088×612 is the floor;
  cut the reading before shrinking the player.
