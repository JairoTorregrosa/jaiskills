# Audio transcription with askcodex

Use `askcodex transcribe` to turn a WAV recording into text. The command
transcribes the supplied audio; it does not take an instruction prompt.

## Prepare the input

Use a WAV file containing the speech to transcribe. The client accepts a
RIFF/WAVE signature and enforces a 25 MiB client memory limit, not a claimed
server limit. Input must be a regular file; symlinks to regular files work,
while devices and FIFOs are rejected before reading. Convert other formats
before calling it; renaming an extension does not convert the audio.

With FFmpeg installed:

```sh
mkdir -p /tmp/askcodex
ffmpeg -i recording.m4a -ar 16000 -ac 1 /tmp/askcodex/recording.wav
```

These conversion settings are a practical starting point, not required
server settings. Do not overwrite the original recording. For a long file,
prepare smaller segments with clear names and preserve their order.

## Transcribe and save

```sh
askcodex transcribe /tmp/askcodex/recording.wav --no-refresh > /tmp/askcodex/transcript.txt
```

For structured output:

```sh
askcodex transcribe /tmp/askcodex/recording.wav --json --no-refresh > /tmp/askcodex/transcript.json
jq -r .result.text /tmp/askcodex/transcript.json
```

Queue the call or use tmux when the recording may take minutes to process.
The command uses the existing subscription credentials. `--no-refresh`
prevents authentication changes; an authentication error must be resolved
before trying again.

## Use the transcript

Check names, numbers, technical terms, and unclear passages against the
recording. An empty transcript can be a valid response; inspect the audio
before treating it as a failure or retrying.

Keep the original transcription separate from subsequent editing. To
summarize, extract decisions, or format notes, supply the transcript to
`askcodex ask` with a complete brief from [prompting-text.md](prompting-text.md).

Do not promise a selected speech model, language hint, timestamps, speaker
labels, or incremental transcript output: this command provides none of those
controls. `--events` emits the final transcript result when it completes.
