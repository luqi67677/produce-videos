---
version: 1.0
name: Watchlist
slot: risk
description: >
  Risk register excerpt. Exactly three risks as ruled rows — mono
  index, risk title at display scale, a one-line named mitigation
  beneath, and two outlined mono chips (likelihood, impact) at the
  right margin. Severity is carried by words and type, never by
  traffic-light colors; the one accent row is the risk the deck
  wants a decision on.
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

# Watchlist — risk layout

## Intent

Risk slides fail in two directions: the 5×5 heat map nobody can
read from the third row, and the single hedged sentence that
pretends risk away. Watchlist does what a good board pack does —
**names three risks in plain type, says who is doing what about
each, and grades them in words**. Refusing red/amber/green is the
design's spine: color-coded risk lets the eye skip the reading,
and skipped reading is how risks mature. Use it when the deck owes
the room honesty; the full register stays in the appendix.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · REGISTER EXCERPT               [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  Three risks we are watching              ← headline           │
│                                                                │
│  R1  Fiber cuts on the northern ring   [LIKELIHOOD HIGH]       │
│      Mitigation — dual-path by Q4;     [IMPACT MAJOR]          │
│      owner: N. INFRA                                           │
│  ─────────────────────────────────────────────────────────     │
│  R2  Operator attrition, night shift   [LIKELIHOOD MEDIUM]     │
│      Mitigation — cert bonus + rotation; owner: OPS            │
│  ─────────────────────────────────────────────────────────     │
│  R3  Procurement rule change, 2027     [LIKELIHOOD LOW]        │
│      ← accent: decision requested       [IMPACT SEVERE]        │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / FULL REGISTER                            11 / 12     │
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
| Headline | x:96, y:164, max-width 1400px, 1 line | `--lp-font-display`, 60px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Risk rows (×3) | tops at y:288, 506, 724; each ~200px tall, closed by a hairline 18px above the next row's top | — | rules `--lp-line` |
| Indexes (R1–R3) | x:96, aligned with the title's cap height | `--lp-font-mono`, 22px | `--lp-fg-muted`; accent row `--lp-accent` |
| Risk titles | x:180, max-width 1150px, 1 line | `--lp-font-display`, 36px, weight 700 | `--lp-fg` |
| Mitigations | x:180, 16px under the title, max-width 1150px, ≤ 2 lines; pattern "Mitigation — <action>; owner: <NAME>" | `--lp-font-body`, 23px, line-height 1.45 | `--lp-fg-muted`; the owner may be `--lp-fg` |
| Chips (×2 per row) | right-aligned to x:1824, stacked, 12px apart, outlined 1px, padding 8×16px | `--lp-font-mono`, 14px, uppercase, letter-spacing 0.12em | border `--lp-line`, text `--lp-fg-muted`; accent row's chips border+text `--lp-accent` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (register ref) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 risks** — the three that belong in THIS meeting. A
  fourth risk means one of these isn't top-three; the footer names
  where the full register lives.
- **Titles:** ≤ 44 characters, concrete ("Fiber cuts on the
  northern ring", never "execution risk").
- **Mitigations:** ≤ 120 characters, ≤ 2 lines, containing an
  ACTION with a DATE and a NAMED OWNER. "We are monitoring" is not
  a mitigation; write the honest chip pair and leave the line as
  "Mitigation — none yet; owner: OPEN" if that's the truth (that
  row probably earns the accent).
- **Chips:** fixed vocabularies — LIKELIHOOD LOW/MEDIUM/HIGH,
  IMPACT MODERATE/MAJOR/SEVERE. Two chips per row, always both.
- **One accent row:** the risk needing the room's decision or
  attention today — not automatically the scariest.
- **No color coding of severity.** Ever. The words grade; the
  accent directs.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

None — risk is read, not illustrated.

## Choreography

The register is read into the record, total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline rises `translateY(32px→0)` + fade, 0.6s.
3. `0.30s` — rows enter top to bottom, 0.20s apart: index + title
   rise `translateY(24px→0)` + fade (0.6s), mitigation fades 0.12s
   later, chips pop `scale(0.9→1)` 0.2s after that, the row's
   hairline wipes.
4. `1.30s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Chips** → the system's tag vocabulary (filled at ≤ 15% ink,
  underlined tags); both chips of a row always match in treatment.
- **Row hairlines** → the system's divider vocabulary.
- **Indexes** → the system's numbering vocabulary.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg` only. Risk over atmosphere reads
  as theater.

## Failure modes to avoid

- Red/amber/green anywhere — including "just the SEVERE chip."
- Probability percentages ("35% likely") — false precision the
  register can't defend; the coarse words are the honest ones.
- Mitigations without owners or dates.
- A risk written to be dismissed ("competitor does everything
  right") — the room reads the padding.
- Five risks in shrunken rows.
- Branding larger than 40px tall or anywhere but the reserved corner.
