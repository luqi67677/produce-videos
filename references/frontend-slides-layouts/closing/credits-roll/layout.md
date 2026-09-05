---
version: 1.0
name: Credits Roll
slot: closing
description: >
  Film-credits closing. A centered thank-you statement crowns a
  two-column credits block — mono roles right-aligned against display
  names left-aligned around a center gutter — with one contact line at
  the bottom. The deck ends by naming the people who made it true.
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

# Credits Roll — closing layout

## Intent

Every other closing preset thanks the audience; this one thanks the
cast. The two-column role/name grammar is instantly read as credits —
which reframes the whole deck retroactively as a production, and gives
teams the ending they actually deserve. Best for internal decks,
retrospectives, and launches.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  IN CLOSING                                           12 / 12  │
│                                                                │
│                     THANK YOU.       ← statement               │
│                                                                │
│           PLATFORM LEAD  │  A. Rahman                          │
│              EDGE MODELS │  S. Wijaya          ← credits       │
│                 CONSOLE  │  D. Putri              block        │
│             SITE ROLLOUT │  Field Ops Guild                    │
│                                                                │
│           EMAIL · SITE · HANDLE      ← contact line            │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Counter (top-right) | right-aligned x:1824, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |
| Statement | centered, top y:170, text-align center | `--lp-font-display`, 108–120px (default 120), weight 700–800, line-height 0.97, letter-spacing −0.02em | `--lp-fg`; terminal beat / `<em>` → `--lp-accent` |
| Credits block | centered on x:960, top y:420; two columns around a 48px center gutter; rows spaced 30px apart | — | — |
| · role (left col) | right-aligned to the gutter | `--lp-font-mono`, 15px, uppercase, ls 0.16em | `--lp-fg-muted` |
| · name (right col) | left-aligned from the gutter | `--lp-font-display`, 30px, weight 700 | `--lp-fg` |
| Contact line | centered, y:940, items separated by " · " | `--lp-font-mono`, 15px, ls 0.08em | values `--lp-fg-muted`, separators `--lp-accent` |

## Content constraints (hard limits)

- **Statement:** 1 line, ≤ 14 characters uppercase at 120px.
- **Credits:** 4–7 role/name rows. Roles ≤ 22 characters, names ≤ 28.
  A "name" may be a team ("Field Ops Guild"). Order by appearance in
  the deck's story, not by seniority.
- **Contact line:** 2–3 identifier items. Optional.
- The block must end above y:900 — with 7 rows tighten spacing to 24px.

## Image variant

**With images:** each credit row may carry a 56×56 photo chip
(grayscale-friendly headshot, `object-cover`, no border-radius
unless the design system rounds avatars) sitting left of the role
column, 20px gap, all vertically centered per row. All rows get chips
or none. **Without images:** the pure type block above.

**Recommended size / placeholder:** `https://placehold.co/112x112`
(2× for sharpness at 56px). **Dimension fallback:** fixed 56×56 chip,
`object-cover`, token CSS fill behind each `<img>`. Chips are
optional.

## Choreography

1. `0.00s` — kicker and counter fade in, 0.5s.
2. `0.10s` — statement rises `translateY(48px→0)` + fade, 0.8s; its
   accent beat pops `scale(0→1)` at `0.7s`, 0.4s.
3. `0.50s` — credit rows fade up `translateY(16px→0)` in order, 0.45s
   each, 0.1s stagger — the roll.
4. `1.20s` — contact line fades in, 0.5s.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Gutter** → a 1px vertical hairline in `--lp-line` may mark the
  center gutter if the system likes visible structure.
- **Roles** → the system's label treatment.
- **Contact separators** → the system's marker glyph.
- **Background** → flat or a very quiet symmetric texture.

## Failure modes to avoid

- More than 7 rows — a credits slide that scrolls in spirit. Cut or
  group into teams.
- Mixing alignment: roles right-align to the gutter, names left-align
  from it, always.
- Turning it into an org chart (titles like "Senior Staff…"). Credits
  are story roles, short and human.
