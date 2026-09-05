---
version: 1.0
name: Docket
slot: agenda
description: >
  The session's program as a ruled schedule. A headline sets the span,
  then five hairline rows descend: mono start time in the left gutter,
  session title in display type, owner right-aligned in mono. At most
  one session — the live moment — carries the accent. A courtroom
  docket, not a bullet list.
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

# Docket — agenda layout

## Intent

Index Ledger reprints the deck's chapters; Docket schedules the
**room's time**. The difference is the time gutter: real clock times
that promise the audience when they get their coffee back. Announcing
the schedule and keeping it is the cheapest credibility a presenter
can buy. Use it as slide 2 of a working session or workshop; skip it
for a 10-minute pitch.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  The next ninety minutes                  ← headline           │
│                                                                │
│  09:00   Arrival & systems check              OPS TEAM         │
│  ─────────────────────────────────────────────────────────     │
│  09:15   The case for federation              S. WULANDARI     │
│  ─────────────────────────────────────────────────────────     │
│  09:45 ▮ Live control-room walkthrough        B. PRAKOSO       │ ← accent
│  ─────────────────────────────────────────────────────────     │
│  10:20   Procurement & data residency         M. CHEN          │
│  ─────────────────────────────────────────────────────────     │
│  10:45   Open floor                           ALL HANDS        │
│  ─────────────────────────────────────────────────────────     │
│  VENUE / DATE                                      02 / 14     │
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
| Headline | x:96, y:164, max-width 1400px, 1 line | `--lp-font-display`, 64px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Rows (×5) | tops at y:300, 424, 548, 672, 796 (124px pitch), each closed by a full-width hairline at its bottom | — | — |
| Times | x:96, vertically centered in row | `--lp-font-mono`, 24px, letter-spacing 0.06em | `--lp-fg-muted`; accent session `--lp-accent` |
| Accent tick | 10×10px square, 20px left of the accent session's title | — | `--lp-accent` |
| Session titles | x:340, vertically centered, max-width 1000px, 1 line | `--lp-font-display`, 36px, weight 700 | `--lp-fg` |
| Owners | right-aligned to x:1824, vertically centered | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (venue/date) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **4–5 sessions.** Three is a Rule Columns list; six means the
  agenda needs consolidating before it needs a slide.
- **Times:** real clock times, 5 characters ("09:00"), consistent
  format, ascending. Durations ("15 min") are the tolerated
  alternative — never mix the two.
- **Titles:** ≤ 38 characters, one line. Spoken names for the
  sessions, not document headings.
- **Owners:** ≤ 18 characters, uppercase mono. A name, a team, or
  "ALL HANDS". Every row gets one; an unowned session is a warning
  sign the audience will read.
- **Accent session:** at most one — the live demo, the decision
  point, the reason everyone came. Marked by accent time + tick only.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

Docket takes no imagery — a schedule illustrated is a schedule
doubted. The sanctioned addition for venue-specific sessions is a
single mono location note appended to the owner ("B. PRAKOSO — LAB 2").
If the workshop deserves a venue photograph, give it the Cover
Caption opening instead.

## Choreography

Staggered entrance on slide activation, total ≤ 1.7s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline rises `translateY(32px→0)` + fade, 0.6s.
3. `0.30s` — rows enter top to bottom, 0.15s apart: each row's
   hairline wipes `scaleX(0→1)` origin left (0.5s) while its time
   fades in; title and owner fade up `translateY(16px→0)` 0.1s later.
4. `1.20s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Times** → may sit in outlined chips (≤ 120×40px) if the system
  frames labels; the gutter alignment stands.
- **Row hairlines** → the system's divider vocabulary.
- **Accent tick** → the system's marker (arrow, stamp, underline),
  footprint ≤ 20×20px.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; systems with a paper voice may
  add a faint top-edge "clipboard" band ≤ `--lp-fg-faint`.

## Failure modes to avoid

- Vague times ("morning", "later"). Clock times or durations — the
  promise is the point.
- Descriptions under titles. One line per session; the speaker
  narrates the rest.
- Two accent sessions, or accenting the last row by default —
  highlight the genuine peak or nothing.
- Reordering rows out of clock order for emphasis.
- Branding larger than 40px tall or anywhere but the reserved corner.
