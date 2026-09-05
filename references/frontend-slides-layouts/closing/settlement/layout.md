---
version: 1.0
name: Settlement
slot: closing
description: >
  The close as a settled account. Three ruled ledger rows itemize
  what was shown, what is asked, and what the yes unlocks — each row
  a label and a terse right-aligned entry — then a bookkeeper's
  double rule, and beneath it the single settlement line at display
  scale. One contact line ends the page. The deck closes the way a
  ledger closes: totaled and signed.
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

# Settlement — closing layout

## Intent

Most closings restate the vibe; Settlement restates **the account**.
Bookkeeping grammar carries moral weight — itemized, totaled, ruled
off — and borrowing it tells the room the deck's arithmetic is
closed: here is what you saw, here is what it costs, here is what
your yes buys. The double rule (the accountant's mark for a final
total) is the slide's one flourish. Pair it naturally with a Dossier
opening; use Postscript when the close is personal rather than
transactional.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CLOSE OF FILE                  [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│  SHOWN        Twelve cities, one federation      ← row 1       │
│  ─────────────────────────────────────────────────────────     │
│  ASKED        Rp 40B — phase-two budget line     ← row 2       │
│  ─────────────────────────────────────────────────────────     │
│  UNLOCKED     Eight more cities by December      ← row 3       │
│  ═════════════════════════════════════════════════════════     │
│                              ↑ double rule (the total mark)    │
│  One vote settles it.        ← settlement line, display scale  │
│                                                                │
│  ─────────────────────────────────────────────────────────     │
│  CONTACT — EMAIL — DATE                            12 / 12     │
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
| Ledger rows (×3) | tops at y:220, 342, 464; each 122px tall, closed by a hairline at its bottom | — | rules `--lp-line` |
| Row labels | x:96, vertically centered per row | `--lp-font-mono`, 17px, uppercase, letter-spacing 0.16em | `--lp-fg-muted`; the ASKED label `--lp-accent` |
| Row entries | right-aligned to x:1824, vertically centered, 1 line | `--lp-font-display`, 40px, weight 700 | `--lp-fg`; the ASKED entry `--lp-accent` |
| Double rule | x:96 → 1824 at y:586: two 2px rules 6px apart (y:586 and y:594) | — | `--lp-fg` |
| Settlement line | x:96, y:668, max-width 1600px, 1–2 lines | `--lp-font-display`, 96px, weight 800, line-height 1.02, letter-spacing −0.02em | `--lp-fg` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (contact) | x:96, y:984 — email, spaced "—", date | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 rows, in this order:** what was SHOWN (the evidence,
  one line), what is ASKED (the request, one line — the only accent
  row), what the yes UNLOCKS (the consequence, one line). Row
  labels may be reworded to the deck's language but keep the
  evidence → request → consequence order.
- **Entries:** ≤ 42 characters, one line, concrete ("Rp 40B —
  phase-two budget line", never "your support").
- **The ASKED row must contain the real ask** with its real number
  if it has one. A Settlement without a stated ask is a Whisper
  wearing a suit — use Whisper.
- **Settlement line:** ≤ 40 characters, ≤ 2 lines, declarative
  ("One vote settles it." / "We start on your yes."). This is the
  spoken last sentence — write it to be said aloud.
- **Contact:** one line, real coordinates.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

None by default — accounts don't take photographs. The tolerated
substitution: for signed partnership closings, a 300×90 co-signature
strip (two wordmarks flanking an "×") may replace the footer-left
contact, at the same position and ≤ 40px logo height, placeholders
`https://placehold.co/260x80` each.

## Choreography

The account settles line by line, total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.15s` — rows enter top to bottom, 0.18s apart: label fades,
   entry rises `translateY(20px→0)` + fade (0.5s), the row's
   hairline wipes `scaleX(0→1)` origin left (0.5s).
3. `0.75s` — the double rule draws: both lines wipe origin left,
   0.5s, the lower trailing 0.08s — the books close.
4. `1.00s` — the settlement line rises `translateY(40px→0)` + fade,
   0.7s.
5. `1.30s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Double rule** → must stay a doubled line (it IS the grammar),
  but takes the system's rule weights and may tint the lower line
  toward the surface.
- **Row hairlines** → the system's divider vocabulary.
- **ASKED accent** → the system's one hot color on label and entry.
- **Settlement line** → the system's display face; an `<em>` word
  may take the accent.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Four-plus rows (terms, caveats, thank-yous) — appendices exist;
  the close is three lines and a total.
- An ask hedged into mush ("continued partnership"). The ledger
  form makes vagueness look like hidden fees.
- QR codes, "any questions?", or contact blocks beyond one line.
- Using the double rule anywhere else on the slide — one total per
  account.
- A settlement line in question form. Accounts don't ask.
- Branding larger than 40px tall or anywhere but the reserved corner.
