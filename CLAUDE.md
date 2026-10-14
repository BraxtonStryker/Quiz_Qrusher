# Quiz Qrusher

Offline-capable quiz app: users generate multiple-choice question CSVs with an AI prompt pipeline, then load the CSV, take the quiz, and get a graded report. Built for classmates (currently med students; v3 makes it subject-agnostic). Hosted on GitHub Pages starting with v3.0.

**Active work: v3.0. Read [docs/V3_PLAN.md](docs/V3_PLAN.md) first and tick off its checklist as phases finish.**

## Layout
- `index.html`, `lite.html`, `sw.js`, `manifest.webmanifest`: v3 site root (created during v3 build)
- `versions/`: every shipped app version (v1 to v2.3.3). The v3 baseline is `versions/quiz_qrusher_v2.3.3.html`
- `prompts/medical/`: current AI pipeline prompts. `prompts/ee/` is planned. `prompts/dev/` has prompts used to build the app. `prompts/archive/` has superseded prompts
- `docs/guides/`: old user-guide PDFs (v0, v1, v2.1), **gitignored/private**; their content is being rebuilt as the in-app Help menu
- `test-data/csv/`: sample question banks (gitignored, lecture-derived). `test-data/saves_v2/`: v2 resume-code .txt files covering the answered/flagged combinations
- `_archive_local/`: gitignored old zips

## Conventions (match the existing code)
- Single-file HTML apps: inline CSS and JS, vanilla JS in an IIFE, `var` and `function` style like v2.3.3, no frameworks and no build step.
- Mark changes inline with the version, e.g. `//v3.0 - why`, and `<!--v3.0-->` in HTML. Keep the existing `//v2.x` comments.
- Lite must be fully self-contained (fonts inlined, no network). The hosted app may load nothing from CDNs either. Bundle everything.
- Use American spelling in UI text and code: "color", not "colour".
- Use CSS custom properties on `:root` for every color, so themes and settings just swap tokens.
- CSV contract (never break it): `Category, Question_Text, Option_1..Option_6, Correct_Option_Number`, with lenient header matching (see `norm`/`findCol` in v2.3.3).
