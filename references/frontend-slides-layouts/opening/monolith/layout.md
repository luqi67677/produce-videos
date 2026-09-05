---
version: 1.0
name: Monolith
slot: opening
description: >
  Centered monumental opening. A massive stacked title sits dead-center
  under a thin "plumb line" dropping from the top edge, with a wide-tracked
  inscription beneath it and deck metadata pinned to the four corners.
  Radically symmetric — the counterpoint to Offset Marquee.
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

# Monolith — opening layout

## Intent

Where Offset Marquee is editorial and asymmetric, Monolith is **ceremonial
and symmetric**: one enormous centered statement, weighted like an
inscription on stone. The composition's tension comes from scale contrast —
four whisper-quiet corner labels against a title that owns the center.
The plumb line is the single decorative device: a thin accent line falling
from the top edge to point at the title.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL              │                    08 JUL 2026  │ ← corners
│                              │  ← plumb line, 2px, y:0→210     │
│                              │                                 │
│                        TEN YEARS                                │
│                         DEEPER            ← centered title      │
│                                                                │
│            A  L E T T E R  O N  T H E  D E C A D E             │ ← inscription,
│                                                                │   wide tracking
│                                                                │
│  PRESENTER — ORG                                      01 / 14  │ ← corners
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Corner insets: **96px**
left/right, **72px** top/bottom.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Corner top-left (kicker) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Corner top-right (date/event) | right-aligned to x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Corner bottom-left (presenter — org) | x:96, y:984 | same as top-right | `--lp-fg-muted` |
| Corner bottom-right (counter) | right-aligned to x:1824, y:984 | same as top-right | `--lp-fg-muted` |
| Plumb line | x:959, y:0 → y:210, 2px wide | — | `--lp-accent` |
| Title | horizontally centered, vertical center ≈ y:520, max-width 1728px, text-align center | `--lp-font-display`, 180–208px (default 200), weight 700–800, line-height 0.95, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Inscription | centered, 56px below title | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.35em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 1–2 lines, each line in its own span. At 200px a line fits
  roughly **10–11 characters uppercase** or **12–13 mixed case**; verify
  after applying the design system's face, stepping down to 180px at most.
  Never 3 lines — a 3-line center stack loses the monumental register.
- **Inscription:** single line, ≤ 60 characters including tracking.
  Optional but strongly recommended — it grounds the symmetry.
- **Corners:** one line each, real deck chrome only. All four corners must
  be occupied; an empty corner breaks the balance. Natural fills: kicker,
  date/event, presenter — org, counter.

## Image variant

**With an image:** a 160×160 framed image (1px `--lp-line` border)
hangs at the plumb line's end — centered on x:960, its top edge at
y:210, the line shortening to meet it. The image must read as an
emblem (a mark, a detail crop, a medallion portrait), not a scene;
symmetric content only.

**Recommended size / placeholder:** `https://placehold.co/320x320`
(2× for sharpness at 160px). **Dimension fallback:** fixed 160×160
frame, `object-cover`, token CSS fill behind the `<img>`. The
image is optional — the bare plumb line is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.4s:

1. `0.00s` — plumb line draws downward via `transform: scaleY(0→1)`,
   `transform-origin: top`, 0.7s.
2. `0.30s` — title lines rise: `translateY(40px→0)` + slight
   `scale(0.97→1)` + fade, 0.8s, 0.12s stagger per line.
3. `0.85s` — inscription fades up, 0.6s.
4. `1.00s` — all four corners fade in together, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Plumb line** → the system's linear device (double rule, dotted drop,
  a hanging glyph or ornament) — same axis (x:960), length 160–260px,
  colored `--lp-accent`.
- **Inscription** → the system's label treatment; keep tracking ≥ 0.25em.
- **`<em>` treatment** → the system's emphasis move, colored `--lp-accent`.
- **Background** → flat `--lp-bg` by default; a centered/radial
  atmospheric treatment is allowed if it stays symmetric and preserves
  text contrast. Directional or corner-weighted backgrounds break this
  layout — use Offset Marquee instead.

## Failure modes to avoid

- Adding any left/right-weighted element (logos, ghost numerals, side
  rails). Monolith tolerates zero asymmetry; one logo is permitted only
  centered above the plumb line's origin, ≤ 40px tall.
- Long titles. If the title can't say it in two short lines, this is the
  wrong preset.
- Letting the plumb line touch the title — keep ≥ 80px clearance.
- Corner text longer than one line, or in body type instead of mono/label.
