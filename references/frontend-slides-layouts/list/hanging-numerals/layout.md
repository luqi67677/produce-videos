---
version: 1.0
name: Hanging Numerals
slot: list
description: >
  Marginalia list. Giant solid-faint numerals hang in a wide left
  gutter — one per item — with the item's title and description set
  beside each like annotations on the numbers. Three items, enormous
  air, the quietest list in the pack.
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

# Hanging Numerals — list layout

## Intent

Ledger List rules its items into a table; Hanging Numerals lets them
float against three vast, barely-there figures. The faint numerals do
double duty — counters and texture — so the slide needs no rules, no
cards, no markers at all. For short lists whose items deserve slow
reading: principles, bets, commitments.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       07 / 14  │
│  THREE BETS               ← headline                           │
│                                                                │
│  ▒▒▒▒     Edge first                                           │
│  ▒01▒     Two lines of description set beside                  │
│  ▒▒▒▒     the hanging figure.                                  │
│  ▒▒▒▒     One console                                          │
│  ▒02▒     Description …                                        │
│  ▒▒▒▒                                                          │
│  ▒▒▒▒     Latency as law                                       │
│  ▒03▒     Description …                                        │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line | `--lp-font-display`, 84px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Items | 3 rows, tops at y:340 / y:560 / y:780 | — | — |
| · hanging numeral | x:96, font-size 190px, line-height 0.85, **solid fill** | `--lp-font-display`, weight 800 | `--lp-fg-faint` |
| · item title | x:400, top-aligned with the numeral's cap height (+18px) | `--lp-font-display`, 42px, weight 700, line-height 1.1 | `--lp-fg` |
| · item description | x:400, 12px below title, max-width 1100px | `--lp-font-body`, 20px, line-height 1.5 | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 items.** Two is a comparison, four crowds the figures —
  this preset's generosity is its content limit.
- **Titles:** 1 line ≤ 30 characters. **Descriptions:** 1–2 lines
  ≤ 130 characters; keep the three within one line of each other.
- **Numerals:** sequential, zero-padded, always solid faint — never
  outline, never accent. If one item must lead, use Spotlight instead.

## Image variant

**With an image:** a 420×760 image plate (1px `--lp-line` border,
mono caption below) fills the right margin at x:1404 → 1824, y:340;
item descriptions then cap at 900px width. **Recommended size /
placeholder:** `https://placehold.co/420x760`. **Dimension fallback:**
fixed frame, `object-cover`, token CSS fill behind the `<img>`.
The image is optional.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.35s` — per item, top to bottom (0.18s stagger): the numeral
   fades in to its faint resting state (opacity only, slow — 0.8s),
   then its title and description fade up `translateY(24px→0)`
   0.55s at `+0.2s`.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Numerals** → the system's display figures; serif figures make this
  preset sing. A texture fill (grain, halftone) is allowed at ≤ 18%
  contrast.
- **Item titles** → the system's h3 treatment.
- **Background** → flat or a whisper of texture; the faint numerals
  need silence to read.

## Failure modes to avoid

- Promoting the numerals to full contrast "for legibility" — they are
  atmosphere with a job, not data.
- Rules, cards, or bullets sneaking in; the whitespace is the
  structure.
- Descriptions longer than two lines — this is the pack's slowest
  list; respect its pace.
