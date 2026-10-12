# map-overlay.md — Peta sebagai visual tambahan/overlay

> Relevan: FASE 0 (kumpulkan aset) & FASE 1 (kolom VISUAL). Ketika sebuah beat
> membahas negara/daerah, peta adalah visual tambahan yang memperkuat —
> BUKAN pengganti visual utama beat tersebut.

## Sumber: SimpleMaps SVG World Map

- URL: https://simplemaps.com/resources/svg-world
- Proyeksi Robinson, ~150 KB, setiap negara = 1 path dengan `id` = kode ISO2
  (contoh: `id="ID"`, `id="AU"`, `id="US"`) — highlight negara tertentu
  semudah `document.getElementById('ID').setAttribute('fill', warna)`.
- Lisensi: **gratis untuk komersial & personal**, atribusi diapresiasi
  (tidak wajib). Cantumkan "Map: SimpleMaps.com" di deskripsi/caption bila
  praktis.
- Salinan lokal (gitignored, unduh sekali per instalasi):
  `assets/world.svg`
  ```bash
  curl -sL "https://simplemaps.com/static/demos/resources/svg-library/svgs/world.svg" \
    -o assets/world.svg
  ```
- Kenapa SVG ini, bukan generate AI: geometrinya akurat secara data
  (konsisten dengan aturan ilustrasi peta yang ditarik manual pakai kode —
  peta AI rawan ngaco).

## Kapan dipakai

- Beat menyebut **negara**: overlay peta dunia/region dengan negara tersebut
  di-highlight. Contoh: "di Australia Barat" → peta + highlight Australia.
- Beat menyebut **daerah/wilayah** (bukan negara): zoom ke region + pin
  marker di lokasi. Contoh: "Campion, Australia Barat" → peta Australia
  di-zoom + pin di titik Campion.
- Beat membandingkan **2+ negara**: highlight semua negara yang dibandingkan
  dengan warna berbeda + label.

## Cara pakai (di template HTML)

1. Embed SVG inline (bukan `<img>`) agar path bisa diwarnai via JS/CSS.
2. Highlight: negara target = warna aksen video (default emas `#d9a441`);
   negara lain = netral gelap.
3. Label nama negara/daerah SELALU tampil (teks, bukan mengandalkan bentuk
   yang dikenali penonton).
4. Untuk negara kecil (tidak terlihat di peta dunia): zoom ke region-nya
   dulu, baru highlight — jangan biarkan penonton mencari titik 3px.
5. Timing: overlay peta muncul MENGIKUTI kata nama negara diucapkan
   (±0,2 dtk, seperti teks kinetik) — bukan dari awal beat.

## Aturan

- **Tambahan, bukan pengganti.** Peta adalah overlay/visual kedua. Visual
  utama beat tetap mengikuti aturan subjek per kalimat (`av-script.md`).
- Jangan menutupi subjek utama: peta di sudut/bawah, atau sebagai background
  dengan konten utama di depan.
- Satu gaya peta per video: warna highlight & label konsisten di semua beat.
- Verifikasi: negara yang di-highlight = negara yang disebut narasi.
  (Salah highlight = setara footage salah subjek.)
