---
version: 1.0
name: Ruled Verse
slot: quote
description: >
  The quotation set like handwriting on ruled paper. Each display-scale
  line of the quote stands on its own full-width hairline rule, the key
  phrase carries the accent, and the attribution signs off beneath the
  last rule like a letter. No quote glyph, no portrait by default — the
  ruled lines themselves are the motif.
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

# Ruled Verse — quote layout

## Intent

Testimony makes a quote monumental with a giant glyph; Ruled Verse makes
it **intimate and documentary** — the words appear transcribed onto ruled
paper, each line resting on a hairline as if written by hand. The rules
give the slide rhythm and honesty: this is testimony taken down verbatim.
Use it when the quote is the entire argument of the slide and the deck's
register is editorial rather than ceremonial.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│  We stopped arguing                                            │
│  ──────────────────────────────────────────────────────────    │
│  about screenshots and                                         │
│  ──────────────────────────────────────────────────────────    │
│  started shipping decisions.        ← accent phrase            │
│  ──────────────────────────────────────────────────────────    │
│                                                                │
│                      ▮ Dewi Anggraini — VP Eng, Arka  ←───────┼─ attribution
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / PROGRAM                                  07 / 12     │
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
| Quote block | x:96, top y:236, width 1728px, exactly 3 ruled lines | — | — |
| Quote line text | sits 44px above its rule | `--lp-font-display`, 96–112px (default 104), weight 700, line-height 1, letter-spacing −0.01em | `--lp-fg`; one `<em>` phrase → `--lp-accent` |
| Line rules (×3) | x:96 → 1824 under each line, 1px, 196px vertical pitch | — | `--lp-line` |
| Attribution tick | 12×12px square, inline before the name | — | `--lp-accent` |
| Attribution | right-aligned to x:1824, y:876 | name: `--lp-font-display`, 30px, weight 700; role after a spaced "—": `--lp-font-body`, 24px | name `--lp-fg`, role `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Quote:** exactly 3 lines, ≤ 26 characters per line at 104px (wrap
  each line in its own span; nothing may reflow). If a line overflows,
  re-break or trim the quote first, then step down to 96px — never below,
  never to 4 lines. No quotation marks glyphs around the text — the ruled
  treatment already frames it as speech.
- **Accent phrase:** exactly one `<em>` phrase, ideally in the final
  line (the payoff position). Zero is acceptable, two is not.
- **Attribution:** one line — real name, spaced "—", role/org. No titles
  stacked on multiple lines.
- **Kicker / footer:** single line each, real deck chrome only (program,
  source, counter). Never render internal labels.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`). Swap the
  placeholder for the real logo file, or use a text wordmark in
  `--lp-font-display` weight 700 instead.
- **Fully removable:** delete the slot and nothing else moves — the
  chrome hairline already terminates the header on its own.

## Image variant

**With a portrait:** a 300×300 square portrait may sit top-right at
x:1524 → 1824, y:180 → 480; the quote block then narrows to 1360px and
line character limits drop to ≤ 21. The branding slot stays in the
header; the attribution gains nothing (the face already attributes).

**Recommended size / placeholder:** `https://placehold.co/600x600`
(rendered 300×300). **Dimension fallback:** fixed square frame,
`object-fit: cover`, token CSS fill behind the `<img>` for load
failures. The portrait is optional — the default composition is
type-only and is the stronger form.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.15s` — the three line rules wipe in `scaleX(0→1)` from the left,
   0.6s each, 0.10s stagger.
3. `0.35s` — quote lines rise `translateY(40px→0)` + fade, 0.7s each,
   0.14s stagger (text arrives just after its rule).
4. `0.95s` — attribution fades up, 0.5s.
5. `1.10s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Line rules** → the system's divider vocabulary (dashed, dotted,
  doubled) at the same coordinates; a paper-grain or notebook texture
  behind the block if the system has one, kept ≤ `--lp-fg-faint`.
- **Accent phrase** → the system's emphasis move; an accent underline
  (≤ 6px) directly under the phrase is the sanctioned extra.
- **Attribution tick** → the system's marker (arrow, asterisk, stamp),
  footprint ≤ 20×20px.
- **Branding slot** → the system's lockup rules apply; monochrome
  versions of logos are preferred on strong-colored surfaces.
- **Background** → flat `--lp-bg` by default; a ruled-paper tint is the
  natural atmospheric upgrade if the system can keep contrast.

## Failure modes to avoid

- Adding quotation-mark glyphs or a giant quote ornament — that is
  Testimony's grammar; here the rules do the framing.
- Letting a quote line float free of its rule (uneven pitch). The
  196px rhythm IS the layout.
- Centering the quote or the attribution. Everything hangs left except
  the attribution, which signs off right.
- Stacking a second quote or adding commentary paragraphs — one voice,
  three lines, done.
- Branding larger than 40px tall or placed anywhere but the reserved
  corner slot.
