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

## Batas dengan skill motion-studio (2026-10-12)

- **keyframe = metodologi produksi (orkestrator).** Mengatur alur 5 fase dan
  aturan timing VO-anchored. BUKAN engine render animasi.
- **motion-studio = eksekusi animasi.** Dipanggil keyframe di FASE 3 untuk
  sisipan animasi, dengan durasi PRESISI dari beat sheet — JANGAN langsung ke
  huashu-art-motion / bang-motion.
- **Pembagian kerja:** "bikin video animasi/motion graphic" → motion-studio
  langsung. "Produksi video narasi ber-VO dengan timing presisi" → keyframe
  mengatur alur, motion-studio mengeksekusi sisipan animasinya. Jangan
  menjalankan pipeline penuh dua-duanya secara terpisah dalam satu tugas.
- **Perintah master:** konten video "Semua tentang dunia" WAJIB lewat
  motion-studio.

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

## Standar editor profesional (2026-10-12, arahan master)

Aturan rasa editor profesional — berlaku untuk SEMUA produksi via skill ini:

**Hierarki visual:**
1. FOOTAGE ASLI subjeknya — prioritas tertinggi, cari sungguh-sungguh (jangan
   puas dengan footage generik bila footage aslinya ada).
2. FOTO DOKUMENTASI ASLI subjeknya — foto orang yang disebut namanya, foto
   tempat asli, foto spesimen. DIIZINKAN liberal (bukan dekorasi).
3. Footage generik yang relevan — hanya untuk pernyataan umum.
4. Still dekoratif/generik — MAKSIMAL 2 per video.
- Setiap NAMA ORANG yang disebut narasi WAJIB divisualkan fotonya bila ada;
  setiap TEMPAT spesifik diusahakan foto aslinya.
- DILARANG footage yang salah subjek — lebih baik footage generik yang benar
  daripada footage spesifik yang salah.

**Pacing & transisi:**
- 1,5–2,5 dtk/shot di bagian isi; hook ≤2 dtk/shot; shot punchline/penutup =
  TERLAMA.
- Tiap beat >5 dtk pecah jadi ≥2 visual berbeda (wide → tight → interesting).
- Menu transisi — pilih sesuai energi beat, bukan selera acak:

  | Energi beat | Transisi | Contoh pakai |
  |---|---|---|
  | Hook / fakta mengejutkan | flash putih, whip-pan, whip-zoom | kalimat hook, angka mustahil |
  | Body / penjelasan | cut langsung, mask wipe halus | narasi mengalir |
  | Impak / punchline | zoom punch, impact shake, match-cut | angka kunci, kalimat penutup |
  | Tech / AI | glitch, RGB split | konten teknologi |
  | Arsip / nostalgia | film burn, light leak hangat | footage lama, foto arsip |

- DILARANG dip-to-black.
- Cut HANYA di batas kalimat/topik VO — dengan nuansa **pre-lap**: transisi
  DIMULAI 0,15–0,3 dtk SEBELUM batas kalimat, sehingga shot baru sudah stabil
  TEPAT saat kalimat baru dimulai. Cut yang mulai persis di batas terasa telat.
- Satu video maksimal 2–3 jenis transisi. Ganti-ganti tiap beat terlihat murahan.

**Sumber landscape → portrait (dilarang crop habis-habisan):**
- Teknik baku: **blur-bg** — layer tajam di-fit lebar penuh TANPA di-crop;
  di belakangnya, salinan frame yang sama di-blur kuat + digelapkan sebagai
  pengisi bingkai portrait. Tidak ada satu piksel subjek pun yang hilang.
- Varian: Ken Burns pelan (zoom/pan) pada layer tajam sementara bg blur diam —
  memberi gerak tanpa mengorbankan komposisi.
- Cover-crop HANYA bila: subjek memang memenuhi frame, ATAU posisi subjek
  diketahui dan `object-position` menjaganya tetap dalam frame.
  (Contoh: wajah di sepertiga kanan → `object-position: 75% 50%`, bukan
  center-crop buta.)
- DILARANG: center-crop buta (memenggal subjek), stretch (distorsi tubuh/
  wajah), bar hitam (video terlihat mengecil di tengah layar).

**Kontinuitas timeline:**
- Segmen visual harus CONTIGUOUS — tidak boleh ada jeda kosong antar segmen
  (jeda = layar hitam).
- Verifikasi: scan brightness per detik; tidak ada frame dengan rata-rata
  brightness <5.

**Treatment warna:**
- Samakan koreksi dasar (kontras/saturasi) SEMUA klip SEBELUM grading gaya.
  Lompatan B&W arsip → warna modern tanpa treatment = tempelan.

**QA editor (tambahan untuk FASE 4):**
- Tonton 15 detik pertama: target ≥5 visual berbeda.
- Cek subjek: tiap entitas spesifik yang disebut narasi tampil wujud yang benar.
- Cek jeda: tidak ada frame hitam/gap di seluruh durasi.
- Cek crop: tidak ada subjek terpenggal di tepi frame; sumber landscape
  memakai blur-bg, bukan crop buta.

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
dari VO. Panggil motion-studio untuk sisipan animasi dengan durasi PRESISI
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
