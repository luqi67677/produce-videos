---
version: 1.0
name: Number Story
slot: stats
description: >
  Statistics as a sentence. One display-scale sentence fills the
  middle of the stage with its figures set larger and in accent —
  "We shipped 214 releases in 92 days with 0 rollbacks." — and a
  mono source line certifying them below. The narrative sibling of
  Manifesto, for numbers.
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

# Number Story — stats layout

## Intent

Tiles and tickers present numbers; a sentence *claims* them. Setting
the figures oversized inside running prose does two things no grid
can: it forces the numbers into one causal story (the sentence's
grammar relates them), and it makes the slide quotable — people
repeat sentences, not tables. Use it when 2–4 numbers share one
narrative; use Stat Strip when they are merely siblings.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       13 / 14  │
│                                                                │
│                                                                │
│  We shipped 214 releases                                       │
│  in 92 days with 0                 ← one sentence,             │
│  rollbacks.                           figures oversized        │
│                                       and in accent            │
│                                                                │
│  ALL FIGURES: PLATFORM TELEMETRY, Q2   ← source line           │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Sentence | x:96, vertically centered (block center ≈ y:520), max-width 1650px | `--lp-font-display`, 88px, weight 600, line-height 1.3, ls −0.01em, sentence case | words `--lp-fg`; figures: 1.22em, weight 800, `--lp-accent`, ls −0.02em |
| Source line | x:96, y:940 | `--lp-font-mono`, 14px, uppercase, ls 0.16em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly one sentence,** ≤ 170 characters, 3–6 rendered lines,
  containing **2–4 figures**. One figure → Keynote Figure; five+ →
  Ticker.
- **Figures are numerals with units,** never spelled out; everything
  else in the sentence is words, never digits. The contrast between
  the two registers is the design.
- **The sentence must be causally honest** — its grammar relates the
  numbers ("in", "with", "across"), so the relations must be true.
- **Source line:** required, 1 line ≤ 60 characters, covering *all*
  figures.
- Sentence case; no headline — the sentence is the headline.

## Image variant

**With an image:** full-bleed behind the sentence under a heavy
uniform scrim (`--lp-bg` at ≥ 88%) — texture only. **Recommended
size / placeholder:** `https://placehold.co/1920x1080`. **Dimension
fallback:** full-bleed frame, `object-cover`, flat `--lp-bg`
behind the `<img>`. The image is optional and usually omitted.

## Choreography

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.15s` — the sentence fades in with its figures at word color
   (camouflaged), 0.8s.
3. `0.85s` — figures arrive: each crossfades to accent and scales
   1→1.0 from 0.92 in reading order, 0.4s each, 0.18s stagger — the
   numbers step out of the prose.
4. `1.60s` — source line fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Decks with a counting
vocabulary may count figures up instead of crossfading. Under
`prefers-reduced-motion`, figures render in accent immediately.

## Skin points

- **Sentence face** → serif systems use their serif; figures may take
  the system's stat-figure treatment (its serif numerals, mono
  digits) while words stay in the display face.
- **Figure emphasis** → the system's accent plus its emphasis move;
  the 1.22em size step is structural and stays.
- **Source line** → the system's caption/footnote treatment.

## Failure modes to avoid

- A sentence that is really three clauses stapled with "and" — if the
  grammar doesn't genuinely relate the numbers, use Stat Strip.
- Digits sneaking into the prose ("38 sites in 3 regions across 2
  quarters" — pick which numbers are figures; the rest become words
  or leave).
- Dropping the source line; a claims-sentence without provenance
  reads as advertising.
