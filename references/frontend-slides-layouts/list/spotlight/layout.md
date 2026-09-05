---
version: 1.0
name: Spotlight
slot: list
description: >
  One leads, three follow. The featured item runs large across the
  upper field — accent numeral, display title, full description — then
  a hairline, then the remaining three items compressed into a quiet
  row. An honest hierarchy for lists that secretly have one.
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

# Spotlight — list layout

## Intent

Most four-item lists are really one important thing and three
supporting things, flattened into equality by the layout. Spotlight
says it out loud: the lead item gets two-thirds of the stage and the
full typographic register, the rest share one modest row below the
rule. The audience's takeaway matches the deck's intent — which is
the whole job of hierarchy.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  KICKER · LABEL                                       10 / 14  │
│  THIS QUARTER'S FOCUS       ← headline                         │
│                                                                │
│  01   EDGE INFERENCE EVERYWHERE      ← featured item           │
│       Three lines of description at full width,                │
│       the argument for why this one leads.                     │
│                                                                │
│  ──────────────────────────────────────────────────────────    │
│  02 Console v3      03 Partner APIs     04 Latency budgets     │
│     one line …         one line …          one line …          │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker / Counter | x:96 / right x:1824, y:72 | mono 15px as usual | `--lp-accent` / `--lp-fg-muted` |
| Headline | x:96, top y:118, 1 line | `--lp-font-display`, 84px, weight 800, line-height 1.02, ls −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Featured numeral | x:96, top y:330 | `--lp-font-display`, 72px, weight 800, line-height 1 | `--lp-accent` |
| Featured title | x:260, top y:330, max-width 1450px, 1–2 lines | `--lp-font-display`, 56px, weight 700, line-height 1.08 | `--lp-fg` |
| Featured description | x:260, 20px below title, max-width 1100px | `--lp-font-body`, 22px, line-height 1.6 | `--lp-fg-muted` |
| Divider | x:96 → 1824, y:640, 1px | — | `--lp-line` |
| Follower row | 3 equal columns, x:96 → 1824, 64px gaps, top y:696 | numeral: `--lp-font-mono` 16px; title: `--lp-font-display` 28px weight 700, inline after numeral (16px gap); desc: `--lp-font-body` 17px lh 1.5, 10px below | numerals `--lp-fg-muted`, titles `--lp-fg`, descs `--lp-fg-muted` |

## Content constraints (hard limits)

- **Exactly 1 + 3 items.** All four numbered sequentially — the
  followers are ranked, not orphaned.
- **Featured title:** 1–2 lines ≤ 44 characters. **Featured
  description:** 2–3 lines ≤ 240 characters — this is the one place a
  list item gets to argue.
- **Follower titles:** 1 line ≤ 20 characters. **Follower descs:**
  1–2 lines ≤ 80 characters.
- The featured item must genuinely lead; if the four are equals, use
  Counter Cards.

## Image variant

**With an image:** the featured item gains a 560×280 image plate
(1px `--lp-line` border) at x:1264 → 1824, y:330; featured description
caps at 900px. Followers never get images. **Recommended size /
placeholder:** `https://placehold.co/560x280`. **Dimension fallback:**
fixed frame, `object-cover`, token CSS fill behind the `<img>`.
The image is optional.

## Choreography

1. `0.00s` — kicker, counter fade; headline rises at `0.1s`, 0.7s.
2. `0.35s` — featured numeral pops `scale(0.6→1)` + fade 0.5s; title
   and description fade up `translateY(28px→0)` 0.6s at `0.45s`.
3. `0.75s` — divider wipes `scaleX(0→1)`, 0.6s.
4. `0.90s` — follower columns fade up left-to-right, 0.5s, 0.1s
   stagger.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Featured numeral** → the system's display figure or tag treatment;
  the one accent moment besides the headline's `<em>`.
- **Divider** → the system's hairline vocabulary.
- **Followers** → the system's caption/compact register.

## Failure modes to avoid

- A featured item chosen by politics rather than argument — the
  description must justify the spotlight.
- Followers with multi-line titles or growing descriptions until the
  row rivals the feature.
- Restyling followers as mini-cards; they are a row of lines, not
  boxes.
