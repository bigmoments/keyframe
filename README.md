# keyframe

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Format: Markdown](https://img.shields.io/badge/format-markdown-blue.svg)](#)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A deterministic, **VO-anchored** video production pipeline as an agent skill.
The voiceover is the master clock: every visual event and subtitle is anchored
to measured VO timestamps — never guessed. Renders twice, get identical output.

Use it when producing narrated video (explainers, fact reels, short documentaries)
— anywhere visual/text/VO sync actually matters.

> **Note:** the skill content is written in **Bahasa Indonesia** (its trigger
> phrases and working language). This README is in English for the GitHub audience.

---

## Why VO-anchored?

The classic failure: the visual timeline is authored from *estimated* timings
(proportional to character count), then the VO is generated. Result: a count-up
animation still running when the VO already moved on, footage cutting mid-sentence,
subtitles drifting ±1 second per card.

This pipeline flips it: **lock script → generate VO once → measure word
timestamps with Whisper → anchor everything to them.** No guessed durations, ever.

## The 5 phases

```
0  research & assets   — verify facts, gather real footage/photos, anchor moments, backsound
1  AV script (2-col)   — AUDIO + VISUAL written together per beat → LOCKED
2  parallel production — TTS || visual assets || backsound → Whisper → timed beat sheet
3  build               — pre-render checklist → build HTML → single deterministic render
4  QA                  — stills + sync QA (each anchor moment checked vs VO)
5  final               — mix, mux, verify artifacts, upload, log
```

Target: ≤35–40 min for a ~60s video (down from 57 min with the old pipeline).

## Anchor rules (the core idea)

| Visual event | Rule |
|---|---|
| Number count-up | Start 0.3–0.5s BEFORE the VO says the number; land EXACTLY when it finishes saying it |
| Footage/photo cut | ONLY at VO sentence/topic boundaries |
| Kinetic text | Appear ±0.2s from the spoken word |
| Animation insert | Duration from the beat sheet, never "5–10 seconds" |

## Installation

Pure Markdown + scripts, standard `SKILL.md` format. No hooks, plugins, or MCP.
Copy the `keyframe/` folder into your harness's skills directory:

| Harness | Skills directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Cursor | `<project>/.cursor/skills/` or `~/.cursor/skills/` |
| Codex | `~/.codex/skills/` |
| Antigravity / Gemini CLI | per each tool's docs |

```bash
cp -r keyframe ~/.claude/skills/
```

Scripts need: **Node 18+** with `puppeteer`, **ffmpeg**, **Python 3.10+** with
`faster-whisper` (`pip install faster-whisper`), and Chromium at
`/opt/meta-chromium/chrome` (or edit the path in `scripts/render_parallel.mjs`).

> `render_parallel.mjs` resolves `puppeteer` via ESM (which ignores `NODE_PATH`):
> symlink your existing install —
> `ln -s ~/workspace/std-video/v2/node_modules ~/workspace/skills/keyframe/node_modules`
> — or `npm install puppeteer` inside the skill directory.

## Usage

- *"Bikin video explainer tentang X"* / *"make a narrated video about X"*
- *"Produksi video 60 detik dari naskah ini"*
- *"Subtitle-nya nggak sinkron, benerin"*

Or follow the phases manually — each `references/` module covers one concern.

## Project structure

```
keyframe/
├── SKILL.md                  # Pipeline definition: phases, principles, anchor rules
├── README.md                 # This file
├── LICENSE                   # MIT
├── CHANGELOG.md
├── references/
│   ├── av-script.md          # Two-column AV script format + example
│   ├── whisper-clock.md      # faster-whisper setup, word timestamps → subtitle cards
│   ├── beat-sheet.md         # Timed beat sheet JSON schema + anchor rules
│   ├── render-efficient.md   # Parallel deterministic render + tuning
│   └── qa-sync.md            # Pre-render checklist + sync QA
├── scripts/
│   ├── whisper_timestamps.py # WAV → JSON word timestamps
│   ├── beat_sheet.py         # av_script.md + timestamps → beat_sheet.json
│   └── render_parallel.mjs   # Parallel deterministic renderer (2 pages)
└── examples/
    ├── av-script-example.md
    └── beat-sheet-example.json
```

## License

MIT — see [LICENSE](LICENSE).
