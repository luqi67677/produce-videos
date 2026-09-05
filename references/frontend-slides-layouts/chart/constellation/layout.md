---
version: 1.0
name: Constellation
slot: chart
description: >
  Labeled scatter for positioning stories. 6–10 named points on a
  field bounded by two bare rails — no ticks, no grid, just min and
  max printed at each rail's ends and the two dimensions named. Every
  point carries its label directly; one point (usually "us") is the
  accent. No quadrant shading, no bubble sizes — position is the
  only encoding.
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

# Constellation — chart layout

## Intent

"Where do we sit in the field?" is a two-dimensional question, and
every honest answer is a scatter. Constellation strips the consulting
theater from it — **no magic-quadrant shading, no bubble sizes, no
"LEADERS" corner label** — and leaves named points in honest
positions. The audience finds the accent point themselves, which is
the persuasion: discovered positions convince; announced ones don't.
Use it for 6–10 entities measured on two stated dimensions.

## The chart contract (inherited refusals)

No gridlines, no ticks. The two rails are bare hairlines whose
printed end-values declare the spans — and the reading line admits
the spans cover the data, not zero. No legend: every point is
labeled directly. One encoding (position); point sizes are uniform.
Exactly one accent element (the claimed point + its label).

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  The field, measured                      ← headline           │
│  PRECISION VS COST · RAILS SPAN THE DATA, NOT ZERO             │
│  98% ┐                                                         │
│      │    ▪ Halcyon (accent)              ▪ Saros              │
│      │                       ▪ Corvus                          │
│      │              ▪ Vireo                                    │
│      │                             ▪ Tessel                    │
│      │         ▪ Quanta   ▪ Ostra                              │
│  80% └──────────────────────────────────────────────────       │
│      $4         COST PER STREAM / MONTH →           $28        │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / METHOD                                   06 / 12     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px** left/right
margins, **72px** top/bottom margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72, single line | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Branding slot (top-right, optional) | right-aligned to x:1824, y:66, ≤ 40px tall, ≤ 260px wide | wordmark in `--lp-font-display` 700 or an image logo | `--lp-fg` |
| Chrome hairline | x:96 → 1824, y:118, 1px | — | `--lp-line` |
| Headline | x:96, y:164, max-width 1400px, 1 line | `--lp-font-display`, 60px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Reading line | x:96, y:242, single line | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` |
| Plot field | x:460 → 1760, y:330 → 850 | — | — |
| Left rail | vertical 1px at x:460, y:330 → 850 | — | `--lp-line` |
| Bottom rail | horizontal 1px at y:850, x:460 → 1760 | — | `--lp-line` |
| Rail end values | y-max left of rail top, y-min left of rail bottom; x-min under rail left, x-max under rail right | `--lp-font-mono`, 17px | `--lp-fg-muted` |
| Dimension names | y-dimension: rotated 90° along the left rail's middle, 24px left of it; x-dimension: centered under the bottom rail, y:886 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.14em, x-name suffixed "→", y-name "↑" | `--lp-fg-muted` |
| Points (×6–10) | 14×14px squares at their honest coordinates | — | `--lp-fg-muted` |
| Accent point | 20×20px square | — | `--lp-accent` |
| Point labels | 12px offset from each point, flowed away from the nearest edge and from collisions | `--lp-font-mono`, 17px | `--lp-fg`; accent label `--lp-accent`, weight 500 |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source/method) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **6–10 points, every one labeled.** Fewer than 6 is a Fulcrum or
  Ledger Versus comparison; unlabeled points are rumors.
- **Two dimensions, both honestly measurable** and named in plain
  words. If one axis is "vision" or "completeness," this is a
  Gartner cosplay, not a chart — refuse it.
- **Spans:** rails run from data-min to data-max with ~5% padding;
  end values printed. The reading line MUST carry the "rails span
  the data, not zero" admission (or "zeroed" when they are).
- **Uniform point size** except the accent point (+6px). No third
  encoding: no bubbles, no shape coding, no per-point color.
- **One accent point** — the entity the deck argues for. Its
  advantage must be visible in position, or this chart hurts you.
- **Labels never overlap** points or each other — nudge or shorten
  names (≤ 12 characters) until they don't.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

None — chart presets carry data, not imagery.

## Choreography

The sky fills, then the claimed star rises, total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — rails draw (left rail `scaleY` origin bottom, bottom
   rail `scaleX` origin left), 0.6s together; end values and
   dimension names fade 0.2s later.
4. `0.60s` — neutral points pop `scale(0→1)` 0.35s each, 0.07s
   stagger in no particular order (a sky, not a sequence); labels
   fade with their points.
5. `1.25s` — the accent point pops last with its label, 0.45s —
   found, not announced, but it does arrive last.
6. `1.40s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Points** → the system's point vocabulary (circles, diamonds),
  uniform, ≤ 16px; the accent point keeps its +6px lead.
- **Rails** → the system's axis-line treatment; never gain ticks.
- **Dimension names** → may sit in the system's label chips.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Quadrant lines, shaded zones, or corner epithets ("LEADERS") —
  the moment the field is prejudged, the chart stops being evidence.
- Bubble sizes, logos as points, or per-competitor colors.
- Trend/regression lines through the cloud (that's a different
  argument and usually a false one at n=8).
- Cropping the field so the accent point flatters — the printed
  spans keep this auditable; keep them truthful.
- Axis dimensions nobody can measure ("innovation").
- Branding larger than 40px tall or anywhere but the reserved corner.
