# qa-sync.md — Pre-render checklist + QA sinkronisasi

> Relevan: FASE 3–4. Tujuan: render SEKALI, QA SATU ronde. Setiap temuan yang
> lolos dari checklist ini = satu re-render yang mahal.

## Pre-render checklist (sebelum render full)

Jalankan SEMUA — tidak boleh ada yang "nanti dicek pas QA":

- [ ] **Subtitle:** tiap kartu ≤2 baris, tiap baris ≤42 karakter, potong di
      batas klausa/koma alami.
- [ ] **Tidak ada teks tumpuk:** subtitle tidak bertumpuk dengan teks kinetik /
      watermark / label. Saat subtitle aktif, teks kinetik besar digeser atau
      digantian.
- [ ] **Safe area:** SEMUA teks penting di pita tengah 1080×1440 (240px atas
      dan 240px bawah kanvas bebas teks penting).
- [ ] **Foto arsip sudah di-crop** dari bingkai putih SEBELUM Ken Burns.
- [ ] **Setiap visual event punya anchor timestamp** dari VO (lihat
      `beat-sheet.md`). Tidak ada durasi tebakan.
- [ ] **Font & watermark:** font ter-load (`document.fonts`), watermark header
      sesuai gaya baku, tidak bertumpuk dengan judul bawaan.
- [ ] **Smoke test:** render 5 frame sampel (awal/tengah/akhir + 2 momen jangkar)
      via screenshot — teks terbaca, tidak kepotong.

## QA stills (setelah render)

Ambil stills di: tiap momen jangkar + 3 titik merata (awal/tengah/akhir).
Cek per still:

- [ ] Teks tidak kepotong / tidak overflow.
- [ ] Tidak ada dua teks bertumpuk.
- [ ] Komposisi benar, watermark sesuai gaya.
- [ ] Entitas spesifik = wujud aslinya (bukan footage generik yang salah subjek).

## QA sinkronisasi (wajib — ini yang sering miss)

Untuk TIAP momen jangkar di beat sheet, tonton ±3 detik di sekitarnya:

- [ ] **Angka:** counter mulai 0,3–0,5 dtk SEBELUM VO menyebut angka, landing
      TEPAT saat VO selesai menyebutnya. Toleransi ±0,2 dtk.
- [ ] **Footage cut:** terjadi di batas kalimat/topik — tidak di tengah kalimat.
- [ ] **Teks kinetik:** muncul ±0,2 dtk dari kata yang diucapkan.
- [ ] **Subtitle:** kartu berganti mengikuti irama ucapan (bukan terlalu cepat
      atau tertinggal).

Cara cepat: `ffprobe`/ekstrak audio + catat waktu, atau putar dengan overlay
timestamp. Untuk tiap miss: catat `beat_n`, `selisih_dtk`, `arah` (visual
terlalu cepat/lambat).

## Keputusan re-render

- Miss ≤0,2 dtk di ≤2 momen non-jangkar → TERIMA, catat untuk perbaikan berikut.
- Miss di momen JANGKAR, atau >0,5 dtk di mana pun → perbaiki HTML, re-render.
- Re-render kedua masih gagal → hentikan, eskalasi ke manusia. Jangan loop.

## Anti-pattern

- "Nanti dicek pas QA" untuk hal yang bisa dicek pre-render.
- QA hanya lihat visual tapi tidak dengerin VO (sinkronisasi butuh keduanya).
- Re-render full karena 1 typo kecil di teks kinetik — pertimbangkan patch
  bila pipeline mendukung (atau terima bila di bawah ambang).
