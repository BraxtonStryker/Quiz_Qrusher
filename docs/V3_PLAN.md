# Quiz Qrusher v3.0 — Build Plan

Condensed from the planning chat on 2026-10-14. Decisions below are **settled**; don't re-ask them. Items under "Open items" and "Interpretations to confirm" still need the user.

Baseline: `versions/quiz_qrusher_v2.3.3.html` (CSV load → scrollable quiz → results/report/follow-up .md; flags, notes dock, .txt resume code).

---

## 1. What v3.0 is

| Piece | Summary |
|---|---|
| **Full app** (`index.html`, GitHub Pages) | Home screen with tiles, library of past quizzes in browser storage, autosave, optional saves folder (Chrome/Edge), tutor mode, timer, settings, Help, Feedback, Prompt Builder, PWA. |
| **Lite** (`lite.html`) | v2.3.3 flow + v3 UI polish + settings + autosave. Downloadable single file ("Download for offline use"), and also served on the site for unsupported browsers. |
| **Prompts** | Medical pipeline prompts downloadable from Home; Prompt Builder generates prompts for any subject. |

---

## 2. Settled decisions

### Home screen (full app)
- Top tabs: **Home · Prompt Builder · Help · Settings · Feedback**.
- Home tiles: **[Start new quiz] [Resume previous quiz] [Review previous quiz] [Import previous quiz]**.
- Footer links: **Download prompts** (zip of `prompts/medical/`), **Download for offline use** (Lite with current settings baked in), version and "What's new".
- Help is also reachable from the quiz screen (from the old todo).

### Library and storage
- Model: **Question bank** (one CSV; name defaults to the file name; rename and delete allowed) → **Attempts** (`in_progress` | `submitted`).
  Resume lists in-progress attempts; Review lists submitted ones.
- Browser storage: IndexedDB for banks and attempts, localStorage for settings and small flags. Call `navigator.storage.persist()`. Namespace every key with `quizQrusher:` because all of the user's GitHub Pages projects share one origin.
- **Autosave on every change**, in both the full app and Lite. The old manual "Save progress to file" becomes **Export backup**.
- Safari deletes site storage after about 7 days of no visits. Mitigations: Export backup, the PWA install, and a note in Help.

### Save format (v3, shared by full and Lite)
One self-contained JSON file per attempt; the CSV is embedded so no separate file is needed:
```json
{ "format": "quiz-qrusher-save", "version": 3, "app": "3.0",
  "bank":    { "id": "", "name": "", "fileName": "", "csvText": "", "csvHash": 0, "questionCount": 0 },
  "attempt": { "id": "", "createdAt": 0, "updatedAt": 0, "status": "in_progress|submitted",
               "mode": "test|tutor", "questionOrder": [], "optionOrder": [], "answers": [], "flags": [],
               "revealed": [], "notes": "", "elapsedMs": 0, "results": null } }
```
- Question IDs = `hashStr(category|text|correct)`, the same as v2.3.3.
- **Import** accepts: a v3 `.json`; a v2 `.txt` resume code (then ask for its CSV and match `csvHash`); a bare CSV (creates a new bank).
- Test fixtures for v2 import: `test-data/saves_v2/*.txt` with `test-data/csv/qus_input_25.csv`.

### Saves folder (File System Access API; Chrome/Edge desktop only)
- Detect support with `'showDirectoryPicker' in window`, never by user-agent. User-agent is only used for wording.
- Setting: "Link a saves folder". Store the directory handle in IndexedDB. On later visits use `queryPermission`. If the result is `prompt`, show a one-click **Reconnect** (needs a user click; Chrome 122+ offers "Allow on every visit").
- Write order: browser storage instantly on every change, then the attempt's `.json` to the folder about 1 second later.
- Status line in the quiz header: "✓ Saved to folder · just now" or "⚠ Saved in browser only — Reconnect".
- On open, compare folder and browser copies and keep the newer one per attempt (`updatedAt`).
- Handle: a missing or renamed folder (fall back to browser storage plus a banner), the same attempt open in two tabs (BroadcastChannel or Web Locks), and `.crswap` temp files inside iCloud/OneDrive folders. Help should suggest a dedicated folder set to "Always keep on this device".
- Firefox and Safari can't link a folder; they use browser storage plus export/import.

### Unsupported-browser dialog (full app and Lite)
- Shown when the app opens and `showDirectoryPicker` is missing:
  "This app works best on Chrome or Edge for settings and progress saving."
  Buttons: **[Use Lite version] [Use full version]**, plus a **☐ Don't show again** checkbox.
- The checkbox is stored in browser storage, so on Safari it may come back after the 7-day storage wipe. That's acceptable; mention it in Help.
- Full app → "Use Lite version" opens the hosted `lite.html`. Downloaded Lite → "Use full version" opens the hosted site.
- Settings → Data has a "Show the browser notice again" option.

### Lite specifics
- Contents: v2.3.3 flow + v3 visual updates + settings + autosave + the v3 save format. **No** home library, tutor mode, timer, Prompt Builder, PWA or analytics, unless trivially shared.
- **Settings are baked into the HTML** inside a marked block, e.g. `<script id="qq-settings" type="application/json">`.
  - Settings changes **preview live**. **[Apply]** writes a new Lite HTML containing the new settings block.
  - If the linked saves folder is Lite's own folder (Chrome/Edge), Apply overwrites Lite in place and reloads.
  - Otherwise it downloads the new file under the same fixed name, with the message: "Delete the old Lite file and put this one in its place, then reopen it and relink your saves folder (Chrome/Edge)."
  - Build the regenerated file from a **snapshot of the page source taken at startup**, never from the live DOM. That keeps extension-injected markup and quiz state out.
- When Lite is served from the site (https) instead of opened from disk, settings live in browser storage and Apply just saves.
- Saving: Chrome/Edge can link a folder. Other browsers have **no saves folder**: they autosave to browser storage and download v3 `.json` save files.
  - This is a trial: "we'll try the download JSON and see if it's functional". Collect feedback after release.
  - Setting **"Prompt me to download a save file"** fires **at the end of the quiz (on Submit)**.
  - It can also fire **on an interval timer**: off / every 5 / 10 / 15 / 30 min, chosen in Settings.
- Recommended Lite folder layout: `Quiz Qrusher Lite/quiz_qrusher_v3.0_lite.html` + `saves/`.
- The full app's "Download for offline use" uses the same mechanism: fetch `lite.html`, swap in the current settings, download.

### Quiz features in 3.0
| ID | Feature | Status |
|---|---|---|
| a | Retake only **missed** / **flagged** / **missed + flagged** (from Results and Review) | ✅ in |
| b | PWA: `manifest.webmanifest` + `sw.js` + icons; offline cache; "New version available — reload" toast | ✅ in |
| c | **Tutor/Test mode toggle in the side dock next to Notes**; per-question **Show answer** button (can be turned off in Settings). Scoring rules are below the table. | ✅ in |
| d | `Explanation` CSV column | ⏸ deferred |
| e | Category score trends across attempts of the same bank (Review screen) | ✅ in |
| f | Keyboard shortcuts | ❌ not now |
| g | Timer showing time spent; can be turned off in Settings | ✅ in |
| h | "What's new" page in Help, built from the `//vX.Y.Z` notes | ✅ in |

**Show-answer scoring (decided by user):**
- Revealed questions are **not scored**, *unless an incorrect answer was logged before Show answer was clicked*. That case counts as **incorrect**.
- Revealed with no answer → excluded from the score; shown as "Revealed — not scored".
- Answered **correctly** before reveal → counts as correct (confirmed by the user). The answer was committed before seeing the solution.
- Once revealed, the question's answer **locks**, so it can't be changed afterwards.
- Excluded questions leave the score denominator. Results show "X of Y scored (Z revealed)". Category stats and trends use the same rule.
- Store the answer-at-reveal-time in `revealed[]`, e.g. `null` = not revealed, `{at, answerBefore}` = revealed.

### Settings (full app; Lite gets the applicable subset)
- **Appearance:**
  - theme (Light / Dark / Match system)
  - accent color presets
  - color-blind-safe correct/incorrect colors
  - reduced motion
- **Text:**
  - font size scale
  - line spacing
  - font (System / Serif / Atkinson Hyperlegible, inlined as base64 woff2; OFL license)
- **Quiz:**
  - shuffle questions on/off
  - shuffle options on/off
  - show category tag
  - warn on submit with unanswered or flagged questions
  - Focus cut-off (default 70%)
  - Show-answer button on/off
  - timer on/off
- **Follow-up:** default difficulty, default question count.
- **Saving:**
  - link saves folder (Chrome/Edge)
  - prompt to download a save file (Lite / unsupported browsers): on Submit + optional interval
- **Privacy:** share anonymous usage stats (on by default; off disables analytics).
- **Data:**
  - storage used
  - export all
  - import
  - clear all (with confirmation)
  - show the browser notice again

### Feedback tab
- Embedded **Google Form** (iframe) with a fallback link. Prefill the app version and browser using the form's prefilled-URL entry IDs.
- **No email address anywhere in the app.** The form replaces it.

### Help tab
- Subject-agnostic guide, with the medical pipeline as the worked example.
- Rebuild it from `docs/guides/instructions_quiz_qrusher_v2.1.pdf` and update it. The PDF is out of date: it names `*_v2.md` prompts and `quiz_qrusher_v2.html`, and has no saving, notes, flags or tutor mode.
- Sections:
  - Getting started
  - The AI workflow: model table and Steps 1–5 using the current prompt names `slide_miner_v1`, `data_sanitizer_v2` (optional step 1.5), `style_researcher_v2`, `que_generator_v3`
  - Taking a quiz: flags, notes, Tutor/Test mode, Show answer, timer
  - Saving and resuming: autosave, saves folder, export/import, browser limits
  - Review and retake
  - Follow-up requests
  - Lite version
  - Settings
  - Privacy
  - What's new
- Each prompt gets copy and download buttons.

### Prompts
- Current medical set: `prompts/medical/` (slide_miner_v1, data_sanitizer_v2, style_researcher_v2, que_generator_v3).
- Home footer: "Download prompts" downloads a zip. Either commit a prebuilt `prompts/medical/medical_prompts.zip` or build a store-only zip in JS; prefer the prebuilt zip.
- **Prompt Builder tab** (any subject or major):
  - Form inputs: subject or course, level (undergrad / grad / professional / board exam), exam style (e.g. USMLE Step 1, FE, AP), difficulty, question count.
  - Output: the four pipeline prompts with copy/download.
  - Make generic templates from the medical prompts with `{{placeholders}}`.
  - Build this **last**; if time runs short, ship 3.0 with the medical set and "More subjects coming".
- EE prompts: not needed for 3.0 (`prompts/ee/README.md` placeholder).

### Analytics
- User wants usage stats, privacy-friendly. Use **GoatCounter**: no cookies, no personal data, free for non-commercial use, one script tag.
- Track page views plus a few events: quiz started / submitted, tutor mode used, Lite downloaded, prompts downloaded, feedback opened.
- Respect the Privacy setting and Do Not Track. Never send quiz content or file names.
- No analytics in Lite.
- Disclose in Help → Privacy.

### Code conventions
- Keep everything single-file per app, the inline `//v3.0` change comments, and vanilla JS matching the v2.3.3 style.
- Shared code between `index.html` and `lite.html` (settings, theme, save format, CSV parser): keep identical blocks fenced with `/* === QQ-SHARED:<name> === */ … /* === /QQ-SHARED === */`. When one changes, copy it to the other.

---

## 3. Repo and GitHub Pages
- Repo name: **`Quiz_Qrusher`**, public (free GitHub Pages needs public).
  - GitHub user: `BraxtonStryker` (`gh` is logged in).
  - Site: `https://braxtonstryker.github.io/Quiz_Qrusher/`. The repo path is case-sensitive.
- **Commit identity (repo-local, not global):** `git config user.name "Brax"` and `git config user.email "124317557+BraxtonStryker@users.noreply.github.com"`. Set this **before the first commit**. The user's gmail must not appear in any commit. Check with `git log --format='%an <%ae>'` before pushing.
- **Private, never pushed:** `test-data/csv/`, `docs/guides/` (the PDFs are replaced by the in-app Help menu), `_archive_local/`. All are gitignored.
- Push the previous versions **one at a time** so the history shows version control. Plan:
  1. Create the history with the app as a single file, `quiz_qrusher.html` at the repo root. One commit per version, in order: v1, v2.0, v2.1.0, v2.2, v2.3.0, v2.3.1, v2.3.2, v2.3.3. Tag each `vX.Y.Z`, so GitHub shows real diffs between versions. Write the commit messages from the actual diffs and the `//vX` comments. (v2.1.1 was byte-identical to v2.1.0 and was dropped, so tag v2.1.1 on the same commit.)
  2. Then one commit adding the organized tree (`versions/`, `prompts/`, `docs/V3_PLAN.md`, `test-data/saves_v2/`, `CLAUDE.md`, `.gitignore`). Remove the temporary root `quiz_qrusher.html` in that commit.
  3. Then the v3 work.
- **No backdating** (decided). Commits just need to be in version order.
- Enable Pages: deploy from the `main` branch, root folder.

---

## 4. Build phases (tick as done)
- [x] **0. Repo:** `git init`, set the repo-local identity from §3, build the history, create `Quiz_Qrusher` on GitHub, push, enable Pages. All Phase 0 decisions are made.
  - Done 2026-10-14: 8 version commits tagged `v1.0.0`, `v2.0.0`, `v2.1.0` (+`v2.1.1`), `v2.2.0`, `v2.3.0`–`v2.3.3`, then the organized-tree commit. Pushed to `github.com/BraxtonStryker/Quiz_Qrusher`. Repo-local `core.autocrlf=false` (files stay LF).
  - Stray root files from the earlier reorganization were moved: dev prompts → `prompts/dev/`, old zips → `_archive_local/`, `system_user_guide.pdf` → `docs/guides/`.
  - [ ] **Pages not enabled yet** (Claude's tool call was blocked). Enable it by hand: repo Settings → Pages → Deploy from branch `main`, folder `/ (root)`. Nothing serves until `index.html` exists (Phase 2).
- [x] **1. Folder-access test page** (`test-data/fsa_test.html`). The user opens it **from disk** in Chrome and Edge. It reports:
  - Can it link a folder?
  - Does the handle survive a reload or a browser restart?
  - Does a newly downloaded copy of the file still see the handle (shared `file://` storage)?
  - Can the page overwrite its own file?

  Record the results here; they decide the Lite saving and Apply design.
  - Built 2026-10-14. Also tests whether the startup snapshot exactly matches the file on disk (step 4) and whether "Allow on every visit" works on `file://` (steps 6–7). The page rewrites its own settings block in step 3, so restore `test-data/fsa_test.html` with git after the test runs.
  - Found while building it: an `outerHTML` snapshot taken as the first statement of the last script matches the source except for (1) whitespace between `<html>` and `<head>`, which the parser drops, and (2) the closing tags after that script. So "rebuild from the startup snapshot" is viable for Lite. (The serializer would also rewrite boolean attributes as `attr=""` and escape `>`/`&` in text. That's harmless to a rebuilt page; it only matters for byte-exact comparison, so the test page avoids them.) `navigator.storage.persist()` returned `false` in headless Chrome, so don't await it in startup paths.
  - **Results, Chrome 155 / Windows (2026-10-14), test folder inside iCloud Drive:**
    | Question | Result |
    |---|---|
    | Link a folder | ✅ Writes and reads back; the handle is stored in IndexedDB |
    | Survives reload | ✅ Permission stays `granted` |
    | Overwrite its own file | ✅ Rewrote in place and the reload picked up the new settings. No `.crswap` left behind, even in iCloud |
    | Startup snapshot = source | ✅ Only the two known parser differences |
    | Downloaded copy sees the handle | ✅ The copy in `Downloads/` saw the handle and the localStorage. **All `file://` pages share one storage.** In-session permission carried over (`granted`) |
    | Survives browser restart | ✅ The handle survives, but permission resets to `prompt`; one Reconnect click restores it |
    | "Allow on every visit" | ❌ Not offered on `file://`. Every browser session needs one Reconnect click |
    - Implications for Lite:
      - The saves-folder status line, with "⚠ Saved in browser only — Reconnect", will show on the first open after every browser restart. That's expected, not an error.
      - Apply can call `requestPermission` inside its own click, so in-place Apply always works with no extra step.
      - Shared `file://` storage means a replaced Lite file keeps its browser autosaves and its folder handle. Proposed: change the Apply fallback message from "relink your saves folder" to "press Reconnect". **Confirm with the user.**
      - The `quizQrusher:` key namespace matters on `file://` too, since every local HTML page shares that storage.
      - Chrome renamed the second download to `fsa_test_copy (1).html`. A fixed-name Lite download gets ` (1)` if the old file is still in Downloads; the Apply message should say so.
      - `persist()` is `false` on `file://` too. Export backup and the saves folder are the real safety net.
  - **Results, Edge 155 / Windows (2026-10-14):** identical to Chrome on every row, including no "Allow on every visit" on `file://`.
    - Also seen: one Reconnect returned `prompt` (the user dismissed the permission bubble). Reconnect must treat `prompt` as "not yet", keep the button visible, and not show an error.
  - **Firefox (2026-10-14, informal):** no `showDirectoryPicker`, as expected. It did **grant persistent storage** (`persist()`), which helps Lite's browser-storage fallback there.
    - Unverified: whether Firefox shares storage across `file://` pages. By default Firefox treats each local file as its own origin, so a replaced Lite file may *not* see the old autosaves. Test this in Phase 6. If it doesn't share, the Firefox path relies on the downloaded `.json` saves.
- [x] **2. Core:**
  - app shell (tabs, Home tiles)
  - storage layer (IndexedDB plus fallback)
  - v3 save format
  - library (banks/attempts)
  - Start / Resume / Review / Import (v3 JSON, v2 txt+CSV, CSV)
  - autosave
  - Export backup
  - Done 2026-10-14 in `index.html`. The Prompt Builder, Help, Settings and Feedback tabs are placeholders until their phases. Implementation notes:
    - **Storage:** IndexedDB database `quizQrusher:app` with stores `banks` and `attempts` (keyPath `id`) and `kv` (reserved for the Phase 5 folder handle). If IndexedDB fails or doesn't answer within 5 s, it falls back to localStorage keys `quizQrusher:db:<store>:<id>`, then to memory. Each fallback shows a banner on Home.
    - **Banks** are deduplicated by `csvHash`: loading the same CSV again reuses the bank. Deleting a bank deletes its attempts.
    - **Attempts** are stored with a `bankId`. The export drops it (the bank travels inside the file), so the exported JSON matches the §2 format exactly.
    - `attempt.results = { submittedAt, correct, total, scored, revealed, byCategory: {name: {correct, total}} }`. `scored`/`revealed` are ready for Tutor mode (Phase 3). `elapsedMs` stays 0 until the timer exists.
    - **Import:**
      - A v3 `.json` keeps whichever copy has the newer `updatedAt`.
      - A v2 `.txt` matches an existing bank by `csvHash`, and only asks for the CSV when there's no match. Its attempt id is `v2-<csvHash>-<timestamp>`, so importing it twice doesn't duplicate it.
      - A bare `.csv` creates a bank.
    - **Autosave:** answers and flags save immediately, notes after 500 ms, and pending saves flush on leaving the quiz, hiding the tab or closing it. The quiz header shows "✓ Saved in browser · just now". **Export backup** is in the quiz, the notes dock, Results, and each Resume/Review row.
    - The shared blocks `QQ-SHARED:csv` and `QQ-SHARED:save-format` are fenced for Lite. The commented-out dead code from v2 wasn't carried over (it's in git history).
    - **Regression harness:** [test-data/harness/app_harness.html](../test-data/harness/app_harness.html) (how to run is at the top of the file). It runs 56 checks covering every flow above, against both IndexedDB and the localStorage fallback. Rerun it after each phase and extend it as features land.
- [x] **3. Quiz features:** Tutor/Test toggle + Show answer, timer, retake missed/flagged, category trends, Help from the quiz screen.
  - Done 2026-10-14. Notes:
    - **Tutor mode:** a "TEST MODE / TUTOR MODE" tab sits above NOTES in the side dock. Tutor mode shows a Show answer button on each question. Switching back to Test hides the buttons; revealed questions stay revealed and locked. `attempt.mode` holds the current toggle.
    - **Settings stub:** `settings.showAnswer` false hides the toggle and every Show answer button. Settings are read from localStorage `quizQrusher:settings` with defaults `{showAnswer: true, timer: true, focusCutoff: 0.7}`; Phase 4 adds the UI.
    - **Reveal:** marks the correct option ("Correct answer") and a wrong pick ("Your answer"), and adds a note: "Revealed — not scored" or "Revealed after answering — counts as correct/incorrect". `revealed[i] = {at, answerBefore}`.
    - **Scoring:** revealed with no answer → excluded and listed as "Revealed — not scored". Answered before the reveal → counts as given. Correct-before-reveal counts as correct (confirmed). Results read "X of Y correct · Z revealed (not scored)". `results.total` = every question, `results.scored` = the scored ones.
    - **Timer:** counts only while the quiz is on screen and the tab is visible. It's saved in `elapsedMs` (also every 60 s), shown as ⏱ in the quiz bar and as "time m:ss" on Results. `settings.timer` false hides it; time is still tracked.
    - **Retake:** All / Missed / Flagged / Missed + flagged, with counts, on Results (and so on Review). "Missed" = wrong, unanswered or revealed. A subset retake is a new attempt with `retake: {of, kind}`, an optional field added to the save format (older files simply don't have it). Its title reads "Bank · flagged questions".
    - **Category trends:** on Results/Review once a bank has 2+ submitted *full* attempts (subset retakes are left out because they'd skew every category). Shows the last 6 as % chips, oldest to newest, with the viewed attempt outlined and the change since the previous attempt.
    - **Help from the quiz:** a Help link in the quiz bar; the Help screen then shows "← Back to quiz".
    - **Browser Back button (user request):** from any screen, Back returns to Home instead of leaving the app. One history entry sits on top of Home while another screen shows.
    - Harness: 90 checks. `test-data/harness/cdp_shot.py` takes screenshots of app states driven in real time.
- [x] **4. Settings + theming:** move all colors to tokens, the Settings tab, the unsupported-browser dialog.
  - Done 2026-10-14. Notes:
    - **Theming:** `QQ-SHARED:appearance` is a small script in `<head>` (so there's no flash of the wrong theme). It sets `data-theme` (absent = match system), `data-font`, `data-motion`, and inline `--accent*`, `--good/--bad*` (color-blind preset), `--fs` and `--lh` on `<html>`, and re-applies when the OS theme changes. The dark tokens exist twice in CSS: under `@media (prefers-color-scheme: dark) :root:not([data-theme="light"])` and under `:root[data-theme="dark"]`. Every `font-size`/`line-height` is `calc(... * var(--fs|--lh))`.
    - **Accent presets:** Indigo (default), Blue, Teal, Purple, Rose, Orange, each with light and dark values and its own text-on-accent color. Color-blind-safe colors use Okabe-Ito blue/orange.
    - **Fonts:** System, Serif (system serif stack), Atkinson Hyperlegible (Latin 400/700 woff2 inlined as base64, about 46 KB; OFL notice in the CSS comment; credit it in Help → Privacy/credits in Phase 7).
    - **Settings tab:** built from `SETTINGS_UI` (a schema of switch / seg / select / swatches / custom rows). Keys and defaults are in `SETTINGS_DEFAULTS`. Changes apply live and save to `quizQrusher:settings`. Quiz settings affect new attempts (shuffles) or re-render the open quiz (category tag, Tutor, timer).
    - **Saving:**
      - The folder row is a placeholder until Phase 5.
      - "Prompt me to download a save file when I submit" defaults **on only without folder access** (`!showDirectoryPicker`).
      - "Also prompt during a quiz" can be off or every 5/10/15/30 min.
      - Prompts are a bottom toast with Download / Not now, and any export resets the interval.
    - **Data:**
      - storage summary plus `navigator.storage.persisted()`
      - **Export all**: a bundle `{format: "quiz-qrusher-backup", version: 3, app, exportedAt, settings, banks, attempts}`
      - Import (goes to the Import screen, which now also takes bundles: banks matched by CSV, the newer copy of each quiz wins, and it asks before restoring settings)
      - Show the browser notice again
      - Reset settings
      - Clear all (deletes the stores and every `quizQrusher:` key, then reloads)
    - **Unsupported-browser dialog** (`<dialog>`): appears when `showDirectoryPicker` is missing, once per browser session unless "Don't show again" (`quizQrusher:hideBrowserNotice`). On mobile it says "on a computer". "Use Lite version" goes to `lite.html` (exists from Phase 6).
    - **Harness:** 129 checks. `logserver.py` serves `/_variant/nofsa/…` and `/_variant/noidb/…` (the app with `showDirectoryPicker` or IndexedDB removed). Run it as-is and with `?src=/_variant/noidb/index.html`.
- [x] **5. Saves folder** (Chrome/Edge): link, reconnect, debounced writes, reconciliation, multi-tab safety, status line.
  - Done 2026-10-14. Notes:
    - **Storage of the link:** the handle and bookkeeping live in IndexedDB `kv`: `savesDir` `{handle, name, linkedAt}`, `folderNames` (attempt id → file name), `deleted` (tombstones). The folder needs IndexedDB, so it's off on the localStorage/memory fallbacks.
    - **Files:** one per quiz, `<bank>_<YYYY-MM-DD>_<last 6 of attempt id>.json`, in the v3 save format. Files are matched by the attempt id **inside**, never by name. Renaming a bank rewrites its files under the new name and deletes the old ones.
    - **Writes:** browser storage first, then the folder 1 s later (debounced, one write at a time per file). Imports and bundles queue folder writes too.
    - **Reconcile** runs on start (if permission is `granted`), on link and on reconnect. The newer `updatedAt` wins per quiz: folder-only quizzes are imported, and browser-only or newer ones are written out. The open quiz always wins. Non-`.json` files (including iCloud/OneDrive `.crswap`) and non-save JSON are skipped.
    - **Deletes:** deleting a quiz removes its file and leaves a tombstone, so a stale copy (e.g. synced back by iCloud) is deleted rather than re-imported.
    - **Problems → UI:** "needs permission" (the normal state after a browser restart), "folder not found", "blocked" and "write error" each get a prominent accent **Reconnect folder / Choose folder / Try again** button in the quiz bar, a banner above the questions, and the same banner on Home. The status ✓ becomes a red "⚠ Saved in browser only". A dismissed permission bubble (`prompt`) just leaves the button there.
    - **Two tabs:** opening a quiz broadcasts a claim on BroadcastChannel `quizQrusher:tabs`. The other tab saves, replies with its `updatedAt` (the newer copy is reloaded in the claiming tab), and shows a modal "Open in another tab" with **Use it here** / **Go to Home**. A paused tab never writes. Escape can't dismiss the modal.
    - **Settings → Saving → Saves folder:** Link a folder / Change folder / Unlink, plus the fix button when there's a problem. The description recommends a dedicated folder set to "Always keep on this device" in iCloud/OneDrive. Clear all data also unlinks (the files stay).
    - **Harness:** 149 checks. The `fsatest` variant in `logserver.py` makes the picker return a real OPFS directory and fakes `prompt`/`granted` via `qqtest:*` localStorage keys. That covers linking, write-through, reconcile both ways, `.crswap`, Reconnect (including a dismissed prompt), tombstones, a missing folder and two tabs. Real-folder checks on Chrome/Edge are still part of Phase 10.
- [x] **6. Lite:**
  - `lite.html` from v2.3.3 + shared blocks
  - baked settings + Apply regeneration
  - "Download for offline use" from the full app
  - prompt-to-download setting
  - [x] Done 2026-10-14 (`lite.html`). Notes:
    - **Shared code:** the CSS and the `QQ-SHARED` blocks (appearance, csv, baked-settings, save-format) are copied verbatim from `index.html`. `python -I test-data/harness/check_shared.py` verifies they match, and `--sync` copies them from `index.html`, the source of truth. Run it after touching any shared block.
    - **Contents:** Home has a "Continue / Last quiz" card for the one quiz Lite keeps, the CSV drop, and a save-file drop (v3 `.json`; v2 `.txt` once its CSV is loaded; an Export-all bundle gets a pointer to the full app). Plus Quiz, Results (retake reshuffled), Help (short guide) and Settings, with an app bar of Home, then Full version · Help · ⚙ on the right.
    - **Left out:** library, Tutor mode, timer, trends, partial retakes, two-tab handling, analytics and PWA. Saves from the full app still open correctly: revealed questions show locked and scored the same way, and `elapsedMs`/`mode` are kept.
    - **Storage:** `quizQrusher:lite:current` (localStorage, one v3 save object), `:lite:settings` (hosted only), `:lite:hideBrowserNotice`, `:lite:lastorder:*`. The folder handle is in IndexedDB `quizQrusher:lite:kv`. None of it touches the full app's keys.
    - **Settings source:** `window.qqReadSettings` (defined before the shared appearance block, which now calls it if present). Opened from a file (anything not http(s)), it reads the baked `qq-settings` block `{v, nonce, madeAt, app, settings}`. On the hosted site it reads `quizQrusher:lite:settings`, falling back to the baked block.
    - **Apply:** changes preview live, and an apply bar plus a Home banner show while there are unapplied changes. A `beforeunload` warning catches leaving with them. Apply then:
      1. if the linked folder holds this file (name + nonce match), rewrites it in place and reloads;
      2. else, on the hosted site, saves to browser storage;
      3. else downloads `quiz_qrusher_v3.0_lite.html` rebuilt from the startup snapshot, with the agreed "delete the old file… press Reconnect" dialog and the "(1)" warning.
    - **Snapshot:** taken as the first statement of the last script. Its `<html>` tag is reset to `<html lang="en">` so the theme attributes the head script added are never baked in.
    - **Saves folder:** linking the folder that holds Lite also makes Apply work in place, and quiz files then go to `<folder>/saves/`. Any other folder gets them at its root. On getting permission, a newer folder copy of the current quiz is taken.
    - **Download for offline use** (full app, Home footer): fetches `lite.html`, bakes in the `LITE_KEYS` subset of the current settings plus a fresh nonce, downloads it, and shows a toast suggesting a dedicated "Quiz Qrusher Lite" folder. It needs http(s); from `file://` it says so.
    - **Harness:** 180 checks. The Lite ones cover the hosted flow, baked settings from a file (blob URL stand-in), a rebuilt copy that loads and runs, in-place Apply through the OPFS fake folder, the browser notice, and Download for offline use.
    - **Still to test by hand (Phase 10):** a real `file://` Apply in Chrome/Edge (link Lite's folder, change a setting, Apply → reload), and Firefox `file://` storage sharing between an old and a replaced Lite file.
- [ ] **7. Content tabs:**
  - Help (+ What's new, Privacy)
  - Feedback (Form iframe; placeholder until the link arrives)
  - prompts zip + Home footer
  - GoatCounter (placeholder code until the account exists)
- [ ] **8. PWA:** manifest, service worker (versioned cache, update toast), icons.
- [ ] **9. Prompt Builder** (generic subject templates).
- [ ] **10. Release:**
  - test in Chrome, Edge, Firefox and Safari (desktop + iPad if possible), both from the site and opened from disk
  - tag `v3.0.0`
  - update the "What's new" page
  - remove "preview build" from the Home footer

---

## 5. Open items (ask the user when you reach them)
1. **Google Form link (Phase 7):** the user is creating it. If prefilling is wanted, the form needs "App version" and "Browser" short-answer fields. Use a placeholder until the link arrives.
2. **GoatCounter site code (Phase 7):** the user needs an account at goatcounter.com. Use a placeholder until then.

Resolved on 2026-10-14:
- `gh` is logged in.
- Use the noreply commit email.
- No backdating.
- `test-data/csv/` and `docs/guides/` stay private.
- Show-answer scoring is decided.
- Lite non-Chrome saving is browser storage plus downloaded JSON (trial).
- Show answer after a **correct** answer counts as **correct** (confirmed 2026-10-14; built that way in Phase 3).
- The download prompt fires on Submit, plus an optional interval set in Settings.
- Lite Apply fallback message: "Delete the old Lite file and put this one in its place, then reopen it and press Reconnect (Chrome/Edge)." Relinking isn't needed (Phase 1). Also warn that the browser may save the file as `... (1).html`.
- **Save status is just a green ✓** (full app and Lite). "Saved in browser · just now" appears on hover or keyboard focus, and the check carries it as its `aria-label`. Warnings (⚠) always show their full text. (User request, 2026-10-14.)
- **Tutor mode toggle is an iOS-style switch** inside the dock tab: a vertical "TUTOR MODE" label above a **vertical** switch whose knob slides down and turns green when on. Off = Test mode. The dock is a column on the right edge with the Tutor tab **above** NOTES, and above the notes panel when it's open, so it never covers the quiz. (User requests, 2026-10-14.)
- **Quiz screen:** no "Options shuffled" label. The spot only shows the Tutor-mode note. (User request, 2026-10-14.)
- **App bar spans the full window width, nothing centered:** "Quiz Qrusher", Home and Prompt Builder at the left edge; Feedback, Help and a ⚙ Settings cog at the right edge, in that order. Page content below stays in the centered column. (User request, 2026-10-14. The user wrote "Home and Prompt Builder on the right", read as left because the right group is Feedback/Help/cog; confirm if wrong.)
- **The Reconnect button must be hard to miss** (full app and Lite): a prominent accent-colored button in the quiz header/status line, plus a banner on Home and on quiz open whenever a linked folder needs permission. Never just a small text link.
