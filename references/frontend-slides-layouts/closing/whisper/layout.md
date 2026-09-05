---
version: 1.0
name: Whisper
slot: closing
description: >
  The anti-scale closing. After a deck of display type, one small
  centered line — statement at 44px, a single accent mark above it, a
  quiet contact line at the very bottom, and nothing else. The volume
  drop is the drama.
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

# Whisper — closing layout

## Intent

Every other closing raises its voice; Whisper lowers it. Coming after
40 minutes of 150px headlines, a 44px line alone on an empty stage
lands like the pause before applause — the audience leans in to read
it, which is the whole trick. Highest-risk, highest-poise preset:
it only works when the room's attention is already yours.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│                                                       12 / 12  │
│                                                                │
│                                                                │
│                            ▪            ← accent mark          │
│                  Thank you for the hour.  ← 44px statement     │
│                                                                │
│                                                                │
│                                                                │
│                 CONTACT · @auric                         │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Counter (top-right) | right-aligned x:1824, y:72 — the only chrome | `--lp-font-mono`, 13px, uppercase, ls 0.12em | `--lp-fg-muted` at 70% |
| Accent mark | centered, y:472; 10×10px square (or the system's smallest glyph) | — | `--lp-accent` |
| Statement | centered, y:520, full content width, text-align center, 1 line | `--lp-font-display`, 40–48px (default 44), weight 500–600, line-height 1.3, letter-spacing 0 | `--lp-fg` |
| Contact line | centered, y:960, single line | `--lp-font-mono`, 14px, ls 0.08em | `--lp-fg-muted`, separators `--lp-accent` |

## Content constraints (hard limits)

- **Statement:** exactly 1 line, ≤ 60 characters, sentence case with a
  period. No uppercase, no `<em>`, no exclamation mark — raising any
  volume breaks the whisper.
- **Contact line:** 1–2 items. Optional; omit for maximum silence.
- **Nothing else.** No kicker, no headline, no logo. The counter is
  the only witness that this belongs to the deck.

## Image variant

**With an image:** a single 96×96 circular portrait (the presenter)
replaces the accent mark, centered at the same coordinates —
`rounded-full`, 1px `--lp-line` ring, `object-cover`.

**Recommended size / placeholder:** `https://placehold.co/192x192`
(2× for sharpness at 96px). **Dimension fallback:** fixed 96×96
circular frame, `object-cover`, token CSS fill behind the
`<img>`. The portrait is optional — the accent mark is the default.

**Without an image:** the accent mark as specified.

## Choreography

1. `0.00s` — nothing for 0.4s. The pause is part of the design; the
   slide arrives empty.
2. `0.40s` — accent mark (or portrait) fades in, 0.6s.
3. `0.60s` — statement fades in — opacity only, no rise; movement is
   volume — 0.9s.
4. `1.30s` — contact line and counter fade in at 70%, 0.6s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything simply appears (the initial pause is dropped).

## Skin points

- **Accent mark** → the system's smallest signature glyph (dot, dash,
  its bullet marker) ≤ 16px.
- **Statement face** → the system's body or display face at text
  weight; a serif system should use its serif here — this is the one
  preset where bookish beats bold.
- **Background** → flat `--lp-bg` only. Any texture competes with the
  silence.

## Failure modes to avoid

- Scaling the statement up "so it reads better." 48px is the ceiling;
  if it doesn't read, the line is too long.
- Adding a second line, a headline, or any display-scale element —
  that is Center Seal, not Whisper.
- Using it in decks that never went loud. The whisper needs contrast
  with what came before.
