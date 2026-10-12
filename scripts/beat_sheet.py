#!/usr/bin/env python3
"""beat_sheet.py — av_script.md + timestamps JSON -> beat_sheet.json.

Usage:
    python3 beat_sheet.py av_script.md timestamps.json [-o beat_sheet.json]

- Parsing kolom AUDIO / VISUAL / TEKS per BEAT.
- Mencocokkan kata tiap beat ke Whisper timestamps (fuzzy).
- Menerapkan aturan anchor untuk [JANGKAR: ...].
- Memecah subtitle per aturan 2 baris x 42 char.
Lihat references/beat-sheet.md untuk skema output.
"""
import argparse
import difflib
import json
import re
import sys

MAX_LINE = 42
LEAD_IN = 0.4          # counter mulai 0,4 dtk sebelum angka disebut
KINETIC_TOL = 0.2


def norm(w):
    return re.sub(r"[^\w]", "", w.lower())


def parse_av(path):
    with open(path) as f:
        text = f.read()
    beats = []
    # blok BEAT n | label ... sampai BEAT berikutnya / akhir
    parts = re.split(r"^BEAT\s+(\d+)\s*\|\s*(.+)$", text, flags=re.M)
    # parts[0] = preamble, lalu grup (n, label, body)
    for i in range(1, len(parts), 3):
        n, label, body = parts[i], parts[i + 1].strip(), parts[i + 2]
        cols = {}
        for key in ("AUDIO", "VISUAL", "TEKS"):
            m = re.search(rf"^{key}\s*:\s*(.+)$", body, flags=re.M)
            cols[key.lower()] = m.group(1).strip() if m else ""
        beats.append({"n": int(n), "label": label, **cols})
    return beats


def align_beat(beat_words, ts_words, start_idx):
    """Cocokkan beat_words ke ts_words[start_idx:]; kembalikan (s, e)."""
    rem = ts_words[start_idx:]
    rem_norm = [norm(w["word"]) for w in rem]
    bn = [norm(w) for w in beat_words]
    bn = [w for w in bn if w]
    if not bn or not rem_norm:
        return None
    sm = difflib.SequenceMatcher(None, rem_norm, bn, autojunk=False)
    block = sm.find_longest_match(0, len(rem_norm), 0, len(bn))
    if block.size < max(2, len(bn) // 3):
        return None
    s = start_idx + block.a
    # rentang = awal block .. awal block + panjang beat (clamp ke sisa)
    e = min(s + len(bn), len(ts_words)) - 1
    return (s, max(e, s))


def find_phrase(phrase_words, ts_words, lo, hi):
    """Cari frasa (list kata) dalam rentang [lo, hi]; kembalikan (s, e) atau None."""
    pn = [norm(w) for w in phrase_words if norm(w)]
    if not pn:
        return None
    window = [norm(ts_words[i]["word"]) for i in range(lo, hi + 1)]
    for i in range(len(window) - len(pn) + 1):
        if all(difflib.SequenceMatcher(None, window[i + j], pn[j]).ratio() > 0.8
               for j in range(len(pn))):
            return (lo + i, lo + i + len(pn) - 1)
    return None


def split_subtitle(words):
    """words: list {word,start,end} -> list kartu {start,end,lines[]}."""
    cards, cur, cur_len = [], [], 0
    last_gap = 0
    for idx, w in enumerate(words):
        wl = len(w["word"]) + 1
        # kandidat potong di jeda alami bila kartu kepanjangan
        if cur and cur_len + wl > MAX_LINE * 2:
            # potong di batas klausa terakhir bila ada
            cut = len(cur)
            for j in range(len(cur) - 1, 0, -1):
                if cur[j]["brk"]:
                    cut = j + 1
                    break
            cards.append(make_card(cur[:cut]))
            cur, cur_len = cur[cut:], sum(len(x["word"]) + 1 for x in cur[cut:])
        gap = w["start"] - words[idx - 1]["end"] if idx else 0
        cur.append({**w, "brk": gap > 0.35 or w["word"].endswith((",", ".", "!", "?"))})
        cur_len += wl
    if cur:
        cards.append(make_card(cur))
    # gabung kartu terlalu pendek (<0,8 dtk) ke berikut dalam beat yang sama
    merged = []
    for c in cards:
        if merged and (merged[-1]["end"] - merged[-1]["start"]) < 0.8:
            p = merged[-1]
            p["end"] = c["end"]
            p["lines"] = rewrap(p["lines_text"] + " " + c["lines_text"])
        else:
            merged.append(c)
    return [{"start": c["start"], "end": c["end"], "lines": c["lines"]} for c in merged]


def make_card(words):
    text = " ".join(w["word"] for w in words)
    return {"start": words[0]["start"], "end": words[-1]["end"],
            "lines": rewrap(text), "lines_text": text}


def rewrap(text):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > MAX_LINE:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines[:2]


def detect_visual_type(visual):
    v = visual.lower()
    # [JANGKAR: angka ...] selalu berarti counter — prioritas tertinggi
    if re.search(r"\[jangkar:\s*angka", v):
        return "counter"
    if "peta" in v or "map" in v:
        return "map"
    if any(k in v for k in ("footage", "video")):
        return "footage"
    if "foto" in v or "photo" in v:
        return "photo"
    if any(k in v for k in ("animasi", "diagram")):
        return "insert"
    return "kinetic"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("av_script")
    ap.add_argument("timestamps")
    ap.add_argument("-o", "--output", default="beat_sheet.json")
    ap.add_argument("--vo-file", default="", help="nama file VO untuk meta")
    args = ap.parse_args()

    beats = parse_av(args.av_script)
    if not beats:
        sys.exit("ERROR: tidak ada BEAT terparse dari " + args.av_script)
    with open(args.timestamps) as f:
        ts = json.load(f)

    out_beats, idx, warnings = [], 0, []
    for b in beats:
        awords = b["audio"].split()
        m = align_beat(awords, ts, idx)
        if m is None:
            warnings.append(f"BEAT {b['n']}: tidak cocok ke timestamps — pakai estimasi")
            # fallback: lanjutkan dari idx, durasi proporsional 3 dtk
            s = e = idx
            start = ts[s]["start"] if s < len(ts) else 0
            end = start + 3.0
            wrange = []
        else:
            s, e = m
            start, end = ts[s]["start"], ts[e]["end"]
            wrange = ts[s:e + 1]
            idx = e + 1

        vtype = detect_visual_type(b["visual"])
        anchors = []
        # jangkar angka: [JANGKAR: angka "frasa yang diucapkan"]
        jm = re.search(r'\[JANGKAR:\s*([^\]]+)\]', b["visual"])
        if jm and vtype == "counter":
            spec = jm.group(1)
            qm = re.search(r'"([^"]+)"', spec)
            if qm and wrange:
                ph = find_phrase(qm.group(1).split(), ts, s, e)
                if ph:
                    ns, ne = ts[ph[0]]["start"], ts[ph[1]]["end"]
                    anchors.append({"at": round(ns - LEAD_IN, 3), "event": "counter_start",
                                    "note": f"{LEAD_IN} dtk sebelum VO sebut angka"})
                    anchors.append({"at": round(ne, 3), "event": "counter_landing",
                                    "note": "tepat saat VO selesai sebut angka"})
                else:
                    warnings.append(f"BEAT {b['n']}: frasa jangkar tidak ketemu "
                                    f"'{qm.group(1)}' — anchor dilewati")
            elif wrange:
                # fallback: tengah beat
                mid = (start + end) / 2
                anchors.append({"at": round(mid - LEAD_IN, 3), "event": "counter_start",
                                "note": "fallback tengah beat (frasa tidak dispesifikasi)"})
                anchors.append({"at": round(mid, 3), "event": "counter_landing",
                                "note": "fallback tengah beat"})
        if vtype in ("footage", "photo"):
            anchors.append({"at": round(start, 3), "event": "cut",
                            "note": "cut di batas kalimat/topik VO"})
        # teks kinetik: jangkarkan ke kata yang cocok bila ketemu
        kinetic_at = round(start, 3)
        if b["teks"] and wrange:
            ph = find_phrase(b["teks"].split(), ts, s, e)
            if ph:
                kinetic_at = round(ts[ph[0]]["start"], 3)

        subs = split_subtitle(wrange) if wrange else []
        out_beats.append({
            "n": b["n"], "label": b["label"],
            "vo_text": b["audio"],
            "start": round(start, 3), "end": round(end, 3),
            "visual": {"type": vtype, "desc": re.sub(r"\[JANGKAR:[^\]]+\]", "",
                                                    b["visual"]).strip(),
                       "anchor": anchors[0] if anchors else None},
            "kinetic_text": b["teks"],
            "kinetic_at": kinetic_at,
            "anchors": anchors,
            "subtitle": subs[0] if len(subs) == 1 else subs,
            "estimated": m is None,
        })

    vo_dur = ts[-1]["end"] if ts else 0
    out = {"meta": {"title": "", "vo_file": args.vo_file,
                    "vo_duration": round(vo_dur, 3), "fps": 24,
                    "canvas": [1080, 1920]},
           "beats": out_beats}
    with open(args.output, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"OK: {len(out_beats)} beats -> {args.output} (VO {vo_dur:.1f}s)")
    for w in warnings:
        print("WARN:", w)


if __name__ == "__main__":
    main()
