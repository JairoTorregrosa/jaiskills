#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy>=1.26"]
# ///
"""Procedural sound effects in pure numpy: deterministic, 48 kHz, 24-bit WAV.

Usage:
  sfx.py OUT_DIR                          write all sounds
  sfx.py OUT_DIR --only whoosh,hit        write some of them
  sfx.py OUT_DIR --seed 11 --peak -3      another variation, peak level in dBFS

Sounds: whoosh, hit, riser, tadum, glitch, click, blip, pop, swell, braam.

Placement (see references/audio.md for the sync rules):
  whoosh  loudest at 0.65 of its length: start it at cut - 0.65 * 0.7 s to peak on the cut
  hit     on the exact impact frame; layer a swell ending on it for reveals
  riser   ends hard on the drop or reveal
  tadum   two-hit logo sting, second hit 0.37 s after the first
  braam   low detuned pad for a title card

Import it for custom cue beds:
  from sfx import whoosh, hit, mix, write
  write("bed.wav", mix([(0.55, whoosh(), -4), (1.0, hit(), 0)], 3.0))

Normalize by peak, not LUFS: files under 0.4 s have no gating block and read
around -70 LUFS. The -3 dBFS default leaves room for inter-sample peaks.
Never synthesize continuous ambience beds with this: periodic pads read as
nausea to viewers. Accents only.
"""

from __future__ import annotations

import argparse
import os
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def T(d):
    return np.arange(int(d * SR)) / SR


def env(t, a=0.005, d=0.3):
    """Linear attack, exponential decay."""
    return np.where(t < a, t / a, np.exp(-(t - a) / d))


def glide(f, t):
    """Phase for a time-varying pitch."""
    return 2 * np.pi * np.cumsum(np.broadcast_to(f, t.shape)) / SR


def filt(x, gain):
    """Zero-phase FFT filter; gain(freqs_hz) -> 0..1."""
    return np.fft.irfft(np.fft.rfft(x) * gain(np.fft.rfftfreq(len(x), 1 / SR)), len(x))


def hp(x, fc):
    return filt(x, lambda f: 1 / (1 + (fc / (f + 1e-9)) ** 4))


def lp(x, fc):
    return filt(x, lambda f: 1 / (1 + (f / fc) ** 4))


def norm(x):
    return x / (np.abs(x).max() + 1e-12)


def pan(x, p):
    """p: -1 (left) .. 1 (right), scalar or per-sample array; constant-power."""
    th = (np.asarray(p) + 1) * np.pi / 4
    return np.stack([x * np.cos(th), x * np.sin(th)], 1)


def band_noise(d, fc, bw=1.0, n=2048):
    """Noise band centred on fc(u), u = 0..1 over d seconds; bw in octaves."""
    hop, f, w = n // 4, np.fft.rfftfreq(n, 1 / SR), np.hanning(n)
    out = np.zeros(int(d * SR) + 2 * n)
    for i in range(0, int(d * SR) + n, hop):
        mag = np.exp(-0.5 * (np.log2((f + 1) / fc(min(i / (d * SR), 1))) / (bw / 2)) ** 2)
        out[i:i + n] += np.fft.irfft(mag * np.exp(2j * np.pi * rng.random(len(f))), n) * w
    return norm(out[n // 2:n // 2 + int(d * SR)])


def whoosh(d=0.7, f0=250, f1=3000, peak=0.65):
    """Pass-by: slow approach, fast exit, pans left to right."""
    t = T(d)
    k = np.log(0.5) / np.log(peak)
    s = np.sin(np.pi * (t / d) ** k) ** 2
    y = band_noise(d, lambda u: f0 * (f1 / f0) ** np.sin(np.pi * u ** k), bw=1.2)
    return pan(y * s, np.linspace(-0.7, 0.7, len(t)))


def hit(d=1.2, f=48, click=0.35):
    """Impact: sub sine with a fast pitch drop plus a noise transient."""
    t = T(d)
    body = np.sin(glide(f * (1 + 3 * np.exp(-t / 0.03)), t)) * env(t, 0.002, d / 4)
    snap = hp(rng.standard_normal(len(t)), 1500) * np.exp(-t / 0.012)
    return np.tanh(1.6 * (body + click * norm(snap))) * np.clip((d - t) / 0.05, 0, 1)


def riser(d=2.5, f0=300, f1=9000):
    """Noise band and tone sweeping up with accelerating tremolo; ends hard."""
    t = T(d)
    x = t / d
    tone = np.sin(glide(110 * 8 ** x, t)) * (0.5 + 0.5 * np.sin(glide(4 + 20 * x ** 2, t)))
    y = 0.6 * band_noise(d, lambda u: f0 * (f1 / f0) ** u) * x ** 2 + 0.4 * tone * x ** 1.5
    return y * np.clip((d - t) / 0.01, 0, 1)


def tadum(gap=0.37):
    """Two-hit logo sting; the second hit is lower and longer."""
    return mix([(0, hit(0.6, 62, 0.4), 0), (gap, hit(1.8, 44, 0.5), 1.5)], gap + 1.8)


def glitch(d=0.35, slice_ms=(12, 35)):
    """Random slices of square wave, crushed noise, silence and stutter."""
    out, prev = [], np.zeros(1)
    while sum(map(len, out)) < d * SR:
        n = int(rng.uniform(*slice_ms) * SR / 1000)
        t = T(n / SR)
        s = [np.sign(np.sin(2 * np.pi * rng.uniform(200, 3000) * t)),
             np.round(rng.standard_normal(n) * 3) / 3, np.zeros(n), np.resize(prev, n)][rng.integers(4)]
        out.append(s * 0.6)
        prev = s
    y = np.concatenate(out)[:int(d * SR)]
    return np.repeat(y[::6], 6)[:len(y)]  # sample-and-hold: 8 kHz aliasing crunch


def click(f=3200):
    t = T(0.03)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.004) + 0.3 * rng.standard_normal(len(t)) * np.exp(-t / 0.0008)


def blip(f=880, up=1.5):
    t = T(0.14)
    return np.sin(glide(f * (1 + (up - 1) * np.clip(t / 0.04, 0, 1)), t)) * env(t, 0.003, 0.045)


def pop():
    t = T(0.09)
    return np.sin(glide(260 + 900 * np.exp(-t / 0.01), t)) * env(t, 0.001, 0.025)


def swell(d=1.5):
    """Reversed cymbal: rises into the next hit."""
    t = T(d)
    return (hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / (d / 3)))[::-1]


def drone(d=4, f=55, a=0.6, r=1.0):
    """Detuned saw pad; a lower f and shorter attack make a braam."""
    t = T(d)
    saw = sum(np.sin(2 * np.pi * f * k * c * t) / k for k in range(1, 12) for c in (0.997, 1, 1.003))
    return lp(saw, 900) * np.clip(t / a, 0, 1) * np.clip((d - t) / r, 0, 1)


def mix(cues, d):
    """cues: [(t_seconds, signal, gain_db)] -> stereo array of shape (n, 2)."""
    out = np.zeros((int(d * SR), 2))
    for t0, s, g in cues:
        s = s if s.ndim == 2 else np.stack([s, s], 1)
        i = int(round(t0 * SR))
        n = max(0, min(len(s), len(out) - i))
        out[i:i + n] += s[:n] * 10 ** (g / 20)
    return out


def write(path, x, peak_db=-3.0):
    """24-bit PCM WAV, peak-normalized to peak_db dBFS."""
    x = x.reshape(len(x), -1)
    x = x / (np.abs(x).max() + 1e-12) * 10 ** (peak_db / 20)
    pcm = (x * (2 ** 23 - 1)).astype("<i4")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(3)
        w.setframerate(SR)
        w.writeframes(np.frombuffer(pcm.tobytes(), np.uint8).reshape(-1, 4)[:, :3].tobytes())


SOUNDS = {
    "whoosh": whoosh, "hit": hit, "riser": riser, "tadum": tadum, "glitch": glitch,
    "click": click, "blip": blip, "pop": pop, "swell": swell,
    "braam": lambda: drone(2.5, 41, 0.05, 1.8),
}


def main() -> None:
    global rng
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_dir")
    ap.add_argument("--only", help="comma-separated sound names")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--peak", type=float, default=-3.0, help="peak level in dBFS")
    args = ap.parse_args()

    names = args.only.split(",") if args.only else list(SOUNDS)
    unknown = [n for n in names if n not in SOUNDS]
    if unknown:
        ap.error(f"unknown sound(s): {', '.join(unknown)}; choose from {', '.join(SOUNDS)}")
    rng = np.random.default_rng(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    for name in names:
        sig = SOUNDS[name]()
        path = os.path.join(args.out_dir, f"{name}.wav")
        write(path, sig, args.peak)
        print(f"{path}  {len(sig) / SR:.2f}s")


if __name__ == "__main__":
    main()
