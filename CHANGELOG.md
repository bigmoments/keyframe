# Changelog

## [1.4.0] — 2026-10-12
### Added
- Style caption ketiga: `pop` — satu kata per layar, efek pop tiap ganti kata, kata KAPITAL SEMUA otomatis highlight kuning. Snippet: `examples/caption-pop.html`. Cocok untuk motivasi/tips cepat; jangan untuk narasi padat fakta.

## [1.3.0] — 2026-10-12
### Added
- `references/captions.md`: opsi style caption — `default` (kartu subtitle, tetap baku) dan `capcut` (karaoke kata-per-kata: highlight + pop kata aktif dari Whisper word timestamps). Konfigurasi via `"caption_style"` di beat_sheet.json.
- `examples/caption-capcut.html`: drop-in snippet layer caption capcut (deterministik via `window.__setTime`).

## [1.2.0] — 2026-10-12
### Added
- `references/av-script.md`: menu 4 tipe hook (bold statement / question / problem / benefit) per niche, beat intro opsional untuk tutorial, 4 pola body, 4 varian CTA. Aturan hook lama tetap sebagai default.

## [1.1.0] — 2026-10-12
### Changed
- Renamed skill `video-pipeline` → **`keyframe`** (public release prep; no functional changes).

All notable changes to this skill are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-10-11

### Added
- Initial release: VO-anchored deterministic video production pipeline.
- `SKILL.md`: 5 phases (research → AV script → parallel production → build →
  QA → final), core principles (VO is the master clock, no guessed timings,
  verify every artifact), anchor rules.
- `references/`: av-script (two-column format), whisper-clock (faster-whisper
  setup + subtitle card grouping), beat-sheet (JSON schema + anchor rules),
  render-efficient (parallel render + tuning), qa-sync (pre-render checklist +
  sync QA).
- `scripts/whisper_timestamps.py`: WAV → JSON word timestamps (faster-whisper,
  model small default, base fallback, Indonesian default).
- `scripts/beat_sheet.py`: av_script.md + timestamps JSON → beat_sheet.json
  (fuzzy beat alignment, `[JANGKAR: angka "..."]` anchor extraction, subtitle
  card splitting 2 lines × 42 chars).
- `scripts/render_parallel.mjs`: parallel deterministic renderer — 1 browser,
  2 pages, setTime+wait in one evaluate, per-page ffmpeg (veryfast), concat
  with `-c copy`. Same CLI as `render_full.mjs`.
- `examples/`: AV script sample + beat sheet JSON sample.

### Notes
- Skill content in Bahasa Indonesia; README in English.
- Born from a daily faceless-video production workflow (57-min run analysis,
  2026-10-11): fixes VO re-takes, 2-round QA rework, late backsound, and
  visual/VO desync (counter landing after the VO moved on).
