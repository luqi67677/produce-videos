---
version: 1.0
name: Nameplate
slot: spec
description: >
  Technical specifications as an engraved machine nameplate. A
  double-bordered plate holds the product name, a mono model line,
  and a ruled 2×4 grid of eight label/value spec pairs — real units,
  one accent value — with a serial/certification line along the
  plate's foot. The slide equivalent of the metal plate riveted to
  the chassis.
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

# Nameplate — spec layout

## Intent

Spec slides usually arrive as feature bullets wearing adjectives.
Nameplate strips them to **what a commissioning engineer would rivet
to the machine**: eight measured facts in a bordered plate, units
honest, tolerances stated. The plate frame — the pack's only
double-bordered element — signals "manufacturer's declaration," and
audiences extend it the trust they give physical nameplates. Use it
for hardware, appliances, and SLAs-as-products; a service without
measurable specs has no business on a plate.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · PRODUCT LINE                   [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│      ╔═══════════════════════════════════════════════╗        │
│      ║   SENTINEL EDGE X4        ← product name       ║        │
│      ║   FIELD UNIT · REV C · 2026                     ║        │
│      ║   ───────────────────┬───────────────────      ║        │
│      ║   STREAMS   64 ←acc  │  POWER      220 W       ║        │
│      ║   INFERENCE 400 TOPS │  WEIGHT     9.8 KG      ║        │
│      ║   OPERATING −10…55°C │  INGRESS    IP66        ║        │
│      ║   UPLINK    2×10GbE  │  MTBF       60,000 H    ║        │
│      ║   ─────────────────────────────────────        ║        │
│      ║   S/N SPEC-SHEET-01 · CERTIFIED SNI/IEC        ║        │
│      ╚═══════════════════════════════════════════════╝        │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / DATASHEET REV                            08 / 12     │
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
| Plate | x:400 → 1520, y:210 → 880; outer border 2px, inner border 1px inset 10px (the double frame) | — | outer `--lp-fg`, inner `--lp-line` |
| Product name | centered in the plate, y:270 | `--lp-font-display`, 58px, weight 800, letter-spacing 0.02em, uppercase | `--lp-fg` |
| Model line | centered, 16px under the name | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.18em, items joined by " · " | `--lp-fg-muted` |
| Grid rules | horizontal at y:400; vertical center divider x:960 from y:400 → 760; row hairlines at y:490, 580, 670 spanning each column with a 56px inset | — | `--lp-line` |
| Spec labels | left-aligned at each cell's start (x:456 / x:1016), rows centered in 90px pitch | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` |
| Spec values | right-aligned at each cell's end (x:904 / x:1464) | `--lp-font-mono`, 27px, weight 500 | `--lp-fg`; ONE value `--lp-accent` |
| Plate foot rule | x:456 → 1464, y:790, 1px | — | `--lp-line` |
| Serial line | centered, y:816 | `--lp-font-mono`, 14px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (datasheet rev) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 8 specs** in a 2×4 grid, measured facts with real units
  (W, kg, °C, GbE, h). "Easy to use" is not a spec; if it can't be
  measured, it can't be engraved. With only 6 honest specs, run 2×3
  (grid rows at y:400/510/620, foot at y:700).
- **Labels:** ≤ 12 characters. Values: ≤ 10 characters including
  unit.
- **One accent value** — the headline spec the deck is arguing
  (capacity, efficiency), never the weakest one dressed up.
- **Model line:** ≤ 40 characters — variant, revision, year. Real.
- **Serial line:** certification/standards actually held ("SNI",
  "IEC 62676", "IP66 TESTED") — inventing certifications on a
  nameplate is the one lie with legal consequences.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

**With a product photo:** the plate narrows to x:400 → 1180 and a
520×670 product photograph stands to its right (x:1240 → 1760,
y:210 → 880), no frame (the plate carries the framing). Spec grid
drops to one column of 6.

**Recommended size / placeholder:** `https://placehold.co/520x670`.
**Dimension fallback:** fixed frame, `object-fit: cover`, token CSS
fill behind the `<img>`. Optional — the plate-only form is the
default.

## Choreography

Stamped, then engraved — total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.15s` — the plate borders draw: outer frame fades + scales
   `scale(0.97→1)`, inner border fades 0.15s later, 0.6s.
3. `0.45s` — product name + model line rise `translateY(20px→0)` +
   fade, 0.6s.
4. `0.70s` — grid rules wipe in, 0.5s; spec pairs fade cell by cell
   in reading order (left column top→bottom, then right), 0.35s
   each, 0.07s stagger.
5. `1.35s` — the accent value re-pops `scale(1→1.06→1)` subtly —
   the engraver's second strike.
6. `1.45s` — serial line + footer fade, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Double frame** → the system's frame vocabulary (single heavy
  rule + corner ticks, rounded ≤ 12px) — but doubled or visibly
  "plated"; a plain box loses the grammar.
- **Spec values** → the system's numeral face.
- **Plate surface** → may take a half-step tint (≤ `--lp-fg-faint`)
  or the system's brushed texture.
- **Branding slot** → the system's lockup rules; the plate itself
  may carry a small maker's mark ≤ 32px beside the serial line.

## Failure modes to avoid

- Adjective specs ("BLAZING FAST"), or benchmarks without
  conditions (TOPS at what precision — say it in the datasheet
  line).
- Nine-plus specs, or empty cells to make eight.
- Accent on more than one value, or on the border.
- The plate stretched full-bleed — a nameplate is an object, not
  a background; the surrounding whitespace is what makes it one.
- Marketing names in the serial line.
- Branding larger than 40px tall or anywhere but the reserved slots.
