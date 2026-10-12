# av-script.md — Naskah AV dua kolom

> Relevan: FASE 1. Naskah adalah kontrak antara audio dan visual — ditulis bareng,
> dikunci sebelum TTS, tidak boleh berubah setelahnya.

## Format

Setiap beat = satu baris blok dengan tiga kolom:

```
BEAT <n> | <label singkat>
AUDIO : <teks yang diucapkan VO, persis>
VISUAL: <apa yang tampil PERSIS saat baris ini diucapkan>
TEKS  : <teks kinetik/subtitle yang muncul (opsional)>
```

Aturan:
- Satu beat = satu kalimat atau satu napas. Jangan dua topik dalam satu beat.
- Kolom VISUAL wajib konkret: footage apa / foto apa / animasi apa / angka apa.
  "Visual menarik" bukan instruksi — tulis objeknya.
- Tandai **momen jangkar** dengan `[JANGKAR: angka]` — angka/momen yang wajib
  sinkron presisi dengan VO (lihat `beat-sheet.md`).
- Hook 3 detik: BEAT 1 harus kalimat yang bikin penonton tidak bisa scroll,
  muncul di suara DAN teks visual besar. Clickbait di bingkai boleh, fakta di
  dalamnya 100% benar. Pilih SATU tipe hook sesuai niche:

  | Tipe | Contoh | Cocok untuk |
  |------|--------|-------------|
  | Bold statement | "Australia pernah perang melawan BURUNG. Dan KALAH." | fakta, sejarah, mitos |
  | Question | "Kenapa HP baru 6 bulan udah lemot?" | tips, tutorial, problem-solving |
  | Problem | "90% orang salah pakai cara ini..." | edukasi, how-to |
  | Benefit | "3 menit, hemat 2 juta setahun." | finance, produktivitas, life-hack |

  Uji: lolos "hah, masa sih?" (niche fakta) atau "wah, aku butuh ini" (niche tips).
- Beat intro (OPSIONAL, hanya niche tutorial/explainer): 1 beat setelah hook —
  akui masalah → janji solusi → preview isi. JANGAN dipakai untuk format fakta
  cepat: merusak pacing.
- Pola body: pilih satu per video (wajib dipikirkan untuk channel/niche baru):

  | Pola | Struktur beat | Cocok untuk |
  |------|---------------|-------------|
  | Punchline (default) | konteks → angka/fakta → punchline | fakta, sejarah |
  | Step-by-step | langkah 1 → 2 → 3, satu beat per langkah | tutorial, how-to |
  | Problem-solution | masalah → kenapa terjadi → solusi | edukasi, tips |
  | List | "cara 1, 2, 3", satu beat per item | life-hack, rekomendasi |
- Penutup: pilih SATU varian CTA, di suara DAN teks (bila untuk sosmed):

  | Varian | Contoh |
  |--------|--------|
  | Follow/subscribe | "Follow biar nggak ketinggalan fakta berikutnya." |
  | Next video (session time) | "Besok aku bahas X — jangan sampai lolos." |
  | Engagement | "Setuju atau nggak? Tulis di komen." |
  | Link/afiliasi | "Link-nya di bio." |

## Contoh konkret

```
BEAT 1 | hook (bold statement)
AUDIO : Australia pernah menyatakan perang... melawan BURUNG. Dan mereka KALAH.
VISUAL: teks hook besar "KALAH MELAWAN BURUNG?" + footage emu berlari (close-up)
TEKS  : KALAH MELAWAN BURUNG?

BEAT 2 | konteks
AUDIO : Tahun 1932, dua puluh ribu emu menyerbu ladang gandum di Australia Barat.
VISUAL: peta Australia Barat + penanda Campion [JANGKAR: angka 20.000]
TEKS  : 1932 — Australia Barat

BEAT 3 | angka kunci
AUDIO : Petani panik. Pemerintah mengirim tentara, lengkap dengan senapan mesin Lewis.
VISUAL: foto arsip tentara Australia 1932 (sudah di-crop) + label "Senapan Lewis"
TEKS  : tentara + senapan mesin

BEAT 4 | punchline
AUDIO : Hasilnya? Dalam seminggu, sepuluh ribu peluru ditembakkan. Emu yang mati: kurang dari seribu.
VISUAL: counter 0→10.000 peluru, lalu counter 0→986 emu [JANGKAR: angka 10.000, 986]
TEKS  : 10.000 peluru vs 986 emu
```

## Checklist kunci naskah

- [ ] Setiap beat satu kalimat/napas, satu topik.
- [ ] Kolom VISUAL konkret (objek, bukan sifat).
- [ ] Momen jangkar ditandai `[JANGKAR: ...]`.
- [ ] Fakta (angka/tahun/nama) sudah verifikasi via search.
- [ ] Hook 3 detik: tipe hook dipilih sesuai niche, lolos uji "hah, masa sih?" / "aku butuh ini".
- [ ] Pola body + varian CTA dipilih (terutama untuk channel/niche baru).
- [ ] Estimasi durasi wajar (±750–800 karakter ≈ 60 detik untuk VO natural).
- [ ] Dibaca ulang keras-keras sekali — tidak ada kalimat yang bikin tersedak.

Setelah checklist lolos: **KUNCI.** Perubahan setelah TTS = VO re-take = buang
kuota + waktu. Satu-satunya alasan mengulang TTS adalah file corrupt/gagal total.
