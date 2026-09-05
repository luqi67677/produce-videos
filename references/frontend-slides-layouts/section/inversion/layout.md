---
version: 1.0
name: Inversion
slot: section
description: >
  The divider that changes the weather. The entire slide flips to the
  deck's alternate surface; on it, only an outlined part-number tag, a
  vertically centered title, and a row of progress segments. The
  surface swap is the decoration — the layout stays almost empty.
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

# Inversion — section layout

## Intent

After five content slides on one surface, a full flip to the opposite
surface is the strongest "new chapter" signal a deck can send — the
room feels the lights change before reading a word. Because the flip
does the work, the composition must stay austere: one tag, one title,
one progress row. **Token rule:** on this slide, `--lp-bg`/`--lp-fg`
map to the design system's *alternate* surface pair (navy slide in a
cream deck, and vice versa); single-surface systems invert literally.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  PART THREE          ┌────┐                                    │
│                      │ 03 │  ← outlined tag                    │
│                      └────┘                                    │
│                                                                │
│  EXECUTION,                                                    │
│  DAY BY DAY          ← title, vertically centered              │
│                                                                │
│                                                                │
│                              ▬▬ ▬▬ ▰▰ ▭▭ ▭▭  ← progress        │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Part tag | x:96, y:120; outlined box, 1px border, padding 14×22 | `--lp-font-mono`, 20px, ls 0.1em | border + text `--lp-accent` |
| Title | x:96, vertically centered (block center ≈ y:540), max-width 1500px, 1–2 lines | `--lp-font-display`, 144–160px (default 156), weight 700–800, line-height 0.96, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Progress segments | right-aligned to x:1824, y:960; one 48×4px segment per part, 16px gaps | — | done `--lp-fg-muted`, current `--lp-accent`, future `--lp-fg-muted` at 35% |

## Content constraints (hard limits)

- **Title:** 1–2 lines, ≤ 14 characters uppercase per line at 156px.
- **Tag:** the zero-padded part number only.
- **Progress:** 3–6 segments, exactly one current. No labels — the
  segments are rhythm, not navigation (label the parts in Chapter Gate
  or Index Ledger instead).
- **Nothing else.** No framing sentence; the flip plus the title is
  the whole message.

## Image variant

**With an image:** full-bleed behind everything under a heavy uniform
scrim of this slide's (inverted) `--lp-bg` at ≥ 85% — texture, not
picture. **Recommended size / placeholder:**
`https://placehold.co/1920x1080`. **Dimension fallback:** full-bleed
frame, `object-cover`, flat surface behind the `<img>`. The image
is optional and usually omitted.

## Choreography

1. `0.00s` — the surface is already flipped when the slide arrives (a
   cross-fade between slides sells it; do not animate the flip inside
   the slide).
2. `0.10s` — kicker and tag fade in, 0.5s.
3. `0.25s` — title lines rise `translateY(52px→0)` + fade, 0.8s,
   0.12s stagger.
4. `0.80s` — progress segments fade in left-to-right, 0.3s each,
   0.06s stagger; the current one last.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Tag** → the system's tag/pill vocabulary.
- **Segments** → the system's marker glyphs (dots, ticks, dashes) at
  the same rhythm.
- **Surface** → dual-surface systems use their real alternate surface;
  the flip must be unmistakable side-by-side with a content slide.

## Failure modes to avoid

- Using Inversion when the deck never established a home surface —
  the flip only reads against a norm.
- Two Inversion dividers on the same surface in a row; alternate or
  choose another divider.
- Filling the space (ghosts, rails, sentences). Austerity is the
  register.
