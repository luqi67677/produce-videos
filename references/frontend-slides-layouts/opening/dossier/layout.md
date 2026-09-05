---
version: 1.0
name: Dossier
slot: opening
description: >
  Case-file opening. A four-cell ruled metadata grid (prepared for /
  program / date / status) sits under the chrome like a form header;
  an outlined classification chip states what the meeting is for; the
  title lands beneath at display scale like the subject line of a
  filed document. For decision meetings and briefings where the deck
  is a record, not a show.
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

# Dossier — opening layout

## Intent

Some decks should feel like documents with consequences — board
papers, procurement briefs, incident reviews. Dossier opens them
with **form grammar**: who this is for, what program it belongs to,
when it was filed, and what state it's in, all answered before the
title speaks. The outlined chip ("FOR DECISION — 30 MIN") sets the
meeting's contract in the first five seconds. Use it when the
audience signs things; use Offset Marquee when they applaud things.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · FILE REFERENCE                 [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│  PREPARED FOR   │ PROGRAM        │ FILED       │ STATUS        │
│  Metro Council  │ Vision Grid    │ 09 Jul 26   │ Final         │
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│  ┌ FOR DECISION — 30 MIN ┐   ← outlined chip (accent)          │
│                                                                │
│  Metro vision,                                                 │
│  under one command            ← title, ≤ 2 lines               │
│                                                                │
│  One consolidated request: the operating structure,            │
│  the budget line, and the accountability. ← lead               │
│  ─────────────────────────────────────────────────────────     │
│  PRESENTER — ROLE                                  01 / 12     │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

All values are stage pixels at 1920×1080. Content box: **96px** left/right
margins, **72px** top/bottom margins.

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72, single line — a real file reference | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.18em | `--lp-accent` |
| Branding slot (top-right, optional) | right-aligned to x:1824, y:66, ≤ 40px tall, ≤ 260px wide | wordmark in `--lp-font-display` 700 or an image logo | `--lp-fg` |
| Chrome hairline | x:96 → 1824, y:118, 1px | — | `--lp-line` |
| Metadata grid | y:170 → 290, bounded by hairlines at both edges; 4 cells at x:96, 528, 960, 1392 (432px each) with vertical hairlines between | — | rules `--lp-line` |
| Cell labels | cell top + 26px | `--lp-font-mono`, 14px, uppercase, letter-spacing 0.14em | `--lp-fg-muted` |
| Cell values | 14px under the label | `--lp-font-display`, 27px, weight 700, 1 line | `--lp-fg` |
| Classification chip | x:96, y:356, outlined 2px, padding 12×22px, single line | `--lp-font-mono`, 16px, uppercase, letter-spacing 0.16em | border + text `--lp-accent` |
| Title | x:96, y:446, max-width 1600px, ≤ 2 lines | `--lp-font-display`, 116px, weight 800, line-height 1.0, letter-spacing −0.02em | `--lp-fg` |
| Lead | x:96, 44px under the title, max-width 980px, ≤ 2 lines | `--lp-font-body`, 26px, line-height 1.5 | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (presenter) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 4 metadata cells** with real answers: PREPARED FOR,
  PROGRAM (or CASE/FILE), FILED (a real date), STATUS (Draft /
  Final / Rev n). Cells left blank or filled with "—" undermine the
  whole conceit — if a field can't be answered, this isn't a
  dossier deck.
- **Cell values:** ≤ 20 characters, one line.
- **Chip:** ≤ 28 characters, states the meeting's contract ("FOR
  DECISION — 30 MIN", "FOR REVIEW", "READ-AHEAD"). Exactly one chip.
- **Title:** ≤ 2 lines, ≤ 16 characters per line at 116px (wrap each
  line in a span). Subject-line voice — declarative, no punctuation
  theatrics.
- **Lead:** ≤ 150 characters, ≤ 2 lines. Optional; the layout holds
  without it.
- **Kicker is a file reference** ("DOSSIER 26-041 — METRO COMMAND"),
  not a slogan.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

**With an exhibit:** a 460×420 photograph (the site, the system, the
evidence) may sit right at x:1364 → 1824, y:356 → 776, framed by a
1px `--lp-line` border with a mono caption chip at its lower-left;
the title max-width tightens to 1180px and drops to 104px.

**Recommended size / placeholder:** `https://placehold.co/460x420`.
**Dimension fallback:** fixed frame, `object-fit: cover`, token CSS
fill behind the `<img>`. Optional — the type-only form is the
default and the more official one.

## Choreography

Filed, stamped, then titled — total ≤ 1.6s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.15s` — metadata grid rules wipe in (`scaleX`/`scaleY` origin
   left/top), 0.5s; labels fade at 0.35s, values fade up
   `translateY(14px→0)` at 0.5s, 0.08s cell stagger.
3. `0.70s` — the chip pops `scale(0.85→1)` + fade, 0.4s — the stamp
   lands.
4. `0.85s` — title lines rise `translateY(44px→0)` + fade, 0.7s,
   0.12s stagger.
5. `1.15s` — lead fades up, 0.5s.
6. `1.30s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Chip** → the system's stamp/tag vocabulary (filled tab, rounded
  chip, literal rubber-stamp rotation ≤ 2°), accent ink, footprint
  ≤ 420×52px.
- **Metadata grid** → the system's form/table vocabulary (dotted
  rules, boxed cells); coordinates stand.
- **Cell values** → the system's emphasis face; STATUS may take the
  accent when it is the story ("Final", "Rev 3").
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; paper-grain texture is the
  natural upgrade for file grammar.

## Failure modes to avoid

- Fictional metadata theater (a "CASE NO" invented to look serious).
  Real reference or no dossier.
- Two chips, or a chip used as decoration ("AWESOME!"). The chip is
  a contract with the room.
- Centering anything. Files are left-anchored artifacts.
- A five-cell grid or double-row grid — four questions, answered.
- Title in interrogative or teaser voice ("What if cities could
  see?") — files state subjects.
- Branding larger than 40px tall or anywhere but the reserved corner.
