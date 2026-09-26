# Audio: music, voice, SFX, sync, mix

Verified 2026-09-26 against the live ElevenLabs docs + changelog (through `music_v2_5`, 2026-09-14), the ElevenLabs Python SDK 2.69.0 (method signatures introspected), ffmpeg 9.0.2 filter help, ACE-Step-1.5 @ `ca1e85f` (2026-08-29), Spotify/Apple Podcasts/EBU R128/AES TD1008 loudness docs, Netflix + BBC subtitle guides, ITU-R BT.1359-1, Apple TN2258, and the GitHub/PyPI state of mlx-audio 0.5.6, whisperX 3.8.6, whisper.cpp 1.9.4, librosa 1.0.0, beat_this 1.1.0, demucs 4.1.0, audio-separator 0.47.0 and Qwen3-TTS. Everything marked **tested** ran on an Apple Silicon Mac that day (ffmpeg 9.0.2, numpy 2.5, librosa 1.0.0, mlx-whisper 0.4.3). Sound is half the video: pick what leads before you animate anything.

## 1. Sound strategy by video type

| Type | Leads | Follows | Recipe |
|---|---|---|---|
| Music / lyric video | the song (make or pick it first, lock the file) | cuts on bars, text on sung words, sections on downbeats | song -> timing sheet (grid + words) -> animate; captions = lyrics |
| Explainer with VO | the VO (script -> TTS -> alignment) | picture beats on key words; music bed ducked; SFX on reveals only | VO 8-10 dB over the bed; bed ducked 10-15 dB under speech |
| Brand opener / sting (3-8 s) | the sting (whoosh -> hit -> tail) | logo moves land on the transients | build the sting first; logo "lands" on the hit frame; end on a button, not a fade |
| Data-art / generative | tempo grid of the track | data events quantized to the grid; SFX per event, quiet | value -> pitch/pan; cap density (~8 events/s); keep it loopable |
| Product demo / screen | VO or captions | UI clicks and cursor whooshes at -20 dB relative | quiet instrumental bed, never lyrics under speech |

- Sound on frame 0. No silent lead-in, no 8-bar intro; the hook lands within 1 s. Ask generators for "one bar pickup then vocals" and trim anything longer.
- Design for muted autoplay first (story readable without sound; captions per the policy in craft.md section 10), then make the sound reward unmuting (a groove, a sting, a VO with character). The famous "85% watch muted" is publishers quoted by Digiday in 2016, not a measurement (https://digiday.com/media/silent-world-facebook-video/); Verizon/Publicis 2019 found 69% watch sound-off in public, while TikTok/Kantar 2021 reports 88% of users call sound essential. Both are true: captions carry the story, sound carries the share.
- End with a button (hit + short tail) for shares; for loops make the last bar lead into the first.
- Lock the leader: hash the audio file or its word timings; any re-voice or re-generation means re-timing the picture (see `vo_mix-<hash>` trick, section 7).

## 2. ElevenLabs (API reference, verified)

Auth: `export ELEVENLABS_API_KEY=...` from a secret store; code reads `os.environ["ELEVENLABS_API_KEY"]`; never inline, log or commit it (`.env` gitignored). Base URL `https://api.elevenlabs.io`, header `xi-api-key`. SDKs: `uv add elevenlabs` (PyPI 2.69.0, `ElevenLabs()` reads the env var) / `npm i @elevenlabs/elevenlabs-js` (2.69.0). CLI: `brew install elevenlabs/tap/elevenlabs` (`@elevenlabs/cli` 1.4.0; every endpoint is a subcommand, `--dry-run`, `elevenlabs say "[whispers] hi"`; https://github.com/elevenlabs/cli). MCP: `elevenlabs-mcp` 0.12.2. Pricing is USD per usage (https://elevenlabs.io/pricing/api): TTS v3/multilingual $0.10 per 1K chars, flash $0.05 per 1K, music $0.15/min, SFX $0.12/min, Scribe v2 $0.22/h, forced alignment billed like STT. Music API: paid plans only.

### TTS models (https://elevenlabs.io/docs/overview/models)

| model_id | langs | max chars | use |
|---|---|---|---|
| `eleven_v3` | 70+ | 5,000 | most expressive, audio tags, GA since 2026-02; no request stitching |
| `eleven_multilingual_v2` | 29 | 10,000 | API default; stable long-form narration; supports `previous_text`/`next_text` |
| `eleven_flash_v2_5` | 32 | 40,000 | ~75 ms, half price; number normalization off by default (write numbers as words) |
| `eleven_v3_conversational` | 70+ | - | realtime agents, not video |

`eleven_turbo_v2(_5)` are deprecated (use flash); v1 models were removed 2026-07-09 (https://elevenlabs.io/docs/changelog/2026/6/8).
`voice_settings`: `stability` (0.5), `similarity_boost` (0.75), `style` (0; >0 adds latency), `use_speaker_boost` (true), `speed` 0.7-1.2 (1.0). Other body fields: `seed` (best-effort determinism), `language_code`, `previous_text`/`next_text` or `previous_request_ids` (max 3; from the `request-id` header), `apply_text_normalization` auto|on|off, `pronunciation_dictionary_locators`. `output_format` query: `mp3_44100_128` default; `mp3_44100_192` (Creator+), `pcm_48000`/`wav_48000` (44.1 kHz+ PCM/WAV need Pro), `opus_48000_*` (https://elevenlabs.io/docs/api-reference/text-to-speech/convert).

v3 prompting (https://elevenlabs.io/docs/overview/capabilities/text-to-speech/best-practices): no SSML `<break>`; use `...`, CAPS for emphasis and tags: `[whispers] [laughs] [sighs] [exhales] [sarcastic] [curious] [excited] [crying] [mischievously] [shouts] [clears throat] [pause]`, sound tags `[applause] [explosion] [swallows]`, experimental `[sings] [strong X accent]`. Stability modes Creative (expressive, can hallucinate) / Natural / Robust (stable but less responsive to tags). Use an IVC or a designed voice (PVCs are not tuned for v3). Multi-speaker: `POST /v1/text-to-dialogue` (`inputs:[{text, voice_id}]`, <= 10 voices, keep <= 2,000 chars; `/with-timestamps` adds `voice_segments`).

Line-by-line VO with timestamps (**production pattern**, one request per line so lines can be re-timed and re-voiced independently):

```bash
curl -sS -X POST "https://api.elevenlabs.io/v1/text-to-speech/$VOICE_ID/with-timestamps?output_format=mp3_44100_192" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"text":"Ana y Beto se postularon al mismo trabajo.","model_id":"eleven_multilingual_v2","seed":7,
       "voice_settings":{"stability":0.5,"similarity_boost":0.8,"style":0.15,"use_speaker_boost":true,"speed":1.05}}' \
  > L1.json && jq -r .audio_base64 L1.json | base64 -d > L1.mp3
```

Response: `{audio_base64, alignment:{characters[], character_start_times_seconds[], character_end_times_seconds[]}, normalized_alignment}`. Characters -> words, placed at `t0` on the timeline:

```python
def words_from_chars(al, t0=0.0):
    out, cur, s, e = [], "", None, None
    for c, c0, c1 in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if c.isspace():
            if cur: out.append({"text": cur, "start": round(t0 + s, 3), "end": round(t0 + e, 3)}); cur = ""
            continue
        if not cur: s = c0
        cur += c; e = min(c1, c0 + 0.3)   # the last char absorbs trailing silence: clamp it
    if cur: out.append({"text": cur, "start": round(t0 + s, 3), "end": round(t0 + e, 3)})
    return out
```

SDK equivalent: `ElevenLabs().text_to_speech.convert_with_timestamps(voice_id=..., text=..., model_id=..., output_format=..., voice_settings={...}, seed=7)`.

### Music (https://elevenlabs.io/docs/api-reference/music/compose)

- Models `music_v1`, `music_v2` (2026-06-15), `music_v2_5` (2026-09-14). **API default is still `music_v1`: always pass `model_id`.** Endpoints: `POST /v1/music` (audio), `/v1/music/detailed` (multipart: JSON metadata + audio), `/stream`, `/v1/music/plan` (prompt -> plan), `/upload` + inpainting, `/video-to-music` (<= 10 videos, <= 600 s), `/stem-separation` (ZIP).
- Length 3 s-10 min via `music_length_ms` (prompt mode only; the capabilities page still says 5 min). `force_instrumental` (prompt only). `seed` is rejected with `prompt`, fine with a plan (production passed it in the raw HTTP body; the SDK's `compose_detailed` has no `seed` arg, use `compose` or raw HTTP). `output_format` default `auto` = `mp3_48000_192` for v2; `mp3_48000_320` and pcm exist, no wav.
- v2/v2.5 plans are **chunks** (v1 `sections` schema errors on v2): `{"chunks":[{"text":"[Chorus]\n¡Vente, vente pa'l parche!\n{band drops out}","duration_ms":8889,"positive_styles":[...],"negative_styles":[...],"context_adherence":"high"}]}`. <= 30 chunks, `text` <= 6,132 chars: section name in `[ ]`, one lyric per line, vocal sounds in `( )`, performance cues in `{ }`. Styles in English; lyrics any language (https://elevenlabs.io/docs/eleven-api/guides/how-to/music/composition-plans). v2 always enforces chunk durations.
- Make every chunk a whole number of bars: `duration_ms = bars * beats_per_bar * 60000 / BPM` and put the BPM in the styles ("2/4 cumbia groove 108 BPM"): 108 BPM -> 4 bars = 8889 ms, 5 bars = 11111 ms (**production**). Put the full global style block on chunk 1 and a short reminder + local styles on later chunks; negatives kill genre drift ("reggaeton", "autotune", "EDM drop", "English lyrics"; "vocals, singing, spoken word" for scores).
- Artist names, song titles or copyrighted lyrics -> HTTP error `detail.status == "bad_prompt"` with `detail.data.prompt_suggestion` (plans: `bad_composition_plan`). Write phonetic spellings for brand names the singer must pronounce ("Clod Comiúniti") and display the real spelling on screen.

```python
# signatures checked against elevenlabs 2.69.0; returns MultipartResponse(.json, .audio, .song_id)
import json
from elevenlabs.client import ElevenLabs          # reads ELEVENLABS_API_KEY
el = ElevenLabs()
r = el.music.compose_detailed(composition_plan=json.load(open("plan.json")), model_id="music_v2_5",
                              with_timestamps=True, output_format="mp3_48000_192")
open("take.mp3", "wb").write(r.audio); json.dump(r.json, open("take.json", "w"), ensure_ascii=False)
words = [w for w in r.json.get("words_timestamps", []) if not w["word"].startswith(("{", "[", "("))]
```

`words_timestamps` items are `{word, start_ms, end_ms}`; direction tokens (`{spoken,`, `[Intro]`) come back with 0 ms, drop them. Measured on a real take: word starts within 15 ms median (p90 56 ms) of a whisper+CTC alignment, but `end_ms` is 150-360 ms early on sustained vowels, so extend ends to the next word or the vocal-stem offset. A 60 s song came back in ~10 s. Generate 2-3 seeds per plan and pick by ear + ASR lyric recall.
Terms (https://elevenlabs.io/eleven-music-model-specific-terms, updated 2026-05): free plan has no downloads and requires attribution; Starter+ no attribution; streaming-platform rights need Creator+; self-serve commercial use excludes film, TV, radio and studio games (Enterprise only); prompts may not name artists, songs, labels or include substantial existing lyrics (https://elevenlabs.io/music-terms).

### Sound effects, alignment, STT, voices

```bash
# SFX: text 0.5-30 s, prompt_influence 0-1 (default 0.3), loop (v2 only), model eleven_text_to_sound_v2
curl -sS -X POST "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_192" -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" -d '{"text":"deep smooth cinematic whoosh, airy, no impact","duration_seconds":1.5,"prompt_influence":0.6}' -o whoosh.mp3
# Forced alignment: known text -> word + char times. Response {characters:[{text,start,end}], words:[{text,start,end,loss}], loss}
curl -sS https://api.elevenlabs.io/v1/forced-alignment -H "xi-api-key: $ELEVENLABS_API_KEY" -F file=@vo.wav -F text="$(cat script.txt)" > fa.json
# Speech-to-text (Scribe v2): words[] = {text, start, end, type: word|spacing|audio_event, speaker_id, logprob}
curl -sS https://api.elevenlabs.io/v1/speech-to-text -H "xi-api-key: $ELEVENLABS_API_KEY" -F model_id=scribe_v2 \
  -F file=@vo.wav -F language_code=es -F timestamps_granularity=word -F tag_audio_events=false > stt.json
```

- SFX cost 40 credits/s when duration is set (https://elevenlabs.io/docs/overview/capabilities/sound-effects). Prompt like a sound designer: source + material + space + length + "no impact/no music" exclusions. Generate 2 variants each and **measure them**: one generated `pop_soft` came back at -58.6 LUFS (silent) in production.
- Scribe v2 (`scribe_v1` removed 2026-07-09): `diarize`, `num_speakers` <= 32, `keyterms` (+20%), `source_url` accepts YouTube/TikTok. Forced alignment limits: 10 h audio / 675k chars (https://elevenlabs.io/docs/api-reference/forced-alignment/create).
- Voice design: `POST /v1/text-to-voice/design` `{voice_description, model_id: eleven_ttv_v3|eleven_multilingual_ttv_v2, text (100-1000 chars) | auto_generate_text, seed, guidance_scale}` -> `previews[{audio_base_64, generated_voice_id}]`; save with `POST /v1/text-to-voice {voice_name, voice_description, generated_voice_id}`. Library: `GET /v1/shared-voices?language=es&accent=...&search=...`, add with `POST /v1/voices/add/{public_user_id}/{voice_id}` (not on free tier). Clean a noisy recording: `POST /v1/audio-isolation` (field `audio`).

## 3. Local and free alternatives

**Music: ACE-Step 1.5** (MIT; https://github.com/ACE-Step/ACE-Step-1.5; 10 s-10 min, 50+ lyric languages, MLX backend on Apple Silicon; XL 4B DiT variants since 2026-04 need >= 12-20 GB).

```bash
git clone https://github.com/ACE-Step/ACE-Step-1.5.git && cd ACE-Step-1.5 && uv sync   # Python 3.11-3.12; models auto-download
./start_gradio_ui_macos.sh            # or ./start_api_server_macos.sh (MLX); `uv run acestep` elsewhere; `python cli.py` = wizard
```

Scripted generation (production, 16 GB M1 Pro): `AceStepHandler().initialize_service(config_path="acestep-v15-turbo", device="auto")`, `LLMHandler().initialize(lm_model_path="acestep-5Hz-lm-1.7B", backend="mlx")`, then `generate_music(dit, llm, params=GenerationParams(task_type="text2music", caption=..., lyrics="[Verse]\n...\n[Chorus]\n..." or "[Instrumental]", vocal_language="es", bpm=150, keyscale="D major", timesignature="4", duration=22, inference_steps=8, guidance_scale=1.0, shift=3.0, seed=7), config=GenerationConfig(batch_size=1, use_random_seed=False, seeds=[7], audio_format="wav"), save_dir=...)`. Turbo: 8 steps, guidance 1.0; base/sft: ~50 steps, guidance ~7. Measured: 22 s clip in 50 s of pipeline (~106 s with overhead), 62 s song in 142 s, first model load ~2 min; output 48 kHz WAV peak-normalized to -1 dB (62 s song measured -14.1 LUFS, -0.8 dBTP). Caption (<= 512 chars) = comma-separated genre, instruments, vocal, BPM, key, mood; lyrics <= 4096 chars with `[Intro] [Verse] [Pre-Chorus] [Chorus] [Bridge] [Outro]` tags, 6-10 syllables per line; bpm 30-300. PyPI `ace-step` is the old v1: install from git. On 16 GB, drop the PyTorch DiT decoder copy and keep the MLX copy in bf16. ASR-check sung lyrics (measured 0.91 word recall on Spanish); expect brand names to be misheard.

**Voice: Qwen3-TTS on MLX** (Apache-2.0 code and weights, 10 languages incl. Spanish, clones from ~3 s of reference; official examples assume CUDA, so on a Mac use mlx-audio, MIT, 0.5.6, all five models on `mlx-community` in bf16 to 4-bit). Design one reference voice, then clone every line from it:

```python
from mlx_audio.tts.utils import load_model      # uv add mlx-audio  (0.5.1 in production)
d = load_model("mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16")
ref = next(d.generate("Reference sentence.", instruct="Adult male, calm documentary narrator, warm, measured pace", lang_code="english", temperature=0.7))
sf.write("ref.wav", np.asarray(ref.audio, dtype=np.float32), ref.sample_rate)   # import numpy as np, soundfile as sf
m = load_model("mlx-community/Qwen3-TTS-12Hz-1.7B-Base-bf16")
line = next(m.generate(text, ref_audio="ref.wav", ref_text="Reference sentence.", lang_code="english", temperature=0.6))
```

Render 2 takes per line and keep the one closest to the target duration; never `atempo` a Qwen clone (garbles it); pace by rewriting the text; verify every line with Whisper. Post: pad 50 ms head / 180 ms tail, `highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=9`, 48 kHz mono.

**Scratch VO: macOS `say`** (free, instant, deterministic; perfect for timing drafts):

```bash
say -v '?' | grep -E 'es_(MX|ES)'                        # Paulina, Mónica, Eddy, Flo...
say -v Paulina -r 170 -o vo.aiff "Cada punto es una respuesta real."
ffmpeg -i vo.aiff -ar 48000 -ac 1 -c:a pcm_s24le vo.wav   # say writes 22.05 kHz AIFF
```

**Alignment / STT (local)**: mlx-whisper 0.4.3 (CLI `mlx_whisper a.wav --model mlx-community/whisper-large-v3-turbo --language es --word-timestamps True -f json`); whisperX 3.8.6 (BSD-2; whisper + wav2vec2 CTC word alignment): `uvx whisperx a.wav --model large-v3 --language es --output_format json --output_dir out --device cpu --compute_type int8`; whisper.cpp 1.9.4 (`brew install whisper.cpp`, Metal; needs 16 kHz 16-bit WAV): `whisper-cli -m ggml-large-v3-turbo.bin -f in16k.wav -l es -ml 1 -sow -ojf -of out`; known text: `Qwen3-ForcedAligner-0.6B` in mlx-audio (11 languages incl. es, <= 5 min). stable-ts is archived (2.19.1): do not build on it. https://github.com/m-bain/whisperX, https://github.com/ggml-org/whisper.cpp, https://github.com/Blaizzy/mlx-audio

```python
# mlx-whisper word timestamps (tested: 10 s Spanish clip, 20 s wall incl. model load, cached large-v3-turbo)
import mlx_whisper   # uv run --no-project --with mlx-whisper python ...
r = mlx_whisper.transcribe("vo.wav", path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="es",
                           word_timestamps=True, condition_on_previous_text=False)
words = [{"text": w["word"].strip(), "start": w["start"], "end": w["end"]} for s in r["segments"] for w in s["words"]]
```

**Beats / onsets**: librosa 1.0.0 (2026-08; Python >= 3.12, keyword-only args; script in section 5). beat_this 1.1.0 (MIT, ISMIR 2024 SOTA; `pip install beat-this` + torch): `beat_this song.wav -o song.beats` or `File2Beats(checkpoint_path="final0", device="cpu", dbn=False)(path) -> (beats, downbeats)`; production ran `Audio2Beats(..., device="mps")` with CPU fallback (https://github.com/CPJKU/beat_this). Avoid madmom (PyPI 0.16.1 from 2018 breaks on numpy 2; models CC BY-NC-SA) and essentia for shipped code (AGPL-3.0; RhythmExtractor2013 needs 44.1 kHz).

**Stems**: demucs 4.1.0 (facebookresearch repo archived, continued at https://github.com/adefossez/demucs): `uvx --python 3.13 --with numpy --from demucs==4.1.0 demucs -n htdemucs --two-stems=vocals -d mps -o out song.mp3` -> `out/htdemucs/song/{vocals,no_vocals}.wav` (production: ~27 s for a 64 s song incl. env setup; `htdemucs_ft` ~4x slower, slightly better). python-audio-separator 0.47.0 (MIT, BS-RoFormer; MPS/CoreML): `pip install "audio-separator[cpu]"; audio-separator song.wav -m model_bs_roformer_ep_317_sdr_12.9755.ckpt --single_stem=Vocals --output_format=WAV --output_dir out`. ElevenLabs has `/v1/music/stem-separation` for its own songs. Use stems for: word alignment on the vocal, an instrumental bed under VO, onset detection on drums.

Other local TTS worth knowing: Kokoro-82M (Apache-2.0, tiny, Spanish `lang_code='e'`), Chatterbox (MIT, 23 languages, LatAm Spanish finetune, outputs watermarked), F5-TTS (weights CC-BY-NC: not for commercial posts); all but F5 run in mlx-audio.

## 4. Procedural SFX kit (numpy only, **tested**)

`scripts/sfx.py OUT_DIR` writes ten deterministic (seeded), 48 kHz, 24-bit WAV accents in ~0.3 s: `whoosh`, `hit`, `riser`, `tadum` (two-hit logo sting), `glitch`, `click`, `blip`, `pop`, `swell` (reversed cymbal), `braam`. `--only whoosh,hit` picks some, `--seed` gives a variation, and `from sfx import whoosh, hit, mix, write` builds a cue bed in code: `write("bed.wav", mix([(t, signal, gain_db), ...], duration))`. Use it for accents and scratch timing; for a finished piece, generated or recorded SFX usually sound richer (section 2), and continuous ambience should never be synthesized (periodic pads made viewers nauseous).

Tested 2026-09-26 (`scripts/sfx.py sfx`, ffprobe: all `pcm_s24le, 48000 Hz`, correct durations; spectrogram checked: whoosh arc, hit sub + transient, riser sweep, reversed-cymbal swell). Placement rules: a whoosh's loudest point is at `peak*d`, so start it at `cut - 0.65*d` to peak on the cut; put the `hit` at the exact impact frame; layer `swell` ending on the hit for reveals; `drone(2.5, 41, .05, 1.8)` is a braam. Normalize SFX by peak, not LUFS: files under 0.4 s measure -70 LUFS (no gating block) and sample-peak -1 dBFS still read +0.5 dBTP on the square-wave glitch, hence the -3 dBFS default.

## 5. Sync pipeline: grid, onsets, words -> cue sheet

1. **Pick BPM so a beat is a whole number of frames**: frames/beat = fps*60/BPM. 30 fps: 90, 100, 120, 150 BPM (20, 18, 15, 12 frames); 24 fps: 96, 120, 144; 60 fps: any divisor of 3600. Then `beat_i = offset + i*60/BPM`, `frame = round(t*fps)`, snap to subdivision s: `offset + round((t-offset)*BPM/60*s)/s*60/BPM`.
2. **Measure the rendered track anyway.** Generated songs do not start on t=0 (a 108 BPM ElevenLabs take measured 108.01 BPM, first downbeat 0.425 s). `scripts/beats.py` fits a constant grid with a fine hop and snaps it onto backtracked onsets (**tested** on synthetic 120 BPM beds: 120.0 BPM, 1.5 ms residual, accented downbeats found; librosa defaults gave 117.45 BPM with beats 17-35 ms late). Its JSON is a valid `--cues` file for `scripts/video_gates.py`:

```bash
scripts/beats.py song.wav --fps 30 --out beats.json   # bpm, offset, beats[] grid, downbeats[] guess, onsets[], residual
```

   For real songs with swing or sparse intros use `beat_this` (CPJKU) raw beats + the same grid fit; production measured 7.5 ms grid residual at 108 BPM, 98% inliers, and beat_this locking onto off-beats in a sparse intro, which the continuous grid overrode. Downbeats come from beat_this or from the song's section starts.
3. **Words.** Sources in order of trust: forced alignment of the known text (ElevenLabs FA, or CTC wav2vec2 as WhisperX does) > TTS `with-timestamps` > music `words_timestamps` > raw whisper. Whisper alone put line starts a median 330 ms off on sung Spanish; whisper + per-line CTC got 31 ms median vs an independent reference. Mark low-confidence words and eyeball a preview: render a sync-check video with a scrolling spectrogram strip, beat ticks, bar numbers and the karaoke burned in, and look at every flagged line.
4. **Cue sheet** (one JSON the renderer imports; everything in seconds, `frame` precomputed):

```json
{"version":1,"fps":30,"duration":16.0,"tempo":{"bpm":120,"offset":0.0,"beats_per_bar":4},
 "beats":[0.0,0.5,1.0],"downbeats":[0.0,2.0],"sections":[{"label":"intro","start":0,"end":8.0},{"label":"drop","start":8.0,"end":16.0}],
 "vo":{"file":"vo.wav","at":2.0},"words":[{"text":"Cada","start":2.0,"end":2.22,"line":"L1"}],
 "phrases":[{"start":2.0,"end":11.64,"text":"Cada punto es una respuesta real. ..."}],
 "cues":[{"kind":"sfx","name":"whoosh","t":1.05,"frame":32,"gain_db":-4},{"kind":"sfx","name":"hit","t":8.0,"frame":240,"gain_db":0},
         {"kind":"anim","target":"title","action":"slam","t":8.0,"frame":240}],
 "captions":[{"start":2.0,"end":4.12,"lines":["Cada punto es","una respuesta real."]}]}
```

5. **Consume it as a pure function of the frame** (Remotion, canvas, p5 alike; never Web Audio clocks):

```ts
const t = frame / fps;
const b = (t - tempo.offset) * tempo.bpm / 60;            // beats since the grid origin
const phase = b - Math.floor(b);                            // 0 on every beat
const pulse = Math.exp(-phase * 6);                         // decaying flash / scale bump per beat
const downbeat = Math.floor(b) % tempo.beats_per_bar === 0;
const since = (c: {frame: number}) => (frame - c.frame) / fps;   // drive springs from a cue
const word = words.findLast(w => w.start <= t && t < w.end + 0.15); // karaoke highlight
```

   Anticipation: viewers tolerate late audio far more than early audio (ITU-R BT.1359-1: detectable at audio 45 ms early / 125 ms late, acceptable +90 / -185 ms; EBU R37 +40 / -60 ms; https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-1-199811-I!!PDF-E.pdf). So a picture event must never trail its sound: put the impact/contact frame on the frame that contains the transient, or 1 frame early (33 ms at 30 fps). "Cut 1-2 frames before the beat" is editor folklore (e.g. Filmmaker IQ's one-frame rule), not a standard: default to 1 frame early for hard cuts and hits, 0 for beat pulses. Text lands slightly ahead of its word (production leads: karaoke line 0.15 s, title punch 0.04 s). Wind-ups start 2-6 frames before the beat so the extreme pose lands on it. Snap the transient, not the file start (whoosh peak at 0.65*d; measure onsets of generated SFX).

## 6. Mix and master (ffmpeg, **tested**)

Targets: deliver **-14 LUFS integrated, <= -1 dBTP** (master at -1.5 so the AAC stays under -1). Spotify normalizes to -14 LUFS and asks for <= -1 dBTP, <= -2 if louder than -14 (https://support.spotify.com/us/artists/article/loudness-normalization/); YouTube's -14 turn-down-only is measured by practitioners, not published by Google (https://productionadvice.co.uk/stats-for-nerds/); TikTok, Reels, X and LinkedIn publish no target (practitioner advice -16 to -10). References: Apple Podcasts -16 LKFS +/-1, <= -1 dBTP; AES TD1008 speech -18, music -16/-14; EBU R128 broadcast -23. Do not chase -9: limiter crush flattens the transients the picture is cut to. Balance that worked in production: VO stem at -18 LUFS pre-master; loudest music section 9-10 dB under the voice; SFX files normalized to -20 LUFS (true peak capped at -8 dBTP) and then scaled per cue (1.0 is about 4 dB under the VO, 0.3-0.5 an accent, 0.15-0.25 texture).

```bash
# mix: VO cleaned + compressed, music EQ-carved at 3 kHz and sidechain-ducked by the VO, SFX bus; normalize=0 keeps gains honest
ffmpeg -y -i music.wav -i vo.wav -i sfx_bus.wav -filter_complex "
[1:a]aresample=48000,adelay=2000:all=1,apad=whole_dur=16,highpass=f=80,deesser=i=0.4,
     acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,aformat=channel_layouts=stereo,asplit=2[vo][key];
[0:a]aresample=48000,equalizer=f=3000:t=q:w=1:g=-4[mus];
[mus][key]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350:makeup=1[bed];
[bed][vo][2:a]amix=inputs=3:weights='0.9 1 0.8':normalize=0:duration=first[mix]" -map "[mix]" -c:a pcm_f32le mix_pre.wav
```

Filter gotchas (ffmpeg 9 `-h filter=`): `sidechaincompress` threshold is linear amplitude (0.02 ~ -34 dBFS; default 0.125), ratio 1-20, inputs `[main][key]`; `alimiter` defaults to `level=true` (auto-gain up to the ceiling) so always pass `level=disabled`; `deesser` intensity `i` defaults to 0 (does nothing); `amix` defaults to `normalize=true` and `dropout_transition=2` (level jumps when an input ends).

Ducking by automation instead of a compressor (exact depth, no pumping; build the expression from `phrases`, attack 0.25 s before, release 0.6 s after): `volume='pow(10,(-12*min(1,between(t,1.75,12.24)+...))/20)':eval=frame` on the music chain. Measured on the test bed under the VO: sidechain -15.2 dB, automation -12.0 dB; both masters landed the same. In Remotion do it per frame: merge words into phrases bridging pauses < 1 s (so the bed does not breathe between sentences), ramp in dB with a smoothstep, attack 0.35 s, release 0.9 s, `volume={(f) => gains[f]}` (production `Soundtrack.tsx`). Remotion mixes into 16-bit PCM with no dynamics: keep its mix near -18 LUFS with >= 3 dB headroom and master afterwards.

Master: `scripts/audio_check.py mix.wav --normalize master.wav` is the default. It applies gain plus a 4x-oversampled limiter at -1.5 dBTP and iterates against the same EBU R128 meter that judges the result, because `loudnorm`'s integrated reading was measured more than 0.5 LU away from `ebur128` on short, dynamic or mono mixes (it overshot to -13.4 LUFS on one film). The `loudnorm` route below also works when you read `normalization_type`:

```bash
#!/usr/bin/env bash
# master.sh IN.wav OUT.wav [I=-14] [TP=-1.5]
set -euo pipefail; in=$1; out=$2; I=${3:--14}; TP=${4:--1.5}
meas() { ffmpeg -hide_banner -nostats -i "$1" -af "loudnorm=I=$I:TP=$TP:LRA=20:print_format=json" -f null - 2>&1 | awk '/^\{/{j=1} j{print} /^\}/{j=0}'; }
m=$(meas "$in"); gain=$(jq -r "$I - (.input_i|tonumber)" <<<"$m"); lim=$(awk -v tp="$TP" 'BEGIN{printf "%.5f", 10^((tp-0.5)/20)}')
ffmpeg -v error -y -i "$in" -af "volume=${gain}dB,aresample=192000,alimiter=limit=$lim:attack=1.5:release=80:level=disabled,aresample=48000" -c:a pcm_f32le "$out.pre.wav"
m=$(meas "$out.pre.wav"); j() { jq -r ".$1" <<<"$m"; }
ffmpeg -hide_banner -nostats -y -i "$out.pre.wav" -af "loudnorm=I=$I:TP=$TP:LRA=20:measured_I=$(j input_i):measured_TP=$(j input_tp):measured_LRA=$(j input_lra):measured_thresh=$(j input_thresh):offset=$(j target_offset):linear=true:print_format=json,aresample=48000" \
  -c:a pcm_s24le "$out" 2>&1 | awk '/^\{/{j=1} j{print} /^\}/{j=0}' | jq -c '{normalization_type, output_i, output_tp}'; rm -f "$out.pre.wav"
# check: ffmpeg -hide_banner -nostats -i OUT -af ebur128=peak=true -f null - 2>&1 | grep -E '^\s+(I|LRA|Peak):'
# deliver: ffmpeg -i video.mp4 -i OUT.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac_at -b:a 256k -ar 48000 -movflags +faststart final.mp4  (aac_at = macOS AudioToolbox; elsewhere -c:a aac -b:a 320k)
```

Measured (16 s test: music + `say` VO + SFX): mix -14.9 LUFS / -2.1 dBTP. Plain two-pass `loudnorm ... linear=true` straight on it reported `normalization_type: dynamic` (the +0.9 dB gain would push peaks past -1.5, so it silently fell back; LRA shrank 3.8 -> 2.7). With `master.sh`: `linear`, **-14.2 LUFS, -2.0 dBTP, LRA 3.8**; AAC 256k -14.2 / -2.0; AAC 128k -14.2 / -1.8; muxed MP4 -14.2 / -2.0. Always read `normalization_type`.

- EQ: high-pass VO at 70-80 Hz; dip the music 3-4 dB around 2-5 kHz (`equalizer=f=3000:t=q:w=1:g=-4`) only while VO plays if you can; de-ess VO (`deesser=i=0.4`) after any brightening; compress VO gently (2.5-3:1, soft knee) after per-line loudness matching (TTS lines arrive up to 6.5 dB apart; normalize each line to -18 LUFS first, 30 ms crossfades at line joins).
- Room tone: never hard-cut to digital silence under picture; keep the bed or a -60 dBFS noise floor (`anoisesrc=color=pink:amplitude=0.001`) across VO gaps. Fades: 20-30 ms `afade` on every edit point; music out 1.5-3 s (`afade=t=out:st=13.5:d=2.5`), or cut on a downbeat with the tail ringing.
- Per-window checks: `ffmpeg -ss 3 -to 7 -i bed.wav -af ebur128 -f null -` (integrated over the window). Report VO-minus-bed per line; flag any SFX within 6 dB of the VO.

## 7. Captions from alignment

Rules (Netflix: 42 chars/line, 2 lines, 5/6 s min, 7 s max, 2-frame gap, 20 cps adult English, **17 cps adult Spanish** (https://partnerhelp.netflixstudios.com/hc/en-us/articles/217349997); BBC: 37 chars, 160-180 wpm, ~25 chars and up to 3 lines inside the central 75% x 90% for 9:16 (https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/)):
- <= 2 lines per card; 25-32 chars/line on 9:16, <= 32 on 4:5 (tested: a 28-char line at libass size 18 nearly fills a 1080 px wide frame), <= 42 on 16:9.
- 1-6 s per card (never under 0.83 s), reading speed <= 17 chars/s for Spanish, <= 20 for English (spaces included); extend the card toward the next one rather than speeding the reader; >= 2 frames between cards.
- Break on phrase boundaries: sentence end first, then after commas/colons, before conjunctions and prepositions. Never end a line on an article, preposition or conjunction (`de`, `la`, `y`, `the`, `of`); keep name + surname and number + unit together; balance the two lines.
- Card in = first word start (0-2 frames early at most); out = last word end + 0.2 s, clipped to 1 frame before the next card; never overlap.
- Display text may differ from speech (digits for numbers, real brand spelling for a phonetic lyric). Keep `(spoken, display)` pairs and assert token by token against the alignment so a re-voiced take fails loudly instead of drifting (production `make_srt.py`).
- Social style: 1-3 word "karaoke" pops driven by `words[]`, current word highlighted, inside the platform safe area (commonly quoted for Reels/TikTok: clear top ~14%, bottom ~35%, sides ~6%; Meta asks for the bottom 40% clear on Reels ads with disclaimers; TikTok publishes templates, not numbers). A 4:5 center crop of a 16:9 master must still hold every line.

```bash
scripts/captions.py words.json captions.srt --max-chars 32 --max-cps 17   # prints each card with its reading speed
```

Tested: whisper words -> cards (`Cada punto es / una respuesta real.`, 15.6 cps; `Ante una pregunta imposible, / el modelo adivina.`; `A veces, la respuesta más / inteligente es, no se sabe.`). Burn-in: Homebrew ffmpeg 9.0.2 ships **without libass and drawtext** (`Unknown filter 'subtitles'`), so either draw captions in the renderer (preferred: brand fonts, per-word animation, one source of truth with the cue sheet) or use the static ffmpeg 7.1 inside the `imageio-ffmpeg` wheel (tested):

```bash
FF=$(uv run -q --no-project --with imageio-ffmpeg python -c 'import imageio_ffmpeg as i; print(i.get_ffmpeg_exe())')
"$FF" -i silent.mp4 -i master.wav -vf "subtitles=captions.srt:force_style='FontName=Helvetica,FontSize=18,Bold=1,Outline=2,MarginV=60'" \
  -map 0:v -map 1:a -c:v libx264 -crf 20 -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -movflags +faststart final.mp4
```

Also upload the `.srt` as a sidecar where the platform accepts it (YouTube, LinkedIn): searchable, toggleable, and it survives re-encodes.

## 8. Pitfalls and fixes

1. **AAC priming shifts sync.** Tested: a click encoded to raw ADTS `.aac` decodes +1024 samples (21.3 ms @ 48 kHz) late; the same audio in `.m4a`/`.mp4` (edit list) and LAME `.mp3` decoded by ffmpeg is sample-exact, and AudioToolbox `aac_at` adds 384 samples of tail padding. Fix: keep WAV/PCM through the pipeline, encode AAC exactly once into MP4 at the final mux, never concatenate encoded segments (concat PCM, then encode). Apple's encoder primes 2112 samples (~44 ms at 48 kHz), which MP4/M4A/CAF can signal and ADTS cannot (https://developer.apple.com/library/archive/technotes/tn2258/_index.html); LAME MP3 carries 1105 samples, trimmed only by decoders that read the LAME tag; concatenating AAC with ffmpeg can leave gaps (https://trac.ffmpeg.org/ticket/4676).
2. **44.1 vs 48 kHz.** ElevenLabs defaults to 44.1 kHz MP3, `say` writes 22.05 kHz, ACE-Step and video want 48 kHz. Resample every input at ingest (`aresample=48000`); raw-PCM math at the wrong rate plays 8.8% off-speed and drifts. Word times in seconds survive resampling; sample indices do not.
3. **`loudnorm linear=true` silently goes dynamic** when the gain would break the TP ceiling (tested). Read `normalization_type` from the pass-2 JSON; limit first (`master.sh`).
4. **loudnorm output rate**: tested, `loudnorm` in dynamic mode (single pass, or a failed linear pass) writes a 192000 Hz file. Always append `aresample=48000` (or `-ar 48000`).
5. **Clipping in the mix bus.** `amix` defaults to `normalize=1` (levels jump as inputs end); with `normalize=0` sums exceed 0 dBFS. Keep intermediates `pcm_f32le`, limit only in the master. Remotion's 16-bit bus clips hard: keep its mix near -18 LUFS.
6. **Sample peak is not true peak, and the encoder adds peaks.** Tested: -1 dBFS sample peak read +0.5 dBTP on a square-wave glitch; AAC 128k raised TP by 0.2 dB on a soft mix, and ffmpeg's native `aac` at 192k raised a bright film mix from -1.7 to +0.2 dBTP while AudioToolbox `aac_at` kept -1.6. Master at -1.5 dBTP, encode with `aac_at` (or native `aac` at 320k), encode once, and measure every export, not just the master (`scripts/video_gates.py`).
7. **Music intro too long.** Generators open with 4-8 bars; social viewers leave in 1-2 s. Trim to one bar before the hook, ask for "one bar pickup then vocals", or open the video on the drop.
8. **VO too fast in Spanish.** Spanish runs ~20% longer than the English script. Budget ~130-140 words per 60 s (production: 137 words, lines 113-177 wpm), ElevenLabs `speed` <= 1.07; cut words instead of speeding audio.
9. **Credits burn.** Draft timing with `say` or flash, test music with a 10 s plan, cap at 2-3 seeds, cache every take next to its JSON (plan, seed, model, song_id) and re-time instead of regenerating. v3 Creative mode needs more retries.
10. **Direction text gets sung.** Music `words_timestamps` include `{cue}`/`[Section]` tokens at 0 ms, and a `(hablado)` direction was vocalized as "¡Habladora!". Use `{}` only for cues, `()` only for vocal sounds, filter tokens, ASR-check the take.
11. **Last-character alignment runs long** (trailing silence): clamp each word end to start + 0.3 s; extend sung word ends to the vocal offset instead.
12. **TTS lines arrive at different loudness** (6.5 dB spread measured): normalize per line before compression, or quiet lines drown under the drop.
13. **Forgetting `model_id` on music** gives `music_v1` (sections schema); `chunks` on v1 errors. Stitching params are ignored/unsupported on `eleven_v3`.
14. **Stale processed stems.** After a re-voice the mix still plays the old stem. Name stems by a hash of the word timings (`vo_mix-<fnv1a>.wav`) and fall back to the raw VO when the hash misses.
15. **No libass/drawtext in Homebrew ffmpeg 9**: burn captions in the renderer or with the imageio-ffmpeg 7.1 binary (section 7).
16. **Whisper traps**: first word of a segment 0.3-0.9 s early, hallucinated "Gracias." over silence, skipped lines when prompted with lyrics. Refine with CTC/forced alignment, cross-check vocal-stem activity, do not prompt with lyrics.
17. **librosa defaults are coarse**: 23 ms frames, tempo quantized (117.45 vs 120 BPM tested), beat peaks after the attack. Use hop 256, polyfit a constant grid, shift onto backtracked onsets.
18. **Short or generated SFX mislevel**: < 0.4 s files read -70 LUFS, generated files can be near-silent (-58.6 LUFS) or 50 dB apart. Measure all files (`ebur128=peak=true`) into a `levels.json`, normalize by LUFS with a TP cap, then per-cue gain.
19. **Truncated synth tails click** (visible as a vertical line in the spectrogram at the cut): fade the last 30-50 ms of every generated or trimmed sound; 20-30 ms `afade` at every edit.
20. **Ducking that breathes** between sentences reads as pumping: bridge pauses < 1 s, ramp in dB, prefer automation from word timings over a compressor; `sidechaincompress` input order is `[main][key]`.
21. **Copyrighted music** gets the video muted, claimed or blocked; "sounds like <artist>" prompts are rejected by ElevenLabs and risky anywhere. Safe sources: generated music on a plan that grants rights (ElevenLabs Starter+ commercial, Creator+ for streaming platforms), ACE-Step outputs (MIT, check originality), YouTube Audio Library (monetizable on YouTube, CC tracks need credit), TikTok Commercial Music Library (business accounts, TikTok only), Meta Sound Collection. Suno free-tier songs stay non-commercial even after upgrading, and UMG + Sony sued Suno again on 2026-09-18; Udio disabled downloads. YouTube requires disclosure of realistic AI-generated content, and non-exclusive tracks cannot be Content ID references (https://support.google.com/youtube/answer/2605065). Keep a license note per track: source, plan/prompt, seed, account tier, date.
