---
version: 1.0
name: Manifesto
slot: list
description: >
  The list as one flowing sentence. Item keywords stand at full
  contrast inside a display-scale paragraph whose connective words
  recede to muted — the audience reads prose and remembers a list.
  A mono footnote anchors the bottom. The most literary list in
  the pack.
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

# Manifesto — list layout

## Intent

Bullets chop meaning into fragments; Manifesto restores the sentence
and lets contrast do the itemizing. Connectives sit at `--lp-fg-muted`,
the three-to-five keywords at full `--lp-fg`, and exactly one keyword
takes the accent — so the paragraph carries rhythm, priority, and
completeness in a single breath. For value statements, principles,
and any list the presenter would rather *say* than enumerate.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       11 / 14  │
│                                                                │
│  We plan WEEKLY, ship                                          │
│  DAILY, write EVERYTHING                                       │
│  down, and treat LATENCY       ← one flowing paragraph,        │
│  as the feature.                  keywords at full contrast    │
│                                                                │
│                                                                │
│  FOUR COMMITMENTS — IN EFFECT SINCE Q2   ← mono footnote       │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Paragraph | x:96, top y:280, max-width 1620px | `--lp-font-display`, 76px, weight 700, line-height 1.28, letter-spacing −0.01em, sentence case (no uppercase transform) | connectives `--lp-fg-muted`; keywords `--lp-fg`; exactly one keyword `--lp-accent` |
| Footnote | x:96, y:940 | `--lp-font-mono`, 14px, uppercase, ls 0.16em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **One sentence** (a second short sentence is allowed only as the
  coda of the first), ≤ 200 characters, 4–7 rendered lines.
- **3–5 keywords,** each 1–2 words, each a real list item. Read the
  keywords alone in order — if they don't reconstruct the list, the
  sentence isn't doing its job.
- **Exactly one accent keyword** — the one the deck is really about.
- **Footnote:** 1 line ≤ 60 characters, naming the count ("Four
  commitments — in effect since Q2"). Required: it certifies that
  the prose really was a list.
- Sentence case only; uppercase kills the prose register.

## Image variant

**With an image:** full-bleed behind the paragraph under a heavy
uniform scrim (`--lp-bg` at ≥ 88%) — texture only, as with Waypoint.
**Recommended size / placeholder:** `https://placehold.co/1920x1080`.
**Dimension fallback:** full-bleed frame, `object-cover`, flat
`--lp-bg` behind the `<img>`. The image is optional and usually
omitted — the words are the picture.

## Choreography

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.15s` — the paragraph fades in as a block at muted contrast
   (keywords included), 0.8s.
3. `0.80s` — keywords arrive: each keyword crossfades from muted to
   its full color in reading order, 0.35s each, 0.15s stagger — the
   list assembles itself out of the prose.
4. `1.60s` — footnote fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
keywords render at full contrast immediately.

## Skin points

- **Paragraph face** → serif systems must use their serif here; this
  preset was born for editorial systems.
- **Keyword emphasis** → the system's emphasis move may add weight or
  italic to keywords, on top of the contrast shift.
- **Accent keyword** → the system's `<em>` treatment.

## Failure modes to avoid

- A sentence written around the keywords that reads as filler — the
  connectives must be a real sentence a person would say.
- More than one accent keyword, or keywords longer than two words.
- Uppercase, bullets sneaking back in, or line breaks placed to make
  it "look like a list" — trust the contrast.
