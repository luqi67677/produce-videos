---
version: 1.0
name: Cover Coda
slot: closing
description: >
  Cinematic full-bleed closing — the bookend to the Cover Caption
  opening. A full-frame image (or token-built atmosphere) under a bottom
  scrim, closing statement lower-left, and a single inline contact row
  beneath it. The deck ends on a picture worth ending on.
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

# Cover Coda — closing layout

## Intent

Some decks earn a last photograph — the shipped hardware, the team at
the site, the skyline the product watches over. Cover Coda gives it the
full frame and keeps the words to two registers: one emotional line and
one practical row. Pairs naturally with Cover Caption for a
symmetrical film-frame deck, but closes any deck that has the image.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  IN CLOSING                                           12 / 12  │
│                                                                │
│                (full-bleed image or atmosphere)                │
│                                                                │
│ ░░░░░░░░░░░░░░░░░░ scrim begins ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  UNTIL THE                                                     │
│  NEXT SITE.              ← statement                           │
│  EMAIL · SITE · HANDLE   ← contact row                         │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Media layer | full bleed, `object-cover` | — | — |
| Scrim | full width, y:460 → 1080, linear gradient transparent → `--lp-bg` at 94% | — | — |
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Statement | x:96, bottom edge ≈ y:900, max-width 1400px, 1–2 lines | `--lp-font-display`, 136–152px (default 148), weight 700–800, line-height 0.95, letter-spacing −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Contact row | x:96, 32px below statement, single line, items " · " separated | `--lp-font-mono`, 15px, ls 0.08em | values `--lp-fg-muted`, separators `--lp-accent` |

## Content constraints (hard limits)

- **Statement:** 1–2 lines, ≤ 14 characters uppercase per line at
  148px. Forward-looking, not a repeat of the opening title.
- **Contact row:** 2–3 identifier items, ≤ 70 characters total.
- **Image:** key subject in the upper two-thirds; it must read through
  the closing register — end-of-day light beats product glamour.

## Image variant

This preset is image-first; the case above is the image case.

**Recommended size / placeholder:** `https://placehold.co/1920x1080`.
**Dimension fallback:** full-bleed fixed frame + `object-cover`;
keep the CSS atmosphere behind the `<img>` so a failed load degrades
to the no-image variant. The image is optional.

**Without an image:** the media layer becomes a token-only CSS
atmosphere (the design system's signature background treatment, or
layered radial gradients of `--lp-fg-faint` on `--lp-bg` drifting
darker toward the top — dusk, where Cover Caption's atmosphere is
dawn). Composition unchanged.

## Choreography

1. `0.00s` — media layer fades in with a slow 1.04→1 settle, 1.2s;
   scrim fades at `0.3s`, 0.8s.
2. `0.45s` — statement lines rise `translateY(56px→0)` + fade, 0.8s,
   0.12s stagger.
3. `0.95s` — contact row fades up, 0.5s.
4. `1.05s` — kicker and counter fade in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms or settles.

## Skin points

- **Scrim** → the system's fullbleed scrim convention.
- **Contact separators** → the system's marker glyph.
- **Media treatment** → the system's duotone/grain vocabulary; a
  closing may run the same image as the opening at a different crop —
  a deliberate echo, worth doing when the deck is a single story.

## Failure modes to avoid

- A contact grid or tri-column strip — one quiet row; this ending's
  weight is in the frame, not the directory.
- Re-using the opening statement verbatim. Echo the image if you like;
  never the words.
- A bright, busy crop fighting the scrim.
