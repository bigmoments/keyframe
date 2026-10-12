# Contoh AV script (3 beat)

```
BEAT 1 | hook
AUDIO : Australia pernah menyatakan perang... melawan BURUNG. Dan mereka KALAH.
VISUAL: teks hook besar "KALAH MELAWAN BURUNG?" + footage emu berlari
TEKS  : KALAH MELAWAN BURUNG?

BEAT 2 | angka kunci
AUDIO : Tahun 1932, dua puluh ribu emu menyerbu ladang gandum di Australia Barat.
VISUAL: peta Australia Barat + penanda Campion [JANGKAR: angka "dua puluh ribu"]
TEKS  : 1932 — Australia Barat

BEAT 3 | punchline
AUDIO : Sepuluh ribu peluru ditembakkan. Emu yang mati: kurang dari seribu.
VISUAL: counter 0→10.000, lalu counter 0→986 [JANGKAR: angka "sepuluh ribu"]
TEKS  : 10.000 peluru vs 986 emu
```

Catatan:
- `[JANGKAR: angka "..."]` memakai frasa persis seperti diucapkan di AUDIO
  (bukan "20.000") agar bisa dicocokkan ke Whisper timestamps.
- Setelah naskah ini dikunci, TTS 1x — tidak ada revisi kalimat.
