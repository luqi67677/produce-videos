---
version: 1.0
name: Cover Caption
slot: opening
description: >
  Cinematic full-bleed opening. The image is the slide; a bottom scrim
  carries the title lower-left with a mono caption line, and only a thin
  chrome row survives at the top. Without an image, the same composition
  sits on a full-bleed CSS atmosphere — layered gradients in the
  system's own tones.
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

# Cover Caption — opening layout

## Intent

The film-poster register: one frame, one line of type, total commitment.
Everything the other openings do with grids and rules, this one does
with a photograph and restraint. The caption line under the title is
what keeps it a document rather than an ad — it timestamps and locates
the image like a photo essay's first plate.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       01 / 12  │
│                                                                │
│                                                                │
│                (full-bleed image or atmosphere)                │
│                                                                │
│ ░░░░░░░░░░░░░░░░░░░ scrim begins ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  TWELVE SITES,                                                 │
│  ONE NETWORK            ← title                                │
│  JAVA DEPLOYMENT CORRIDOR — JUNE 2026   ← caption line         │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Media layer | full bleed, `object-cover` | — | — |
| Scrim | full width, y:480 → 1080, linear gradient transparent → `--lp-bg` at 92% | — | — |
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` (both may sit on a scrim chip if the crop is bright) |
| Title | x:96, bottom edge ≈ y:920, max-width 1400px, 1–2 lines | `--lp-font-display`, 136–152px (default 152), weight 700–800, line-height 0.95, letter-spacing −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Caption line | x:96, 28px below title | `--lp-font-mono`, 15px, uppercase, ls 0.16em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 1–2 lines, ≤ 15 characters uppercase per line at 152px.
- **Caption line:** 1 line, ≤ 60 characters — where/when of the image
  (or, without an image, the presenter — org — date line).
- **No lead paragraph.** The image is the lead.
- **Image:** must survive a bottom scrim — key subject in the upper
  two-thirds. Faces near the bottom edge will be swallowed.

## Image variant

This preset is image-first; the case above is the image case.

**Recommended size / placeholder:** `https://placehold.co/1920x1080`.
**Dimension fallback:** full-bleed fixed frame + `object-cover`
absorbs any delivered aspect ratio; keep the CSS atmosphere behind the
`<img>` so a failed image degrades to the no-image variant unnoticed.
The image is optional — removing the `<img>` yields the variant below.

**Without an image:** the media layer becomes a full-bleed CSS
atmosphere built only from tokens — e.g. two large radial gradients of
`--lp-fg-faint` on `--lp-bg`, or the design system's signature
background treatment at full strength. The scrim, title, caption
(now presenter — org — date), and chrome are unchanged. This is the
skill's CSS-generated-visuals path, first-class not fallback.

## Choreography

1. `0.00s` — media layer fades in with a slow 1.04→1 scale settle, 1.2s.
2. `0.30s` — scrim fades in, 0.8s.
3. `0.50s` — title lines rise `translateY(56px→0)` + fade, 0.8s, 0.12s
   stagger.
4. `0.95s` — caption line fades up, 0.5s.
5. `1.05s` — kicker and counter fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms or scale settles.

## Skin points

- **Scrim** → the system's fullbleed scrim convention (color, height,
  strength) if it has one; legibility over the title zone is the only
  hard rule.
- **Caption line** → the system's label treatment.
- **Media treatment** → duotone, grain, or desaturation per the
  system's image vocabulary.

## Failure modes to avoid

- Centering the title. Lower-left under the scrim is the composition.
- Stacking chrome (logos, badges) on the image beyond the two corner
  items.
- A scrim so heavy the image dies — if the crop needs > 92% cover to be
  legible, choose a different image or Half Plate.
