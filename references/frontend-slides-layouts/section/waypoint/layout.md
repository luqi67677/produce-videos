---
version: 1.0
name: Waypoint
slot: section
description: >
  Symmetric section divider. A centered part-kicker and section title
  float above an explicit journey line — a thin horizontal track with one
  node per part, travelled nodes filled, the current node enlarged in
  accent with its label beneath. The deck's map, drawn as a slide.
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

# Waypoint — section layout

## Intent

The progress metaphor made literal and elegant: the audience sees the
whole journey as a line, and sees exactly which stop this is. Waypoint is
the calm, symmetric counterpart to Chapter Gate — no giant numeral, no
asymmetry, just typography and one precise diagram. Use it in decks that
already lean centered/ceremonial (Monolith, Center Seal), or whenever the
part structure itself is worth showing off.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  DECK TITLE                                           06 / 14  │
│                                                                │
│                        PART THREE OF FIVE                      │
│                                                                │
│                         EXECUTION                              │
│                     ← centered title →                         │
│                                                                │
│           ●────────●────────◉────────○────────○               │ ← journey line
│                          EXECUTION                             │   current node
│                                                                │   labeled
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Everything except the corner
chrome is centered on x:960.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Deck title (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Counter (top-right) | right-aligned to x:1824, y:72 | same | `--lp-fg-muted` |
| Part kicker | centered, y:300 | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.3em | `--lp-accent` |
| Section title | centered, top y:380, full content width, text-align center | `--lp-font-display`, 136–160px (default 150), weight 700–800, line-height 0.97, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Journey line | centered, y:700, width 800px, 1px track | — | `--lp-line` |
| Nodes | evenly spaced along the track (first at 0%, last at 100%); past/current filled 10px circles, current enlarged to 16px, future 10px hollow | — | past `--lp-fg-muted`, current `--lp-accent`, future hollow with `--lp-fg-muted` border at 50% opacity |
| Current-node label | centered under the current node, 28px below the track | `--lp-font-mono`, 14px, uppercase, letter-spacing 0.18em | `--lp-accent` |

## Content constraints (hard limits)

- **Title:** 1 line strongly preferred, 2 maximum; ≤ 13 characters
  uppercase / ≤ 16 mixed case per line at 150px. One word is the ideal
  register ("Execution", "Proof").
- **Part kicker:** one line, spelled out ("Part three of five") — the
  redundancy with the diagram is intentional.
- **Journey line:** 3–7 nodes. Exactly one current node, and only the
  current node is labeled. With more than 7 parts, collapse to
  Chapter Gate's rail instead — a crowded track loses its elegance.
- **No framing sentence.** Waypoint's field stays empty below the track;
  if the section needs explanation, use Chapter Gate.

## Image variant

**With an image:** the image goes *behind* the composition — a
full-bleed background under a heavy uniform scrim (`--lp-bg` at ≥ 88%
opacity) so the slide keeps its symmetry and legibility; the layout
itself does not change. Use only quiet, symmetric-tolerant crops
(sky, texture, architecture straight-on).

**Recommended size / placeholder:** `https://placehold.co/1920x1080`.
**Dimension fallback:** full-bleed frame, `object-cover`, flat
`--lp-bg` behind the `<img>`. The image is optional and usually
omitted — Waypoint is at its best bare.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — corner chrome fades in, 0.5s.
2. `0.10s` — part kicker fades in, 0.5s.
3. `0.25s` — title rises: `translateY(44px→0)` + fade, 0.8s.
4. `0.55s` — track wipes via `scaleX(0→1)`, origin left, 0.7s.
5. `0.75s` — nodes pop left-to-right via `scale(0→1)`, 0.35s each,
   0.08s stagger; the current node pops last and slightly larger.
6. `1.15s` — current-node label fades up, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Nodes** → the system's marker vocabulary (squares, ticks, diamonds);
  the three states must stay distinguishable and the current node must
  read as emphasized (size or fill, in `--lp-accent`).
- **Track** → the system's hairline style (dashed, doubled).
- **Part kicker** → the system's label treatment; keep tracking ≥ 0.2em.
- **Background** → symmetric atmospheric treatments only (vignette,
  centered glow) — directional backgrounds fight the axis.

## Failure modes to avoid

- Labeling every node. One label — the current stop — is the discipline
  that keeps the diagram elegant.
- Sliding the composition off-center or left-aligning the title.
- Using the journey line as a timeline of dates. It maps deck parts,
  not chronology; a dated timeline is a content slide, not a divider.
- Decorating the empty lower field. The silence below the track is the
  slide's poise.
