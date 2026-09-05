---
version: 1.0
name: Horizons
slot: roadmap
description: >
  Roadmap as three receding horizons. Now / Next / Later columns, each
  headed by a phase word with a mono date range and a hairline, each
  carrying up to three commitments. The columns fade with distance —
  Now at full contrast, Next at 70%, Later at 45% — so the slide's own
  ink admits how certainty decays. NOW carries the accent.
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

# Horizons — roadmap layout

## Intent

Roadmap slides lie by uniformity: an item shipping next sprint and a
2028 aspiration get the same bullet, the same weight, the same
confidence. Horizons builds the honesty into the ink — **the further
the horizon, the fainter the type**. Audiences read the fade without
being told, and the presenter never has to walk back a "commitment"
that was always a sketch. Use it whenever someone asks "what's on the
roadmap"; the fade is the answer's integrity.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Where the platform goes                  ← headline           │
│                                                                │
│  ▮ Now          Next             Later                         │
│  Q3 2026        Q4 26 — Q1 27    2027 +                        │
│  ───────────    ───────────      ───────────                   │
│  Item           Item (70%)       Item (45%)                    │
│  note           note             note                          │
│  Item           Item             Item                          │
│  note           note             note                          │
│  Item           Item                                           │
│  note           note                                           │
│  ─────────────────────────────────────────────────────────     │
│  CAVEAT / BASIS                                    13 / 14     │
└────────────────────────────────────────────────────────────────┘
     full contrast    fading           faintest
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px** left/right
margins, **72px** top/bottom margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72, single line | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Branding slot (top-right, optional) | right-aligned to x:1824, y:66, ≤ 40px tall, ≤ 260px wide | wordmark in `--lp-font-display` 700 or an image logo | `--lp-fg` |
| Chrome hairline | x:96 → 1824, y:118, 1px | — | `--lp-line` |
| Headline | x:96, y:164, max-width 1400px, 1 line | `--lp-font-display`, 64px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Columns (×3) | x:96, 672, 1248; each 480px wide, 96px gutters | — | — |
| Phase words | column top y:300; NOW takes a 14×14px accent tick inline before it | `--lp-font-display`, 44px, weight 700 | `--lp-fg` (subject to column fade) |
| Date ranges | 10px under the phase word | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` (subject to fade) |
| Column hairlines | full column width at y:408, 1px | — | `--lp-line` |
| Items | from y:444, up to 3 per column, 150px pitch: title + note | title: `--lp-font-display`, 30px, weight 700; note: `--lp-font-body`, 20px, line-height 1.4, ≤ 2 lines | title `--lp-fg`, note `--lp-fg-muted` (both subject to fade) |
| Column fade | Now: opacity 1.0; Next: 0.70; Later: 0.45 — applied to the whole column | — | — |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (caveat) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 horizons** with these words (or the deck language's
  equivalents): Now, Next, Later. Quarters/years go in the date
  range, not the phase word.
- **Items:** Now 2–3, Next 2–3, Later 1–2. LATER MUST HOLD FEWER OR
  EQUAL ITEMS THAN NOW — a roadmap fat at the far end is a wish list.
- **Item titles:** ≤ 26 characters, one line. Notes: ≤ 80 characters,
  ≤ 2 lines, optional per item but consistent within a column.
- **Date ranges:** ≤ 16 characters, honest ("2027 +" beats "H1 2027"
  when nobody believes H1).
- **The fade is fixed** (1.0 / 0.70 / 0.45) and applies to the whole
  column including its phase word. Only the footer caveat may state
  it in words ("later items are directional").

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

Horizons is type-only — pictures of the future are the exact
dishonesty the fade exists to avoid. The sanctioned addition is the
design system's texture fingerprint behind the LATER column only, at
≤ `--lp-fg-faint`, reinforcing its sketch status.

## Choreography

The horizons arrive nearest first, total ≤ 1.6s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline rises `translateY(32px→0)` + fade, 0.6s.
3. `0.30s` — NOW column: phase word + date fade up `translateY(24px→0)`
   0.5s, hairline wipes, items follow 0.08s apart.
4. `0.55s` — NEXT column, same sequence (to its 0.70 opacity).
5. `0.80s` — LATER column, same sequence (to its 0.45 opacity).
6. `1.20s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms (at final opacities).

## Skin points (where the design system may substitute)

- **Accent tick** → the system's marker vocabulary, ≤ 20×20px, NOW
  only.
- **Column hairlines** → the system's divider vocabulary.
- **Fade mechanics** → systems with an ink-mix convention may step
  color toward the surface instead of using opacity, matching 70% /
  45% perceived contrast.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; no atmosphere behind NOW (the
  concrete column stays concrete).

## Failure modes to avoid

- Equal ink across all three columns — that uniformity is the lie
  this preset exists to kill. Never "fix" the faint columns.
- Dates promising precision the fade contradicts ("14 Mar 2028").
- A fourth horizon, or renaming to Q3/Q4/Q1 (quarters are dates, not
  horizons).
- LATER holding the most items.
- Progress bars, percent-complete chips, or status colors — this is
  a statement of intent, not a Jira board.
- Branding larger than 40px tall or anywhere but the reserved corner.
