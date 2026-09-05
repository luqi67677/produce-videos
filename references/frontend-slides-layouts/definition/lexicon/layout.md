---
version: 1.0
name: Lexicon
slot: definition
description: >
  Dictionary-entry grammar for the one term the deck hinges on. The
  headword sits at display scale with pronunciation and part of speech
  in mono beside it; below a hairline, two numbered senses — the
  general meaning muted, the deck's own meaning at full contrast with
  an accent numeral — then one italic usage line. Type-only.
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

# Lexicon — definition layout

## Intent

Every strong deck has one load-bearing word the audience must hold
correctly — "federation," "edge," "digital twin." Lexicon stops the
deck and **defines it like a dictionary would**, then quietly commits
a heresy: sense 2, the deck's own usage, outranks the general meaning.
The audience gets the joke and keeps the definition. Use it once per
deck at most, before the term starts doing heavy lifting.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│  federation        /ˌfɛd·əˈreɪ·ʃən/ · noun                     │
│                                                                │
│  ─────────────────────────────────────────────────────────     │
│                                                                │
│  1   A union of partly self-governing entities under a         │
│      central authority.                        ← muted         │
│                                                                │
│  2   A network of city vision systems that share alerts        │
│      without sharing raw footage.      ← full contrast         │
│                                                                │
│  — as in: "Jakarta joins the federation without moving         │
│    a single frame."                                            │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / GLOSSARY                                 04 / 12     │
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
| Headword | x:96, baseline ≈ y:372, single line | `--lp-font-display`, 132px, weight 800, lowercase, letter-spacing −0.02em | `--lp-fg` |
| Pronunciation + POS | inline after the headword, 48px gap, aligned to its baseline | `--lp-font-mono`, 26px; POS italic after a spaced "·" | `--lp-fg-muted` |
| Entry hairline | x:96 → 1824, y:452, 1px | — | `--lp-line` |
| Sense numerals | x:96, at each sense's first line | `--lp-font-mono`, 30px | sense 1 `--lp-fg-muted`; sense 2 `--lp-accent` |
| Sense bodies | x:180, max-width 1380px, ≤ 2 lines each; sense 1 at y:520, sense 2 at y:660 | `--lp-font-body`, 34px, line-height 1.4 | sense 1 `--lp-fg-muted`; sense 2 `--lp-fg` |
| Usage line | x:180, y:824, max-width 1380px, ≤ 2 lines | `--lp-font-body`, 26px, italic, line-height 1.5; opens with an em dash | `--lp-fg-muted`; the headword inside the quote may be `--lp-accent` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left (source) | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Headword:** one word, ≤ 14 characters, set lowercase (dictionary
  convention) even if it is normally capitalized. Two-word terms
  (≤ 18 chars with space) are the tolerated maximum.
- **Pronunciation:** real IPA-ish notation ≤ 24 characters. If nobody
  can produce honest IPA, drop it and keep only the POS — never
  invent decorative slashes.
- **Exactly 2 senses.** Sense 1 = the world's meaning (muted). Sense 2
  = the deck's meaning (full contrast, accent numeral). Each ≤ 130
  characters, ≤ 2 lines. One sense is a caption, three is a glossary.
- **Usage line:** ≤ 120 characters, italic, opens with "— as in:".
  Optional — the layout holds without it.
- **The headword must recur in the deck.** Defining a word the deck
  never uses again is theater.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image variant

Lexicon is type-only by design — a picture beside a definition turns
the slide into a flashcard. The sole sanctioned addition is the
design system's texture fingerprint behind the headword band at
≤ `--lp-fg-faint` contrast. If the term truly needs a visual, give
it its own Plate Caption slide immediately after.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headword rises `translateY(40px→0)` + fade, 0.7s.
3. `0.35s` — pronunciation + POS fade in, 0.5s.
4. `0.45s` — entry hairline wipes `scaleX(0→1)` origin left, 0.6s.
5. `0.60s` — sense 1 fades up `translateY(24px→0)`, 0.6s.
6. `0.78s` — sense 2 fades up, 0.6s (the beat lands here).
7. `1.00s` — usage line fades in, 0.5s.
8. `1.10s` — footer fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Sense numerals** → the system's numbering vocabulary (roman
  numerals, boxed digits) ≤ 40px; sense 2 keeps the accent.
- **Entry hairline** → the system's divider vocabulary; a doubled
  rule suits archival systems.
- **Headword** → serif systems may set it in their display italic;
  lowercase stands.
- **Usage line** → may become the system's blockquote treatment at
  the same position and scale.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg`; a paper tint is the natural
  atmosphere for dictionary grammar.

## Failure modes to avoid

- Three or more senses, sub-senses, or etymology blocks — this is a
  slide, not the OED. Two senses, one usage, done.
- Setting sense 1 at full contrast: the muting IS the argument (the
  world's meaning steps back; ours steps forward).
- A headword phrase longer than two words. If the term needs a
  clause, the deck needs a better term.
- Title-casing or uppercasing the headword.
- Branding larger than 40px tall or anywhere but the reserved corner.
