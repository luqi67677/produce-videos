---
version: 1.0
name: Echo Stack
slot: closing
description: >
  Typographic crescendo. The closing phrase repeats down the slide in five
  rows that climb from near-invisible to full contrast, the final row
  landing the accent. Contacts run as a single quiet line in the footer.
  A poster, not a page.
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

# Echo Stack — closing layout

## Intent

Repetition as emphasis: the same short phrase stacked five times, fading
in weight of presence until the last row says it "for real." The audience
reads one sentence but feels a drumroll. Works because the content is
minimal — this preset trades information density for a single memorable
beat, so all practical details compress into one footer line.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  IN CLOSING                                           12 / 12  │
│                                                                │
│  Thank you        ← row 1, 10% opacity                         │
│  Thank you        ← row 2, 18%                                 │
│  Thank you        ← row 3, 32%                                 │
│  Thank you        ← row 4, 55%                                 │
│  Thank you.       ← row 5, 100%, period in accent              │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  EMAIL · SITE · HANDLE                                FATHOM   │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned to x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Echo stack | x:96, top y:160, 5 rows, font-size 140px, line-height 1.04 (row pitch ≈ 146px) | `--lp-font-display`, weight 700–800, letter-spacing −0.02em | rows 1–4: `--lp-fg` at 10% / 18% / 32% / 55% opacity; row 5: `--lp-fg` at 100% |
| Final-row punctuation or `<em>` | inside row 5 | inherits row type | `--lp-accent` |
| Footer hairline | x:96 → 1824, y:958, 1px | — | `--lp-line` |
| Footer left (contacts) | x:96, y:982, single line, items separated by " · " | `--lp-font-mono`, 15px, letter-spacing 0.08em | values `--lp-fg-muted`, separators `--lp-accent` |
| Footer right (org / deck title) | right-aligned to x:1824, y:982 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Echo phrase:** one phrase, ≤ 16 characters mixed case (≤ 13
  uppercase) at 140px so all five rows fit x:96 → 1824 on one line each.
  Rows 1–4 are identical and unpunctuated; row 5 carries the terminal
  punctuation (in `--lp-accent`) or one `<em>` word. The phrase does not
  change between rows — variation kills the drumroll.
- **Exactly 5 rows.** Four reads as a mistake, six overflows the stage.
- **Footer contacts:** 2–3 items, single line, identifiers only
  (email, site, handle).
- **Kicker / counter / footer-right:** one line each, real chrome only.

## Image variant

**With an image:** a tall image strip occupies x:1400 → 1824,
y:150 → 890 (424×740, 1px `--lp-line` border) — the stack's short
rows leave that field empty, so the strip becomes the counterweight.
Choose a quiet vertical crop; the strip must not out-shout row 5.

**Recommended size / placeholder:** `https://placehold.co/424x740`.
**Dimension fallback:** fixed 424×740 frame, `object-cover`,
token CSS fill behind the `<img>`. The image is optional — the empty
right field is the default and is equally correct.

## Choreography

Staggered entrance on slide activation, total ≤ 1.6s:

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.20s` — rows 1–4 fade to their resting opacity in order, 0.45s
   each, 0.13s stagger (0.20 / 0.33 / 0.46 / 0.59).
3. `0.75s` — row 5 rises: `translateY(40px→0)` + fade, 0.7s; its accent
   punctuation pops via `scale(0→1)` at `1.15s`, 0.4s.
4. `1.20s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Opacity ladder** → a system with layered tints may express rows 1–4
  in its tint scale (e.g., four steps of its muted palette) instead of
  raw opacity, as long as the crescendo to row 5 stays monotonic.
- **Row 1–4 rendering** → systems with an outline/stroke vocabulary may
  render the faint rows as outline text at `--lp-fg-faint`, keeping
  row 5 solid.
- **Final punctuation** → the system's emphasis move (color, underline
  flick, stamp) on the last row's terminal beat, colored `--lp-accent`.
- **Footer hairline** → the system's divider vocabulary.
- **Background** → flat `--lp-bg` or a very quiet texture; anything busy
  destroys the ladder's legibility.

## Failure modes to avoid

- Using a long phrase. "Thank you" works; a sentence does not — if the
  phrase wraps, this is the wrong preset.
- Randomizing the opacity ladder or making two rows equal — the
  crescendo must strictly increase downward.
- Adding a coda paragraph, QR code, or contact grid to the field. The
  stack and one footer line is the entire slide.
- Centering the stack. Left-anchored rows with the ragged right edge are
  the poster's texture.
