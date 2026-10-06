#!/bin/sh
# Self-check for scripts/check.py's sparse warning on tiny synthetic clips (needs ffmpeg). Exit 1 on a wrong verdict.
set -eu
C="$(cd "$(dirname "$0")/.." && pwd)/skills/oneshotted/scripts/check.py"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
# clip <name> <background lavfi> <card colour> <card w> <card h>: a moving card (overlay animates; drawbox's t does not everywhere)
clip() { ffmpeg -v error -y -f lavfi -i "$2" -f lavfi -i "color=$3:s=${4}x$5" \
  -filter_complex "[0][1]overlay=x='(W-w)/2-20+t*14':y='(H-h)/2':shortest=1" -t 3 -r 30 -pix_fmt yuv420p "$T/$1.mp4"; }
white="color=white:s=320x180"; grad="gradients=s=320x180:c0=0x1e1b4b:c1=0x7c3aed:speed=0.02"
clip card9-white "$white" black 96 54          # 9% of the frame
clip card20-white "$white" black 144 81        # 20%
clip card9-gradient "$grad" white 96 54
clip card45-white "$white" black 216 121       # 45%: full enough
clip card45-gradient "$grad" white 216 121
ffmpeg -v error -y -f lavfi -i "$grad" -t 3 -r 30 -pix_fmt yuv420p "$T/blank-gradient.mp4"
ffmpeg -v error -y -f lavfi -i "testsrc2=s=320x180" -t 3 -r 30 -pix_fmt yuv420p "$T/full.mp4"
ffmpeg -v error -y -f lavfi -i "testsrc2=s=320x180" -vf "drawbox=c=white:t=fill:enable='between(t,1,2)'" -t 4 -r 30 -pix_fmt yuv420p "$T/blank-mid.mp4"
ffmpeg -v error -y -f lavfi -i "testsrc2=s=320x180" -vf "drawbox=c=white:t=fill:enable='gt(t,2)'" -t 4 -r 30 -pix_fmt yuv420p "$T/end-card.mp4"
# The clips must really contain the card: its frame is not uniform.
ffmpeg -v error -i "$T/card9-white.mp4" -vf "select='eq(n,30)',signalstats,metadata=print:key=lavfi.signalstats.YMIN:file=-" -f null - 2>/dev/null \
  | grep -Eq 'YMIN=(1?[0-9]|2[0-9])$' \
  || { echo "FAIL fixture: card9-white has no dark card"; exit 1; }
fail=0
want() { out=$(python3 "$C" "$T/$1.mp4" 2>&1 || true)
  if echo "$out" | grep -q 'WARN sparse'; then got=warn; else got=quiet; fi
  [ "$got" = "$2" ] && echo "ok   $1: $got" || { echo "FAIL $1: want $2, got $got"; echo "$out" | sed 's/^/     /'; fail=1; }; }
want card9-white warn; want card20-white warn; want card9-gradient warn; want blank-gradient warn; want blank-mid warn
want card45-white quiet; want card45-gradient quiet; want full quiet; want end-card quiet
python3 "$C" "$T/full.mp4" | tail -1 | grep -q PASS && echo "ok   full: PASS" || { echo "FAIL full: not PASS"; fail=1; }
python3 "$C" "$T/missing.mp4" 2>&1 | grep -q 'not a readable video' && echo "ok   missing file: clear error" || { echo "FAIL missing file"; fail=1; }
# A truncated render must fail, not PASS on the frames that survive.
ffmpeg -v error -y -f lavfi -i "testsrc2=s=320x180" -t 6 -r 30 -pix_fmt yuv420p -movflags +faststart "$T/long.mp4"
head -c $(( $(wc -c < "$T/long.mp4") / 3 )) "$T/long.mp4" > "$T/cut.mp4"
python3 "$C" "$T/cut.mp4" 2>&1 | grep -Eq 'FAIL decode|not a readable video' && echo "ok   truncated: fails" || { echo "FAIL truncated file passed"; fail=1; }
# Light-mode UI: a pale bordered panel with small grey text filling ~60% of the frame is content, not empty.
ffmpeg -v error -y -f lavfi -i "color=white:s=1920x1080" -vf "drawbox=x=380:y=200:w=1160:h=680:c=0xececec:t=2,$(i=0; while [ $i -lt 14 ]; do printf "drawbox=x=%d:y=%d:w=%d:h=6:c=0x9a9a9a:t=fill," $((420 + (i % 3) * 20)) $((240 + i * 44)) $((600 - (i % 4) * 90)); i=$((i+1)); done)scroll=h=0.002" -t 3 -r 30 -pix_fmt yuv420p "$T/light-ui.mp4"
want light-ui quiet
# WebM with music past the picture: the container is 6 s, the picture 3 s. Not a truncated file.
ffmpeg -v error -y -f lavfi -i "testsrc2=s=320x180:r=30" -f lavfi -i "sine=d=6" -t 3 -map 0:v -c:v libvpx-vp9 -deadline realtime -cpu-used 8 "$T/v.webm"
ffmpeg -v error -y -i "$T/v.webm" -f lavfi -i "sine=d=6" -map 0:v -map 1:a -c:v copy -c:a libopus "$T/tail.webm"
python3 "$C" "$T/tail.webm" 2>&1 | grep -q 'FAIL decode' && { echo "FAIL webm with an audio tail fails decode"; fail=1; } || echo "ok   webm audio tail: no false decode FAIL"
exit $fail
