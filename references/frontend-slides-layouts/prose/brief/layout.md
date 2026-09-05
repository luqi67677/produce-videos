---
version: 1.0
name: Brief
slot: prose
description: >
  The reading slide. A display-scale lead sentence states the
  argument; below a hairline, ONE well-set memo paragraph carries the
  reasoning at genuine reading size, annotated by two or three mono
  margin notes in the right column. For the moment a deck must slow
  down and actually explain something — the pack's only prose layout.
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

# Brief — prose layout

## Intent

Decks fear paragraphs, so nuance gets shredded into fragments and
the one idea that needed three connected sentences never survives.
Brief is the sanctioned exception: **one paragraph, set like a
magazine would set it** — generous size, real leading, a measure the
eye can track — with the argument stated first at display scale so
skimmers still leave with it. The margin notes hold the numbers so
the prose doesn't have to. Use it at most twice per deck, at the
moments that genuinely need reasoning; three Briefs in a row is a
memo, and memos should be sent, not projected.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│  The cameras were never                                        │
│  the hard part.                    ← lead sentence, ≤ 2 lines  │
│                                                                │
│  ──────────────────────────────────                            │
│                                          ┊  ─────────          │
│  One measured paragraph, six lines       ┊  MARGIN NOTE        │
│  at most, at genuine reading size,       ┊  90 characters      │
│  carrying the reasoning the rest         ┊                     │
│  of the deck compresses. It ends         ┊  ─────────          │
│  on its own conclusion.                  ┊  MARGIN NOTE        │
│                                                                │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / AUTHOR                                   05 / 12     │
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
| Lead sentence | x:96, y:196, max-width 1250px, ≤ 2 lines | `--lp-font-display`, 64px, weight 700, line-height 1.1, letter-spacing −0.01em | `--lp-fg`; one `<em>` phrase may take `--lp-accent` |
| Lead rule | x:96, 40px under the lead, 560×2px | — | `--lp-line` |
| Paragraph | x:96, 48px under the rule, max-width 1150px, ≤ 6 lines | `--lp-font-body`, 29px, line-height 1.65 | `--lp-fg` |
| Margin column | x:1360 → 1824 (464px) , first note top-aligned with the paragraph | — | — |
| Margin notes (×2–3) | each opened by a 48×2px rule, 12px gap, ≤ 3 lines, 120px vertical rhythm between notes | `--lp-font-mono`, 17px, line-height 1.5, letter-spacing 0.02em | rule `--lp-accent`; text `--lp-fg-muted`; one figure per note may be `--lp-fg` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source/author) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Lead sentence:** ≤ 90 characters, ≤ 2 lines, and it must BE the
  argument — a reader who stops here has the thesis.
- **Exactly one paragraph,** 350–550 characters, ≤ 6 lines at the
  fixed measure. It must read as connected reasoning (because,
  therefore, unless) — a paragraph of stapled fragments is a list
  slide in disguise; use Ledger List.
- **No mid-paragraph emphasis** beyond at most one bold phrase.
  Prose earns attention by cadence, not decoration.
- **Margin notes:** 2–3, each ≤ 90 characters, each carrying a
  FIGURE or citation the paragraph references — never a second
  argument. Zero notes is acceptable (the paragraph widens to
  1400px).
- **One Brief per argument;** at most two per deck.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

**With a supporting exhibit:** the margin column may instead hold one
440×300 image (a document scan, a site photo the paragraph cites)
with a mono caption beneath, top-aligned with the paragraph; margin
notes then drop to at most one, below the image.

**Recommended size / placeholder:** `https://placehold.co/440x300`.
**Dimension fallback:** fixed frame, `object-fit: cover`, token CSS
fill behind the `<img>`. Optional — notes are the default.

## Choreography

Reading order, unhurried, total ≤ 1.5s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — lead sentence rises `translateY(36px→0)` + fade, 0.7s.
3. `0.40s` — lead rule wipes `scaleX(0→1)` origin left, 0.5s.
4. `0.55s` — the paragraph fades in AS ONE BLOCK (no line-by-line
   theatrics — it's for reading), 0.7s.
5. `0.90s` — margin notes fade up `translateY(16px→0)`, 0.5s, 0.12s
   stagger.
6. `1.20s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Paragraph face** → serif systems shine here; the measure and
  leading stand regardless of face.
- **Lead rule** → the system's signature rule/marker, ≤ 560×8px.
- **Margin note rules** → the system's tick vocabulary, accent ink.
- **First-line treatment** → the system may add a drop cap (3 lines
  deep, display face) if it owns one; the measure adjusts around it.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Two paragraphs, or a paragraph plus bullets — the discipline IS
  one block of reasoning.
- Type below 26px "to fit more" — cut words, never size. This slide
  is read from the back row.
- Margin notes that argue instead of cite (a second voice splits
  the slide).
- Justified text (rivers) or centered prose.
- A lead sentence in title case — it's a sentence, not a heading.
- Branding larger than 40px tall or anywhere but the reserved corner.
