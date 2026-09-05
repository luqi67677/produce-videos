---
version: 1.0
name: Stat Strip
slot: stats
description: >
  Three numbers, equal weight. An editorial header introduces the story;
  below it, three ruled stat tiles sit in one calm row — value, label,
  and a mono footnote each. The quarterly-report register: confident
  because it is undecorated.
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

# Stat Strip — stats layout

## Intent

For the slide that says "here is the quarter in three numbers." No hero,
no hierarchy — three measurements of equal standing, each on its own
ruled tile, aligned to one baseline grid. The elegance comes from what's
absent: no boxes, no icons, no charts-for-decoration. If one number
should dominate, use Keynote Figure instead.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       10 / 14  │
│  THE QUARTER IN                                                │
│  THREE NUMBERS            ← headline, ≤2 lines                 │
│                                                                │
│  ────────────────    ────────────────    ────────────────      │
│  214                 38ms                99.98%                │
│  Production          P99 inference      Platform uptime        │
│  deployments         latency                                   │
│  UP 3.1× YOY         DOWN FROM 91MS     TRAILING 12 MONTHS     │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  SOURCE / PERIOD                                     SOLSTICE  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px**
left/right margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned to x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Headline | x:96, top y:118, max-width 1200px | `--lp-font-display`, 84px, weight 700–800, line-height 1.02, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Tile row | x:96 → 1824, top y:460; 3 equal columns, 64px gap | — | — |
| Tile rule | full column width, 1px, at tile top | — | `--lp-line` |
| Tile value | 36px below rule | `--lp-font-display`, 136px, weight 800, line-height 0.95, letter-spacing −0.02em; unit glyphs (%, ms, ×) → `--lp-accent` | `--lp-fg` |
| Tile label | 24px below value | `--lp-font-body`, 22px, line-height 1.4 | `--lp-fg-muted` |
| Tile note | 20px below label | `--lp-font-mono`, 13px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` at 75% |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source/period) / right (org) | x:96 / right-aligned x:1824, y:984 | `--lp-font-mono`, 14px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 tiles.** Two → merge into the headline or use Keynote
  Figure; four → cut the weakest number. Three is the rhythm.
- **Tile value:** ≤ 7 glyphs including unit. Values must share a scale
  of precision — "214 / 38ms / 99.98%" works; "214 / 38.4271ms" doesn't.
- **Tile label:** 1–2 lines, ≤ 44 characters. Plain language, no
  abbreviations that need decoding.
- **Tile note:** 1 line, ≤ 28 characters — a delta, comparison, or
  period ("UP 3.1× YOY"). All tiles have notes or none.
- **Headline:** 1–2 lines, ≤ 30 characters per line at 84px.
- **Footer:** data source and period on the left — stats without
  provenance look decorative.

## Image variant

**With an image:** a 520×220 image plate (1px `--lp-line` border)
sits top-right at x:1304 → 1824, y:96 → 316; the headline max-width
tightens to 1100px. Use for context, not another number — the period's
setting, the thing that was measured.

**Recommended size / placeholder:** `https://placehold.co/520x220`.
**Dimension fallback:** fixed 520×220 letterbox frame, `object-cover`, token CSS fill behind the `<img>`. The image is optional.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.10s` — headline rises: `translateY(36px→0)` + fade, 0.7s.
3. `0.45s` — tiles enter left-to-right: rule wipes `scaleX(0→1)`
   (0.5s) while value, label, note fade up in sequence within each
   tile (0.55s, 0.08s internal stagger); 0.15s stagger between tiles.
4. `1.10s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Decks with a counting vocabulary
may count values up over ≤ 1s. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Tile rules** → the system's divider vocabulary; a system with stat-
  card chrome may put its surface behind each tile at the same geometry.
- **Value figures** → the system's stat treatment (serif figures in
  accent, mono digits) — if the system colors entire stat values in its
  accent, that overrides the unit-glyph convention.
- **Note** → the system's tag/badge treatment (outlined pill) if it has
  one, same position.
- **Background** → flat or quiet texture; charts and grids behind
  numbers are noise.

## Failure modes to avoid

- Sparklines, gauges, or icons inside tiles — the number is the
  visualization.
- Unequal tile widths or re-ordering for "visual balance" — equal
  weight is the statement.
- Values in mixed formats or precision that begs comparison questions.
- Skipping the source footer while presenting externally.
