---
version: 1.0
name: Bookmark
slot: section
description: >
  A solid accent ribbon drops from the top edge like a bookmark left in
  the deck, carrying the part number at its notched tail. The section
  title sits mid-left beside it, with the part count bottom-right.
  The only section preset where the accent is a surface.
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

# Bookmark — section layout

## Intent

Every other divider treats the accent as a line or a letter; Bookmark
lets it become an object — a ribbon physically left between the deck's
pages. The notch at its tail is what sells the metaphor (a straight
bar is a decoration; a notched one is a bookmark). Warm and tactile
where Inversion is cool; suits story-driven and editorial decks.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│         ██████                                                 │
│         ██████  ← ribbon, from top edge                        │
│         ██████                                                 │
│         █ 03 █  ← numeral near the tail                        │
│         ██▼▼██  ← notch                                        │
│                                                                │
│                 WHERE THE WORK                                 │
│                 GOT HARD          ← title                      │
│                                                                │
│                 One-line framing sentence, muted.              │
│                                                    PART 3 / 5  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Ribbon | x:200 → 320 (120px wide), y:0 → 440; notch cut via `[clip-path:polygon(0_0,100%_0,100%_100%,50%_calc(100%_-_44px),0_100%)]` | — | fill `--lp-accent` |
| Ribbon numeral | centered in the ribbon's width, baseline 76px above the ribbon's bottom | `--lp-font-mono`, 34px, weight 500 | `--lp-bg` (text on the accent surface) |
| Title | x:420, top y:440, max-width 1300px, 1–2 lines | `--lp-font-display`, 128–140px (default 136), weight 700–800, line-height 0.97, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Framing line | x:420, 40px below title, max-width 720px | `--lp-font-body`, 23px, line-height 1.5 | `--lp-fg-muted` |
| Part count (bottom-right) | right-aligned x:1824, y:984 | `--lp-font-mono`, 15px, uppercase, ls 0.14em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Title:** 1–2 lines, ≤ 15 characters uppercase per line at 136px.
- **Framing line:** 1 line ≤ 90 characters. Optional.
- **Ribbon numeral:** the zero-padded part number only.
- **Part count:** "PART N / M" — this preset's whole wayfinding; do
  not add a rail.

## Image variant

**With an image:** a 560×420 image plate (1px `--lp-line` border,
mono caption below) anchors bottom-right at x:1264 → 1824, its bottom
edge at y:920; the part count moves above the plate's caption. The
chapter's key visual balancing the ribbon diagonally. **Recommended
size / placeholder:** `https://placehold.co/560x420`. **Dimension
fallback:** fixed frame, `object-cover`, token CSS fill behind
the `<img>`. The image is optional.

## Choreography

1. `0.00s` — ribbon drops: `translateY(−100%→0)` + fade, 0.8s — the
   bookmark falls into place; numeral fades at `0.55s`.
2. `0.35s` — title lines rise `translateY(48px→0)` + fade, 0.7s,
   0.12s stagger.
3. `0.80s` — framing line fades up, 0.6s.
4. `0.95s` — part count fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Ribbon** → the one place a design system's accent runs as a fill;
  systems whose accent is too hot for a 120×440 block may use their
  secondary surface with an accent edge. The notch stays.
- **Ribbon texture** → the system's pattern (stripe, grain) may fill
  the ribbon.
- **Numeral** → the system's figure style, always in the surface color.

## Failure modes to avoid

- A ribbon without the notch — it reads as a random bar.
- Moving the ribbon to the center or right; it marks where you *are*,
  left of the reading direction.
- Ribbon longer than ~480px — past half the stage it becomes a panel
  (Split Ledger's territory).
