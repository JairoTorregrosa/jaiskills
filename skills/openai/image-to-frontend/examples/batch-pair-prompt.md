# Desktop + mobile pair template (secondary use case)

When a single idea needs both a desktop screenshot and a mobile screenshot rendered as a deployed-looking app, fire one `askcodex image create` call per idea using this template (two calls if desktop and mobile are separate images).

```
Product: "{title}" — {audience}. Promise: {promise}. Demo: {demoTitle}.

(1) DESKTOP 1536x1024. Photorealistic dark-mode SaaS web app, as if
already deployed. Accent {hex}. Top bar wordmark "{title}" + 4 nav
tabs. Left rail filters. Main panel "{demoTitle}" with 4 result
cards using these SHORT labels (5-6 words max each):
- "{label1}"  /  "{label2}"  /  "{label3}"  /  "{label4}"
No fake browser chrome, no watermarks.

(2) MOBILE 1024x1536 portrait. Same product on phone — place the UI
in a clean iPhone frame. Title at top with accent. Input placeholder
"{shortPlaceholder}". Four stacked cards (same labels). Bottom tab
bar with 4 icons.

Save BOTH to:
/abs/path/{id}/desktop.png
/abs/path/{id}/mobile.png
Print absolute paths.
```
