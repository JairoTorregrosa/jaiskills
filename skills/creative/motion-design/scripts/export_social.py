#!/usr/bin/env python3
"""Export a finished master into share-ready files.

Usage:
  export_social.py MASTER.mp4 [--name NAME] [--out DIR] [--targets feed,whatsapp]
                   [--whatsapp-mb 175] [--crf 18]

Targets:
  feed      H.264 High, yuv420p BT.709 (converted and tagged), CRF (default 18),
            +faststart. Audio is copied when it is already AAC 48 kHz stereo,
            otherwise encoded once (AudioToolbox AAC when available).
            Safe for LinkedIn, X, Instagram, YouTube and Slack uploads.
  whatsapp  Two-pass H.264 sized under --whatsapp-mb (default 175 MB), video
            bitrate capped at 17 Mbit/s. For review cuts sent over WhatsApp.
  prores    ProRes 422 HQ .mov, for handing to an editor or re-grading.

The script never re-frames: design each aspect ratio natively instead of
cropping or padding a master made for another one.
Requires ffmpeg and ffprobe on PATH. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AUDIO_KBPS = 192
WHATSAPP_MAX_VIDEO_KBPS = 17_000


def probe(path: Path) -> dict:
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-print_format", "json",
            "-show_entries",
            "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,"
            "color_space,color_range,sample_rate,channels",
            str(path),
        ],
        check=True, capture_output=True, text=True,
    ).stdout
    data = json.loads(out)
    video = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    if audio is not None and "sample_rate" not in audio:
        audio = dict(audio, sample_rate="0")
    if video is None:
        sys.exit(f"error: {path} has no video stream")
    return {
        "duration": float(data["format"]["duration"]),
        "size": int(data["format"].get("size", 0)),
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": video["r_frame_rate"],
        "pix_fmt": video.get("pix_fmt", ""),
        "color_space": video.get("color_space", "unknown"),
        "color_range": video.get("color_range", "unknown"),
        "has_audio": audio is not None,
        "audio_copyable": audio is not None and audio.get("codec_name") == "aac"
        and audio.get("sample_rate") == "48000" and int(audio.get("channels", 0)) == 2,
    }


def loudness(path: Path) -> tuple[float, float] | None:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn",
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summary = err[err.rfind("Summary:"):]
    i = re.search(r"\bI:\s+(-?[\d.]+)", summary)
    tp = re.search(r"Peak:\s+(-?[\d.]+)", summary)
    return (float(i.group(1)), float(tp.group(1))) if i and tp else None


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def color_args(info: dict) -> list[str]:
    """Convert to BT.709 limited range and tag it, which is what players assume for HD.

    Frames rendered from PNG/JPEG usually arrive untagged BT.601 or full-range yuvj420p;
    left alone they shift colours and crush or lift blacks on some players.
    """
    matrix = {"bt709": "bt709", "smpte170m": "bt601", "bt470bg": "bt601",
              "bt2020nc": "bt2020"}.get(info["color_space"], "bt601")
    full = info["color_range"] == "pc" or info["pix_fmt"].startswith("yuvj")
    vf = (f"scale=in_color_matrix={matrix}:out_color_matrix=bt709:"
          f"in_range={'full' if full else 'limited'}:out_range=limited,format=yuv420p,"
          "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv")
    return ["-vf", vf, "-colorspace", "bt709", "-color_primaries", "bt709",
            "-color_trc", "bt709", "-color_range", "tv"]


def aac_encoder() -> list[str]:
    """AudioToolbox AAC when available (macOS): ffmpeg's native encoder at 192-256k was
    measured adding ~2 dB of true-peak overs on bright mixes; aac_at kept the mastered peak."""
    encoders = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    if " aac_at " in encoders:
        return ["-c:a", "aac_at", "-b:a", f"{AUDIO_KBPS}k"]
    return ["-c:a", "aac", "-b:a", "320k"]


def audio_args(info: dict) -> list[str]:
    if not info["has_audio"]:
        return ["-an"]
    if info["audio_copyable"]:
        return ["-c:a", "copy"]  # re-encoding mastered AAC only adds loss and peak drift
    return [*aac_encoder(), "-ar", "48000", "-ac", "2"]


def export_feed(src: Path, dst: Path, info: dict, crf: int) -> None:
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
        "-map", "0:v:0", "-map", "0:a:0?",
        *color_args(info),
        "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
        "-profile:v", "high", "-pix_fmt", "yuv420p",
        "-maxrate", "25M", "-bufsize", "50M",
        *audio_args(info),
        "-movflags", "+faststart", str(dst),
    ])


def export_whatsapp(src: Path, dst: Path, info: dict, budget_mb: float) -> None:
    budget_kbit = budget_mb * 8 * 1000  # MB (10^6 bytes) -> kbit
    audio_kbps = AUDIO_KBPS if info["has_audio"] else 0
    video_kbps = int(budget_kbit / info["duration"] * 0.97) - audio_kbps  # 3% mux overhead
    video_kbps = min(video_kbps, WHATSAPP_MAX_VIDEO_KBPS)
    if video_kbps < 1500:
        sys.exit(
            f"error: {budget_mb} MB is too small for {info['duration']:.1f}s "
            f"({video_kbps} kbit/s video); shorten the cut or raise --whatsapp-mb"
        )
    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, "x264pass")
        common = [
            "-map", "0:v:0", *color_args(info), "-c:v", "libx264", "-preset", "slow",
            "-b:v", f"{video_kbps}k", "-maxrate", f"{int(video_kbps * 1.5)}k",
            "-bufsize", f"{video_kbps * 2}k", "-profile:v", "high", "-pix_fmt", "yuv420p",
            "-passlogfile", log,
        ]
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
             *common, "-pass", "1", "-an", "-f", "null", os.devnull])
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
             *common, "-pass", "2", "-map", "0:a:0?", *audio_args(info),
             "-movflags", "+faststart", str(dst)])
    size_mb = dst.stat().st_size / 1e6
    if size_mb > budget_mb:
        sys.exit(f"error: {dst.name} is {size_mb:.1f} MB, over the {budget_mb} MB budget")


def export_prores(src: Path, dst: Path, info: dict) -> None:
    run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
        "-map", "0:v:0", "-map", "0:a:0?",
        "-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le",
        *(["-c:a", "pcm_s16le"] if info["has_audio"] else ["-an"]),
        str(dst),
    ])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("master", type=Path)
    ap.add_argument("--name", help="output base name (default: master file stem)")
    ap.add_argument("--out", type=Path, help="output directory (default: next to master)")
    ap.add_argument("--targets", default="feed,whatsapp", help="comma list: feed,whatsapp,prores")
    ap.add_argument("--whatsapp-mb", type=float, default=175.0)
    ap.add_argument("--crf", type=int, default=18)
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            sys.exit(f"error: {tool} not found on PATH")
    src = args.master.resolve()
    info = probe(src)
    out = (args.out or src.parent).resolve()
    out.mkdir(parents=True, exist_ok=True)
    name = args.name or src.stem
    fmt = f"{info['width']}x{info['height']}"

    made = []
    for target in [t.strip() for t in args.targets.split(",") if t.strip()]:
        if target == "feed":
            dst = out / f"{name}-{fmt}-feed.mp4"
            export_feed(src, dst, info, args.crf)
        elif target == "whatsapp":
            dst = out / f"{name}-{fmt}-whatsapp.mp4"
            export_whatsapp(src, dst, info, args.whatsapp_mb)
        elif target == "prores":
            dst = out / f"{name}-{fmt}-prores.mov"
            export_prores(src, dst, info)
        else:
            sys.exit(f"error: unknown target {target!r}")
        made.append(dst)

    for dst in made:
        i = probe(dst)
        line = (f"{dst}  {i['size'] / 1e6:.1f} MB  {i['width']}x{i['height']}  "
                f"{i['duration']:.2f}s")
        lv = loudness(dst) if i["has_audio"] else None
        if lv:
            line += f"  {lv[0]:.1f} LUFS  TP {lv[1]:.1f} dBTP"
            if lv[1] > -1.0:
                line += "  WARN true peak over -1 dBTP after re-encode: master at -1.5 (audio_check.py --normalize)"
        else:
            line += "  no audio"
        print(line)


if __name__ == "__main__":
    main()
