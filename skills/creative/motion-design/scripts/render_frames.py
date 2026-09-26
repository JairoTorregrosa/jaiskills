#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.49"]
# ///
"""render_frames.py: deterministic HTML -> video. Headless Chromium seeks each frame, screenshots it, pipes it to ffmpeg.

Page contract (see references/stack-html-frames.md; examples/gsap-page.html implements it):
  window.__ready    Promise that resolves once fonts, images and the timeline are built
  window.__seek(t)  put the page in its state at t seconds; pure function of t; may return a Promise
  window.__meta     optional {width, height, fps, duration}; CLI flags override it
  window.__RENDER__ set to true by this script, so the page can skip its live-preview loop

  render_frames.py scene.html --out out.mp4 [--fps 30] [--duration 6] [--range 0:3] [--scale 2] [--workers 4] [--audio a.wav]
  render_frames.py scene.html --sheet 0,0.5,1,2 --out sheet.png   # contact sheet of chosen times (a:b = every frame in a:b)
  render_frames.py scene.html --stills 0 --out stills/            # full-res PNGs (t=0 is the thumbnail)
  render_frames.py scene.html --transparent --out overlay.mov     # ProRes 4444 with alpha (.webm = VP9 alpha)
First run: uv run --with playwright playwright install chromium
Pass --gpu for WebGL/WebGPU/canvas-heavy pages (Metal via ANGLE on macOS; the headless default is software).
"""
import argparse, base64, math, os, pathlib, subprocess, sys, tempfile
from concurrent.futures import ProcessPoolExecutor
from playwright.sync_api import sync_playwright

FLAGS = ["--force-color-profile=srgb", "--hide-scrollbars", "--mute-audio", "--allow-file-access-from-files",
         "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
         "--disable-backgrounding-occluded-windows", "--font-render-hinting=none"]
GPU = {"darwin": ["--use-angle=metal", "--ignore-gpu-blocklist", "--enable-gpu-rasterization"],
       "linux": ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"]}  # linux+NVIDIA: --use-angle=vulkan


class Session:
    """One browser + page: loaded, fonts ready, returns encoded frames for any t."""
    def __init__(self, a):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(args=FLAGS + (GPU.get(sys.platform, []) if a.gpu else []))
        self.page = self.browser.new_page(viewport={"width": a.width, "height": a.height}, device_scale_factor=a.scale)
        self.page.on("pageerror", lambda e: print(f"[page error] {e}", file=sys.stderr))
        self.page.add_init_script("window.__RENDER__ = true")
        src = a.html if "://" in a.html else pathlib.Path(a.html).resolve().as_uri()
        self.page.goto(src, wait_until="load")
        self.meta = self.page.evaluate("""async () => { await (window.__ready || 0); await document.fonts.ready;
            if (typeof window.__seek !== 'function') throw new Error('page has no window.__seek(t)');
            return window.__meta || {}; }""")
        self.cdp = self.page.context.new_cdp_session(self.page)
        if a.transparent:  # transparent page background; the page itself must not paint an opaque body
            self.cdp.send("Emulation.setDefaultBackgroundColorOverride", {"color": {"r": 0, "g": 0, "b": 0, "a": 0}})
        fmt = {"format": "png"} if (a.transparent or a.png) else {"format": "jpeg", "quality": 95}
        # clip.scale must equal deviceScaleFactor, or CDP returns CSS-pixel frames; optimizeForSpeed = ~4x faster PNG
        self.shot = {**fmt, "optimizeForSpeed": True, "clip": {"x": 0, "y": 0, "width": a.width, "height": a.height, "scale": a.scale}}

    def grab(self, t, label=None):
        self.page.evaluate("async ([t, l]) => { await window.__seek(t); if (l !== null) window.__label(l); }", [t, label])
        return base64.b64decode(self.cdp.send("Page.captureScreenshot", self.shot)["data"])

    def close(self):
        self.browser.close(); self.pw.stop()


def encoder(a, out):
    ext = pathlib.Path(out).suffix.lower()
    if a.transparent and ext == ".mov":
        enc = ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-vendor", "apl0"]
    elif a.transparent:
        enc = ["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24", "-row-mt", "1"]
    else:  # RGB -> BT.709 limited-range YUV, tagged, so players do not shift the colours
        enc = ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"
               "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv",
               "-c:v", "libx264", "-preset", a.preset, "-crf", str(a.crf), "-movflags", "+faststart"]
    return subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps),
                             "-i", "-", *enc, out], stdin=subprocess.PIPE)


def render_chunk(job, s=None):  # runs in its own process when --workers > 1
    a, f0, f1, out = job
    s = s or Session(a); ff = encoder(a, out)
    for f in range(f0, f1):
        ff.stdin.write(s.grab(f / a.fps))
    ff.stdin.close(); s.close()
    return ff.wait()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("html"); p.add_argument("--out", default="out.mp4")
    p.add_argument("--fps", type=float); p.add_argument("--duration", type=float)
    p.add_argument("--width", type=int); p.add_argument("--height", type=int)
    p.add_argument("--range", help="a:b seconds"); p.add_argument("--scale", type=float, default=1, help="deviceScaleFactor")
    p.add_argument("--workers", type=int, default=1); p.add_argument("--crf", type=int, default=18)
    p.add_argument("--preset", default="slow"); p.add_argument("--audio"); p.add_argument("--gpu", action="store_true")
    p.add_argument("--png", action="store_true", help="lossless PNG capture (slower, cleanest)")
    p.add_argument("--transparent", action="store_true"); p.add_argument("--sheet"); p.add_argument("--stills")
    p.add_argument("--cols", type=int, default=4); p.add_argument("--cell", type=int, default=480)
    a = p.parse_args()
    want = (a.width, a.height); a.width, a.height = a.width or 1920, a.height or 1080
    s = Session(a); m = s.meta  # page metadata fills in what the CLI left out; reopen if the viewport was wrong
    size = (want[0] or m.get("width", a.width), want[1] or m.get("height", a.height))
    if size != (a.width, a.height):
        a.width, a.height = size; s.close(); s = Session(a)
    a.fps, a.duration = a.fps or m.get("fps", 30), a.duration or m.get("duration")
    if not (a.duration or a.range or a.sheet or a.stills):
        sys.exit("need --duration, --range or window.__meta.duration")
    t0, t1 = map(float, a.range.split(":")) if a.range else (0.0, a.duration or 0)
    f0, f1 = round(t0 * a.fps), round(t1 * a.fps)

    if a.sheet or a.stills:
        spec = a.sheet or a.stills
        if ":" in spec:
            x, y = map(float, spec.split(":")); ts = [i / a.fps for i in range(round(x * a.fps), round(y * a.fps) + 1)]
        else:
            ts = [float(v) for v in spec.split(",")]
        if a.stills:
            os.makedirs(a.out, exist_ok=True); s.shot = {**s.shot, "format": "png"}; s.shot.pop("quality", None)
            for t in ts:
                pathlib.Path(a.out, f"t{t:06.3f}.png").write_bytes(s.grab(t))
        else:  # label each cell in-page, tile with ffmpeg
            s.page.evaluate("""() => { const d = document.createElement('div'); d.style.cssText = 'position:fixed;left:8px;top:8px;'
                + 'z-index:2147483647;font:600 22px ui-monospace,monospace;background:#000c;color:#fff;padding:2px 8px';
                document.documentElement.append(d); window.__label = s => d.textContent = s; }""")
            cols = min(a.cols, len(ts)); rows = math.ceil(len(ts) / cols)
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-i", "-", "-vf",
                                   f"scale={a.cell}:-2,tile={cols}x{rows}:padding=4", "-frames:v", "1", a.out], stdin=subprocess.PIPE)
            for t in ts:
                ff.stdin.write(s.grab(t, f"{t:.3f}s f{round(t * a.fps)}"))
            ff.stdin.close(); ff.wait()
        s.close(); print(a.out); return

    video = a.out if not a.audio else a.out + ".noaudio" + pathlib.Path(a.out).suffix
    if a.workers <= 1:
        assert render_chunk((a, f0, f1, video), s) == 0, "ffmpeg failed"
    else:  # contiguous frame ranges -> one segment per worker -> lossless concat
        s.close(); tmp = tempfile.mkdtemp(prefix="frames-"); n = a.workers; step = math.ceil((f1 - f0) / n)
        jobs = [(a, f0 + i * step, min(f1, f0 + (i + 1) * step), f"{tmp}/seg{i:03d}{pathlib.Path(a.out).suffix}")
                for i in range(n) if f0 + i * step < f1]
        with ProcessPoolExecutor(len(jobs)) as ex:
            assert all(rc == 0 for rc in ex.map(render_chunk, jobs)), "a worker failed"
        pathlib.Path(tmp, "list.txt").write_text("".join(f"file '{j[3]}'\n" for j in jobs))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
                        "-c", "copy", "-movflags", "+faststart", video], check=True)
    if a.audio:  # audio is cut to the same range as the video
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-ss", str(t0), "-t", str(t1 - t0), "-i", a.audio,
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "libopus" if a.out.endswith(".webm") else "aac",
                        "-b:a", "192k", "-shortest",
                        "-movflags", "+faststart", a.out], check=True)
        os.remove(video)
    print(f"{a.out}  {f1 - f0} frames @ {a.fps:g} fps  {round(a.width * a.scale)}x{round(a.height * a.scale)}")


if __name__ == "__main__":
    main()
