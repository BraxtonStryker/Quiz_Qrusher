# QuizQrusher

Turn your course material into multiple-choice practice quizzes. AI models write the questions as a CSV; QuizQrusher runs the quiz, grades it, shows your weak categories, and writes a follow-up request aimed at what you missed. The same CSV also works in [CwikCard](https://braxtonstryker.github.io/CwikCard/) as flashcards.

**Use it:** https://braxtonstryker.github.io/Quiz_Qrusher/

- **Full app:** a library of question banks, autosave, resume and review, Tutor mode, a timer, retakes of missed or flagged questions, category trends, settings, and Help. It can be installed as an app and then works offline. In Chrome or Edge on a computer it can also save every quiz to a folder you choose.
- **Lite:** a single offline file that keeps one quiz at a time ([lite.html](https://braxtonstryker.github.io/Quiz_Qrusher/lite.html), or **Download for offline use** on Home).
- **Prompts:** ready-made prompt sets for [medical school](prompts/medical/), [dental school](prompts/dental/), [pre-med biology and chemistry](prompts/premed/), [electrical engineering](prompts/ee/) and [mechanical engineering](prompts/me/), picked at the top of Help. The in-app **Prompt Builder** makes the same four prompts for any other subject.

Everything stays in your browser (and your saves folder, if you link one). Nothing is uploaded.

## Question CSV format

```
Category,Question_Text,Option_1,Option_2,Option_3,Option_4,Option_5,Option_6,Correct_Option_Number
```

`Correct_Option_Number` is 1 to 6. Header matching is lenient (case, spaces and annotations like "(1-6)" are ignored).

## Repository

- `index.html`, `lite.html`, `sw.js`, `manifest.webmanifest`, `icons/`: the site. Single-file HTML apps with no build step.
- `versions/`: every earlier release (v1 to v2.3.3); the git tags mark each one.
- `prompts/`: the AI pipeline prompts (`medical/`) and the Prompt Builder's templates (`templates/`).
- `test-data/harness/`: a headless-browser regression suite and the `check_shared.py` consistency check. See [CLAUDE.md](CLAUDE.md) for development notes and [docs/V3_PLAN.md](docs/V3_PLAN.md) for the v3 design.

Feedback: use the **Feedback** tab in the app.
