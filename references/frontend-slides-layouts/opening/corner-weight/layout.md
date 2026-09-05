---
version: 1.0
name: Corner Weight
slot: opening
description: >
  Diagonal counterweight opening. The title block owns the top-left,
  a compact presenter card answers from the bottom-right, and the whole
  diagonal between them stays empty. With an image, the presenter card
  becomes a framed photo card with caption.
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

# Corner Weight — opening layout

## Intent

Two objects and a diagonal of silence. The tension between the heavy
top-left title and the small bottom-right card does all the
compositional work — the emptiness between them is the design, the way
a two-figure photograph works. Quietly confident; suits strategy and
board decks that must feel unhurried.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                                │
│  THE LONG                                                      │
│  GAME             ← title, top-left                            │
│  ────────                                                      │
│                                                                │
│                    (empty diagonal)                            │
│                                                                │
│                                        ▮▮▮▮                    │
│                                        A. Rahman               │
│                                        HEAD OF PLATFORM        │
│                                          FATHOM — 08 JUL 2026  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker | x:96, y:96 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Title | x:96, top y:150, max-width 1100px, 2–3 lines | `--lp-font-display`, 120–140px (default 132), weight 700–800, line-height 0.97, letter-spacing −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Title tail rule | x:96, 40px below title, 200×1px | — | `--lp-line` |
| Presenter card | right-aligned block at x:1824, bottom-anchored at y:984; text right-aligned | — | — |
| · card accent bar | 48×6px, right-aligned, 24px above name | — | `--lp-accent` |
| · card name | | `--lp-font-display`, 34px, weight 700 | `--lp-fg` |
| · card role / meta | one per line, 8px apart | `--lp-font-mono`, 15px, uppercase, ls 0.12em, line-height 1.9 | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 2–3 lines, ≤ 12 characters uppercase per line at 132px.
- **Presenter card:** name + 1–3 mono lines (role, org — date, counter).
  Total card height ≤ 220px.
- **Nothing else.** No lead sentence — if the deck needs one, use
  Offset Marquee. The diagonal stays empty.

## Image variant

**With an image:** the presenter card becomes a framed image card at
the same anchor — 560×420px, 1px border in `--lp-line`, image inset
with `object-cover`, and a mono caption line below the frame
(right-aligned, 13px, `--lp-fg-muted`). The presenter's name and role
move to a single mono line under the kicker (top-left). Portrait or
detail crops; the card is an object, not a window.

**Without an image:** the presenter card as specified above.

**Recommended size / placeholder:** `https://placehold.co/560x420`.
**Dimension fallback:** fixed 560×420 frame, `object-cover`,
token CSS fill behind the `<img>`. The image is optional — swap freely
between card and photo per deck.

## Choreography

1. `0.00s` — kicker fades, 0.5s.
2. `0.10s` — title lines rise `translateY(48px→0)` + fade, 0.7s, 0.12s
   stagger; tail rule wipes `scaleX(0→1)` at `0.5s`.
3. `0.65s` — presenter card (or image card) rises `translateY(32px→0)`
   + fade, 0.7s — deliberately last, the answer to the title.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Tail rule** → the system's small punctuation mark (short accent
  rule, dots, a glyph) ≤ 240px wide.
- **Card accent bar** → the system's marker device.
- **Background** → an atmospheric treatment may occupy the empty
  diagonal (gradient sweep, faint texture) as long as both corners stay
  on quiet ground.

## Failure modes to avoid

- Anything placed on the diagonal between the two corners.
- A third anchor (logo in another corner). Two objects only — a logo
  may join the presenter card, ≤ 40px, above the accent bar.
- Left-aligning the presenter card — it must be right-aligned, hugging
  its corner.
