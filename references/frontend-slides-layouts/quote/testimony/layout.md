---
version: 1.0
name: Testimony
slot: quote
description: >
  Pull-quote content slide. A giant accent quote glyph hangs in the top
  margin, the quotation runs at display scale across two-thirds of the
  stage, and a ruled attribution block signs it. Optional 360×360
  portrait plate on the right.
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

# Testimony — quote layout

## Intent

A quote slide fails when it looks like a slide *about* a quote — boxed,
italicized, decorated. Testimony sets the words themselves at headline
scale so the room reads them as a claim, and lets one oversized glyph
do all the signaling. The attribution is ruled off like a signature on
a document: this person said this, on the record.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       08 / 14  │
│  ❝            ← giant accent glyph                             │
│                                                                │
│   We stopped noticing the                        ┌──────────┐  │
│   platform. That is the                          │ portrait │  │
│   highest compliment          ← quote            │ (option) │  │
│   we can give.                                   └──────────┘  │
│                                                                │
│  ── ────────────────────                                       │
│  D. Putri — VP OPERATIONS, HARBORWORKS   ← attribution         │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Quote glyph | x:88, top y:120, font-size 200px, line-height 0.7 | `--lp-font-display`, weight 700 | `--lp-accent` |
| Quote text | x:96, top y:330, max-width 1360px (1180px with portrait), 3–5 lines | `--lp-font-display`, 58–66px (default 64), weight 600, line-height 1.22, letter-spacing −0.01em | `--lp-fg`; one `<em>` phrase → `--lp-accent` (optional) |
| Attribution block | x:96, y:860 | — | — |
| · rule | 48×4px, 24px above name | — | `--lp-accent` |
| · name + role | name inline with role on one line, or two lines | name `--lp-font-display` 28px weight 700; role `--lp-font-mono` 14px uppercase ls 0.14em | name `--lp-fg`, role `--lp-fg-muted` |
| Portrait plate (optional) | x:1464 → 1824, y:330, 360×360 | 1px border | border `--lp-line` |

## Content constraints (hard limits)

- **Quote:** 3–5 lines at 64px — roughly 90–220 characters. Shorter is
  a statement slide, longer is a paragraph; trim the quote, never the
  type size below 58px. Use the speaker's real words; ellipses allowed,
  paraphrase not.
- **Attribution:** name ≤ 24 characters, role/org line ≤ 44. Required —
  an unattributed quote reads as decoration.
- **Quote glyph:** exactly one, opening only. No closing glyph.
- **One quote per slide.** Two quotes = two slides.

## Image variant

**With an image:** the 360×360 portrait plate on the right; quote
max-width tightens to 1180px. A mono caption line under the plate may
carry the speaker's org.

**Recommended size / placeholder:** `https://placehold.co/360x360`.
**Dimension fallback:** fixed 360×360 frame, `object-cover`,
token CSS fill behind the `<img>`. The portrait is optional; without
it the quote takes the full 1360px measure.

## Choreography

1. `0.00s` — kicker and counter fade, 0.5s.
2. `0.10s` — quote glyph drops in: `translateY(−30px→0)` + fade, 0.7s.
3. `0.30s` — quote lines fade up `translateY(28px→0)`, 0.6s, 0.1s
   stagger per line (wrap lines in spans for the stagger, or fade the
   block as one for quotes that reflow).
4. `0.85s` — attribution rule wipes; name and role fade up at `0.95s`.
5. `0.60s` — portrait plate (if any) fades in with a slow settle, 0.9s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Quote glyph** → the system's quotation mark treatment (serif ❝,
  guillemet, CJK 「) — always oversized, always `--lp-accent`.
- **Quote face** → serif systems must use their serif here at 500–600;
  this is the serif's slide.
- **Attribution rule** → the system's marker device.

## Failure modes to avoid

- Italicizing the whole quote — scale is the emphasis, not slant.
- Boxing the quote in a card or adding a background tint behind it.
- Centering. The left-set measure with the hanging glyph is the design.
- Stock-photo portraits of people who are not the speaker.
