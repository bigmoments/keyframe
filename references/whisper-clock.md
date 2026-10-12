# whisper-clock.md — Whisper sebagai master clock

> Relevan: FASE 2. Word timestamps dari VO adalah satu-satunya sumber kebenaran
> timing. Semua subtitle, animasi, dan footage cut dijangkarkan ke sini.

## Kenapa bukan proporsional karakter

Metode lama: `durasi segmen = karakter segmen / total karakter × durasi VO`.
Ini asumsi kecepatan bicara rata — padahal TTS berhenti di koma/titik dan
menekan kata tertentu. Error tipikal ±0,5–1 detik per kartu: kelihatan jelas
saat ditonton. Whisper pada audio TTS bersih (1 speaker, tanpa noise) akurasinya
nyaris sempurna.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install "faster-whisper" "av==12.3.0"
# PENTING: pin av==12.3.0 — av 19+ tidak kompatibel dengan faster-whisper 1.2.1
# (error: av.open() got an unexpected keyword argument 'metadata_errors')
# model diunduh otomatis saat pertama dipakai (~500MB untuk small, ~150MB base)
# tanpa torch — ringan (CTranslate2)
```

> Bila koneksi ke HuggingFace lambat (<10KB/s), unduh model manual sekali di
> koneksi kencang (`huggingface-cli download Systran/faster-whisper-small`),
> lalu taruh folder model di `models/` dan panggil script dengan path direktorinya
> (lihat bawah). Sudah terverifikasi jalan 2026-10-11.

Jalankan via wrapper (cara yang disarankan — berlaku global di semua chat/worker/cron):

```bash
~/workspace/skills/video-pipeline/scripts/whisper.sh <vo.wav> -o timestamps.json
```

Wrapper otomatis pakai venv skill (faster-whisper + `av==12.3.0` terpin) dan
otomatis memilih model lokal `models/faster-whisper-small` bila ada — tanpa
perlu argumen tambahan dan tanpa memicu unduh HuggingFace. Inilah yang dipakai
semua side chat dan cron.

Manual (bila perlu opsi khusus):

```bash
.venv/bin/python scripts/whisper_timestamps.py <vo.wav> [--model small] [--lang id] -o timestamps.json
# --model bisa berupa path direktori model lokal:
.venv/bin/python scripts/whisper_timestamps.py --model models/faster-whisper-small <vo.wav> -o timestamps.json
# Default --model: model lokal bila models/faster-whisper-small/model.bin ada,
# else "small" dari HuggingFace (fallback "base").

Output: JSON daftar kata `{word, start, end}` dalam detik. Model default `small`
(fallback `base` bila gagal). Bahasa default `indonesian` (`id`).

## Dari kata ke kartu subtitle

Aturan pengelompokan (diimplementasikan di `scripts/beat_sheet.py`):

1. Mulai kartu baru di tiap beat AV (batas beat = batas kartu).
2. Dalam satu beat, pecah lagi bila kartu melebihi **2 baris × ±42 karakter**:
   potong di batas klausa/koma yang alami (gunakan jeda antar kata > 0,35 dtk
   sebagai kandidat potong).
3. Durasi kartu: `start` = start kata pertama, `end` = end kata terakhir.
   Minimum 0,8 dtk (bila kurang, gabung ke kartu berikut dalam beat yang sama);
   maksimum ~4 dtk.
4. Teks kartu: gabung kata-katanya, pecah baris manual agar ≤42 char/baris.

Hasilnya: tiap kartu subtitle punya `{start, end, lines[]}` yang sinkron dengan
ucapan — bukan tebakan.

## Verifikasi

- [ ] Jumlah kata terdeteksi ≈ jumlah kata naskah (±5%; selisih besar = cek audio).
- [ ] Timestamp kata pertama ≈ 0,2–0,8 dtk (awal tidak kosong lama).
- [ ] Tidak ada gap > 2 dtk antar kata di tengah kalimat (tanda transkripsi miss).
- [ ] Spot-check 3 momen jangkar: timestamp angka ≈ saat VO menyebutnya.

## Keterbatasan

- Whisper butuh ~30–60 detik untuk audio 60 detik (model small, CPU 2 core).
- Install/dependensi hilang bila VM di-replace — pasang ulang via pip bila
  `import faster_whisper` gagal.
- **Download model butuh koneksi HuggingFace yang layak** (~500MB untuk small,
  ~150MB base, ~75MB tiny). Bila jaringan lambat/dibatasi proxy, unduh manual
  sekali via `huggingface-cli download Systran/faster-whisper-small` di mesin
  yang kencang lalu salin ke `~/.cache/huggingface/hub/`.
- Jangan pakai untuk audio berisik/multi-speaker — akurasi turun; untuk TTS
  bersih ini skenario ideal.
