"""v3.0 - keeps the QQ-SHARED blocks of index.html and lite.html identical (CLAUDE.md "Code conventions").

Usage (from the repo root):
  python -I test-data/harness/check_shared.py          check: exit 1 and list every block that differs
  python -I test-data/harness/check_shared.py --sync   copy every shared block (and the CSS) from index.html into lite.html,
                                                       and regenerate index.html's embedded prompts + prompts/medical/medical_prompts.zip
                                                       from prompts/medical/*.md, the Prompt Builder templates from prompts/templates/*.md,
                                                       and the other premade prompt sets (v3.1) from prompts/<set>/*.md

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


TEMPLATE_DIR = "prompts/templates"
TEMPLATE_ORDER = ["slide_miner.md", "data_sanitizer.md", "style_researcher.md", "que_generator.md"]
TEMPLATES_BLOCK = re.compile(r"(?s)/\* === PROMPTS:templates === \*/\n.*?\n(\s*)/\* === /PROMPTS === \*/")

# v3.1 - the other premade prompt sets, picked from the dropdown at the top of Help: (block name, JS variable, folder).
# Their text uses the blank [COURSE OR TOPIC], which the app fills in from Help's "Your class or topic" box.
SET_ORDER = ["slide_miner.md", "data_sanitizer.md", "style_researcher.md", "que_generator.md"]
PROMPT_SETS = [("dental", "PROMPTS_DENTAL", "prompts/dental"), ("premed", "PROMPTS_PREMED", "prompts/premed"),
               ("ee", "PROMPTS_EE", "prompts/ee"), ("me", "PROMPTS_ME", "prompts/me")]


def prompt_texts(folder=PROMPT_DIR, order=PROMPT_ORDER):
    import os
    names = order + sorted(n for n in os.listdir(folder) if n.endswith(".md") and n not in order and n != "README.md")
    return [(n, open(folder + "/" + n, encoding="utf-8").read().replace("\r\n", "\n")) for n in names]


def prompts_js(texts, block="medical", var="PROMPTS", folder=PROMPT_DIR):
    import json
    body = json.dumps(dict(texts), ensure_ascii=False, indent=2).replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    body = body.replace("\n", "\n  ")
    return ("/* === PROMPTS:" + block + " === */\n  var " + var + " = " + body + "; // generated from " + folder +
            " by test-data/harness/check_shared.py --sync\n  /* === /PROMPTS === */")


def templates_step(index, sync):
    """Prompt Builder templates: prompts/templates/*.md -> index.html's PROMPTS:templates block."""
    want = prompts_js(prompt_texts(TEMPLATE_DIR, TEMPLATE_ORDER), "templates", "PROMPT_TEMPLATES", TEMPLATE_DIR)
    m = TEMPLATES_BLOCK.search(index)
    if not m:
        return index, ["index.html has no PROMPTS:templates block"]
    if sync:
        index = index[:m.start()] + want + index[m.end():]
        open("index.html", "w", encoding="utf-8", newline="").write(index)
        return index, []
    return index, ([] if m.group(0) == want else ["index.html PROMPTS:templates block is out of date with " + TEMPLATE_DIR])


def sets_step(index, sync):
    """v3.1 - premade prompt sets: prompts/<set>/*.md -> index.html's PROMPTS:<set> blocks."""
    problems = []
    for block, var, folder in PROMPT_SETS:
        want = prompts_js(prompt_texts(folder, SET_ORDER), block, var, folder)
        m = re.search(r"(?s)/\* === PROMPTS:" + block + r" === \*/\n.*?\n(\s*)/\* === /PROMPTS === \*/", index)
        if not m:
            problems.append("index.html has no PROMPTS:" + block + " block")
        elif sync:
            index = index[:m.start()] + want + index[m.end():]
        elif m.group(0) != want:
            problems.append("index.html PROMPTS:" + block + " block is out of date with " + folder)
    if sync:
        open("index.html", "w", encoding="utf-8", newline="").write(index)
    return index, problems


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
    index, template_problems = templates_step(index, "--sync" in sys.argv)
    prompt_problems += template_problems
    index, set_problems = sets_step(index, "--sync" in sys.argv)   #v3.1
    prompt_problems += set_problems
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
    sw_problems = sw_step(sync)   # last: it hashes the files the steps above may have rewritten
    for pr in sw_problems:
        print(pr)
    if bad or missing or leftover or prompt_problems or sw_problems:
        sys.exit(1)
    print("shared blocks match:", ", ".join(sorted(have)))


SW_VERSION = re.compile(r'const VERSION = "([^"]*)";')


def sw_step(sync):
    """sw.js VERSION = hash of every file it precaches, so any change to them ships as a new app version."""
    import hashlib
    sw = open("sw.js", encoding="utf-8").read()
    listed = re.search(r"const PRECACHE = \[(.*?)\];", sw, re.S)
    if not listed:
        return ["sw.js has no PRECACHE list"]
    h = hashlib.sha256()
    for path in re.findall(r'"([^"]+)"', listed.group(1)):
        path = "index.html" if path == "./" else path
        try:
            h.update(path.encode() + b"\0" + open(path, "rb").read())
        except OSError:
            return ["sw.js precaches a missing file: " + path]
    want = h.hexdigest()[:12]
    have = SW_VERSION.search(sw)
    if sync:
        sw = SW_VERSION.sub('const VERSION = "%s";' % want, sw, count=1)
        open("sw.js", "w", encoding="utf-8", newline="").write(sw)
        return []
    if not have or have.group(1) != want:
        return ["sw.js VERSION is stale (run --sync): has %s, files say %s" % (have.group(1) if have else "none", want)]
    return []


main()
