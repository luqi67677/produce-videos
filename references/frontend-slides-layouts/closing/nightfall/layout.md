---
version: 1.0
name: Nightfall
slot: closing
description: >
  The deck ends by crossing to the alternate surface. A fully
  inverted final slide: one centered closing statement at display
  scale, and beneath it a single ruled row of the deck's three
  headline figures in mono — the numbers the audience should walk
  out carrying. One quiet contact line at the bottom. The surface
  swap says "the presentation is over; remember these."
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

# Nightfall — closing layout

## Intent

Inversion flips a slide mid-deck to mark a chapter; Nightfall flips
the LAST slide to mark **the end of the performance**. Lights down,
house dark, and against the dark surface the deck leaves exactly
three numbers and one sentence — the residue it wants in the elevator
conversation afterward. Use it for evidence-heavy decks whose close
should feel like a curtain, not a plea. If the close is an explicit
transaction, use Settlement; if it's personal, Postscript.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│░░░░░░░░░░░░░░░░ inverted surface (bg ↔ fg swap) ░░░░░░░░░░░░░░│
│░ KICKER · CLOSE                          [BRAND / WORDMARK] ←──┼─ optional
│░                                                              ░│
│░                                                              ░│
│░              The grid is no longer                           ░│
│░              the experiment.        ← statement, centered    ░│
│░                                                              ░│
│░   ──────────────────────────────────────────────────────    ░│
│░      6,500          −900 → 0          99.95%                 ░│
│░      CAMERAS LIVE   GAP TO CLOSE      FLEET UPTIME           ░│
│░   ──────────────────────────────────────────────────────    ░│
│░                                                              ░│
│░              contact@org — 09 Jul 2026                       ░│
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080, on the INVERTED surface
(the slide sets `[--lp-bg:#1a1a1a] [--lp-fg:#f1f0ee]`-style swaps in
the demo; dual-surface design systems map it to their alternate
surface instead).

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72, single line | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Branding slot (top-right, optional) | right-aligned to x:1824, y:66, ≤ 40px tall, ≤ 260px wide | wordmark in `--lp-font-display` 700 or an image logo (light/mono version) | `--lp-fg` |
| Statement | centered on x:960, block y:300 → 520, max-width 1300px, ≤ 2 lines | `--lp-font-display`, 92px, weight 800, line-height 1.05, letter-spacing −0.02em, centered | `--lp-fg`; one `<em>` word may take `--lp-accent` |
| Figure band rules | x:310 → 1610, at y:600 and y:790, 1px | — | `--lp-line` |
| Figures (×3) | three equal 433px columns across the band, centered; value at y:646, label 14px under it | value: `--lp-font-mono`, 54px, weight 500; label: `--lp-font-mono`, 15px, uppercase, letter-spacing 0.14em | value `--lp-fg`; labels `--lp-fg-muted`; ONE value may be `--lp-accent` |
| Contact line | centered on x:960, y:900 | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` |

No footer chrome — the darkness is the frame.

## Content constraints (hard limits)

- **Statement:** ≤ 60 characters, ≤ 2 lines, declarative and final —
  it must survive being the last sentence anyone reads.
- **Exactly 3 figures**, each already SHOWN earlier in the deck —
  Nightfall reprises evidence, it never introduces any. Values ≤ 9
  characters; labels ≤ 18. At most one value in accent.
- **Contact:** one line, one channel, one date. No QR, no socials
  row.
- **Surface:** full inversion (or the system's alternate surface).
  If the deck used Inversion for a section divider, Nightfall
  still works — recurrence reads as rhyme, not repetition.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot — on the dark surface, use the mark's
light or monochrome version:

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

None — the dark field is the image. Systems with a signature
texture may breathe it into the surface at ≤ 8% contrast.

## Choreography

Lights down, then the residue — total ≤ 1.7s:

1. `0.00s` — the inverted surface is already present (the slide
   transition itself is the blackout); kicker + branding fade, 0.5s.
2. `0.20s` — statement rises `translateY(36px→0)` + fade, 0.8s.
3. `0.60s` — band rules wipe `scaleX(0→1)` from center
   (`transform-origin: center`), 0.6s.
4. `0.80s` — figures fade up `translateY(20px→0)`, 0.5s, 0.12s
   stagger left → right; labels trail each by 0.1s.
5. `1.30s` — contact line fades, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Surface** → the system's alternate surface (navy, charcoal,
  deep brand color) rather than a literal token swap.
- **Figure band** → the system's divider vocabulary; rules may
  become the system's bracket or frame device at the same span.
- **Statement emphasis** → the system's emphasis move on one word,
  accent ink.
- **Branding slot** → light/mono lockup only; a full-color logo on
  the dark field is the classic final-slide wound.

## Failure modes to avoid

- Introducing a NEW number in the band — the close is a reprise;
  new evidence this late reads as something you hid.
- Four-plus figures, sparklines, or units repeated in every label.
- "Thank you" as the statement — gratitude is spoken; the slide
  carries the argument's residue.
- Low-contrast body text on the dark surface (muted is for labels,
  never the statement).
- A light logo swapped for its dark-surface version — check it.
- Branding larger than 40px tall or anywhere but the reserved corner.
