---
version: 1.0
name: Screening Room
slot: video
description: >
  Centered cinema. One bordered 16:9 player holds the middle of a dark
  stage; the film's title and runtime sit on its lower edge like a
  festival program line. Nothing competes with the screen — the slide
  is the room going dark.
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

# Screening Room — video layout

## Intent

For the moment the deck stops talking and shows the film. The player is
centered and generously margined so the act of playing it feels like an
event, and the program line beneath (title left, runtime right) frames
it as a *screening*, not an embedded asset. Best for demo videos,
launch films, and any clip longer than a minute that deserves full
attention.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       07 / 14  │
│      ┌──────────────────────────────────────────────────┐      │
│      │                                                  │      │
│      │                 16:9 player                      │      │
│      │                (poster + ▶)                      │      │
│      │                                                  │      │
│      └──────────────────────────────────────────────────┘      │
│      THE ROLLOUT FILM                     04:32 — SOUND ON      │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Player | x:320 → 1600 (1280×720), y:150 → 870; 1px border; media flush inside | — | border `--lp-line` |
| Play glyph | centered on the player: 96px circle, 1.5px border, triangle inside | — | `--lp-fg` at 90%, on a `--lp-bg` 35% scrim disc |
| Program line left (title) | x:320, y:904 | `--lp-font-display`, 40px, weight 700 | `--lp-fg` |
| Program line right (runtime/meta) | right-aligned x:1600, y:916 | `--lp-font-mono`, 15px, uppercase, ls 0.14em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 1 line, ≤ 36 characters. The film's name, not a sentence.
- **Meta:** 1 line, ≤ 32 characters — runtime, and "sound on" if the
  clip needs audio.
- **Nothing else on the slide.** No lead, no bullets; context belongs
  on the slide before the screening.

## Video embed & fallbacks

- **Preferred embed:** a local `<video controls preload="metadata"
  poster="...">` filling the player frame. For hosted video, an
  `<iframe>` (YouTube/Vimeo, `allowfullscreen`) at the same geometry.
  Never autoplay with sound.
- **Poster / placeholder:** `https://placehold.co/1280x720` — the
  poster is required; it is what the room sees until play is pressed.
- **Dimension fallback:** the frame is fixed 1280×720 with the media at
  `object-cover` (posters) — non-16:9 sources letterbox inside the
  player natively, which is acceptable for video.
- **No-video variant:** the frame holds the poster image alone (this
  becomes an image slide with cinema framing) or is dropped and the
  slide cut — a screening room without a film has no reason to exist.
- **Reduced motion:** never autoplay here regardless; the play glyph
  waits.

## Choreography

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.15s` — player fades in with a 1.02→1 settle, 0.9s.
3. `0.60s` — play glyph fades + scales 0.8→1, 0.5s.
4. `0.75s` — program line fades up, 0.6s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms or settles.

## Skin points

- **Player border** → the system's image/media chrome (corner ticks,
  double hairline). No drop shadows unless the system is elevational.
- **Play glyph** → the system's control vocabulary; keep it ≥ 80px and
  centered — an off-corner play button reads as a thumbnail.
- **Background** → flat `--lp-bg`, ideally the system's darkest
  surface; a screening room is dark even in light design systems (a
  light system may invert this one slide — documented dual-surface
  move).

## Failure modes to avoid

- Shrinking the player to fit commentary beside it — that is Side
  Reel's layout, not this one.
- Autoplay of any kind; the presenter presses play.
- A poster with burned-in title text fighting the program line.
