---
version: 1.0
name: Terrace
slot: chart
description: >
  Histogram for the shape of one distribution. Ten near-touching
  columns rise from a zero baseline over labeled bin edges; the modal
  bin carries the accent and the only count label. No axis, no grid —
  the silhouette is the finding: skewed, peaked, long-tailed, or
  double-humped, the audience sees which world they're in.
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

# Terrace — chart layout

## Intent

Averages answer "how much," distributions answer **"what kind of
world is this"** — and many arguments (SLAs, latencies, ticket
sizes) turn entirely on the shape: is the mass where we promised,
and how heavy is the tail? Terrace draws that shape with almost no
ink: contiguous columns whose profile the eye reads instantly.
Skyline is for one series marching through TIME; Terrace is one
variable spread over its VALUES. Confusing the two is the fastest
way to lie with columns.

## The chart contract (inherited refusals)

No gridlines, no y-axis. Columns rise from a true zero baseline in
true proportion. Bin edges are labeled directly under the baseline;
equal bin widths only. One count appears — on the modal bin — and
the total N lives in the reading line. Exactly one accent element
(the modal bin + its count). Columns nearly touch (4px gaps):
contiguity is what says "histogram," separation says "categories."

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Most alerts verify in under a minute     ← headline           │
│  VERIFY TIME, SECONDS · N = 4,320 · ZERO-BASED                 │
│                                                                │
│                      1,214 ← modal count (accent)              │
│                     ┌──┐                                       │
│                ┌──┐ │▒▒│ ┌──┐                                  │
│           ┌──┐ │  │ │▒▒│ │  │                                  │
│      ┌──┐ │  │ │  │ │▒▒│ │  │ ┌──┐                             │
│ ┌──┐ │  │ │  │ │  │ │▒▒│ │  │ │  │ ┌──┐ ┌──┐ ┌──┐              │
│ ┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴─ baseline  │
│ 0s        20        40        60        80        100+         │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / PERIOD                                   08 / 12     │
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
| Reading line | x:96, y:242, single line (carries the total N) | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` |
| Baseline | x:96 → 1824, y:820, 1px | — | `--lp-line` |
| Columns (×10) | 168px wide, 4px gaps, from x:100; heights in true proportion, tallest ≈ 440px | — | `--lp-fg` at 30% (the mass); modal bin `--lp-accent` solid |
| Modal count | centered above the modal bin, 20px up | `--lp-font-mono`, 22px, weight 500 | `--lp-accent` |
| Bin edge labels | under the baseline at y:844, on every OTHER edge (6 labels for 10 bins), centered on the edge; first label carries the unit, last may be "n+" | `--lp-font-mono`, 17px | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **8–12 equal-width bins** (10 is canonical). Fewer hides the
  shape; more turns the slide into a lab plot. A final open bin
  ("100+") is allowed and must be labeled as such.
- **One variable, one period, one population** — stated in the
  reading line with the total N. Overlaid or back-to-back second
  distributions are refused (two shapes = two slides).
- **The modal bin carries the only count.** If the story is a
  threshold rather than the mode (e.g. "94% under the SLA"), say it
  in the headline — the accent stays on the modal bin, and the
  threshold may be marked by ONE dashed vertical at its bin edge,
  replacing the modal accent (never both).
- **Heights are counts (or shares), zero-based, never log-scaled.**
- **Bin edges honest and equal** — variable-width bins are how
  distributions get gerrymandered.

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

The terrace rises as one landform, total ≤ 1.5s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline + reading line rise `translateY(28px→0)` +
   fade, 0.6s.
3. `0.30s` — baseline wipes `scaleX(0→1)` origin left, 0.5s.
4. `0.50s` — columns grow `scaleY(0→1)` origin bottom, 0.6s each,
   0.05s stagger left → right — a wave, not a countdown.
5. `1.10s` — bin edge labels fade, 0.4s.
6. `1.20s` — the modal count fades up `translateY(12px→0)`, 0.4s.
7. `1.30s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Column mass** → the system's ink mixed toward the surface at
  ~30% perceived contrast; may carry the system's texture at the
  same value.
- **Modal bin** → the system's one hot color.
- **Baseline** → the system's axis-line treatment.
- **Threshold variant** → the dashed vertical takes the system's
  dashed vocabulary and a small mono tag at its top.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Gaps wide enough to read as separate categories — this is one
  continuous variable; 4px, no more.
- Counts printed on every column (the silhouette is the message).
- A second distribution overlaid, mirrored, or ghosted behind.
- Smoothing the profile into a density curve — bins are honest
  about their own coarseness; curves pretend to knowledge the data
  doesn't have.
- Log scales, truncated baselines, or unequal bins.
- Branding larger than 40px tall or anywhere but the reserved corner.
