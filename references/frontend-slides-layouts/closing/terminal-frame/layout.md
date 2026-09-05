---
version: 1.0
name: Terminal Frame
slot: closing
description: >
  Closing slide composed inside an inset hairline frame. A huge closing
  statement anchors the lower-left over a cropped ghost echo word, with a
  tri-column contact strip pinned to the frame's bottom edge. Reads as a
  deliberate full-stop to the deck in any design system's skin.
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

# Terminal Frame — closing layout

## Intent

The last slide should feel like a **full stop, not a fade-out**: the deck's
voice at maximum scale, plus the practical exits (contact, links) in one
disciplined strip. The inset frame formally "closes" the deck — it is the
visual signal that nothing follows.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│   ┌────────────────────────────────────────────────────────┐   │ ← frame
│   │ IN CLOSING                                     12 / 12 │   │   inset 48px
│   │                                                        │   │
│   │                                       ┌────────────────┼───┼──
│   │                (empty space)          │ ghost echo word│   │  cropped by
│   │                                       └────────────────┼───┼──  frame edge
│   │  THANK <em>YOU.</em>   ← closing statement             │   │
│   │  One-line coda, muted.                                 │   │
│   │                                                        │   │
│   │  ────────────────┬──────────────────┬───────────────── │   │
│   │  EMAIL           │ SITE             │ HANDLE           │   │ ← contact
│   │  CONTACT         │ example.com      │ @example         │   │   strip
│   └────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Frame | absolute inset 48px (48,48 → 1872,1032), 1px border, no fill, no radius | — | `--lp-line` |
| Inner content box | 72px padding inside the frame (x:120 → 1800) | — | — |
| Closing kicker (top-left) | x:120, y:112 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned to x:1800, y:112 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Ghost echo word | right:96 (inside frame), vertically centered on the statement's top edge, 380px, cropped by the frame's right edge (frame clips overflow) | `--lp-font-display`, weight 700–800, outline (2px text-stroke, transparent fill) | `--lp-fg-faint` |
| Closing statement | x:120, bottom edge ≈ y:690, max-width 1400px | `--lp-font-display`, 160–192px (default 176), weight 700–800, line-height 0.95, letter-spacing −0.02em | `--lp-fg`; `<em>` phrase → `--lp-accent` |
| Coda line | x:120, 36px below statement, max-width 760px | `--lp-font-body`, 24px, line-height 1.5 | `--lp-fg-muted` |
| Contact strip | pinned to frame bottom: x:120 → 1800, top edge y:872; 3 equal columns; 1px hairline across the top; 1px vertical hairlines between columns; each cell padded 32px top, columns 2–3 padded 48px left | labels: `--lp-font-mono` 13px uppercase ls 0.16em; values: `--lp-font-body` 24px | labels `--lp-fg-muted`, values `--lp-fg` |

## Content constraints (hard limits)

- **Statement:** 1–2 lines, ≤ 16 characters per line at 176px. This is a
  statement, not a paragraph: "Thank you.", "Let's build it.", a short
  callback to the deck's title. At most one `<em>` phrase.
- **Coda:** 1–2 lines, ≤ 140 characters. Optional.
- **Ghost echo word:** one word, ≤ 6 characters — an echo of the statement
  or the deck's core noun. Must be clipped by the frame's right edge.
- **Contact strip:** exactly 3 cells. Natural fills: email / site / handle,
  or email / repo / next-step date. Each value is a single line. If only
  2 real items exist, the third cell holds the deck title or org name —
  never leave a cell empty, never drop to 2 columns.

## Image variant

**With an image:** the ghost echo word is replaced by a 700×500 image
plate anchored to the frame's right edge — its right edge bleeding
80px past the frame so the frame clips it (the same crop rule the
ghost obeys), top at y:200. No border; the frame's clipping IS the
chrome. The statement and contact strip are unchanged.

**Recommended size / placeholder:** `https://placehold.co/700x500`.
**Dimension fallback:** fixed 700×500 frame, `object-cover`,
token CSS fill behind the `<img>`. The image is optional — the ghost
echo word is the default.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — frame fades in, 0.7s.
2. `0.20s` — kicker and counter fade in, 0.5s.
3. `0.30s` — ghost echo drifts in from +40px right with fade, 0.9s.
4. `0.45s` — statement lines rise: `translateY(56px→0)` + fade, 0.7s,
   0.12s stagger per line.
5. `0.85s` — coda fades up, 0.6s.
6. `1.00s` — contact cells rise with 0.1s stagger per column, 0.6s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Frame** → the system's border vocabulary (double rule, dashed, corner
  ticks, thick offset frame) at the same inset; it must remain an inset
  rectangle that clips the ghost element.
- **Ghost echo word** → the system's texture fingerprint or signature
  glyph (a quote mark, a monogram) at `--lp-fg-faint` contrast.
- **Contact strip hairlines** → the system's divider style; the tri-column
  rhythm is structural and stays.
- **`<em>` treatment** → the system's emphasis move, colored `--lp-accent`.
- **Background** → flat `--lp-bg` by default; the system's atmospheric
  background is allowed inside the frame if text contrast is preserved.

## Failure modes to avoid

- Centering the statement. The lower-left anchor against the upper-right
  ghost is the composition.
- Adding a QR code, logo wall, or "Questions?" bullet list. One logo is
  permitted, only in place of the counter, ≤ 40px tall.
- Letting the ghost word render fully inside the frame — uncropped it
  reads as a second headline. It must bleed past the frame edge.
- Filling the contact values with sentences. Values are identifiers,
  not prose.
