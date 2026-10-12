# captions.md — Opsi style caption

> Relevan: FASE 3 (Build). Caption adalah layer teks di atas video yang mengikuti
> ucapan VO. Pilih SATU style per video — jangan campur.

## Style yang tersedia

| Style | Nama | Cara kerja | Cocok untuk |
|-------|------|-----------|-------------|
| `default` | Kartu subtitle | Kartu 1–2 baris berganti per irama ucapan (aturan 2 baris/42 char di `whisper-clock.md` + `qa-sync.md`) | fakta, dokumenter, STD — footage sinematik tidak tertutup teks besar |
| `capcut` | Karaoke kata-per-kata | Kata muncul satu per satu mengikuti ucapan; kata aktif di-highlight + pop | talking-head, tips, tutorial — konten personal yang energik |

`default` adalah style baku. `capcut` hanya dipakai bila diminta eksplisit
atau untuk channel/niche yang gayanya personal.

## Konfigurasi

Di `beat_sheet.json`, tambah field opsional:

```json
{ "caption_style": "capcut" }
```

Tanpa field ini = `default`. Render template membaca field ini dan memuat
layer caption yang sesuai.

## Spesifikasi style `capcut`

Sumber data: **word timestamps Whisper** (bukan kartu subtitle) — tiap kata
punya `{word, start, end}`.

- **Pengelompokan frasa:** kata dikelompokkan per kalimat, atau maksimal
  6 kata / 3 detik per frasa — mana yang tercapai dulu. Satu frasa tampil
  utuh, kata muncul progresif mengikuti ucapan.
- **Highlight kata aktif:** kata yang sedang diucapkan (`start <= t < end`)
  berwarna highlight (default kuning `#ffd23f`) + scale 1.15 (pop).
  Kata yang sudah lewat: putih. Kata yang belum: transparan.
- **Tipografi:** bold berat (Anton / Archivo Black atau setara), uppercase
  untuk penekanan, stroke hitam 2px (`paint-order: stroke fill`) agar terbaca
  di atas footage ramai.
- **Posisi:** area aman — pita tengah 1080x1440, teks di sepertiga bawah
  area aman (y ≈ 1050–1350 pada canvas 1080x1920). Jangan menutup wajah
  subjek bila ada.
- **Maksimal 2 baris** per frasa. Kata panjang yang sendirian (mis. angka)
  boleh 1 baris besar.
- **Deterministik:** semua state dihitung dari `window.__setTime(t)` —
  tidak ada animasi berbasis waktu nyata. Lihat `examples/caption-capcut.html`
  sebagai drop-in snippet.

## Aturan yang tetap berlaku

- Caption tidak boleh bertumpuk dengan teks kinetik besar / watermark / label
  (`qa-sync.md`).
- Kata aktif harus sinkron dengan suara dalam ±0.1 detik — ini gratis karena
  datanya word timestamps Whisper yang sama dengan master clock.
- Bahasa mengikuti VO apa adanya (termasuk angka: "20 ribu" tampil "20 ribu",
  bukan "20000").
