#!/usr/bin/env python3
"""Make frame 0 the thumbnail.

Feeds, WhatsApp, Slack and most players show the first frame as the preview
until the video plays. A black or white frame 0 reads as broken. The right fix
is designing frame 0 of the composition as the poster; this is the fallback
for an already-rendered master.

Usage:
  poster_frame.py VIDEO --image thumb.png --out OUT.mp4 [--frames 2]
  poster_frame.py VIDEO --from-time 11.9 --out OUT.mp4 [--frames 2]

--image      a designed thumbnail (scaled and center-cropped to the video size)
--from-time  reuse the strongest frame of the video itself as the poster
--frames     how many leading frames to replace (default 2; timing and audio
             are untouched, so sync is preserved)
Requires ffmpeg and ffprobe on PATH. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def size(video: Path) -> tuple[int, int]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-print_format", "json",
         "-show_entries", "stream=width,height", str(video)],
        check=True, capture_output=True, text=True,
    ).stdout
    s = json.loads(out)["streams"][0]
    return int(s["width"]), int(s["height"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=Path)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--image", type=Path)
    src.add_argument("--from-time", type=float)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--frames", type=int, default=2)
    ap.add_argument("--crf", type=int, default=16)
    args = ap.parse_args()

    if args.out.resolve() == args.video.resolve():
        sys.exit("error: --out must differ from the input")
    w, h = size(args.video)
    with tempfile.TemporaryDirectory() as tmp:
        poster = args.image
        if poster is None:
            poster = Path(tmp) / "poster.png"
            subprocess.run(
                ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{args.from_time:.4f}",
                 "-i", str(args.video), "-frames:v", "1", str(poster)],
                check=True,
            )
        graph = (
            # Convert the RGB poster with the BT.709 matrix before overlaying; overlay's own
            # RGB->YUV conversion assumes BT.601 and would shift the poster's colors.
            f"[1:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,"
            f"scale=out_color_matrix=bt709:out_range=tv,format=yuv420p[p];"
            f"[0:v][p]overlay=0:0:enable='lt(n,{args.frames})':format=yuv420,format=yuv420p,"
            f"setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv[v]"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(args.video),
             "-i", str(poster), "-filter_complex", graph, "-map", "[v]", "-map", "0:a?",
             "-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf), "-pix_fmt", "yuv420p",
             "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
             "-c:a", "copy", "-movflags", "+faststart", str(args.out)],
            check=True,
        )
    print(args.out)


if __name__ == "__main__":
    main()
