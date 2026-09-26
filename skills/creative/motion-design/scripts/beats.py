#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["librosa>=0.11", "numpy>=1.26"]
# ///
"""Fit a constant beat grid to a song: BPM, first-beat offset, beats, onsets.

Usage:
  beats.py SONG.wav [--fps 30] [--beats-per-bar 4] [--out beats.json]

Writes JSON with bpm, offset (s), beats[] (the fitted grid over the whole song),
downbeats[] (a guess: the bar position with the most onset energy; confirm it
against the song's first section), onsets[] and the fit residual. The file is a valid --cues input
for video_gates.py and the tempo block of the cue sheet in references/audio.md.

Why not librosa's defaults: 23 ms frames and a quantized tempo (117.45 BPM on a
120 BPM test bed) with beats landing 17-35 ms after the attack. This uses a
256-sample hop, a least-squares constant grid and shifts it onto backtracked
onsets (tested: 120.01 BPM, 1.5 ms residual). For swing, rubato or sparse intros,
use beat_this raw beats with the same grid fit.
"""

from __future__ import annotations

import argparse
import json

import librosa
import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("song")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--beats-per-bar", type=int, default=4)
    ap.add_argument("--out", help="write JSON here instead of stdout")
    args = ap.parse_args()

    y, sr = librosa.load(args.song, sr=44100, mono=True)
    hop = 256
    env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    _, bf = librosa.beat.beat_track(onset_envelope=env, sr=sr, hop_length=hop)
    beats = librosa.frames_to_time(bf, sr=sr, hop_length=hop)
    if len(beats) < 4:
        raise SystemExit("error: fewer than 4 beats detected; is this a rhythmic track?")
    period, offset = np.polyfit(np.arange(len(beats)), beats, 1)
    resid = beats - (offset + period * np.arange(len(beats)))
    onsets = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=hop, units="time", backtrack=True)
    lag = float(np.median([onsets[np.argmin(np.abs(onsets - b))] - b for b in beats])) if len(onsets) else 0.0
    offset = (offset + lag + period / 2) % period - period / 2  # first grid beat nearest t=0

    duration = len(y) / sr
    first = int(np.ceil(-offset / period))
    grid = [offset + i * period for i in range(first, int((duration - offset) / period) + 1)]
    # Downbeat guess: the bar position whose beats carry the most onset energy (accents, kicks).
    strength = env[np.clip(librosa.time_to_frames(np.array(grid), sr=sr, hop_length=hop), 0, len(env) - 1)]
    phase = int(np.argmax([strength[p::args.beats_per_bar].sum() for p in range(args.beats_per_bar)]))
    out = {
        "bpm": round(60 / period, 2),
        "offset": round(offset, 4),
        "beats_per_bar": args.beats_per_bar,
        "fps": args.fps,
        "frames_per_beat": round(args.fps * period, 3),
        "attack_lag_ms": round(1000 * lag, 1),
        "resid_ms": round(1000 * float(np.abs(resid).mean()), 1),
        "beats": [round(b, 4) for b in grid],
        "downbeats": [round(b, 4) for b in grid[phase::args.beats_per_bar]],
        "onsets": np.round(onsets, 3).tolist(),
    }
    text = json.dumps(out, indent=1)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text + "\n")
        print(f"wrote {args.out}: {out['bpm']} BPM, offset {out['offset']} s, residual {out['resid_ms']} ms")
    else:
        print(text)


if __name__ == "__main__":
    main()
