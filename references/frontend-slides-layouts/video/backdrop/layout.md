---
version: 1.0
name: Backdrop
slot: video
description: >
  Ambient video. A muted, looping full-bleed clip runs behind a heavy
  scrim; a statement holds the lower-left and one outlined "watch the
  full film" chip is the only control. The video is atmosphere with an
  exit to the real thing.
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

# Backdrop — video layout

## Intent

Sometimes the footage should be felt, not watched: drone passes over a
site, timelapse of the ops floor, product running in the wild. Backdrop
runs it silent and looping as the slide's weather, keeps the words
readable under a strong scrim, and offers exactly one deliberate exit —
the chip that leads to the full film. This is the only preset in the
pack where autoplay is correct, and only because it is muted.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       03 / 14  │
│                                                                │
│           (muted looping video, full bleed, scrimmed)          │
│                                                                │
│ ░░░░░░░░░░░░░░░░░░░░ scrim deepens ░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  FORTY SITES,                                                  │
│  ALWAYS ON.            ← statement                             │
│  [ ▶ WATCH THE FULL FILM — 03:58 ]   ← outlined chip           │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Video layer | full bleed, `object-cover`, muted loop | — | — |
| Scrim | full bleed: uniform `--lp-bg` at 45% plus a bottom gradient to `--lp-bg` at 94% from y:480 down | — | — |
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Statement | x:96, bottom edge ≈ y:856, max-width 1400px, 1–2 lines | `--lp-font-display`, 128–140px (default 140), weight 700–800, line-height 0.95, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Watch chip | x:96, 40px below statement; outlined pill, 1px border, padding 16×28; small play triangle + label inline | `--lp-font-mono`, 15px, uppercase, ls 0.14em | border `--lp-line`, triangle `--lp-accent`, label `--lp-fg` |

## Content constraints (hard limits)

- **Statement:** 1–2 lines, ≤ 13 characters uppercase per line at
  140px.
- **Chip:** 1 line, ≤ 40 characters, always naming the runtime. One
  chip only — it is a doorway, not a menu.
- **Footage:** slow, low-contrast motion (drone, timelapse, ambient
  machine). Cuts, faces, or on-screen text in the loop fight the
  statement.
- **Loop length:** 8–30s, seamless or cross-faded.

## Video embed & fallbacks

- **Embed:** `<video autoplay muted loop playsinline preload="auto"
  poster="...">` — autoplay is permitted here **only because it is
  muted**; browsers require `muted` + `playsinline` for it to work at
  all. No controls; the chip links to the full film (next slide, a
  lightbox, or an external URL).
- **Poster / placeholder:** `https://placehold.co/1920x1080` — the
  poster shows until the loop buffers, so it must look correct as a
  still.
- **Dimension fallback:** full-bleed frame, `object-cover`; keep
  a token CSS atmosphere behind the video element for load failures.
- **No-video variant:** the poster as a static full-bleed image — the
  slide becomes Cover Caption's grammar with a chip — or the CSS
  atmosphere alone. The video is optional.
- **Reduced motion:** under `prefers-reduced-motion`, do not autoplay;
  show the poster (pause the element via JS or omit `autoplay` when
  the media query matches).

## Choreography

1. `0.00s` — poster/video fades in, 1.0s; scrim with it.
2. `0.40s` — statement lines rise `translateY(56px→0)` + fade, 0.8s,
   0.12s stagger.
3. `0.90s` — chip fades up, 0.5s.
4. `1.00s` — kicker and counter fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms and no autoplay.

## Skin points

- **Chip** → the system's button/tag vocabulary (its pill, its
  bracket-chip); keep the runtime in the label.
- **Scrim** → the system's fullbleed scrim convention; legibility over
  the statement zone is the hard rule.
- **Loop treatment** → the system's duotone/grain may be applied via
  CSS filter on the video element.

## Failure modes to avoid

- Sound. Ever. Autoplay with audio is the fastest way to lose a room.
- Busy footage that makes the statement shimmer — when in doubt,
  darken the scrim before swapping the clip.
- Multiple chips or embedded controls; one doorway.
- Using Backdrop for content that must be *watched* — that is
  Screening Room's job.
