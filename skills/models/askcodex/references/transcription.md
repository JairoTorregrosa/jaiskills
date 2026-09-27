# Audio transcription with askcodex

You are about to turn a recording into text with `askcodex transcribe`. The command transcribes
the audio it is given; it takes no instruction prompt. Prepare a WAV file, transcribe it, check the
transcript against the recording, and hand it over separately from any later editing.

## Context you must respect

- Input is one WAV file (RIFF/WAVE signature) up to 25 MiB, a client memory limit rather than a
  known server limit. It must be a regular file; symlinks to regular files work, devices and FIFOs
  are rejected before reading. Renaming an extension does not convert the audio.
- There is no model selector, language hint, timestamps, speaker labels, or incremental output.
  `--events` emits only the final transcript result.
- The command uses the existing subscription credentials. `--no-refresh` prevents authentication
  changes.

## Facts already verified (2026-09-08)

- A synthetic WAV returned HTTP 200 with the exact spoken sentence as `text`. WAV is the only
  format exercised; duration limits and language behavior are unverified (see the repository's
  `docs/PROTOCOL.md` §3.8).

## Do this

1. Convert other formats to WAV without overwriting the original. With FFmpeg installed:

   ```sh
   mkdir -p /tmp/askcodex
   ffmpeg -i recording.m4a -ar 16000 -ac 1 /tmp/askcodex/recording.wav
   ```

   These settings are a practical starting point, not required server settings. Split a long
   recording into clearly named segments and keep their order.
2. Transcribe and save:

   ```sh
   askcodex transcribe /tmp/askcodex/recording.wav --no-refresh > /tmp/askcodex/transcript.txt
   ```

   For structured output:

   ```sh
   askcodex transcribe /tmp/askcodex/recording.wav --json --no-refresh > /tmp/askcodex/transcript.json
   jq -r .result.text /tmp/askcodex/transcript.json
   ```

   Run a call that may take minutes in the background or in tmux.
3. Check names, numbers, technical terms, and unclear passages against the recording. An empty
   transcript can be a valid response: listen to the audio before you treat it as a failure or
   retry.
4. To summarize, extract decisions, or format notes, give the transcript to `askcodex ask` with a
   complete brief from [prompting-text.md](prompting-text.md). Keep the original transcript
   separate from the edited version.

## Rules

- On an authentication error, resolve it before trying again.
- Do not promise a speech model, language selection, timestamps, or speaker labels.

## Report

Tell the user where the transcript was saved, what you checked against the recording, and any
passage you could not confirm.
