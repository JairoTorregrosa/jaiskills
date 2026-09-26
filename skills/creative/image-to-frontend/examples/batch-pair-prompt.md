# Desktop + mobile pair template (secondary use case)

When a single idea needs both a desktop screenshot and a mobile screenshot rendered as a deployed-looking app, fire two `askcodex image create` calls per idea (one image per call), in parallel across ideas:

```sh
askcodex image create "<desktop prompt>" -o mockups/{id}/desktop.png
askcodex image create "<mobile prompt>"  -o mockups/{id}/mobile.png
```

Size is chosen by the backend; the framing words below steer composition. Crop/resize locally if exact pixels matter (`references/sizing.md`).

Desktop prompt:

```
Product: "{title}" — {audience}. Promise: {promise}. Demo: {demoTitle}.

DESKTOP: landscape desktop viewport, full-page screenshot framing.
Photorealistic dark-mode SaaS web app, as if already deployed.
Accent {hex}. Top bar wordmark "{title}" + 4 nav tabs. Left rail
filters. Main panel "{demoTitle}" with 4 result cards using these
SHORT labels (5-6 words max each):
- "{label1}"  /  "{label2}"  /  "{label3}"  /  "{label4}"
No fake browser chrome, no watermarks.
```

Mobile prompt:

```
Product: "{title}" — {audience}. Promise: {promise}. Demo: {demoTitle}.

MOBILE: portrait framing, single phone screen fills the frame. Same
product on phone — place the UI in a clean iPhone frame. Title at top
with accent {hex}. Input placeholder "{shortPlaceholder}". Four stacked
cards with the same labels:
- "{label1}"  /  "{label2}"  /  "{label3}"  /  "{label4}"
Bottom tab bar with 4 icons. No watermarks.
```
