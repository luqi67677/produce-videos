---
version: 1.0
name: Callback
slot: closing
description: >
  Bookend close. The claim the deck opened with returns — set muted
  and struck through under a "WHERE WE STARTED" tag — and the new
  state lands beneath it at full contrast under "WHERE WE LAND". The
  distance between the two lines IS the presentation. One contact
  line closes the page.
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

# Callback — closing layout

## Intent

The strongest proof a deck moved anyone is that its opening sentence
reads differently at the end. Callback stages that literally: **the
first slide's claim comes back and the deck crosses it out**. The
strike-through is theatrical honesty — it says "this was true fifty
minutes ago" — and the landing line beneath inherits all the
evidence between. Use it when the deck genuinely changed a premise
(a plan approved, a doubt retired); if nothing changed, there is
nothing to cross out and this layout will say so out loud.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CLOSE                          [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│  WHERE WE STARTED                                              │
│  T̶w̶e̶l̶v̶e̶ ̶p̶i̶l̶o̶t̶s̶,̶ ̶t̶w̶e̶l̶v̶e̶ ̶s̶i̶l̶o̶s̶.̶   ← the opening claim, muted   │
│                                                                │
│  WHERE WE LAND                    ← accent tag                 │
│  One grid, governed              ← the landing, full contrast  │
│  together.                                                     │
│                                                                │
│  ─────────────────────────────────────────────────────────     │
│  CONTACT — DATE                                    14 / 14     │
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
| Tag 1 ("WHERE WE STARTED") | x:96, y:250 | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.16em | `--lp-fg-muted` |
| Opening claim | x:96, y:296, max-width 1600px, ≤ 2 lines, struck through (2px line-through) | `--lp-font-display`, 76px, weight 700, line-height 1.05 | `--lp-fg-muted` |
| Tag 2 ("WHERE WE LAND") | x:96, y:520 | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.16em | `--lp-accent` |
| Landing line | x:96, y:566, max-width 1650px, ≤ 2 lines | `--lp-font-display`, 108px, weight 800, line-height 1.02, letter-spacing −0.02em | `--lp-fg`; one `<em>` word may take `--lp-accent` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (contact) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **The opening claim must be a real quotation of this deck's
  opening slide** (title or thesis), ≤ 60 characters, ≤ 2 lines.
  Paraphrasing to make the kill easier is cheating the room.
- **Strike-through only for a state that ENDED.** If the premise
  evolved rather than died, drop the strike and keep the muting —
  the tags still carry the arc.
- **Landing line:** ≤ 50 characters, ≤ 2 lines, and it must be
  defensible by the deck's own evidence. It is 40% larger than the
  claim it replaces — the hierarchy is the verdict.
- **Tags:** ≤ 20 characters each, reworded freely ("JANUARY" /
  "TODAY"), keeping the then→now order.
- **Contact:** one line.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

None — the two lines are the picture. Systems may breathe their
texture behind the struck line only, ≤ `--lp-fg-faint`.

## Choreography

The past is re-read, then retired — total ≤ 1.8s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.15s` — tag 1 fades; the opening claim rises `translateY(28px→0)`
   + fade WITHOUT its strike, 0.7s — the room re-reads it as written.
3. `0.75s` — the strike draws across the claim (`scaleX(0→1)`,
   origin left, 0.45s) — the kill, earned mid-slide.
4. `1.00s` — tag 2 fades; the landing line rises `translateY(44px→0)`
   + fade, 0.8s.
5. `1.45s` — footer fades in, 0.5s.

Under `prefers-reduced-motion`, everything appears settled (strike
included) without transforms. Note for implementers: the animated
strike is an absolutely-positioned 2px rule over the text, per line,
so it can wipe; static renders may use CSS `line-through`.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`.

## Skin points (where the design system may substitute)

- **Strike** → the system's redaction vocabulary (single rule,
  double rule, highlighter band at ≤ 40% opacity) — never a scribble.
- **Tags** → the system's label vocabulary; then→now order stands.
- **Landing emphasis** → the system's emphasis move on one word,
  accent ink.
- **Branding slot** → the system's lockup rules; monochrome preferred.

## Failure modes to avoid

- Striking a claim the deck never actually opened with — anyone can
  scroll back.
- A landing line bigger in promise than the evidence shown (the
  layout amplifies overreach as loudly as achievement).
- Three states ("started / midway / land") — the form is a couplet.
- Playing the strike as a joke (comic sans energy in any system).
  It's a retirement, not a roast.
- Both lines at full contrast — the muting of the past is what
  lets the present land.
- Branding larger than 40px tall or anywhere but the reserved corner.
