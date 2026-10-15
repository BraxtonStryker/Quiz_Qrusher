"""v3.0 - keeps the QQ-SHARED blocks of index.html and lite.html identical (CLAUDE.md "Code conventions").

Usage (from the repo root):
  python -I test-data/harness/check_shared.py          check: exit 1 and list every block that differs
  python -I test-data/harness/check_shared.py --sync   copy every shared block (and the CSS) from index.html into lite.html,
                                                       and regenerate index.html's embedded prompts + prompts/medical/medical_prompts.zip
                                                       from prompts/medical/*.md

index.html is the source of truth. lite.html carries index.html's whole <style> contents inside a
"QQ-SHARED:css" fence, followed by its own Lite-only CSS. On the very first run, the /*@@CSS@@*/ and
/*@@SHARED:<name>@@*/ markers in lite.html are filled in.
"""
import re
import sys

BLOCK = re.compile(r"(?ms)^[ \t]*/\* === QQ-SHARED:([\w-]+) === \*/.*?/\* === /QQ-SHARED === \*/")


def blocks(text):
    return {m.group(1): m.group(0) for m in BLOCK.finditer(text)}


def index_css(text):
    a = text.index("<style>") + len("<style>\n")
    b = text.index("</style>")
    return "  /* === QQ-SHARED:css === */ /* index.html's whole stylesheet; Lite-only rules follow */\n" + text[a:b].rstrip("\n") + "\n  /* === /QQ-SHARED === */"


PROMPT_DIR = "prompts/medical"
PROMPT_ORDER = ["slide_miner_v1.md", "data_sanitizer_v2.md", "style_researcher_v2.md", "que_generator_v3.md"]
PROMPTS_BLOCK = re.compile(r"(?s)/\* === PROMPTS:medical === \*/\n.*?\n(\s*)/\* === /PROMPTS === \*/")
ZIP_PATH = PROMPT_DIR + "/medical_prompts.zip"


def prompt_texts():
    import os
    names = PROMPT_ORDER + sorted(n for n in os.listdir(PROMPT_DIR) if n.endswith(".md") and n not in PROMPT_ORDER)
    return [(n, open(PROMPT_DIR + "/" + n, encoding="utf-8").read().replace("\r\n", "\n")) for n in names]


def prompts_js(texts):
    import json
    body = json.dumps(dict(texts), ensure_ascii=False, indent=2).replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    body = body.replace("\n", "\n  ")
    return "/* === PROMPTS:medical === */\n  var PROMPTS = " + body + "; // generated from prompts/medical by test-data/harness/check_shared.py --sync\n  /* === /PROMPTS === */"


def build_zip(texts):
    """Store-deflated zip with fixed timestamps, so rebuilding with unchanged prompts gives the same bytes."""
    import io, zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in texts:
            info = zipfile.ZipInfo("medical_prompts/" + name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, text.encode("utf-8"))
    return buf.getvalue()


def prompts_step(index, sync):
    """Returns (index text, list of problems). The .md files are the source of truth for prompts."""
    texts = prompt_texts()
    want = prompts_js(texts)
    problems = []
    m = PROMPTS_BLOCK.search(index)
    if not m:
        return index, ["index.html has no PROMPTS:medical block"]
    if sync:
        index = index[:m.start()] + want + index[m.end():]
        open("index.html", "w", encoding="utf-8", newline="").write(index)
        open(ZIP_PATH, "wb").write(build_zip(texts))
    elif m.group(0) != want:
        problems.append("index.html PROMPTS block is out of date with " + PROMPT_DIR)
    try:
        if open(ZIP_PATH, "rb").read() != build_zip(texts):
            problems.append(ZIP_PATH + " is out of date")
    except OSError:
        problems.append(ZIP_PATH + " is missing")
    return index, problems


def main():
    index = open("index.html", encoding="utf-8").read()
    index, prompt_problems = prompts_step(index, "--sync" in sys.argv)
    for pr in prompt_problems:
        print(pr)
    lite = open("lite.html", encoding="utf-8").read()
    src = blocks(index)
    src["css"] = index_css(index)
    sync = "--sync" in sys.argv

    if sync:
        lite = lite.replace("/*@@CSS@@*/", src["css"].lstrip())
        for name, body in src.items():
            lite = lite.replace("/*@@SHARED:%s@@*/" % name, body)
        have = blocks(lite)
        for name, body in have.items():
            if name in src and body != src[name]:
                lite = lite.replace(body, src[name])
        open("lite.html", "w", encoding="utf-8", newline="").write(lite)

    have = blocks(lite)
    bad = [n for n in have if n in src and have[n] != src[n]]
    missing = [n for n in src if n not in have]
    leftover = re.findall(r"/\*@@[\w:-]+@@\*/", lite)
    for n in bad:
        print("DIFFERS:", n)
    for n in missing:
        print("missing in lite.html:", n)
    for m in leftover:
        print("unfilled marker:", m)
    if bad or missing or leftover or prompt_problems:
        sys.exit(1)
    print("shared blocks match:", ", ".join(sorted(have)))


main()
