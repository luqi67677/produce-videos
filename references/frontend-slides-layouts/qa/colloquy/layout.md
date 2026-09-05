---
version: 1.0
name: Colloquy
slot: qa
description: >
  Three question–answer pairs staged as a spatial dialogue. A vertical
  hairline axis splits the stage; questions hang right-aligned on the
  left side in display type, answers sit left-aligned on the right in
  quiet body type, each pair stepping further down — a magazine
  interview, not an FAQ table.
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

# Colloquy — Q&A layout

## Intent

Objection slides usually bury real questions in a bulleted FAQ box.
Colloquy stages them as **a conversation across an axis**: the room
asks from the left, the deck answers from the right, and the eye
zig-zags down the exchange. The questions are set LARGER than the
answers — respect for the asker is the persuasive move. Use it for
the three questions every audience actually raises (procurement,
security, "what if it fails"), answered in one honest breath each.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│                               │                                │
│     Where does the       Q1   │   A1  On your servers, in      │
│     footage live?  ──────────▶│◀────  your country. …          │
│                               │                                │
│        What happens      Q2   │   A2  Edge nodes buffer        │
│           offline?  ─────────▶│◀────  locally for 72 hours…    │
│                               │                                │
│      Can we audit        Q3   │   A3  Every model ships        │
│        the models?  ─────────▶│◀────  with a signed eval…      │
│                               │                                │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / FORUM                                    12 / 14     │
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
| Axis | vertical 1px line at x:960, y:200 → 920 | — | `--lp-line` |
| Question tags (Q1–Q3) | right-aligned to x:920, at each pair's top | `--lp-font-mono`, 17px, uppercase, letter-spacing 0.14em | `--lp-accent` |
| Questions | right-aligned to x:920, 8px under their tag, max-width 700px, ≤ 2 lines | `--lp-font-display`, 40px, weight 700, line-height 1.15 | `--lp-fg` |
| Answer tags (A1–A3) | x:1000, aligned with the question tag's line | `--lp-font-mono`, 17px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` |
| Answers | x:1000, 8px under their tag, max-width 730px, ≤ 3 lines | `--lp-font-body`, 25px, line-height 1.5 | `--lp-fg-muted` |
| Pair tops | y:228, 462, 696 (234px pitch) | — | — |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (forum/source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 3 pairs.** Two reads as thin; four crushes the pitch.
  If the deck faces five real objections, pick the three hardest —
  dodging the hard ones is legible from the audience.
- **Questions:** ≤ 44 characters, ≤ 2 lines, phrased as the audience
  would say them (first person allowed, jargon not). They must be
  REAL questions — softballs written to be swatted read as theater.
- **Answers:** ≤ 170 characters, ≤ 3 lines, declarative, no hedging
  openers ("Great question!"). The answer commits; the speaker
  elaborates.
- **Tags:** Q1/Q2/Q3 accent, A1/A2/A3 muted — the only chrome the
  exchange gets.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

Colloquy is type-only by design — dialogue needs no illustration.
The sanctioned substitution: if the questions came from a named
public forum, a single 200×200 portrait of the interlocutor may sit
top-left under the kicker (x:96, y:200 → 400), pushing pair tops to
y:260/494/728 and question max-width to 560px.

**Recommended size / placeholder:** `https://placehold.co/400x400`
(rendered 200×200). **Dimension fallback:** fixed square frame,
`object-fit: cover`, token CSS fill behind the `<img>`. Optional —
the axis-only form is the default.

## Choreography

The exchange plays out in turns, total ≤ 1.8s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.15s` — axis grows `scaleY(0→1)` from the top
   (`transform-origin: top`), 0.8s.
3. `0.40s` — pairs enter in conversation order, 0.34s apart per pair:
   the question drifts in from the left (`translateX(-32px→0)` +
   fade, 0.6s), its answer follows 0.17s later from the right
   (`translateX(32px→0)` + fade, 0.6s).
4. `1.30s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Axis** → the system's line vocabulary (dashed, doubled, 2px);
  never a filled band — the gap is the conversation.
- **Tags** → the system's label vocabulary (chips, brackets,
  underlines) at the same anchors, ≤ 90×32px.
- **Question emphasis** → serif systems may set questions in display
  italic; the size lead over answers stands.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; the two halves may take a
  half-step tint difference (≤ `--lp-fg-faint`) in dual-surface
  systems.

## Failure modes to avoid

- Answers set larger or bolder than questions — the hierarchy
  inversion is the layout's ethic; break it and it's an FAQ again.
- Elements crossing the axis. Nothing touches x:960 except the axis.
- Question text left-aligned (the ragged edge must face the axis,
  both sides mirroring toward the middle).
- More than one exchange per pair (no follow-ups, no "see slide 9").
- Branding larger than 40px tall or anywhere but the reserved corner.
