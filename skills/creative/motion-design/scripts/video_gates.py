#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26"]
# ///
"""Mechanical gates for a finished video. Fails closed; taste is the critics' job.

Usage:
  video_gates.py VIDEO [--cues cues.json] [--lufs -14] [--tp -1] [--max-mb 180]
                       [--expect-duration 60] [--expect-size 1080x1350] [--allow-silent]

Checks (PASS / WARN / FAIL):
  format      H.264 High or Main, yuv420p, even dimensions, constant frame rate
  audio       present, AAC, 48 kHz, stereo
  faststart   moov atom before mdat (feeds start playing before full download)
  decode      a full decode produces no errors
  duration    matches --expect-duration within one frame (if given)
  size        file under --max-mb (if given); dimensions match --expect-size (if given)
  loudness    integrated LUFS within 1 LU of --lufs, true peak at or below --tp
  poster      frame 0 is not flat (it is the preview in feeds and chats)
  frozen      longest run of identical frames (holds without grain/boil read as a stall)
  tremolo     periodic loudness wobble under 8 Hz (a fake ambience bed that nauseates)
  cuts        with --cues: detected cuts vs the beat grid, offset in frames

Exit code 1 if any gate FAILs. Requires ffmpeg and ffprobe on PATH.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

RESULTS: list[tuple[str, str, str]] = []


def report(gate: str, status: str, detail: str) -> None:
    RESULTS.append((gate, status, detail))


def ffprobe(video: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(video)],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out)


def fps_of(stream: dict) -> float:
    num, den = stream["r_frame_rate"].split("/")
    return float(num) / float(den)


def check_format(info: dict) -> tuple[dict, float, float]:
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    fps = fps_of(v)
    problems = []
    if v.get("codec_name") != "h264":
        problems.append(f"codec {v.get('codec_name')} (want h264)")
    if v.get("profile") not in ("High", "Main", "Constrained Baseline"):
        problems.append(f"profile {v.get('profile')} (4:4:4 and 10-bit profiles fail on phones)")
    if v.get("pix_fmt") not in ("yuv420p",):
        problems.append(f"pix_fmt {v.get('pix_fmt')} (want yuv420p)")
    if int(v["width"]) % 2 or int(v["height"]) % 2:
        problems.append(f"odd dimensions {v['width']}x{v['height']}")
    avg = v.get("avg_frame_rate", "0/1").split("/")
    if float(avg[1]) and abs(float(avg[0]) / float(avg[1]) - fps) > 0.01:
        problems.append("variable frame rate")
    detail = f"{v.get('codec_name')} {v.get('profile')} {v.get('pix_fmt')} {v['width']}x{v['height']} @ {fps:g} fps"
    report("format", "FAIL" if problems else "PASS", "; ".join(problems) or detail)
    return v, fps, float(info["format"]["duration"])


def check_audio(info: dict, allow_silent: bool = False) -> bool:
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if a is None:
        if allow_silent:
            report("audio", "PASS", "no audio stream (silent by design)")
        else:
            report("audio", "FAIL", "no audio stream (silent videos lose the share; --allow-silent if intended)")
        return False
    problems = []
    if a.get("codec_name") != "aac":
        problems.append(f"codec {a.get('codec_name')}")
    if a.get("sample_rate") != "48000":
        problems.append(f"{a.get('sample_rate')} Hz")
    if int(a.get("channels", 0)) != 2:
        problems.append(f"{a.get('channels')} channel(s)")
    report("audio", "WARN" if problems else "PASS",
           "; ".join(problems) or f"aac {a.get('sample_rate')} Hz stereo")
    return True


def check_faststart(video: Path) -> None:
    with open(video, "rb") as fh:
        head = fh.read(4 * 1024 * 1024)
    moov, mdat = head.find(b"moov"), head.find(b"mdat")
    if moov == -1 and mdat == -1:
        report("faststart", "WARN", "atoms not found in the first 4 MB")
    elif moov != -1 and (mdat == -1 or moov < mdat):
        report("faststart", "PASS", "moov before mdat")
    else:
        report("faststart", "FAIL", "moov after mdat: re-mux with -movflags +faststart")


def check_decode(video: Path) -> None:
    err = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"],
                         capture_output=True, text=True).stderr.strip()
    report("decode", "FAIL" if err else "PASS", err.splitlines()[0] if err else "clean full decode")


def check_loudness(video: Path, lufs: float, tp: float) -> None:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-vn",
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    i = re.search(r"\bI:\s+(-?[\d.]+)", summary)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf)", summary)
    if not i or not p:
        report("loudness", "FAIL", "could not measure")
        return
    iv, pv = float(i.group(1)), float(p.group(1))
    ok = abs(iv - lufs) <= 1.0 and pv <= tp
    report("loudness", "PASS" if ok else "FAIL",
           f"{iv:.1f} LUFS (target {lufs}), true peak {pv:.1f} dBTP (ceiling {tp}); fix: audio_check.py --normalize")


def gray_frames(video: Path, width: int = 96) -> tuple[np.ndarray, int, int]:
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
         "-of", "csv=p=0", str(video)], check=True, capture_output=True, text=True).stdout.strip()
    w0, h0 = (int(x) for x in probe.split(",")[:2])
    h = max(2, round(h0 * width / w0 / 2) * 2)
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={width}:{h}:flags=area,format=gray",
         "-f", "rawvideo", "-"], check=True, capture_output=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, h, width).astype(np.int16)
    return frames, width, h


def check_frames(video: Path, fps: float) -> np.ndarray:
    frames, _, _ = gray_frames(video)
    if frames[0].std() < 4:
        report("poster", "FAIL", "frame 0 is flat (black/white/solid): design it as the thumbnail "
               "or run poster_frame.py")
    else:
        report("poster", "PASS", f"frame 0 has content (std {frames[0].std():.0f})")
    diffs = np.abs(np.diff(frames, axis=0)).mean(axis=(1, 2))
    still = diffs < 0.05
    longest, run = 0, 0
    for s in still:
        run = run + 1 if s else 0
        longest = max(longest, run)
    secs = (longest + 1) / fps if longest else 0.0
    report("frozen", "WARN" if secs > 2.0 else "PASS",
           f"longest identical run {secs:.2f} s" + (" (add grain/boil or a slow drift to holds)" if secs > 2.0 else ""))
    return diffs


def check_tremolo(video: Path) -> None:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "8000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float64) / 32768.0
    if x.size < 8000 * 4:
        report("tremolo", "PASS", "audio too short to judge")
        return
    hop = 80  # 10 ms envelope
    env = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, mode="valid")[::hop] + 1e-12)
    env = env - env.mean()
    spec = np.abs(np.fft.rfft(env * np.hanning(env.size))) ** 2
    freqs = np.fft.rfftfreq(env.size, d=hop / 8000)
    band = (freqs > 0.2) & (freqs < 8.0)
    total = spec[freqs > 0.2].sum()
    if total <= 0:
        report("tremolo", "PASS", "silent")
        return
    k = int(np.argmax(spec * band))

    def energy(f: float) -> float:
        i = int(np.argmin(np.abs(freqs - f)))
        return float(spec[max(0, i - 2):i + 3].sum())

    share = energy(freqs[k]) / total
    # Rhythm (hits, kicks, strums) has sharp attacks; a synthesized bed that swells and fades
    # does not. Measure the 99th percentile of loudness rises per 50 ms.
    slow = np.sqrt(np.convolve(x ** 2, np.ones(400) / 400, mode="valid")[::400] + 1e-12)
    db = 20 * np.log10(slow + 1e-6)
    rises = np.diff(db)[db[1:] > db.max() - 40]
    attack = float(np.percentile(rises[rises > 0], 99)) if (rises > 0).any() else 0.0
    smooth = share > 0.18 and attack < 6.0
    if smooth:
        report("tremolo", "WARN", f"smooth loudness wobble at {freqs[k]:.2f} Hz holds {share:.0%} of envelope "
               "energy: a swelling bed like this causes nausea; replace it with silence or real one-shots")
    elif share > 0.18:
        report("tremolo", "PASS", f"rhythmic pulse at {freqs[k]:.2f} Hz ({share:.0%}) with sharp attacks "
               f"({attack:.0f} dB/50 ms): beat-driven, fine")
    else:
        report("tremolo", "PASS", f"no dominant slow wobble (max {share:.0%} at {freqs[k]:.2f} Hz)")


def load_beats(path: Path, duration: float) -> np.ndarray:
    cues = json.loads(path.read_text())
    if cues.get("beats"):
        return np.array(cues["beats"], dtype=float)
    bpm, offset = float(cues["bpm"]), float(cues.get("offset", 0.0))
    return np.arange(offset, duration, 60.0 / bpm)


def check_cuts(video: Path, cues: Path, fps: float, duration: float) -> None:
    # Scene score > 0.30 flags hard cuts in footage and most graphics (validated on past films).
    # A looser spike rule flagged title slams and lyric-card impacts as cuts, so it stays strict;
    # a cut between two flat grounds of similar luma can score ~0.1 and be missed: check such seams
    # in a motion strip. Cuts in the first 0.1 s are the poster stamp, not edits.
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-vf",
                          "select='gt(scene,0.30)',showinfo", "-an", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    raw_cuts = [float(m) for m in re.findall(r"pts_time:([\d.]+)", err) if float(m) >= 0.1]
    cuts: list[float] = []
    for c in raw_cuts:  # a flash frame reads as two cuts; keep the first of any cluster
        if not cuts or c - cuts[-1] > 3.0 / fps:
            cuts.append(c)
    if not cuts:
        report("cuts", "PASS", "no hard cuts detected")
        return
    beats = load_beats(cues, duration)
    offsets = [(c, (c - beats[np.argmin(np.abs(beats - c))]) * fps) for c in cuts]
    off = [f"{c:.2f}s({o:+.1f}f)" for c, o in offsets if abs(o) > 1.0]
    report("cuts", "WARN" if off else "PASS",
           f"{len(cuts)} cuts; off-beat by >1 frame: {', '.join(off[:12])}" if off
           else f"{len(cuts)} cuts, all within 1 frame of a beat")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    ap.add_argument("--cues", type=Path, help="cues.json with beats[] or bpm + offset")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--max-mb", type=float)
    ap.add_argument("--expect-duration", type=float)
    ap.add_argument("--expect-size", help="WIDTHxHEIGHT")
    ap.add_argument("--allow-silent", action="store_true", help="silent by design (a loop, an overlay, a draft)")
    args = ap.parse_args()

    info = ffprobe(args.video)
    v, fps, duration = check_format(info)
    has_audio = check_audio(info, args.allow_silent)
    check_faststart(args.video)
    check_decode(args.video)
    if args.expect_duration is not None:
        ok = abs(duration - args.expect_duration) <= 1.0 / fps + 1e-3
        report("duration", "PASS" if ok else "FAIL", f"{duration:.3f} s (expected {args.expect_duration})")
    size_mb = args.video.stat().st_size / 1e6
    if args.max_mb is not None:
        report("size", "PASS" if size_mb <= args.max_mb else "FAIL", f"{size_mb:.1f} MB (budget {args.max_mb})")
    if args.expect_size:
        ok = f"{v['width']}x{v['height']}" == args.expect_size
        report("dimensions", "PASS" if ok else "FAIL", f"{v['width']}x{v['height']} (expected {args.expect_size})")
    if has_audio:
        check_loudness(args.video, args.lufs, args.tp)
        check_tremolo(args.video)
    check_frames(args.video, fps)
    if args.cues:
        check_cuts(args.video, args.cues, fps, duration)

    width = max(len(g) for g, _, _ in RESULTS)
    for gate, status, detail in RESULTS:
        print(f"{status:4}  {gate:<{width}}  {detail}")
    sys.exit(1 if any(s == "FAIL" for _, s, _ in RESULTS) else 0)


if __name__ == "__main__":
    main()
