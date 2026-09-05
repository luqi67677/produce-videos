---
version: 1.0
name: Alloy
slot: chart
description: >
  The whole as one bar of metal. A single full-width band divided
  into 4–6 segments that sum to exactly 100%, gaps of slide surface
  between them, one segment in accent — each part labeled beneath
  its own left edge like an assay stamp.
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

# Alloy — chart layout

## Intent

When the story is "what the whole is made of", a donut spends half
the stage on a hole. Alloy lays the composition flat: one band, full
content width, segment widths in true proportion, read left to right
in the same order the labels are read. Because every segment shares
the same height, length is the only encoding — the honest one. The
label blocks hang beneath their segments like assay stamps, so the
band itself stays unlettered and monumental.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       08 / 18  │
│  HEADLINE WITH ONE EM                     reading block        │
│                                           (2–4 muted lines)    │
│  ┌────────────────┬───────────┬────────┬──────┬───┐           │
│  │  accent (38%)  │    26%    │  17%   │ 12%  │7% │  ← band   │
│  └────────────────┴───────────┴────────┴──────┴───┘           │
│  ⎸38%             ⎸26%        ⎸17%     ⎸12%   ⎸7%             │
│   Traffic          People      Perim.   Retail  Other          │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  SOURCE / PERIOD                                     BRAND     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px, uppercase, ls 0.18em / 0.12em | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line, ≤ 34 chars | `--lp-font-display`, 76px, weight 800, lh 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Reading block | right x:1824, w:360, top y:128, 2–4 lines | `--lp-font-body`, 18px, lh 1.55 | `--lp-fg-muted` |
| Band | x:96 → 1824, top y:430, height 220; flex row, 3px surface gaps; **segment widths = share of the remaining width via proportional flex-grow — true proportion, descending left→right, "Other" always last** | — | accent segment `--lp-accent`; others `--lp-fg` mixed toward `--lp-bg` at 52% / 34% / 20% / 10% (descending with share) |
| Label row | same flex geometry as the band (same gaps and grow ratios), top y:674; each cell: 16px×2px top tick, share, name | share: mono 28px; name: body 15px, mt 6px | tick `--lp-line`; share `--lp-fg` (accent segment's `--lp-accent`, weight 500); name `--lp-fg-muted` |
| Footer hairline + source | x:96 → 1824, y:962 / y:984 | mono 14px, uppercase, ls 0.12em | `--lp-line` / `--lp-fg-muted` |

## Content constraints (hard limits)

- **4–6 segments summing to exactly 100%,** sorted descending left
  to right; anything under 6% folds into "Other", and "Other" sits
  last regardless of its size.
- **Exactly one accent segment** — the subject. If all parts matter
  equally, none takes the accent (and the headline must carry the
  story some other way).
- **Widths are sacred:** computed from real shares. No minimum
  widths — a 4% sliver reads as a sliver. But no segment may be
  narrower than its label block (~96px); fold instead.
- **The band stays unlettered.** All text lives in the label row;
  never print values inside segments (contrast against remapped
  fills can't be guaranteed).
- **One band only.** Two compositions to compare → two Alloy slides
  or Crossover with shares; stacked multi-band walls are dashboards.
- Shares are integers; names ≤ 20 chars.

## Image variant

**With image:** the reading block may be replaced by a 360×200 image
plate (right x:1824, top y:128, hairline border in `--lp-line`).
**Recommended size / placeholder:** `https://placehold.co/720x400`
(2× for sharpness). **Dimension fallback:** fixed 360×200 frame,
`object-cover`. **Load fallback:** token CSS fill behind the `<img>`.
Segments themselves never carry images.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.40s` — segments grow via `scaleX(0→1)` (origin left),
   left→right, 0.55s each, 0.09s stagger — the band assembles like
   an ingot being poured.
3. Each label cell fades in as its segment finishes (+0.25s after
   its segment starts), tick first by nature of the shared cell.
4. `1.30s` — reading block rises, 0.6s.
5. `1.60s` — footer fades, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
the completed band renders immediately.

## Skin points

- **Segment fills** → derive ALL non-accent steps from one ink
  (`--lp-fg` toward `--lp-bg`, strength descending with share) or
  the system's single sequential ramp; the highest-share non-accent
  segment gets the strongest step. Never one hue per segment.
- **Gaps** → surface-colored, 3px by default; a system may widen to
  its gutter (≤ 8px) but never remove or outline them.
- **Band corners** → square by default; a system that rounds
  everything may round the band's outer corners only (≤ 8px), never
  inner segment edges.
- **Ticks** → may become the system's tick/notch glyph.

## Failure modes to avoid

- Values printed inside segments — remapped fills make contrast a
  lottery.
- Segments ordered by narrative instead of size ("Other" second) —
  the eye reads left-to-right as ranking.
- A legend far from the band; the label row IS the legend, welded
  beneath it.
- 3D bevels, gradients per segment, or outlined segments.
- Percentages that sum to 99 or 101 — round, then reconcile before
  the slide ships.
