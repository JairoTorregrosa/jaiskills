#!/usr/bin/env python3
"""Word timings -> phrase-aware caption cards (SRT) that respect reading speed.

Usage:
  captions.py WORDS.json OUT.srt [--max-chars 32] [--max-cps 17] [--lines 2]

WORDS.json holds {"words": [{"text", "start", "end"}, ...]} in seconds: the
output of forced alignment, TTS with-timestamps, or whisper (see
references/audio.md). Cards break at sentence ends, pauses and full cards; each
two-line card splits where the lines balance, never after an article,
preposition or conjunction. A card holds long enough to read (17 chars/s is the
Spanish subtitle limit, 20 for English) and ends at least 2 frames (at 30 fps) before the next.

Line length: 25-32 characters for 9:16, up to 32 for 4:5, up to 42 for 16:9.
Cards read too fast are printed with a warning. Standard library only.
"""

from __future__ import annotations

import argparse
import json

GLUE = set("a al de del el la los las lo un una unos y e o u en con por para que se no mi tu su "
           "the an of to and or in on at for with my your is".split())  # never end a line on these


def cards(words, maxc=32, lines=2, min_d=1.0, max_d=6.0, pause=0.5, gap=0.07, max_cps=17):
    groups, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        txt = " ".join(x["text"] for x in cur)
        if (not nxt or len(txt) + 1 + len(nxt["text"]) > maxc * lines  # card full
                or nxt["end"] - cur[0]["start"] > max_d  # card too long
                or nxt["start"] - w["end"] > pause  # speaker paused
                or (w["text"][-1] in ".?!:;" and len(txt) > maxc / 2)):  # sentence end
            groups.append(cur)
            cur = []
    out = []
    for j, g in enumerate(groups):
        toks = [x["text"] for x in g]
        txt = " ".join(toks)
        split = [txt]
        if len(txt) > maxc and len(toks) > 1:
            def cost(i, toks=toks):
                a, b = " ".join(toks[:i]), " ".join(toks[i:])
                return (abs(len(a) - len(b)) + 100 * (max(len(a), len(b)) > maxc)
                        - 8 * (toks[i - 1][-1] in ",.:;?!") + 10 * (toks[i - 1].lower() in GLUE))
            i = min(range(1, len(toks)), key=cost)
            split = [" ".join(toks[:i]), " ".join(toks[i:])]
        start = g[0]["start"]
        end = max(g[-1]["end"] + 0.2, start + min_d, start + len(txt) / max_cps)  # hold long enough to read
        if j + 1 < len(groups):
            end = min(end, groups[j + 1][0]["start"] - gap)
        out.append({"start": round(start, 3), "end": round(end, 3), "lines": split,
                    "cps": round(len(txt) / (end - start), 1)})
    return out


def stamp(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words")
    ap.add_argument("out")
    ap.add_argument("--max-chars", type=int, default=32)
    ap.add_argument("--max-cps", type=float, default=17)
    ap.add_argument("--lines", type=int, default=2)
    args = ap.parse_args()

    with open(args.words) as f:
        words = [w for w in json.load(f)["words"] if w["text"].strip()]
    cs = cards(words, maxc=args.max_chars, lines=args.lines, max_cps=args.max_cps)
    with open(args.out, "w") as f:
        f.write("\n".join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n" + "\n".join(c["lines"]) + "\n"
                          for i, c in enumerate(cs, 1)))
    for c in cs:
        flag = "  <-- too fast: cut words or extend the shot" if c["cps"] > args.max_cps else ""
        print(f"{c['start']:7.2f}-{c['end']:6.2f}  {c['cps']:4.1f} cps  {' / '.join(c['lines'])}{flag}")
    print(f"wrote {args.out} ({len(cs)} cards)")


if __name__ == "__main__":
    main()
