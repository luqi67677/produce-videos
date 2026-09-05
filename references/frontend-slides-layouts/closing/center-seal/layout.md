---
version: 1.0
name: Center Seal
slot: closing
description: >
  Fully symmetric closing. A small ring "seal" hangs above a centered
  closing statement and coda, with a single centered contact line near
  the bottom and metadata in the top corners. Ceremonial, quiet, final —
  the closing counterpart to the Monolith opening.
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

# Center Seal — closing layout

## Intent

Where Terminal Frame is architectural and Echo Stack is a poster, Center
Seal is a **ceremony**: everything on the vertical center axis, crowned
by a small ring that reads as a wax seal or medal. The restraint is the
point — a deck that ends this way looks like it planned its own ending.
Pairs naturally with the Monolith opening for a symmetric deck frame,
but stands alone with any opening.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  IN CLOSING                                           12 / 12  │
│                                                                │
│                            ╭────╮                              │
│                            │ NF │        ← ring seal            │
│                            ╰────╯                              │
│                                                                │
│                          ONWARD.         ← centered statement   │
│                                                                │
│          One-sentence coda, centered, max 720px.               │
│                                                                │
│        EMAIL   ·   SITE   ·   HANDLE     ← one contact line     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Everything except the corner
chrome is centered on x:960.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned to x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Ring seal | centered, top y:280, 140×140px circle, 1px border, no fill | monogram inside: `--lp-font-mono`, 20px, uppercase, letter-spacing 0.3em (offset so tracking stays visually centered) | border `--lp-accent`, monogram `--lp-accent` |
| Statement | centered, top y:490, full content width, text-align center | `--lp-font-display`, 160–184px (default 176), weight 700–800, line-height 0.98, letter-spacing −0.02em | `--lp-fg`; `<em>` or terminal punctuation → `--lp-accent` |
| Coda | centered, 40px below statement, max-width 720px | `--lp-font-body`, 24px, line-height 1.55, text-align center | `--lp-fg-muted` |
| Contact line | centered, y:900, single line, items separated by " · " | `--lp-font-mono`, 16px, letter-spacing 0.08em | values `--lp-fg-muted`, separators `--lp-accent` |

## Content constraints (hard limits)

- **Statement:** 1 line strongly preferred, 2 lines maximum; ≤ 12
  characters uppercase / ≤ 15 mixed case per line at 176px. One word
  plus terminal punctuation ("Onward.", "Thank you.") is the ideal
  register. Punctuation or one `<em>` word in `--lp-accent`.
- **Ring monogram:** 1–3 characters (initials, org monogram, or the
  deck number as "№12"). The ring is required; the monogram may be
  omitted, leaving an empty ring.
- **Coda:** 1–2 lines, ≤ 140 characters. Optional.
- **Contact line:** 2–3 identifier items on one line. If it would
  exceed ~70 characters, drop an item rather than shrink the type.
- **Corners:** top two only — bottom corners stay empty; the contact
  line owns the bottom zone alone.

## Image variant

**With an image:** the ring seal becomes a 140px circular image
medallion — same center, `rounded-full`, the 1px `--lp-accent`
ring now enclosing the image (presenter portrait, team mark, or a
circular product detail). The monogram is dropped.

**Recommended size / placeholder:** `https://placehold.co/280x280`
(2× for sharpness at 140px). **Dimension fallback:** fixed 140×140
circular frame, `object-cover`, token CSS fill behind the
`<img>`. The image is optional — the empty ring is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — ring scales in: `scale(0.7→1)` + fade, 0.7s; monogram
   fades at `0.35s`, 0.5s.
2. `0.30s` — statement rises: `translateY(48px→0)` + fade, 0.8s
   (2nd line staggers +0.12s); accent punctuation pops via
   `scale(0→1)` at `0.95s`, 0.4s.
3. `0.75s` — coda fades up, 0.6s.
4. `0.95s` — contact line fades in, 0.5s.
5. `1.10s` — corner chrome fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Ring seal** → the system's emblem vocabulary: a double ring, a
  rotated square, a stamp outline, or its actual logo mark ≤ 150×150px,
  centered at the same coordinates in `--lp-accent`.
- **Contact separators** → the system's marker glyph (dot, dash, slash)
  in `--lp-accent`.
- **`<em>`/punctuation treatment** → the system's emphasis move, colored
  `--lp-accent`.
- **Background** → flat `--lp-bg` or a symmetric atmospheric treatment
  (vignette, centered glow). Directional backgrounds break the ceremony —
  use Terminal Frame or Split Curtain instead.

## Failure modes to avoid

- Anything off-axis: logos in the bottom corner, left-aligned codas,
  a second column. Zero asymmetry is the contract.
- A long statement. If it needs more than two short lines, this is the
  wrong preset.
- Making the ring big. Past ~150px it becomes a graphic and competes
  with the statement; the seal must stay a punctuation-sized object.
- Adding a hairline footer — the bottom zone is intentionally unruled;
  the contact line floats.
