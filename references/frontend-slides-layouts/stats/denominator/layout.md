---
version: 1.0
name: Denominator
slot: stats
description: >
  The number as a typeset fraction. A huge numerator sits over a
  hairline over its denominator phrase — "38 / of 40 sites migrated" —
  with a reading column on the right. For stats whose meaning IS the
  proportion, not the raw count.
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

# Denominator — stats layout

## Intent

"95%" hides the scale; "38 of 40" carries it — but only if the
typography makes the relationship physical. Denominator borrows the
fraction bar from mathematics: the achieved count towers above the
line, the universe it belongs to sits below it, and the ratio reads at
a glance without a percent sign in sight. The right column then says
what the two missing units are, which is usually the honest part.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       12 / 14  │
│                                                                │
│                                        Reading column:         │
│   38                                   what the fraction       │
│   ────────────  ← fraction bar         means, and what the     │
│   OF 40 SITES MIGRATED                 remainder is.           │
│                                                                │
│   ▮▮ 95% COMPLETE ← ratio chip                                 │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  SOURCE / PERIOD                                         ARKA  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Numerator | x:96, top y:230, ≤ 4 glyphs | `--lp-font-display`, 320px, weight 800, line-height 0.85, ls −0.03em | `--lp-fg` |
| Fraction bar | x:96, y:540, 520×4px | — | `--lp-accent` |
| Denominator line | x:96, 28px below the bar | `--lp-font-mono`, 26px, uppercase, ls 0.14em | `--lp-fg-muted` |
| Ratio chip | x:96, y:700; outlined, 1px border, padding 12×20 | `--lp-font-mono`, 16px, ls 0.1em | border `--lp-line`, text `--lp-accent` |
| Reading | x:1200 → 1824 (624 wide), top y:300 | `--lp-font-body`, 23px, line-height 1.6 | `--lp-fg-muted`; key phrase `<em>` → `--lp-fg` |
| Footer hairline + source | x:96 → 1824, y:962 / y:984 | mono 14px | `--lp-line` / `--lp-fg-muted` |

## Content constraints (hard limits)

- **Numerator:** the achieved count, ≤ 4 glyphs, no unit (units live
  in the denominator line).
- **Denominator line:** "OF {N} {THING} {VERB}", ≤ 34 characters. The
  total must be the true universe, not a convenient one.
- **Ratio chip:** the computed percentage or ratio, ≤ 16 characters,
  arithmetically consistent. Optional — omit when the fraction is
  the headline of the talk track.
- **Reading:** 3–6 lines ≤ 280 characters; it should name the
  remainder ("the two still open are…") — that candor is the preset's
  credibility.

## Image variant

**With an image:** a 624×300 image plate (1px `--lp-line` border)
tops the right column at y:300, the reading flowing beneath it from
y:640 (then ≤ 4 lines). **Recommended size / placeholder:**
`https://placehold.co/624x300`. **Dimension fallback:** fixed frame,
`object-cover`, token CSS fill behind the `<img>`. The image is
optional.

## Choreography

1. `0.00s` — kicker, counter fade, 0.5s.
2. `0.15s` — numerator rises `translateY(64px→0)` + fade, 0.9s.
3. `0.55s` — fraction bar wipes `scaleX(0→1)`, 0.5s; denominator
   line fades up at `0.75s`, 0.5s.
4. `0.95s` — ratio chip pops `scale(0.85→1)` + fade, 0.4s.
5. `0.70s` — reading fades up, 0.7s; footer at `1.1s`.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Fraction bar** → the system's rule vocabulary; it is the slide's
  one accent surface besides the chip.
- **Ratio chip** → the system's tag treatment.
- **Numerator face** → the system's stat figures.

## Failure modes to avoid

- A percentage as the numerator — that inverts the whole idea; the
  fraction exists to avoid the percent sign.
- A flattering denominator ("of the 12 sites we tried") — the reading
  will contradict it and the slide dies.
- Stacking a second fraction; one proportion per slide.
