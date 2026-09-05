---
version: 1.0
name: Turnabout
slot: case
description: >
  One case study told in three labeled bands — SITUATION, THE MOVE,
  RESULT — each a single narrative sentence at display scale with its
  one metric standing at the right margin. The result band's metric
  carries the accent. A complete story with a before, an action, and
  a number that changed, on one slide.
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

# Turnabout — case layout

## Intent

Case studies sprawl across four slides and lose the room by slide
two. Turnabout compresses one engagement to **its narrative spine**:
what was broken, what was done, what the number says now. The
three-band structure IS the story grammar — remove any band and it
stops being a case (a result without a situation is a brag; a move
without a result is a confession). Use one Turnabout per case; three
cases means three slides, not nine.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CASE NAME                      [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│  SITUATION   Container thefts averaged nine a        9 /mo     │
│              month across the blind northern yard.            │
│  ─────────────────────────────────────────────────────────     │
│  THE MOVE    Forty-two cameras, thermal at the      42 cams    │
│              fence line, wired into dispatch.                  │
│  ─────────────────────────────────────────────────────────     │
│  RESULT      Thefts fell under one a month —       0.7 /mo     │
│              and stayed there for a year.         ← accent     │
│                                                                │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / VERIFICATION                             07 / 12     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px** left/right
margins, **72px** top/bottom margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72, single line — names the case and period | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Branding slot (top-right, optional) | right-aligned to x:1824, y:66, ≤ 40px tall, ≤ 260px wide | wordmark in `--lp-font-display` 700 or an image logo | `--lp-fg` |
| Chrome hairline | x:96 → 1824, y:118, 1px | — | `--lp-line` |
| Bands (×3) | tops at y:200, 450, 700; each ~230px tall; hairlines at y:430 and y:680 between them | — | rules `--lp-line` |
| Band tags | x:96, top-aligned +54px into each band | `--lp-font-mono`, 17px, uppercase, letter-spacing 0.16em | `--lp-fg-muted`; RESULT tag `--lp-accent` |
| Narratives | x:380, vertically centered per band, max-width 1030px, ≤ 2 lines | `--lp-font-display`, 36px, weight 700, line-height 1.25 | `--lp-fg` |
| Metrics | right-aligned to x:1824, vertically centered per band | `--lp-font-mono`, 46px, weight 500; a small mono unit line ≤ 14 chars may sit under it at 15px | `--lp-fg-muted`; RESULT metric `--lp-accent` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (verification) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 bands, in story order:** SITUATION → THE MOVE →
  RESULT (tags may be reworded — "BEFORE / WHAT WE DID / AFTER" —
  but keep the order and keep them ≤ 12 characters).
- **Narratives:** ≤ 110 characters, ≤ 2 lines, one sentence each,
  concrete nouns. The three sentences must read as one story when
  spoken in sequence — test aloud.
- **Metrics:** ≤ 8 characters plus an optional unit line. The
  SITUATION and RESULT metrics must be THE SAME MEASURE (thefts/mo
  → thefts/mo) so the turnabout is arithmetic, not vibes; THE
  MOVE's metric sizes the intervention.
- **The RESULT band alone carries accent** (tag + metric).
- **Verification line:** who can confirm this (client name if
  cleared, "reference available", audit source). A case nobody may
  verify is a rumor.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

**With a site photo:** narratives may narrow to 820px and a single
360×560 portrait-orientation photograph of the site may run down
the right side (x:1464 → 1824, y:200 → 760), with the metrics
moving inline after each narrative (same ink rules). Use only when
the photograph is of THIS case's site.

**Recommended size / placeholder:** `https://placehold.co/360x560`.
**Dimension fallback:** fixed frame, `object-fit: cover`, token CSS
fill behind the `<img>`. Optional — the type-only form is the
default.

## Choreography

The story tells itself in order, total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.15s` — SITUATION band: tag fades, narrative rises
   `translateY(24px→0)` + fade (0.6s), metric fades at its right.
3. `0.55s` — first hairline wipes `scaleX(0→1)` origin left, 0.5s;
   THE MOVE band enters the same way.
4. `0.95s` — second hairline wipes; RESULT band enters, its accent
   metric landing last at 1.45s — the payoff beat.
5. `1.50s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Band tags** → the system's label vocabulary (chips, brackets);
  RESULT keeps the accent.
- **Hairlines** → the system's divider vocabulary.
- **Metrics** → the system's numeral face at the same scale.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; the RESULT band may take a
  half-step tint (≤ `--lp-fg-faint`) in systems that shade zones.

## Failure modes to avoid

- A second case squeezed in, or bands split into bullet lists —
  one story, three sentences, three numbers.
- SITUATION and RESULT metrics in different units (the reader must
  be able to divide one by the other in their head).
- A RESULT narrative that hedges ("early indications suggest…") —
  if the result isn't ready to be stated, the case isn't ready to
  be shown.
- Accent on all three metrics.
- Logos of the client without clearance; use the verification line.
- Branding larger than 40px tall or anywhere but the reserved corner.
