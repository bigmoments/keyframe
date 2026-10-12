# beat-sheet.md — Timed beat sheet (JSON)

> Relevan: FASE 2–3. Beat sheet adalah kontrak timing antara naskah, visual,
> dan render. Dibangun dari AV script + Whisper timestamps — bukan estimasi.

## Skema

```jsonc
{
  "meta": {
    "title": "Judul video",
    "vo_file": "vo.wav",
    "vo_duration": 62.4,          // detik, dari file WAV aktual
    "fps": 24,
    "canvas": [1080, 1920]
  },
  "beats": [
    {
      "n": 3,
      "label": "angka kunci",
      "vo_text": "Dalam seminggu, sepuluh ribu peluru ditembakkan.",
      "start": 11.9,              // detik — dari Whisper
      "end": 15.2,
      "visual": {
        "type": "counter",        // counter | footage | photo | map | kinetic | insert
        "desc": "counter 0→10.000 peluru",
        "src": "clips/counter-peluru.mp4",   // opsional
        "anchor": { "event": "landing", "at": 15.2 }
      },
      "kinetic_text": "10.000 peluru",
      "anchors": [
        { "at": 13.1, "event": "counter_start", "note": "0,3 dtk sebelum VO sebut angka" },
        { "at": 15.2, "event": "counter_landing", "note": "tepat saat VO selesai sebut angka" }
      ],
      "subtitle": {
        "start": 11.9, "end": 15.2,
        "lines": ["Dalam seminggu, sepuluh ribu", "peluru ditembakkan."]
      }
    }
  ]
}
```

## Aturan anchor (wajib)

Setiap `visual` dengan `type` berikut WAJIB punya anchor:

| Tipe | Aturan |
|---|---|
| `counter` (animasi angka) | `counter_start` = 0,3–0,5 dtk SEBELUM VO menyebut angka; `counter_landing` = TEPAT saat VO selesai menyebutnya. Durasi counter = selisih keduanya (dihitung, bukan fix). |
| `footage` / `photo` (ganti visual) | Cut HANYA di `start` beat (batas kalimat/topik VO). Dilarang cut di tengah kalimat. |
| `kinetic` (teks kinetik) | Muncul ±0,2 dtk dari timestamp kata yang ditonjolkan. |
| `insert` (sisipan animasi motion-studio) | `start`/`end` presisi dari beat sheet — durasi klip = `end - start`, bukan "5–10 detik". |
| `map` | Trigger saat VO menyebut lokasi; label muncul mengikuti elemen. |

**Dilarang:** visual event dengan durasi/himing tebakan ("sekitar 3 detik", "nanti diatur").
Bila timestamp tidak tersedia untuk suatu event → event itu belum siap di-build.

## Membangun

```bash
python3 scripts/beat_sheet.py av_script.md timestamps.json -o beat_sheet.json
```

Script mem-parsing kolom AUDIO/VISUAL/TEKS per beat, mencocokkan kata dengan
Whisper timestamps (fuzzy match per baris), menerapkan aturan anchor untuk
`[JANGKAR: ...]`, dan memecah subtitle per aturan 2 baris/42 char.

## Verifikasi

- [ ] Tiap beat punya `start < end`, dan beat berurutan tidak tumpang tindih.
- [ ] `end` beat terakhir ≈ `vo_duration` (±0,5 dtk).
- [ ] Setiap `[JANGKAR: ...]` di AV script punya entry di `anchors`.
- [ ] Tidak ada `visual.type` tanpa anchor yang diwajibkan tabel di atas.
