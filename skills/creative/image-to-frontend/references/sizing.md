# Sizing under askcodex

`askcodex image create` returns **one opaque PNG whose size the backend chooses** — there are no
size, quality, transparency, format, or batch flags (the backend ignores them, so askcodex does
not offer them). Do not promise a specific resolution or a transparent background.

What you control is **composition, in the prompt wording**:

| Use | Say in the prompt |
|---|---|
| Desktop UI / landing | "landscape desktop viewport, full-page screenshot framing" |
| Mobile UI | "mobile portrait framing, single phone screen fills the frame" |
| Logo / social square | "centered square composition, generous margins" |

If the deliverable requires exact pixel dimensions, generate the closest composition and
crop/resize locally (`sips`, ImageMagick) as a post-step.
