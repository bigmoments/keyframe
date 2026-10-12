#!/usr/bin/env python3
"""whisper_timestamps.py — WAV voiceover -> JSON word timestamps (master clock).

Usage:
    python3 whisper_timestamps.py <vo.wav> [--model small] [--lang id] [-o timestamps.json]

Output JSON: [{"word": str, "start": float, "end": float}, ...]  (detik)

Model default: model lokal di <skill>/models/faster-whisper-small bila ada
(jarang gagal, tanpa unduh); bila tidak ada, "small" dari HuggingFace (fallback: base).
Bahasa default: indonesian.
Butuh: .venv/bin/python (faster-whisper + av==12.3.0 terpin di venv skill)
"""
import argparse
import json
import os
import sys

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_MODEL = os.path.join(SKILL_DIR, "models", "faster-whisper-small")


def default_model():
    # Model lokal selalu menang bila lengkap — berlaku global untuk semua chat/
    # worker tanpa perlu tahu apa-apa. Tanpa ini, tiap side chat memicu unduh
    # HuggingFace (~2KB/s di environment ini = praktis gagal).
    if os.path.isfile(os.path.join(LOCAL_MODEL, "model.bin")):
        return LOCAL_MODEL
    return "small"


def main():
    ap = argparse.ArgumentParser(description="VO wav -> word timestamps (faster-whisper)")
    ap.add_argument("wav", help="file WAV voiceover")
    ap.add_argument("--model", default=None,
                    help="model whisper: path lokal atau nama HF "
                         "(default: model lokal bila ada, else 'small')")
    ap.add_argument("--lang", default="id", help="kode bahasa (default: id)")
    ap.add_argument("-o", "--output", default=None, help="file JSON output (default: stdout)")
    ap.add_argument("--no-word-ts", action="store_true",
                    help="matikan word timestamps (fallback segment-level)")
    args = ap.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("ERROR: faster-whisper belum terinstall. Jalankan: pip install faster-whisper")

    model_name = args.model or default_model()
    print(f"model: {model_name}", file=sys.stderr)
    try:
        model = WhisperModel(model_name, device="cpu", compute_type="int8")
    except Exception as e:
        if model_name != "base":
            print(f"WARN: model '{model_name}' gagal ({e}); fallback ke 'base'",
                  file=sys.stderr)
            model = WhisperModel("base", device="cpu", compute_type="int8")
        else:
            raise

    segments, info = model.transcribe(
        args.wav,
        language=args.lang,
        word_timestamps=not args.no_word_ts,
    )

    words = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                words.append({
                    "word": w.word.strip(),
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                })
        else:
            # fallback: segment-level bila word timestamps tidak tersedia
            words.append({
                "word": seg.text.strip(),
                "start": round(seg.start, 3),
                "end": round(seg.end, 3),
            })

    # buang entri kosong
    words = [w for w in words if w["word"]]

    out = json.dumps(words, ensure_ascii=False, indent=1)
    if args.output:
        with open(args.output, "w") as f:
            f.write(out)
        print(f"OK: {len(words)} kata -> {args.output} "
              f"(durasi audio {words[-1]['end']:.1f}s)" if words else "OK: kosong")
    else:
        print(out)


if __name__ == "__main__":
    main()
