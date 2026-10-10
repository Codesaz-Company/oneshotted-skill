#!/bin/sh
# Renders the template film with the example content and requires check.py to PASS. Run on a machine with
# Node, Chromium and ffmpeg, inside a fresh `npx create-video@latest` project (its strict tsconfig is part of the test).
# Usage: sh tests/film_check.sh <remotion-project-dir>
set -eu
S="$(cd "$(dirname "$0")/.." && pwd)/skills/oneshotted"
P="$1"
rm -rf "$P/src/kit" && cp -R "$S/assets/kit" "$P/src/kit"
cp "$S/assets/kit/Root.example.tsx.txt" "$P/src/Root.tsx"
cp "$S/assets/kit/content.example.ts.txt" "$P/src/content.ts"
mkdir -p "$P/public"
ffmpeg -v error -y -f lavfi -i "testsrc2=s=1920x1080" -frames:v 1 "$P/public/shot-2.png"   # a viewport-sized capture, like scroll-000.png
(cd "$P" && npx tsc --noEmit && npx remotion render src/index.ts Main out/film-check.mp4 --log=error)
python3 "$S/scripts/check.py" "$P/out/film-check.mp4" --expect 1920x1080@30:19
