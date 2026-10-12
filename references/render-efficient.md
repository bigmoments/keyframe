# render-efficient.md — Render deterministik yang efisien

> Relevan: FASE 3. Render adalah langkah tunggal termahal (±10 menit untuk
> 1668 frame @24fps). Dokumen ini menjelaskan di mana waktunya habis dan cara
> memangkasnya tanpa mengorbankan determinisme.

## Anatomi biaya per frame (dari `render_full.mjs`)

Per frame ada **3 CDP round-trip** ke Chromium:

1. `page.evaluate(setTime)` — set waktu timeline.
2. `page.evaluate(2×rAF + logika seek video)` — tunggu render + seek.
3. `page.screenshot(jpeg)` — ambil frame (termahal: encode JPEG + transfer).

Plus 1 encode x264 (`-preset medium`) di ujung pipa.

## Teknik penghematan (diimplementasikan di `scripts/render_parallel.mjs`)

### 1. Paralel 2 page (diukur 1,32x di HTML produksi)

Satu browser, **2 pages** (menyesuaikan 2 CPU). Frame dibagi dua:
page A = frame `0..N/2`, page B = frame `N/2..N`. Tiap page independen karena
`window.__setTime(t)` stateless — tidak ada state antar frame yang dibagi.

Tiap page punya pipa ffmpeg sendiri (`-preset veryfast`, bukan `medium` —
mengurangi kontensi CPU saat 2 encode jalan bareng). Hasil: 2 segmen mp4 →
digabung via `ffmpeg concat -c copy` (tanpa re-encode).

**Hasil ukur (2026-10-11, VM 2 CPU):** HTML produksi `emu.html`, 120 frame —
serial 94 dtk → paralel 71 dtk = **1,32x**. Frame count identik (120), spot-check
visual identik.

### 2. Semua waiting di sisi Node (temuaan kritis)

**Page background membekukan `requestAnimationFrame`/`setTimeout`** — page yang
dibuat pertama macet total (0 frame dalam 5+ menit) bila menunggu di dalam page,
sementara page kedua (foreground) jalan normal. Terbukti via isolasi: evaluate
trivial jalan di kedua page, tapi rAF/setTimeout di page background tidak pernah
fire.

Solusi: `__setTime` via SATU `page.evaluate` trivial (tanpa waiting di dalam),
lalu:
- Tunggu seek video via **polling Node-side** (`video.seeking`, interval 40ms,
  cap 600ms + `console.warn` bila kepakai).
- `page.screenshot()` memaksa fresh compositor frame walau page background
  (terverifikasi: byte-identical dengan foreground untuk `t` yang sama).

Jangan pernah mengandalkan rAF/setTimeout di dalam page pada renderer paralel.

### 3. Seek fallback 600ms + warning

Timeout darurat untuk video yang tidak selesai seek: 600ms (vs 1500ms di
serial), dengan `console.warn` bila kepakai. Catatan: pada workload yang
seek-heavy, 80% frame bisa kena fallback — tiap fallback = 600ms terbuang.
Ini limiter utama speedup (lihat "Keterbatasan" di bawah).

### 4. Yang TIDAK diubah (demi determinisme & kualitas)

- `window.__setTime(t)` — logika timeline sama persis.
- JPEG quality 88, 1080×1920, 24fps — kualitas frame identik.
- Random seeded di sisi HTML — frame A/B identik dengan render serial.

## Cara pakai

```bash
# CLI identik dengan render_full.mjs
node scripts/render_parallel.mjs <html> <durasi-detik> <out.mp4>
```

## Kapan TIDAK pakai paralel

- HTML memakai state global antar frame (mis. akumulasi partikel tanpa reset
  di `__setTime`) — page B yang mulai dari tengah akan salah. Pastikan
  `__setTime(t)` benar-benar stateless: panggil dua kali dengan `t` sama harus
  hasilkan frame identik.
- RAM < 4GB bebas — 2 Chromium + 2 ffmpeg butuh memori lebih.
- Workload yang didominasi video-seek per frame: speedup menyusut (terukur
  1,02x pada HTML uji yang seek tiap frame) karena seek tidak terparalelisasi
  dengan baik dan berebut media pipeline. Pada HTML produksi campuran
  (animasi + B-roll) terukur 1,32x.

## Verifikasi

- [ ] Frame count output = `round(24 × durasi)` — sama seperti serial.
- [ ] Uji determinisme: render 2× → `ffmpeg` frame-compare identik (atau
  bandingkan checksum segmen).
- [ ] Spot-check visual: 3 stills (awal/tengah/akhir) vs render serial —
  tidak ada perbedaan.
