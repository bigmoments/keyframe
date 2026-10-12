---
name: keyframe
description: >
  Pipeline produksi video VO-anchored yang deterministik: riset & bahan, naskah
  AV dua kolom, produksi paralel, Whisper word-timestamps sebagai master clock,
  timed beat sheet, render deterministik paralel, QA sinkronisasi, final mix.
  Gunakan saat memproduksi video narasi/VO (explainer, reel fakta, dokumenter
  pendek) — kapan pun sinkronisasi visual-teks-VO itu penting. Trigger chat:
  "bikin video", "produksi video", "video pipeline", "sinkronisasi subtitle",
  "render video", "make a video", "video production", "voiceover video", "keyframe".
license: MIT
version: 1.0.0
---

# keyframe

Pipeline produksi video narasi yang **VO-anchored**: voiceover adalah jam utama,
semua visual dan teks dijangkarkan ke timestamp VO yang terukur — bukan tebakan.
Deterministik: render dua kali hasilnya identik.

## Kapan dipakai

- Memproduksi video dengan voiceover (explainer, reel fakta, dokumenter pendek,
  video edukasi).
- Kapan pun ada keluhan "visual/teks nggak sinkron sama suara".
- Sebelum render: butuh timed beat sheet sebagai satu-satunya sumber kebenaran timing.

JANGAN dipakai untuk: video tanpa VO (pakai motion-studio langsung), live action
shooting, editing footage mentah non-narasi.

## Prinsip inti

1. **VO adalah jam utama.** Tidak ada visual event yang memakai durasi tebakan —
   semua dijangkarkan ke timestamp VO yang terukur via Whisper.
2. **Naskah dikunci sebelum TTS.** Satu naskah = satu request TTS. Re-take hanya
   bila file corrupt, bukan coba-coba intonasi.
3. **Ukur, jangan tebak.** Timing dari data (word timestamps), bukan proporsional
   panjang karakter. Render sekali; re-render hanya bila temuan QA fatal.
4. **Paralel yang bisa, sekuensial yang harus.** VO || aset visual || backsound
   jalan bareng. Render & mix tetap di akhir (butuh semua input).
5. **Verifikasi tiap artefak.** Tiap tahap selesai = bukti eksplisit (file ada,
   ukuran wajar, timestamp masuk akal). Tanpa bukti = belum selesai.

## Alur 5 fase

```
FASE 0  riset & bahan (fakta, footage/foto, momen jangkar, backsound)
FASE 1  naskah AV dua kolom → KUNCI
FASE 2  paralel: TTS || aset visual || backsound → Whisper → timed beat sheet
FASE 3  pre-render checklist → build HTML → render deterministik SEKALI
FASE 4  QA stills + QA sinkronisasi (target 1 ronde)
FASE 5  mix → mux → verifikasi → upload → log
```

**FASE 0 — Riset & bahan.** Verifikasi fakta kunci via search (angka, tahun, nama
— jangan mengarang). Kumpulkan footage/foto asli per entitas spesifik (Wikimedia
CC / stock kata kunci spesifik); foto arsip di-crop dari bingkai putih SEBELUM
dipakai. Tentukan "momen jangkar": angka-angka kunci dan momen visual yang wajib
sinkron. Pilih backsound dari library lokal sesuai mood.

**FASE 1 — Naskah AV dua kolom.** Format: tiap baris = `AUDIO` (teks VO) +
`VISUAL` (yang tampil persis saat baris itu diucapkan) + teks kinetik.
Lihat `references/av-script.md`. Setelah dikunci: naskah TIDAK BOLEH berubah.

**FASE 2 — Produksi paralel.** Tiga jalur jalan bareng:
  (a) TTS voiceover — 1 request untuk naskah utuh, ukur durasi aktual WAV;
  (b) aset visual — finalisasi footage/foto + siapkan layout klip animasi
      (durasi final menunggu beat sheet);
  (c) backsound — pilih dari library, siapkan untuk ducking.
Lalu: Whisper word-timestamps (`scripts/whisper_timestamps.py`) = MASTER CLOCK.
Petakan tiap beat AV ke timestamp aktual → `beat_sheet.json`
(`scripts/beat_sheet.py`, skema di `references/beat-sheet.md`).

**FASE 3 — Build.** Pre-render checklist (`references/qa-sync.md`): subtitle
≤2 baris / ≤42 char per baris, tidak ada teks tumpuk atau keluar safe area
(1080×1440 tengah kanvas 1080×1920), SETIAP visual event punya anchor timestamp
dari VO. Panggil motion-studio/huashu untuk sisipan animasi dengan durasi PRESISI
dari beat sheet (bukan tebakan "5–10 detik"). Aturan jangkar:
  - Animasi angka: mulai 0,3–0,5 dtk SEBELUM VO menyebut angka, landing TEPAT
    saat VO selesai menyebutnya (durasi dihitung dari timestamp).
  - Footage cut: HANYA di batas kalimat/topik VO.
  - Teks kinetik: muncul ±0,2 dtk dari kata yang diucapkan.
Render deterministik SEKALI via `scripts/render_parallel.mjs`
(panduan efisiensi di `references/render-efficient.md`).

**FASE 4 — QA.** QA stills (visual: kepotong/tumpuk/safe area/watermark) +
QA sinkronisasi: tiap angka dan momen jangkar dicek satu per satu melawan VO.
Target 1 ronde; re-render hanya bila temuan fatal.

**FASE 5 — Final.** Mix VO + backsound (sidechain ducking; max final ≤1dB di atas
max VO). Mux mp4 limited-range (`scale=in_range=pc:out_range=tv,format=yuv420p`).
Verifikasi eksplisit tiap artefak (mp4 ada & ukuran wajar, caption ada, upload
OK). Catat log + laporkan total waktu produksi.

## Indeks modul

| Modul | Kapan dibaca |
|---|---|
| `references/av-script.md` | FASE 1 — format naskah dua kolom + contoh |
| `references/whisper-clock.md` | FASE 2 — setup Whisper, word timestamps → kartu subtitle |
| `references/beat-sheet.md` | FASE 2 — skema JSON timed beat sheet + aturan anchor |
| `references/render-efficient.md` | FASE 3 — render paralel + tuning performa |
| `references/qa-sync.md` | FASE 3–4 — pre-render checklist + QA sinkronisasi |
| `references/captions.md` | FASE 3 — opsi style caption (`default` kartu subtitle / `capcut` karaoke) |

## Scripts

| Script | Fungsi |
|---|---|
| `scripts/whisper_timestamps.py` | WAV → JSON word timestamps (faster-whisper) |
| `scripts/beat_sheet.py` | av_script.md + timestamps JSON → beat_sheet.json |
| `scripts/render_parallel.mjs` | Render deterministik paralel (CLI = render_full.mjs) |

Baca modul yang relevan saja. Target waktu produksi: ≤35–40 menit untuk video
~60 detik (dari 57 menit pipeline lama).
