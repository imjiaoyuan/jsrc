import json

from jsrc.text.core import read_text


def cmd(args):
    text = read_text(args.input)
    lines = text.count("\n")
    if text and not text.endswith("\n"):
        lines += 1
    words = len(text.split())
    chars = len(text)
    payload = {
        "lines": lines,
        "words": words,
        "chars": chars,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    print(f"lines\t{lines}")
    print(f"words\t{words}")
    print(f"chars\t{chars}")
