---
version: 1.0
name: Postscript
slot: closing
description: >
  The deck signs off like a letter. A closing statement and short coda
  read as the final paragraph, followed by an accent rule and a
  signature block (name, role). A P.S. line near the bottom carries the
  one call-to-action people actually remember. Optional portrait or
  signature image beside the sign-off.
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

# Postscript — closing layout

## Intent

Personal where the others are typographic. The letter grammar —
paragraph, signature, P.S. — makes the ending feel authored by a person
rather than produced by a template, and the P.S. exploits the oldest
trick in direct mail: the postscript is the most-read line on the page.
Put the single most important ask there.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  IN CLOSING                                           12 / 12  │
│                                                                │
│  THAT'S THE                                                    │
│  WHOLE STORY.        ← statement                               │
│                                                                │
│  Two lines of coda in body type, the way a letter              │
│  winds down before the signature.                              │
│                                                                │
│  ▮▮▮▮                                                          │
│  A. Rahman           ← signature block      [portrait]         │
│  HEAD OF PLATFORM —  HALCYON                                   │
│                                                                │
│  P.S. One ask: read the roadmap before Friday's review.        │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Statement | x:96, top y:170, max-width 1300px, 1–2 lines | `--lp-font-display`, 116–128px (default 124), weight 700–800, line-height 0.97, letter-spacing −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Coda | x:96, 44px below statement, max-width 900px | `--lp-font-body`, 26px, line-height 1.6 | `--lp-fg-muted` |
| Signature block | x:96, top y:640 | — | — |
| · accent rule | 48×5px, 28px above name | — | `--lp-accent` |
| · name | | `--lp-font-display`, 42px, weight 700 | `--lp-fg` |
| · role line | 10px below name | `--lp-font-mono`, 15px, uppercase, ls 0.14em | `--lp-fg-muted` |
| P.S. line | x:96, y:930, max-width 1400px, single line | "P.S." in `--lp-font-mono` 17px uppercase; rest `--lp-font-body` 24px | "P.S." `--lp-accent`, rest `--lp-fg` |

## Content constraints (hard limits)

- **Statement:** 1–2 lines, ≤ 14 characters uppercase per line at 124px.
  First-person, conclusive ("That's the whole story.", "Now we build.").
- **Coda:** 1–3 lines, ≤ 200 characters. Written like prose, not
  bullet-speak.
- **Signature:** one name + one role line. This is the presenter, not
  a team.
- **P.S.:** exactly one sentence, ≤ 90 characters, containing exactly
  one ask. Two asks in a P.S. is zero asks.

## Image variant

**With an image:** a 300×300 portrait (or a 380×110 scanned-signature
image) sits right of the signature block, its left edge at x:820,
top-aligned with the accent rule; portraits take a 1px `--lp-line`
border, signatures none. **Without an image:** the type-only sign-off
above.

**Recommended size / placeholder:** `https://placehold.co/300x300`
(portrait) or `https://placehold.co/380x110` (signature scan).
**Dimension fallback:** fixed frames with `object-cover`
(portrait) / `object-contain` (signature scan — never crop a signature),
token CSS fill behind the portrait only. Both are optional.

## Choreography

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.10s` — statement lines rise `translateY(48px→0)` + fade, 0.7s,
   0.12s stagger.
3. `0.50s` — coda fades up, 0.6s.
4. `0.70s` — accent rule wipes `scaleX(0→1)`, 0.5s; signature block
   (and portrait, if any) fades up at `0.85s`, 0.6s.
5. `1.10s` — P.S. line fades up, 0.6s — always last; it is the button.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Accent rule** → the system's marker device.
- **Name** → a system with a script/italic voice may set the name in
  it — the one place a flourish is warranted.
- **P.S. label** → the system's label treatment, always visually
  distinct from the sentence that follows.

## Failure modes to avoid

- A P.S. that is a paragraph, or a second P.P.S. line.
- Centering anything — letters are left-set.
- Signature without a person (org name in the name slot); use another
  closing preset if no one signs it.
- Contact grids — this preset's exit is the P.S., not a directory.
