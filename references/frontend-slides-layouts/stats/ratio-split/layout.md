---
version: 1.0
name: Ratio Split
slot: stats
description: >
  Before faces after. Two display-scale figures confront each other
  across a centered accent arrow — the old number muted on the left,
  the new number at full contrast on the right, the delta chip beneath
  the arrow. One change, made physical.
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

# Ratio Split — stats layout

## Intent

"Latency fell from 91ms to 38ms" is a sentence; two enormous numbers
with an arrow between them is an event. The visual grammar carries the
verdict — muted past on the left, bright present on the right, motion
frozen in the middle — so the audience feels the improvement before
they parse it. For exactly one before/after pair; the pack's most
theatrical stat.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       11 / 14  │
│  P99, TWO QUARTERS APART      ← headline                       │
│                                                                │
│                                                                │
│   91ms          ───────▶           38ms                        │
│   (muted)       −58%               (full contrast)             │
│   Q1 BASELINE   ← labels →         Q2, AFTER THE REWRITE       │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  SOURCE / PERIOD                                      VANTAGE  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line | `--lp-font-display`, 72px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Before figure | x:96, top y:400, ≤ 6 glyphs | `--lp-font-display`, 220px, weight 800, line-height 0.9, ls −0.03em | `--lp-fg-muted` |
| Before label | x:96, 32px below figure | `--lp-font-mono`, 15px, uppercase, ls 0.16em | `--lp-fg-muted` |
| Arrow | centered on x:960, y:500; 220px long shaft (3px) with a solid head | — | `--lp-accent` |
| Delta chip | centered on x:960, 36px below the arrow | `--lp-font-mono`, 22px, weight 500, ls 0.06em | `--lp-accent` |
| After figure | right-aligned to x:1824, top y:400 | same as before figure | `--lp-fg`; unit glyph → `--lp-accent` |
| After label | right-aligned to x:1824, 32px below figure | same as before label | `--lp-fg-muted` |
| Footer hairline + source | x:96 → 1824, y:962 / y:984 | mono 14px | `--lp-line` / `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly one pair,** same unit and precision on both sides ("91ms →
  38ms", never "91ms → fast").
- **Figures:** ≤ 6 glyphs including unit. **Labels:** 1 line ≤ 30
  characters each, naming the period or condition.
- **Delta chip:** the computed change ("−58%", "+3.1×"), ≤ 7 glyphs.
  It must be arithmetically consistent with the figures.
- **Improvement flows left → right.** If the number got worse and
  that's the story, the muted/bright roles swap — muted is always
  "then", bright is always "now".

## Image variant

**With an image:** full-bleed behind everything under a heavy scrim
(`--lp-bg` at ≥ 90%) — the setting of the measurement, as texture.
**Recommended size / placeholder:** `https://placehold.co/1920x1080`.
**Dimension fallback:** full-bleed frame, `object-cover`, flat
`--lp-bg` behind the `<img>`. The image is optional and usually
omitted.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.35s` — before figure and label fade in (no rise — the past
   doesn't move), 0.6s.
3. `0.60s` — arrow shaft wipes `scaleX(0→1)` origin left, 0.5s; head
   pops at `1.0s`.
4. `0.95s` — after figure rises `translateY(48px→0)` + fade, 0.7s;
   its label at `1.15s`.
5. `1.25s` — delta chip pops `scale(0→1)`, 0.4s; footer fades, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Decks with a counting
vocabulary may count the after-figure up. Under
`prefers-reduced-motion`, no transforms.

## Skin points

- **Arrow** → the system's connector vocabulary (its em-dash chain,
  a tapered rule); must stay horizontal and centered.
- **Delta chip** → the system's tag/badge treatment.
- **Figures** → the system's stat treatment (serif figures, mono
  digits).

## Failure modes to avoid

- Two pairs on one slide — the confrontation only works solo.
- A delta that doesn't match the arithmetic, or units that differ
  across the arrow.
- Equal visual weight on both figures; the contrast hierarchy is the
  verdict.
