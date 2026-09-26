#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.1"]
# ///
"""Look at a video the way a director does: contact sheets, motion strips, stills.

Usage:
  contact_sheet.py sheet  VIDEO [--cols 4] [--rows 4] [--width 480] [--out sheet.png]
  contact_sheet.py strip  VIDEO --range 3.0:6.0 [--step 0.2] [--cols 6] [--out strip.png]
  contact_sheet.py frames VIDEO --at 0,1.5,12.25 [--out-dir stills/]

sheet   evenly spaced frames across the whole video, each labelled with its
        timestamp and frame number: the pacing and composition overview.
sheet also checks frame 0 (it becomes the feed preview when there is no
custom thumbnail) and flags flat frames (blank, black or white gaps).
strip   dense frames inside a time range: the tool for judging easing,
        overlap, text legibility and whether a hit lands on the beat.
frames  full-resolution stills at exact timestamps for close inspection.

Open the PNGs with an image viewer or the agent's image-reading tool and
critique them; a render nobody looked at is not done.
Requires ffmpeg and ffprobe on PATH; run with `uv run` or make it executable.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat

LABEL_H = 34
PAD = 6
FLAT_STDDEV = 4.0


def probe(video: Path) -> tuple[float, float]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-print_format", "json",
         "-show_entries", "stream=r_frame_rate:format=duration", str(video)],
        check=True, capture_output=True, text=True,
    ).stdout
    data = json.loads(out)
    num, den = data["streams"][0]["r_frame_rate"].split("/")
    return float(data["format"]["duration"]), float(num) / float(den)


def snap(t: float, fps: float) -> float:
    """Exact time of the frame nearest t, so labels name the frame actually shown."""
    return round(t * fps) / fps


def grab(video: Path, t: float, fps: float, width: int | None, dst: Path) -> Image.Image:
    vf = ["-vf", f"scale={width}:-2:flags=lanczos"] if width else []
    # An input seek returns the first frame with pts >= ss; aim a quarter frame early to land on
    # frame round(t * fps) instead of the one after it.
    ss = max(0.0, t - 0.25 / fps)
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{ss:.5f}",
         "-i", str(video), "-frames:v", "1", *vf, str(dst)],
        check=True,
    )
    return Image.open(dst).convert("RGB")


def is_flat(img: Image.Image) -> bool:
    return max(ImageStat.Stat(img.convert("L")).stddev) < FLAT_STDDEV


def label_font(size: int = 20) -> ImageFont.ImageFont:
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def tile(images: list[tuple[Image.Image, str, bool]], cols: int) -> Image.Image:
    w, h = images[0][0].size
    rows = (len(images) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + PAD) + PAD, rows * (h + LABEL_H + PAD) + PAD), (18, 18, 18))
    draw = ImageDraw.Draw(sheet)
    font = label_font()
    for i, (img, label, flagged) in enumerate(images):
        x = PAD + (i % cols) * (w + PAD)
        y = PAD + (i // cols) * (h + LABEL_H + PAD)
        sheet.paste(img, (x, y))
        color = (255, 90, 90) if flagged else (220, 220, 220)
        draw.text((x + 4, y + h + 6), label, fill=color, font=font)
    return sheet


def stamp(t: float, fps: float) -> str:
    return f"{int(t // 60):d}:{t % 60:05.2f}  f{round(t * fps)}"


def cmd_sheet(args: argparse.Namespace) -> None:
    duration, fps = probe(args.video)
    n = args.cols * args.rows - 1  # frame 0 takes the first cell
    times = [snap(duration * (i + 0.5) / n, fps) for i in range(n)]
    out = args.out or args.video.with_name(f"{args.video.stem}-sheet.png")
    with tempfile.TemporaryDirectory() as tmp:
        first = grab(args.video, 0.0, fps, args.width, Path(tmp) / "f0.png")
        if is_flat(first):
            print("WARN frame 0 is flat (blank/solid). It becomes the feed preview: "
                  "make frame 0 the thumbnail.", file=sys.stderr)
        tiles = []
        for i, t in enumerate(times):
            img = grab(args.video, t, fps, args.width, Path(tmp) / f"{i}.png")
            flat = is_flat(img)
            if flat:
                print(f"WARN flat frame at {t:.2f}s", file=sys.stderr)
            tiles.append((img, stamp(t, fps) + ("  FLAT" if flat else ""), flat))
        tile([(first, "frame 0 (preview)", is_flat(first))] + tiles, args.cols).save(out)
    print(out)


def cmd_strip(args: argparse.Namespace) -> None:
    duration, fps = probe(args.video)
    a, b = (float(x) for x in args.range.split(":"))
    b = min(b, duration - 1 / fps)
    times, t = [], a
    while t <= b + 1e-9:
        times.append(snap(t, fps))
        t += args.step
    out = args.out or args.video.with_name(f"{args.video.stem}-strip-{a:g}-{b:g}.png")
    with tempfile.TemporaryDirectory() as tmp:
        tiles = [(grab(args.video, t, fps, args.width, Path(tmp) / f"{i}.png"), stamp(t, fps), False)
                 for i, t in enumerate(times)]
    tile(tiles, args.cols).save(out)
    print(out)


def cmd_frames(args: argparse.Namespace) -> None:
    _, fps = probe(args.video)
    out_dir = args.out_dir or args.video.with_name(f"{args.video.stem}-stills")
    out_dir.mkdir(parents=True, exist_ok=True)
    for t in (snap(float(x), fps) for x in args.at.split(",")):
        dst = out_dir / f"{args.video.stem}-{t:08.3f}s.png"
        grab(args.video, t, fps, None, dst)
        print(dst)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sheet")
    s.add_argument("video", type=Path)
    s.add_argument("--cols", type=int, default=4)
    s.add_argument("--rows", type=int, default=4)
    s.add_argument("--width", type=int, default=480)
    s.add_argument("--out", type=Path)
    s.set_defaults(func=cmd_sheet)

    st = sub.add_parser("strip")
    st.add_argument("video", type=Path)
    st.add_argument("--range", required=True, help="start:end in seconds")
    st.add_argument("--step", type=float, default=0.2)
    st.add_argument("--cols", type=int, default=6)
    st.add_argument("--width", type=int, default=400)
    st.add_argument("--out", type=Path)
    st.set_defaults(func=cmd_strip)

    f = sub.add_parser("frames")
    f.add_argument("video", type=Path)
    f.add_argument("--at", required=True, help="comma list of seconds")
    f.add_argument("--out-dir", type=Path)
    f.set_defaults(func=cmd_frames)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
