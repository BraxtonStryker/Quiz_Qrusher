"""v3.0 - keeps the QQ-SHARED blocks of index.html and lite.html identical (CLAUDE.md "Code conventions").

Usage (from the repo root):
  python -I test-data/harness/check_shared.py          check: exit 1 and list every block that differs
  python -I test-data/harness/check_shared.py --sync   copy every shared block (and the CSS) from index.html into lite.html

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


def main():
    index = open("index.html", encoding="utf-8").read()
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
    if bad or missing or leftover:
        sys.exit(1)
    print("shared blocks match:", ", ".join(sorted(have)))


main()
