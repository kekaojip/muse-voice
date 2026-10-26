#!/usr/bin/env bash
# Fetch a pre-installed sticker pack from ChineseBQB (zhaoolee/ChineseBQB)
# and install it under stickers/packs/<pack>/ with a manifest.json.
#
# Usage:
#   ./scripts/fetch-stickers.sh huaji
#   ./scripts/fetch-stickers.sh huaji <target_dir>
#
# Known packs (pack id -> ChineseBQB category folder):
#   huaji -> 001Funny_滑稽大佬😏BQB (125 stickers, ~5MB)
# To add another pack, pass its category folder as $3, or add a line below.
#
# The images are NOT bundled in this repo: they are fetched on demand
# from the open data source at install time, so the repo stays light.
# ChineseBQB's images are collected from the internet and the repo has
# no LICENSE file — only fetch packs you are comfortable redistributing,
# and credit the source in the pack manifest.
set -euo pipefail

PACK_ID="${1:-huaji}"
TARGET="${2:-stickers/packs/$PACK_ID}"
CATEGORY="${3:-}"

case "$PACK_ID" in
  huaji) CATEGORY="${CATEGORY:-001Funny_滑稽大佬😏BQB}"; PACK_NAME="滑稽大佬" ;;
  *) echo "unknown pack '$PACK_ID' — pass the ChineseBQB category folder as \$3"; exit 2 ;;
esac

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "Fetching $PACK_ID ($CATEGORY) from ChineseBQB..."
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/zhaoolee/ChineseBQB.git "$TMP/ChineseBQB" -q
git -C "$TMP/ChineseBQB" sparse-checkout set "$CATEGORY" -q

mkdir -p "$TARGET"
cp "$TMP/ChineseBQB/$CATEGORY"/* "$TARGET"/

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$SCRIPT_DIR/make-sticker-manifest.py" "$TARGET" "$PACK_ID" "$PACK_NAME" \
  "zhaoolee/ChineseBQB category $CATEGORY"
du -sh "$TARGET"
