---
version: 1.0
name: Countdown Plate
slot: section
description: >
  Monumental symmetric divider. The part numeral fills the stage as a
  solid-faint plate — 880px tall, centered — with the section title
  seated on top of it at dead center. A film-leader countdown card,
  slowed down and made elegant.
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

# Countdown Plate — section layout

## Intent

The centered counterpart to Chapter Gate's asymmetry, and the loudest
quiet slide in the slot: a numeral so large it becomes a field, with
the title small (relatively) and perfectly centered upon it. It reads
like the leader countdown between reels — a beat of pure punctuation.
Pairs naturally with Monolith / Center Seal decks; needs no rail
because its drama *is* the number.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  PART FOUR                                            10 / 14  │
│              ████████████████████████████                      │
│            ██                            ██                    │
│           ██        (numeral "04",        ██  ← 880px          │
│           ██         solid faint)         ██     solid faint   │
│            ██                            ██                    │
│                        P R O O F        ← title, dead center   │
│            ██                            ██                    │
│              ████████████████████████████                      │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Numeral plate | centered on x:960, vertically centered, font-size 880px, line-height 0.8, **solid fill** | `--lp-font-display`, weight 800 | `--lp-fg-faint` |
| Title | centered on both axes (dead center), full content width, text-align center, 1 line | `--lp-font-display`, 104–120px (default 112), weight 700–800, line-height 1, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Sub line (optional) | centered, 44px below title | `--lp-font-mono`, 15px, uppercase, ls 0.3em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** exactly 1 line, ≤ 12 characters uppercase at 112px. One
  word is the ideal ("Proof", "Execution").
- **Numeral:** 2 characters, zero-padded, always solid faint fill —
  never outline (outline ghosts belong to opening/closing slots).
- **Sub line:** 1 line ≤ 44 characters, wide-tracked. Optional.
- **No rail, no framing paragraph.** The number is the information.

## Image variant

**With an image:** full-bleed behind the plate under a symmetric scrim
(`--lp-bg` at ≥ 90%); the numeral must remain the strongest shape on
the slide. **Recommended size / placeholder:**
`https://placehold.co/1920x1080`. **Dimension fallback:** full-bleed
frame, `object-cover`, flat `--lp-bg` behind the `<img>`. The
image is optional and usually omitted.

## Choreography

1. `0.00s` — numeral plate fades in slowly (opacity only — it is
   transform-centered), 1.1s.
2. `0.35s` — title rises through it: `translateY(40px→0)` + fade
   (animate an inner span, not the centered block), 0.8s.
3. `0.85s` — sub line fades up, 0.5s.
4. `0.95s` — kicker and counter fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Numeral face** → the system's display figures (serif numerals
  change this slide's whole character — allowed and encouraged).
- **Faint fill** → the system's texture may fill the numeral
  (halftone, grain) as long as it stays ≤ 18% contrast.
- **Title/sub** → the system's ceremonial treatments (small caps,
  tracked serif).

## Failure modes to avoid

- A numeral small enough to read as a label — below ~700px the slide
  loses its reason; use Chapter Gate instead.
- Off-center anything. Symmetry is the contract.
- Two-line titles or added prose — the beat must stay a beat.
