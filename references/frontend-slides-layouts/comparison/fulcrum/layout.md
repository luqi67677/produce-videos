---
version: 1.0
name: Fulcrum
slot: comparison
description: >
  Tale-of-the-tape comparison. Attribute labels run down the center
  spine of the stage in mono caps; the two options' values flank them
  left and right in ruled rows, reading toward the middle. Option
  nameplates head their columns, the favored one carrying the accent.
  No cards, no checkmarks — a spec-sheet duel.
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

# Fulcrum — comparison layout

## Intent

Ledger Versus argues in prose points; Fulcrum argues in **numbers held
up against each other**. The center spine of attribute labels is the
fulcrum, and every row is a small weighing: the reader's eye lands on
the label, then swings left and right to compare values. Use it when
the comparison is quantitative (times, costs, capacities) and each
attribute has a terse value on both sides. The layout stays honest —
values may favor either side row by row; only the nameplate accent
declares the recommendation.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│  Managed Cloud                              ▮ On-Prem Cluster  │ ← nameplates,
│  mono descriptor                          mono descriptor      │   accent = favored
│  ─────────────────────────────────────────────────────────     │
│  3 days            DEPLOYMENT LEAD TIME           6 weeks      │
│  ─────────────────────────────────────────────────────────     │
│  Provider region      DATA RESIDENCY          Fully on-site    │
│  ─────────────────────────────────────────────────────────     │
│  Grows per stream     COST AT SCALE        Flat after year 1   │
│  ─────────────────────────────────────────────────────────     │
│  1,200 streams       CAMERA CAPACITY         8,000 streams     │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / BASIS                                     08 / 12    │
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
| Left nameplate | x:96, y:186, left-aligned | `--lp-font-display`, 52px, weight 700 | `--lp-fg` |
| Right nameplate | right-aligned to x:1824, y:186, with a 14×14px accent tick inline before it | same as left | `--lp-accent` |
| Nameplate descriptors | 12px under each nameplate, aligned with it | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Row hairlines (×5) | x:96 → 1824, at y:330 and every 132px after (462, 594, 726, 858), 1px | — | `--lp-line` |
| Attribute labels (center spine) | centered on x:960, vertically centered in each 132px row | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.18em | `--lp-fg-muted` |
| Left values | left-aligned at x:96, vertically centered per row | `--lp-font-display`, 40px, weight 700 | `--lp-fg-muted` |
| Right values | right-aligned to x:1824, vertically centered per row | `--lp-font-display`, 40px, weight 700 | `--lp-fg` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (basis/source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 2 options, exactly 4 attribute rows.** Three options is a
  table, not a duel; five rows crowd the spine. With only 3 attributes,
  grow row pitch to 176px (hairlines at 330, 506, 682, 858).
- **Nameplates:** ≤ 18 characters each. The favored option sits RIGHT
  and carries the accent tick + accent color; if the deck makes no
  recommendation, both nameplates stay `--lp-fg` and the tick is
  dropped.
- **Values:** ≤ 18 characters, one line, no wrapping. Prefer figures;
  short phrases are acceptable. Values must be truthful per row — do
  not pad rows so one side "wins" every line.
- **Attribute labels:** ≤ 24 characters, one line, centered. Real
  attributes only — never "criteria 1".
- **Left column reads `--lp-fg-muted`, right column `--lp-fg`** only
  when a recommendation exists; otherwise both sides `--lp-fg`.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves — the
  chrome hairline terminates the header on its own.

## Image variant

**With option marks:** each nameplate may carry a 96×96px product/vendor
mark sitting above it (left mark at x:96, right mark right-aligned to
x:1824, both at y:150; nameplates shift down to y:262 and the first row
hairline to y:390, reducing rows to 3 at 176px pitch).

**Recommended size / placeholder:** `https://placehold.co/192x192`
(rendered 96×96). **Dimension fallback:** fixed square frame,
`object-fit: contain`, token CSS fill behind each `<img>` for load
failures. Marks are optional and must appear on both sides or neither.

## Choreography

Staggered entrance on slide activation, total ≤ 1.6s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.15s` — nameplates + descriptors rise `translateY(32px→0)` + fade,
   0.6s, right side 0.1s after left.
3. `0.35s` — row hairlines wipe `scaleX(0→1)` from center outward
   (`transform-origin: center`), 0.6s each, 0.08s stagger downward.
4. `0.55s` — attribute labels fade, 0.5s, 0.08s stagger.
5. `0.70s` — values fade up `translateY(20px→0)`, 0.5s, 0.08s stagger
   per row (both sides of a row arrive together — it's a weighing).
6. `1.20s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Accent tick** → the system's marker vocabulary (arrow, star, stamp),
  footprint ≤ 20×20px, always on the favored nameplate only.
- **Row hairlines** → the system's divider vocabulary at the same
  coordinates; dashed or dotted spines suit technical systems.
- **Center spine labels** → may sit in small outlined chips or on a
  faint vertical rule at x:960 if the system frames labels; the rule
  must stay ≤ `--lp-fg-faint`.
- **Branding slot** → the system's lockup rules; monochrome marks
  preferred.
- **Background** → flat `--lp-bg`; a subtle two-tone split (left half a
  breath darker) is the sanctioned atmospheric upgrade if contrast holds.

## Failure modes to avoid

- Checkmarks, crosses, or win/lose shading per row — the reader weighs;
  the layout doesn't referee. The accent nameplate is the only verdict.
- Prose sentences as values. If an attribute needs a sentence per side,
  use Ledger Versus.
- Off-center spine: labels must center on x:960 exactly, or the
  weighing metaphor collapses.
- A third option column squeezed in, or rows past four.
- Branding larger than 40px tall or anywhere but the reserved corner.
