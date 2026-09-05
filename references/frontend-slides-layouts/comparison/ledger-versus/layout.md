---
version: 1.0
name: Ledger Versus
slot: comparison
description: >
  Two-column comparison split by a single center hairline. Mono column
  headers (one may carry the accent as the favored side), then 2–3
  horizontally aligned pairs of point-title and description. Optional
  banner image under each header. No table borders, no check/cross
  icons — alignment does the arguing.
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

# Ledger Versus — comparison layout

## Intent

Comparison slides degrade into checkmark tables because tables feel
"fair." Ledger Versus keeps the fairness — identical geometry both
sides, rows aligned to the same baselines — while letting typography
state the verdict: the favored column's header carries the accent.
The audience sees a balanced layout and a clear recommendation at once.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       09 / 14  │
│  BUILD OR BUY            ← headline                            │
│                                                                │
│  BUILD IN-HOUSE            │   PARTNER PLATFORM  ← headers     │
│                            │                                   │
│  Point title               │   Point title                     │
│  Two lines of description  │   Two lines of description        │
│                            │                                   │
│  Point title               │   Point title       ← rows align  │
│  Description               │   Description                     │
└────────────────────────────────────────────────────────────────┘
                       hairline at x:960
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, max-width 1200px, 1 line | `--lp-font-display`, 84px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Center divider | x:960, y:300 → 960, 1px | — | `--lp-line` |
| Columns | left: x:96 → 864; right: x:1056 → 1824 | — | — |
| Column headers | top y:310 — both headers share this baseline | `--lp-font-mono`, 17px, uppercase, ls 0.2em | favored `--lp-accent` (with a 32×4px accent bar floating 20px above it, out of flow so the headers stay aligned), other `--lp-fg-muted` |
| Point rows | first row top y:420; the Nth row starts at the same y in both columns; row pitch 180px | title: `--lp-font-display` 32px weight 700; desc: `--lp-font-body` 19px, line-height 1.5, 10px below title | title `--lp-fg`, desc `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 2 columns.** Three options is a Counter Cards slide.
- **2–3 point rows,** the same count both sides, paired by topic —
  row N left and row N right answer the same question. Never leave an
  empty cell.
- **Point titles:** 1 line ≤ 26 characters. **Descriptions:** 1–2
  lines ≤ 110 characters.
- **At most one favored column.** If genuinely neutral, both headers
  stay muted and no accent bar appears.
- **No icons, checkmarks, or crosses.** Words carry the judgment.

## Image variant

**With images:** each column may carry a 768×160 banner image directly
under its header (y:360 → 520); point rows shift down 200px and cap at
2 rows. Both columns get banners or neither — asymmetric imagery
rigs the comparison visually.

**Recommended size / placeholder:** `https://placehold.co/768x160`.
**Dimension fallback:** fixed 768×160 letterbox frames, `object-cover`,
token CSS fill behind each `<img>`. Banners are optional.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.40s` — center divider draws downward `scaleY(0→1)`, origin top,
   0.7s.
3. `0.55s` — column headers fade in together, 0.5s; the favored
   header's accent bar wipes at `0.75s`.
4. `0.70s` — point rows fade up in horizontal pairs (row 1 both sides,
   then row 2…), 0.55s, 0.15s stagger per pair.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Center divider** → the system's divider vocabulary; a dual-surface
  system may instead tint the favored column's background at ≤ 6%
  contrast and drop the divider.
- **Favored marker** → the system's emphasis device (tag, underline,
  its accent) on the header only — never on every row.
- **Row rhythm** → pitch may open to 200px in airy systems.

## Failure modes to avoid

- Unpaired rows or mismatched row counts — the grid IS the fairness.
- Accent sprinkled on individual winning points; verdict lives in the
  header.
- A third "our recommendation" box below — the accent already said it.
- Vertical column headers or rotated text; this slide reads as a
  ledger, not a poster.
