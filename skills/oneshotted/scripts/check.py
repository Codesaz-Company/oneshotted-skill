#!/usr/bin/env python3
"""Measure a rendered video before anyone watches it: the problems eyes on a contact sheet miss.

    python3 scripts/check.py out/video.mp4 [--sheet out/qa/sheet.jpg] [--first out/qa/first.jpg]

Checks (thresholds are the measured norms of top launch films; move them only with a written reason):
  first-change   something visibly changes by 0.43 s (median 0.10 s): a still opening reads as a stalled player
  first-second   the first second averages real motion (not a held title card)
  dead-hold      no run of near-still frames longer than 1.6 s mid-film; the end card may hold up to
                 max(2.5 s, 15% of the runtime) (measured end cards: 0.9-3.9 s, 2-13% of runtime)
  black          no fully black frame except the very last
  pop            no single-frame flash: a frame that differs a lot from both neighbours, which differ little
  spec           with --expect WxH@fps:seconds, the file really is that size, rate and length (+-0.25 s)
Writes a contact sheet and a strip of the first 3 s (at 0, .17, .33, .5, 1, 1.5, 2, 3 s) to look at.
Needs ffmpeg/ffprobe on PATH; standard library only. Exit code 1 when a check fails.
Technique credit: Cinetic (github.com/Leonxlnx/cinetic, MIT), forensics.py / sheet.py.
"""
import argparse, json, subprocess, sys

W, H = 160, 90  # analysis size: enough to see change, cheap to decode


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate,width,height,duration:format=duration',
                          '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = d['streams'][0]
    num, den = st['r_frame_rate'].split('/')
    return float(num) / float(den), float(st.get('duration') or d['format']['duration']), st['width'], st['height']  # the picture's length, not the audio's


def frames(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={W}:{H}:flags=area,format=gray', '-f', 'rawvideo', '-'],
                         stdout=subprocess.PIPE)
    size = W * H
    while True:
        b = p.stdout.read(size)
        if len(b) < size:
            break
        yield b


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('video'); a.add_argument('--sheet'); a.add_argument('--first')
    a.add_argument('--still', type=float, default=0.5, help='mean abs luma change (0-255) below which a frame counts as near-still')
    a.add_argument('--max-hold', type=float, default=1.6); a.add_argument('--max-end', type=float, default=2.5)
    a.add_argument('--first-change', type=float, default=0.43)
    a.add_argument('--expect', help='spec to verify, e.g. 1920x1080@30:20')
    o = a.parse_args()
    fps, dur, w, h = probe(o.video)

    diffs, means, prev = [], [], None
    for b in frames(o.video):
        means.append(sum(b) / len(b))
        diffs.append(0.0 if prev is None else sum(abs(x - y) for x, y in zip(b, prev)) / len(b))
        prev = b
    n = len(diffs)
    if n < 2:
        sys.exit(f'{o.video}: no readable frames')
    fail = []

    first = next((i for i, d in enumerate(diffs[1:], 1) if d >= 1.0), None)
    t_first = (first / fps) if first is not None else dur
    if t_first > o.first_change:
        fail.append(f'first-change: nothing visibly moves until {t_first:.2f} s (want <= {o.first_change} s)')
    f1 = diffs[1:int(fps) + 1]
    if f1 and sum(f1) / len(f1) < 1.0:
        fail.append(f'first-second: average change {sum(f1) / len(f1):.2f} in the first second, a held card (want >= 1.0)')

    holds, run = [], 0  # every near-still run: (start frame, length)
    for i, d in enumerate(diffs[1:], 1):
        if d < o.still:
            run += 1
        elif run:
            holds.append((i - run, run)); run = 0
    if run:
        holds.append((n - run, run))
    worst = max((r for _, r in holds), default=0)
    for start, r in holds:
        end_card = start + r >= n
        limit = max(o.max_end, 0.15 * dur) if end_card else o.max_hold
        if r / fps > limit:
            fail.append(f"dead-hold: {r / fps:.2f} s near-still from {start / fps:.2f} s{' (end card)' if end_card else ''} (want <= {limit} s)")

    blacks = [i for i, m in enumerate(means[:-1]) if m < 4]
    if blacks:
        fail.append(f'black: {len(blacks)} black frame(s), first at {blacks[0] / fps:.2f} s')
    # A flash: frame i jumps away and i+1 jumps back, while its neighbours are calm (a fast camera move is not a pop).
    calm = lambda j: 0 <= j < n and diffs[j] < 6
    pops = [i for i in range(2, n - 2) if diffs[i] > 25 and diffs[i + 1] > 25 and abs(means[i - 1] - means[i + 1]) < 3 and calm(i - 1) and calm(i + 2)]
    if pops:
        fail.append(f'pop: single-frame flash at {", ".join(f"{p / fps:.2f}s" for p in pops[:5])}')

    if o.expect:
        try:
            size, rest = o.expect.split('@'); ew, eh = (int(x) for x in size.split('x')); ef, es = rest.split(':')
            if (w, h) != (ew, eh) or abs(fps - float(ef)) > 0.01 or abs(dur - float(es)) > 0.25:
                fail.append(f'spec: file is {w}x{h}@{fps:g} for {dur:.2f} s, expected {o.expect}')
        except ValueError:
            sys.exit('--expect looks like 1920x1080@30:20')

    near = sum(1 for d in diffs[1:] if d < o.still) / max(1, n - 1)
    print(f'{o.video}: {w}x{h}, {dur:.2f} s, {fps:g} fps, {n} frames; first change {t_first:.2f} s; near-still {near:.0%}; '
          f'longest hold {worst / fps:.2f} s; median change {sorted(diffs[1:])[(n - 1) // 2]:.2f}')

    if o.sheet:
        step = max(dur / 16, 0.1)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', o.video, '-vf', f'fps=1/{step},scale=480:-1,tile=4x4', '-frames:v', '1', o.sheet], check=True)
        print('sheet:', o.sheet)
    if o.first:
        sel = '+'.join(f'eq(n\\,{round(t * fps)})' for t in (0, 1 / 6, 1 / 3, 0.5, 1, 1.5, 2, 3))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', o.video, '-vf', f"select='{sel}',scale=480:-1,tile=4x2", '-frames:v', '1', o.first], check=True)
        print('first 3 s:', o.first)

    for f in fail:
        print('FAIL', f)
    print('PASS' if not fail else f'{len(fail)} check(s) failed')
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
