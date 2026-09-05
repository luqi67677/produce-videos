---
version: 1.0
name: Aperture
slot: chart
description: >
  Part-to-whole as a lens. A thin-ring donut on the left holds the
  honest total at its center; a ruled ledger on the right names every
  segment with its share and value — the ledger is the legend, so
  color never has to carry meaning alone.
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

# Aperture — chart layout

## Intent

Composition questions ("where does it all run?") want a whole the
eye can hold. The donut gives the whole one glance — a thin ring,
segments separated by surface gaps, exactly one in accent — and its
center states the total, so the denominator is never hidden. But arcs
are hard to read precisely, so Aperture refuses to make the ring do
the numbers' job: every segment reappears as a ruled ledger row with
its swatch, name, value, and share. Ring for the feel, ledger for the
facts.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       11 / 18  │
│  HEADLINE WITH ONE EM                                          │
│                                                                │
│        ▄▄▀▀▀▀▀▄▄                 ■  On-prem edge        46%    │
│      █▀         ▀█   accent →   ─────────────────────────────  │
│     █    14.2B    █             ■  Private cloud        27%    │
│     █   frames    █             ─────────────────────────────  │
│      █▄  daily  ▄█              ■  Public cloud         18%    │
│        ▀▀▄▄▄▄▄▀▀                ─────────────────────────────  │
│                                 ■  Hybrid burst          9%    │
│  ──────────────────────────────────────────────────────────    │
│  SOURCE / PERIOD                                     BRAND     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px, uppercase, ls 0.18em / 0.12em | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line, ≤ 34 chars | `--lp-font-display`, 76px, weight 800, lh 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Donut | SVG 560×560 at x:140, y:340; ring radius 214, stroke 60 (hole ≈ 75% of diameter); segments start at 12 o'clock, run clockwise, descending; ~6px circumference gaps between segments | — | accent segment `--lp-accent`; others `--lp-fg` mixed toward `--lp-bg` at 46% / 28% / 14% (descending with share) |
| Donut center | centered on ring center (x:420, y:620), w:300 | total: display 88px weight 800; unit line: mono 15px | `--lp-fg` / `--lp-fg-muted` |
| Ledger | x:900 → 1824, first row top y:370, row height 120, hairline rules between rows (and above the first) | — | — |
| · swatch | 22×22, left edge | — | matches its segment's fill exactly |
| · name + value | left of center: name, then value line under it | body 24px / mono 15px | `--lp-fg` / `--lp-fg-muted` |
| · share | right-aligned | mono 30px, ls 0.02em | `--lp-fg`; accent row `--lp-accent`, weight 500 |
| Footer hairline + source | x:96 → 1824, y:962 / y:984 | mono 14px, uppercase, ls 0.12em | `--lp-line` / `--lp-fg-muted` |

## Content constraints (hard limits)

- **3–5 segments summing to exactly 100%,** sorted descending from
  12 o'clock; anything under 5% folds into a final "Other".
- **The center holds the TOTAL** (the denominator), never a repeated
  share — hiding the total is how donuts lie.
- **Exactly one accent segment** — the one the talk track is about.
  Its ledger row's share takes the accent too.
- **Ring stays thin:** stroke ≈ 28% of radius (hole ≥ 70% of the
  diameter). Never a filled pie, never 3D, never exploded slices.
- **The ledger is the legend.** Every segment gets a row; no floating
  labels around the ring, no leader lines.
- Names ≤ 18 chars; shares are integers; value lines ≤ 24 chars.
- Comparing two compositions → Alloy on two slides or Crossover;
  never two donuts side by side.

## Image variant

**With images:** each ledger row may carry a 64×64 image chip between
swatch and name (rows keep 120px height; names shorten to ≤ 14
chars). All rows or none. **Recommended size / placeholder:**
`https://placehold.co/128x128` (2× for sharpness at 64px).
**Dimension fallback:** fixed 64×64 frames, `object-cover`. **Load
fallback:** token CSS fill behind each `<img>`.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.45s` — segments sweep clockwise in order (stroke-dasharray
   grows from 0 to the segment's true arc length), 0.6s each,
   starts staggered 0.17s; the accent segment (first) leads.
3. Each ledger row fades in as its segment lands (0.55s / 0.72s /
   0.89s / 1.06s), top to bottom — ring and ledger read as one
   motion.
4. `1.20s` — the center total rises, 0.6s — the whole arrives after
   its parts.
5. `1.70s` — footer fades, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
the completed ring renders immediately.

## Skin points

- **Segment fills** → derive ALL non-accent steps from one ink
  (`--lp-fg` mixed toward `--lp-bg` in descending strength), or the
  system's single sequential ramp. Never one hue per segment —
  the swatches + ledger carry identity, lightness carries order.
- **Gaps** → surface-colored; a system may widen them to its gutter
  width (≤ 10px circumference) but never remove them.
- **Center** → a system with a signature numeral treatment applies
  it to the total; the unit line may become the system's caps/label
  style.

## Failure modes to avoid

- A pie (no hole) — the center total is the point of the hole.
- Rainbow segments, or accent-colored text on non-accent rows.
- Labels orbiting the ring with leader lines; that's the ledger's job.
- Shares that don't sum to 100, or a hidden "everything else".
- Six or more segments — the ring becomes a barcode; fold or split.
