---
version: 1.0
name: Spine
slot: opening
description: >
  Book-spine opening. A full-height vertical rule at x:600 divides a
  narrow spine column — rotated series label, monogram top, date bottom —
  from the title field. Reads like the deck is a volume pulled off a
  shelf. With an image, the spine column becomes a tall image strip.
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

# Spine — opening layout

## Intent

Verticality no other opening preset has. The rotated spine text forces a
double-take — the audience tilts their head the way they would at a
bookshelf — and instantly frames the deck as an edition of something
serial (a quarterly, a volume, a chapter of a longer program). The wide
right field then reads as the cover face.

## Region map (1920×1080 stage)

```
┌──────────────┬─────────────────────────────────────────────────┐
│  ◆ monogram  │                                                 │
│              │   KICKER · LABEL                                │
│      Q       │                                                 │
│      U       │   THE QUIET                                     │
│      A  ←rotated   QUARTER          ← title                    │
│      R       │                                                 │
│      T       │   Lead sentence, max-width 640px.               │
│      E       │                                                 │
│      R       │                                                 │
│              │                                                 │
│  08 JUL 2026 │                                        01 / 12  │
└──────────────┴─────────────────────────────────────────────────┘
      x:0→600 (rule at 600)      x:696→1824
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Spine rule | x:600, y:0 → 1080, 1px | — | `--lp-line` |
| Monogram (spine top) | centered on x:300, y:96, ≤ 64px tall | `--lp-font-display`, weight 800, or the org mark | `--lp-fg` |
| Spine label | rotated −90°, centered on x:300 / y:540, reads bottom-to-top | `--lp-font-mono`, 22px, uppercase, letter-spacing 0.5em | `--lp-fg-muted` |
| Spine date (bottom) | centered on x:300, y:984 | `--lp-font-mono`, 14px, uppercase, ls 0.14em | `--lp-fg-muted` |
| Kicker | x:696, y:180 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Title | x:696, top y:340, max-width 1030px, 2–3 lines | `--lp-font-display`, 128–144px (default 140), weight 700–800, line-height 0.97, letter-spacing −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Lead | x:696, 40px below title, max-width 640px | `--lp-font-body`, 22px, line-height 1.55 | `--lp-fg-muted` |
| Counter | right-aligned x:1824, y:984 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Spine label:** one phrase, ≤ 24 characters — the series name
  ("Quarterly Review · Vol 04"), not the deck title. The wide 0.5em
  tracking is structural.
- **Title:** 2–3 lines, ≤ 10 characters uppercase per line at 140px in
  the 1030px column.
- **Lead:** 1–3 lines, ≤ 140 characters. Optional.
- **Monogram:** 1–2 characters or a logo ≤ 64px.

## Image variant

**With an image:** the spine column (x:0 → 600) becomes a full-height
image strip, `object-cover`. The spine rule stays at x:600. The
rotated label sits on the image inside a scrim chip (its background
`--lp-bg` at ~80%); the monogram and date move onto the chip's ends or
onto the field side. Tall crops — figures, towers, racks — suit the
strip's 600×1080 proportion.

**Without an image:** flat spine column as specified; the design
system may tint the spine column with its alternate surface at ≤ 8%
contrast against `--lp-bg`.

**Recommended size / placeholder:** `https://placehold.co/600x1080`.
**Dimension fallback:** fixed 600×1080 strip, `object-cover`,
token CSS fill behind the `<img>`. The image is optional.

## Choreography

1. `0.00s` — spine rule draws downward via `scaleY(0→1)`, origin top,
   0.8s.
2. `0.25s` — monogram and spine label fade in, 0.6s; date at `0.45s`.
3. `0.40s` — kicker fades; title lines rise `translateY(48px→0)` +
   fade, 0.7s, 0.12s stagger.
4. `0.85s` — lead fades up; counter fades in, 0.6s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Spine rule** → the system's strongest vertical divider (doubled,
  dashed); full height always.
- **Monogram** → the system's mark or emblem.
- **Spine label tracking** → may open further (up to 0.7em) in systems
  with condensed mono faces.

## Failure modes to avoid

- Horizontal text in the spine column (other than monogram and date).
  The rotation is the concept.
- Moving the spine past x:640 — the column must stay a spine, not a
  panel (that is Split Ledger's territory).
- Putting the deck title in the spine and the series in the field —
  the hierarchy is field = this deck, spine = the series it belongs to.
