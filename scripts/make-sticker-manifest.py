#!/usr/bin/env python3
"""Build stickers/<pack>/manifest.json from the image files in a pack directory.

Usage:
    python3 make-sticker-manifest.py <pack_dir> <pack_id> <pack_name> [source]

Label rule: filename without extension, with a leading
"<pack_name><digits>-" prefix stripped when present, e.g.
"滑稽大佬00001-360度鄙视你.gif" -> "360度鄙视你".
"""
import json
import os
import re
import sys

IMAGE_EXTS = (".gif", ".jpg", ".jpeg", ".png", ".webp")


def label_for(filename, pack_name):
    base = os.path.splitext(filename)[0]
    stripped = re.sub(r"^" + re.escape(pack_name) + r"\d+-", "", base)
    return stripped if stripped else base


def main():
    if len(sys.argv) < 4:
        print("usage: make-sticker-manifest.py <pack_dir> <pack_id> <pack_name> [source]")
        sys.exit(2)
    pack_dir, pack_id, pack_name = sys.argv[1], sys.argv[2], sys.argv[3]
    source = sys.argv[4] if len(sys.argv) > 4 else ""
    files = sorted(
        f
        for f in os.listdir(pack_dir)
        if os.path.isfile(os.path.join(pack_dir, f))
        and f.lower().endswith(IMAGE_EXTS)
    )
    stickers = [
        {"file": f, "label": label_for(f, pack_name), "mood": "", "keywords": [label_for(f, pack_name)]}
        for f in files
    ]
    manifest = {
        "pack": pack_id,
        "name": pack_name,
        "source": source,
        "source_url": "https://github.com/zhaoolee/ChineseBQB",
        "stickers": stickers,
    }
    out = os.path.join(pack_dir, "manifest.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print(f"{len(stickers)} stickers -> {out}")


if __name__ == "__main__":
    main()
