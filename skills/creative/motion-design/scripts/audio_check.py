#!/usr/bin/env python3
"""Measure and fix loudness for social delivery.

Usage:
  audio_check.py FILE [--target -14] [--tp -1]            measure and judge
  audio_check.py FILE --normalize OUT [--target -14] [--tp -1]

FILE may be audio or video. Measure prints integrated loudness (LUFS), loudness
range (LU) and true peak (dBTP) and exits 1 when integrated loudness is more
than 1 LU from the target or the true peak is above the ceiling.

--normalize applies gain and a 4x-oversampled (192 kHz) limiter with its ceiling at --norm-tp
(default -1.5 dBTP, headroom for the inter-sample peaks every later AAC re-encode
adds), iterating until the EBU R128 meter reads the target. It keeps the video
stream untouched, writes stereo 48 kHz audio (AAC 256k, AudioToolbox when available, in video containers, 24-bit
WAV for .wav), and re-measures the result.

Defaults (-14 LUFS integrated, -1 dBTP) are the common target for feed video;
check references/delivery.md before shipping to a platform with other specs.
Requires ffmpeg on PATH. Standard library only.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def measure(path: Path) -> dict:
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"error: ffmpeg could not read audio from {path}\n{proc.stderr[-800:]}")
    summary = proc.stderr[proc.stderr.rfind("Summary:"):]

    def grab(label: str) -> float:
        m = re.search(rf"{label}:\s+(-?[\d.]+|-inf)", summary)
        if not m:
            sys.exit(f"error: could not parse {label!r} from ebur128 output")
        return float("-inf") if m.group(1) == "-inf" else float(m.group(1))

    return {"I": grab(r"\bI"), "LRA": grab("LRA"), "TP": grab("Peak")}


def judge(m: dict, target: float, tp: float) -> bool:
    ok_i = abs(m["I"] - target) <= 1.0
    ok_tp = m["TP"] <= tp
    print(f"integrated {m['I']:.1f} LUFS ({'ok' if ok_i else f'target {target}'})  "
          f"range {m['LRA']:.1f} LU  "
          f"true peak {m['TP']:.1f} dBTP ({'ok' if ok_tp else f'ceiling {tp}'})")
    return ok_i and ok_tp


def aac_encoder() -> list[str]:
    """AudioToolbox AAC when available (macOS): ffmpeg's native encoder at 192-256k was
    measured adding ~2 dB of true-peak overs on bright mixes; aac_at kept the mastered peak."""
    encoders = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    if " aac_at " in encoders:
        return ["-c:a", "aac_at", "-b:a", "256k"]
    return ["-c:a", "aac", "-b:a", "320k"]


def normalize(src: Path, dst: Path, target: float, tp: float) -> None:
    """Gain plus a 4x-oversampled limiter, iterated until the EBU R128 meter reads the target.

    Measuring and correcting with the same meter the check uses avoids loudnorm's quirks:
    its linear mode silently falls back to dynamic (pumping) when peaks are in the way, and its
    integrated reading can differ from ebur128 by more than half an LU on short, dynamic mixes.
    Output is stereo 48 kHz; mono sources are upmixed first.
    """
    ceiling = 10 ** ((tp - 0.2) / 20)
    gain = target - measure(src)["I"]
    with tempfile.TemporaryDirectory() as tmp:
        pre = Path(tmp) / "pre.wav"
        for _ in range(6):
            subprocess.run(
                ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-vn", "-ac", "2",
                 "-af", f"volume={gain:.2f}dB,aresample=192000,alimiter=limit={ceiling:.5f}:attack=1.5"
                 f":release=80:level=disabled,aresample=48000", "-c:a", "pcm_f32le", str(pre)],
                check=True,
            )
            off = target - measure(pre)["I"]
            if abs(off) <= 0.2:
                break
            gain += off
        else:
            print("note: could not reach the target within 6 passes; the limiter is working hard, "
                  "lower the loudest section in the mix instead", file=sys.stderr)
        if dst.suffix.lower() in {".wav", ".flac", ".aiff"}:
            codec = ["-c:a", "pcm_s24le"] if dst.suffix.lower() == ".wav" else []
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(pre), *codec, str(dst)]
        else:
            cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src), "-i", str(pre),
                   "-map", "0:v:0?", "-map", "1:a:0", "-c:v", "copy", *aac_encoder(),
                   "-movflags", "+faststart", str(dst)]
        subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", type=Path)
    ap.add_argument("--target", type=float, default=-14.0, help="integrated LUFS target")
    ap.add_argument("--tp", type=float, default=-1.0, help="true-peak ceiling in dBTP")
    ap.add_argument("--norm-tp", type=float, default=-1.5, help="true-peak target when normalizing")
    ap.add_argument("--normalize", type=Path, metavar="OUT")
    args = ap.parse_args()

    before = measure(args.file)
    ok = judge(before, args.target, args.tp)
    if args.normalize:
        normalize(args.file, args.normalize, args.target, args.norm_tp)
        print(f"wrote {args.normalize}")
        ok = judge(measure(args.normalize), args.target, args.tp)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
