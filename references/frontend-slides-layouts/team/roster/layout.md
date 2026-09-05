---
version: 1.0
name: Roster
slot: team
description: >
  Four equal portrait columns under an editorial header. Each column
  opens with a hairline, carries a fixed-frame portrait, then name and
  role. No cards, no shadows, no featured member — the grid's equality
  IS the statement. Portraits are optional as a set; without them the
  columns become a typographic roster.
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

# Roster — team layout

## Intent

A team slide fails two ways: the org-chart (hierarchy nobody asked for)
and the collage (chaos). Roster refuses both with **one ruled row of
equals** — same frame, same type, same pitch, reading like a masthead's
staff list. Use it for the 3–4 people who actually carry the story being
told; it is not a company directory.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · CONTEXT                        [BRAND / WORDMARK] ←──┼─ optional
│  Built by operators                       ← headline           │
│                                                                │
│  ───────────    ───────────    ───────────    ───────────      │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │portrait │    │portrait │    │portrait │    │portrait │      │
│  │ 384×460 │    │ 384×460 │    │ 384×460 │    │ 384×460 │      │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
│  Name           Name           Name           Name             │
│  ROLE — ORG     ROLE — ORG     ROLE — ORG     ROLE — ORG       │
│  ─────────────────────────────────────────────────────────     │
│  SOURCE / NOTE                                     10 / 12     │
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
| Headline | x:96, y:164, max-width 1400px, 1 line | `--lp-font-display`, 68px, weight 700, letter-spacing −0.01em | `--lp-fg` |
| Columns (×4) | x:96, 544, 992, 1440; each 384px wide, 64px gutters | — | — |
| Column hairlines | full column width at y:308, 1px | — | `--lp-line` |
| Portraits | y:332 → 792, 384×460, fixed frame | image `object-fit: cover` over a token CSS fill | fill: `--lp-fg-faint` |
| Names | 28px under the portrait (y:820), 1 line | `--lp-font-display`, 32px, weight 700 | `--lp-fg` |
| Roles | 10px under the name, 1 line | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer hairline | x:96 → 1824, y:962, 1px | — | `--lp-line` |
| Footer left | x:96, y:984 | `--lp-font-mono`, 15px, uppercase, letter-spacing 0.12em | `--lp-fg-muted` |
| Footer right (counter) | right-aligned to x:1824, y:984 | same as footer left | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 4 members** (the deck's core cast). With 3, widen columns
  to 512px at x:96, 704, 1312 (96px gutters). Two people is a
  Ledger-Versus-shaped story; five or more is a directory — cut.
- **Names:** ≤ 20 characters, one line. Real names only.
- **Roles:** ≤ 30 characters, one line, uppercase mono. Pattern
  "ROLE — CREDENTIAL/ORG" (e.g. "CTO — EX-TELCO INFRA").
- **No bios.** If a person needs a paragraph, they need their own
  slide (Testimony with portrait).
- **No featured member:** identical frames and type for all. The
  speaking order is left → right; put the presenter first, not
  biggest.

## Branding / logo slot (optional)

The top-right corner (right-aligned to x:1824, y:66) is a reserved
**optional** branding slot: the presenting org's wordmark or logo,
≤ 40px tall and ≤ 260px wide, vertically centered on the kicker line.

- **Image logo:** recommended placeholder `https://placehold.co/260x80`
  (supplied at 2× and rendered 130×40, `object-fit: contain`), or a
  text wordmark in `--lp-font-display` weight 700.
- **Fully removable:** delete the slot and nothing else moves.

## Image slots

**Recommended size / placeholder:** `https://placehold.co/384x460` per
portrait (or 768×920 supplied at 2×). **Dimension fallback:** fixed
384×460 frames, `object-fit: cover` — any delivered crop fills without
moving the grid. **Load fallback:** token CSS fill (`--lp-fg-faint`)
behind every `<img>`.

Portraits are optional **as a set**: dropping all four turns the
column hairlines + names + roles into a clean typographic roster
(names step up to 40px, hairline pitch tightens — see spec note in
the no-portrait variant). Never drop only some portraits.

## Choreography

Staggered entrance on slide activation, total ≤ 1.5s:

1. `0.00s` — chrome (kicker, branding, hairline) fades in, 0.5s.
2. `0.10s` — headline rises `translateY(32px→0)` + fade, 0.6s.
3. `0.30s` — column hairlines wipe `scaleX(0→1)` from left, 0.5s,
   0.1s stagger left → right.
4. `0.40s` — portraits rise `translateY(40px→0)` + fade, 0.7s,
   0.12s stagger left → right.
5. `0.85s` — names + roles fade up, 0.5s, 0.1s stagger.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
everything appears without transforms.

## Skin points (where the design system may substitute)

- **Portrait treatment** → the system's image vocabulary (duotone,
  grain, rounded corners ≤ 12px) applied uniformly to all four.
- **Column hairlines** → the system's divider vocabulary; may become
  short accent ticks (≤ 48px wide) at the same y.
- **Roles** → may sit in outlined chips if the system frames labels;
  chip footprint ≤ 384×36px.
- **Branding slot** → the system's lockup rules; monochrome preferred.
- **Background** → flat `--lp-bg` only. Portrait rows over atmosphere
  read as marketing, not record.

## Failure modes to avoid

- A featured/CEO card larger than the others — that hierarchy belongs
  in a Testimony slide, not the roster.
- Circular crops. The rectangular frame is the pack's image grammar.
- Bios, LinkedIn URLs, or contact details per member — the closing
  slide owns contact.
- Mixed portrait styles (one studio shot, one selfie, one illustration).
  Uniformity or nothing: with unusable photos, run the no-portrait
  variant.
- Branding larger than 40px tall or anywhere but the reserved corner.
