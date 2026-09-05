---
version: 1.0
name: Keynote Figure
slot: stats
description: >
  One number as the argument. A hero figure at display scale owns the
  left of the slide with its label and a one-sentence reading beneath;
  two or three secondary stats stack in a ruled rail on the right.
  For the moment the deck hangs on a single measurement.
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

# Keynote Figure — stats layout

## Intent

When one number carries the story, give it the whole stage — a figure
set at title scale reads as a claim, not a data point. The right rail
exists so the hero doesn't float alone: two or three quiet supporting
measurements corroborate it without competing. If no single number
deserves this, use Stat Strip instead; three equal numbers on this
layout would be a lie about hierarchy.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       09 / 14  │
│                                                                │
│                                             ── rail ──────     │
│  4.7×            ← hero figure              38ms               │
│                                             P99 INFERENCE      │
│  THROUGHPUT VS LAST YEAR                                       │
│                                             ────────────────   │
│  One sentence reading the number —          12                 │
│  what it means, why it happened.            REGIONS LIVE       │
│                                             ────────────────   │
│                                             99.98%             │
│                                             UPTIME, TRAILING   │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned to x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Hero figure | x:96, top y:280, single line | `--lp-font-display`, 360–420px (default 400), weight 800, line-height 0.9, letter-spacing −0.03em | `--lp-fg`; the unit/multiplier glyph (×, %, ms) → `--lp-accent` |
| Hero label | x:96, 40px below figure | `--lp-font-mono`, 17px, uppercase, letter-spacing 0.2em | `--lp-fg-muted` |
| Reading | x:96, 32px below label, max-width 720px | `--lp-font-body`, 24px, line-height 1.55 | `--lp-fg-muted` |
| Rail | x:1360 → 1824 (464px wide), vertically centered block starting ≈ y:300 | — | — |
| Rail entry | top 1px rule; padding 28px top, 36px bottom | value: `--lp-font-display`, 88px, weight 700, line-height 1; label: `--lp-font-mono`, 14px, uppercase, ls 0.16em, 12px below value | rule `--lp-line`, value `--lp-fg`, label `--lp-fg-muted` |

## Content constraints (hard limits)

- **Hero figure:** ≤ 5 glyphs including the unit ("4.7×", "38ms",
  "212%"). Longer figures (e.g., "$1.2M") may drop to 360px. Numerals
  only — no words in the hero.
- **Hero label:** 1 line, ≤ 32 characters. Says what was measured.
- **Reading:** 1–3 lines, ≤ 160 characters. Interprets, never repeats,
  the number.
- **Rail:** 2–3 entries, each value ≤ 7 glyphs, each label ≤ 24
  characters. One entry is not a rail; four crowds it.
- **Hierarchy is real:** the rail values must genuinely be supporting
  evidence. If any rail number matters as much as the hero, this is a
  Stat Strip slide.

## Image variant

**With an image:** a 464×260 image plate (1px `--lp-line` border)
tops the right rail — plate at y:300, the rail's entries starting
beneath it at y:600 and capped at 2. The image should be evidence for
the hero number (the hardware, the dashboard, the site), captioned by
its first rail label.

**Recommended size / placeholder:** `https://placehold.co/464x260`.
**Dimension fallback:** fixed 464×260 frame, `object-cover`,
token CSS fill behind the `<img>`. The image is optional — the
3-entry rail is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.15s` — hero figure rises: `translateY(64px→0)` + fade, 0.9s; its
   accent unit glyph pops via `scale(0→1)` at `0.75s`, 0.4s.
3. `0.55s` — hero label fades up, 0.5s.
4. `0.70s` — reading fades up, 0.6s.
5. `0.70s` — rail entries enter top-to-bottom: rule wipes `scaleX(0→1)`
   + content fades up, 0.55s, 0.15s stagger.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. For decks with a counting
animation vocabulary, the hero figure may count up to its value over
≤ 1.2s instead of rising — pick one, not both. Under
`prefers-reduced-motion`, everything appears without transforms.

## Skin points (where the design system may substitute)

- **Hero figure face** → the system's stat treatment (serif figures,
  mono digits); the accent unit glyph convention stays.
- **Rail rules** → the system's divider vocabulary.
- **Hero label** → the system's label/kicker treatment.
- **Background** → flat or atmospheric; a subtle treatment behind the
  hero's whitespace works well, but nothing patterned behind the figure
  itself.

## Failure modes to avoid

- Promoting a weak number. A hero figure of "3" (features shipped)
  reads as parody — heroes are ratios, latencies, magnitudes.
- Wrapping the hero or mixing words into it ("4.7× faster" — the word
  belongs in the label).
- Balancing the composition by enlarging the rail — the imbalance is
  the message.
- More than one accent moment: the unit glyph is the only accent in the
  hero zone.
