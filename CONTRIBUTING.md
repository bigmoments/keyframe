# Contributing to keyframe

Thanks for considering a contribution! This skill is a production pipeline —
correctness and determinism beat cleverness.

## What makes a good contribution

- **Anchor rules** proven against real desync cases (with before/after evidence).
- **Render efficiency** wins that keep output bit-identical (determinism is sacred).
- **Corrections** — wrong defaults, broken assumptions, outdated advice.
- **Translations** — skill content is Bahasa Indonesia; an English `references/`
  would be welcome (open an issue first to avoid duplication).

## Ground rules

1. **VO is the master clock.** Never introduce a guessed timing — every visual
   event must anchor to measured timestamps.
2. **Determinism first.** Any render change must produce identical frames to the
   serial renderer (compare checksums).
3. **Measure, don't guess.** Performance claims need numbers (old vs new, speedup).
4. **No AI slop.** Write like an engineer, not a brochure.

## How to contribute

1. Fork, branch (`fix/...`, `feat/...`).
2. Edit the relevant `references/` file or script.
3. For script changes: include your measurement (what you tested, the numbers).
4. Open a PR describing what, why, and how you verified it.
