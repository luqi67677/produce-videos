---
version: 1.0
name: Plate Caption
slot: image
description: >
  Image-feature content slide. A large framed plate (screenshot, photo,
  diagram) fills the right 55% of the stage; the left column carries a
  figure number, kicker, title, and reading — museum-label grammar.
  Without an image, the plate holds the system's texture and an
  oversized keyword.
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

# Plate Caption — image layout

## Intent

Screenshots dropped onto slides read as evidence dumps. Framing the
image as a *plate* — hairline border, figure number, a label column
that interprets rather than repeats — turns the same pixels into an
exhibit. The audience looks at the image the way the deck wants them
to, because the label told them what they are looking at and why it
matters.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       06 / 14  │
│                          ┌───────────────────────────────────┐ │
│  FIG. 06 ← figure no.    │                                   │ │
│                          │                                   │ │
│  THE CONSOLE,            │        framed plate               │ │
│  FINALLY WHOLE  ← title  │        (object-fit cover)         │ │
│                          │                                   │ │
│  Reading: what the image │                                   │ │
│  proves, in 2–4 lines.   │                                   │ │
│                          └───────────────────────────────────┘ │
│                            PROVISION → MONITOR → AUDIT ← strip │
└────────────────────────────────────────────────────────────────┘
       x:96→704                     x:800→1824
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Figure number | x:96, y:170 | `--lp-font-mono`, 16px, uppercase, ls 0.2em | `--lp-accent` |
| Title | x:96, top y:230, max-width 608px, 2–3 lines | `--lp-font-display`, 68–76px (default 76), weight 700–800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Reading | x:96, 36px below title, max-width 560px | `--lp-font-body`, 21px, line-height 1.6 | `--lp-fg-muted` |
| Plate | x:800 → 1824, y:120 → 900; 1px border; image inset flush, `object-cover` | — | border `--lp-line` |
| Caption strip | x:800 → 1824, y:924, single line below the plate | `--lp-font-mono`, 13px, uppercase, ls 0.14em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **One plate per slide.** A second image is a second slide (or a
  grid slide the deck designs in its own system).
- **Title:** 2–3 lines, ≤ 16 characters per line at 76px.
- **Reading:** 2–4 lines, ≤ 220 characters — it says what the image
  *proves*, never "as you can see" narration.
- **Figure number:** "FIG." + the slide's position or an exhibit
  index; sequential across the deck's image slides.
- **Caption strip:** 1 line ≤ 70 characters — literal what/where/when.

## Image variant

This preset is image-first; the case above is the image case.

**Recommended size / placeholder:** `https://placehold.co/1024x780`.
**Dimension fallback:** the plate is a fixed 1024×780 frame with
`object-cover` — screenshots of any ratio fill it; if the exact
pixels matter (UI detail), switch that plate to `object-contain`
with the frame's own background visible as matting. Keep a token CSS
fill behind the `<img>` for load failures.

**Without an image:** the plate stays — filled with the design
system's texture fingerprint (or layered `--lp-fg-faint` gradients)
and one oversized outline keyword (≈ 160px, the subject's name)
centered in it. The caption strip then reads as a definition line.
Use this when the artifact isn't ready but the slide's place in the
argument is.

## Choreography

1. `0.00s` — kicker, counter fade, 0.5s.
2. `0.10s` — plate fades in with a 1.02→1 settle, 0.9s; caption strip
   at `0.7s`.
3. `0.25s` — figure number fades; title lines rise `translateY(36px→0)`
   + fade, 0.65s, 0.12s stagger.
4. `0.70s` — reading fades up, 0.6s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms or settles.

## Skin points

- **Plate border** → the system's image chrome (corner ticks, doubled
  hairline, small mat). No drop shadows unless the system is
  explicitly elevational.
- **Figure number** → the system's label/tag treatment.
- **Annotations** → the system may add ≤ 3 small callout markers on
  the plate (numbered dots), explained in the reading — never text
  boxes on the image itself.

## Failure modes to avoid

- Full-bleeding the image "to make it bigger" — that is Cover
  Caption's job; the frame and label are this slide's meaning.
- A title that names the artifact ("Console screenshot") instead of
  the claim ("The console, finally whole").
- Letterboxing inside the plate with visible dead bands — pick cover
  or a deliberate contain-with-matting, never accidental bars.
