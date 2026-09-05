---
version: 1.0
name: Counterpoise
slot: closing
description: >
  Diagonal closing. The statement holds the top-right, right-aligned;
  a ruled contact stack answers from the bottom-left. The mirror image
  of the Corner Weight opening — a deck framed by the two presets
  closes its diagonal like a bracket.
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

# Counterpoise — closing layout

## Intent

Right-aligned display type is rare on slides, which is exactly why it
reads as an ending — the text leans against the right edge like the
last page of a book. The contact stack in the opposite corner converts
the farewell into logistics without sharing its space. Pairs with
Corner Weight for a mirrored deck frame; stands alone anywhere a quiet
asymmetric ending fits.

## Region map (1920×1080 stage)

```
┌────────────────────────────────────────────────────────────────┐
│  IN CLOSING                                                    │
│                                          SEE YOU               │
│                                        OUT THERE.  ← statement │
│                                          ────────  ← tail rule │
│                                                                │
│                  (empty diagonal)                              │
│                                                                │
│  EMAIL                                                         │
│  CONTACT                                                       │
│  ──────────────────                                            │
│  SITE               ← contact stack                            │
│  example.io                                           12 / 12  │
└────────────────────────────────────────────────────────────────┘
```

## Geometry

| Element | Position & size | Type spec | Color role |
|---|---|---|---|
| Kicker (top-left) | x:96, y:72 | `--lp-font-mono`, 15px, uppercase, ls 0.18em | `--lp-accent` |
| Statement | right-aligned to x:1824, top y:150, max-width 1200px, 2–3 lines, text-align right | `--lp-font-display`, 120–132px (default 128), weight 700–800, line-height 0.97, letter-spacing −0.02em | `--lp-fg`; `<em>` → `--lp-accent` |
| Tail rule | right-aligned to x:1824, 40px below statement, 200×1px | — | `--lp-line` |
| Contact stack | x:96, bottom-anchored at y:984; 2–3 entries; each: mono label, value, 1px rule between entries; entry width ≤ 560px | labels `--lp-font-mono` 13px uppercase ls 0.16em; values `--lp-font-body` 26px | labels `--lp-fg-muted`, values `--lp-fg`, rules `--lp-line` |
| Counter (bottom-right) | right-aligned x:1824, y:984 | `--lp-font-mono`, 15px, uppercase, ls 0.12em | `--lp-fg-muted` |

## Content constraints (hard limits)

- **Statement:** 2–3 lines, ≤ 12 characters uppercase per line at
  128px. Right-aligned ragged-left — never justify.
- **Contact stack:** 2–3 entries, single-line values, identifiers only.
  Stack height ≤ 300px.
- **The diagonal stays empty** — same contract as Corner Weight.

## Image variant

**With an image:** a 480×360 image plate joins the bottom-left corner
*under* the contact stack's anchor — the stack moves up to sit on the
plate's top edge (24px gap), the plate takes a 1px `--lp-line` border
and a mono caption line beneath. Use for a team photo or the shipped
thing — the ending's proof.

**Recommended size / placeholder:** `https://placehold.co/480x360`.
**Dimension fallback:** fixed 480×360 frame, `object-cover`,
token CSS fill behind the `<img>`. The image is optional.

**Without an image:** the type-only stack above.

## Choreography

1. `0.00s` — kicker fades, 0.5s.
2. `0.10s` — statement lines rise `translateY(48px→0)` + fade, 0.7s,
   0.12s stagger; tail rule wipes from the right (`transform-origin:
   right`) at `0.55s`, 0.5s.
3. `0.70s` — contact entries (and plate, if any) fade up bottom-first,
   0.55s, 0.1s stagger; counter fades with them.

Ease: `cubic-bezier(0.16, 1, 0.3, 1)`. Under `prefers-reduced-motion`,
no transforms.

## Skin points

- **Tail rule** → the system's small punctuation, right-anchored.
- **Contact stack rules** → the system's divider style.
- **Background** → an atmospheric sweep may cross the empty diagonal
  as long as both corners stay quiet.

## Failure modes to avoid

- Left-aligning the statement — the right alignment is the preset.
- Filling the diagonal (logos, QR codes, ghosts).
- More than 3 contact entries; a directory belongs to Terminal Frame
  or Split Curtain.
