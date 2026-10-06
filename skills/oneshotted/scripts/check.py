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
  decode         every frame the file claims decodes (a truncated render fails)
  spec           with --expect WxH@fps:seconds, the file really is that size, rate and length (+-0.25 s)
  sparse (warn)  over 0.5 s (the end card excepted) where everything with an edge fits in a box under a quarter of the frame: a
                 blank between beats, or a logo or a lone word on an empty field (flat or gradient). It doesn't see
                 small things spread far apart (a headline at the top, a chip in the middle): that is the critic's
                 job. A warning, not a failure: look at those moments, fill them or say why they stay.
Writes a contact sheet and a strip of the first 3 s (at 0, .17, .33, .5, 1, 1.5, 2, 3 s) to look at.
Needs ffmpeg/ffprobe on PATH; standard library only. Exit code 1 when a check fails.
Technique credit: Cinetic (github.com/Leonxlnx/cinetic, MIT), forensics.py / sheet.py.
"""
import argparse, json, subprocess, sys

W, H = 160, 90  # analysis size: enough to see change, cheap to decode


def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate,width,height,duration:stream_tags=DURATION:format=duration',
                          '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = d['streams'][0]
    num, den = st['r_frame_rate'].split('/')
    tag = st.get('tags', {}).get('DURATION')  # Matroska/WebM keep the picture's length only here (00:00:03.000000000)
    try:
        own = float(st['duration']) if st.get('duration') else sum(float(x) * 60 ** i for i, x in enumerate(reversed(tag.split(':')))) if tag else None
    except ValueError:
        own = None  # a junk tag: fall back to the container's length
    # The picture's length, not the audio's. `exact` is False when only the container's length is known.
    # ponytail: Matroska from muxers that write no DURATION tag skips the decode check; ffmpeg/Remotion/HyperFrames write it.
    return float(num) / float(den), own or float(d['format']['duration']), st['width'], st['height'], bool(own)


def frames(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'scale={W}:{H}:flags=area,format=gray', '-f', 'rawvideo', '-'],
                         stdout=subprocess.PIPE)
    size = W * H
    while True:
        b = p.stdout.read(size)
        if len(b) < size:
            break
        yield b


def coverage(path, rate):
    """Per sampled frame: the share of the frame inside the box around everything with an edge, and its edge-pixel share.
    Edges come from a Sobel filter: a card gives its outline, text gives its strokes, a flat or gradient field gives nothing."""
    cw, ch = 480, 270  # finer than W, H: hairlines and small UI text average away at 160x90
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={rate},scale={cw}:{ch}:flags=area,format=gray,sobel',
                          '-f', 'rawvideo', '-'], stdout=subprocess.PIPE)
    tbl = bytes(1 if v > 24 else 0 for v in range(256))
    while True:
        b = p.stdout.read(cw * ch)
        if len(b) < cw * ch:
            break
        m = b.translate(tbl)
        rows = [(r, m[r * cw:(r + 1) * cw]) for r in range(ch)]
        rows = [(r, row) for r, row in rows if row.count(1) >= 2]  # a stray pixel is noise
        if not rows:
            yield 0.0, 0.0
            continue
        lefts = sorted(row.find(1) for _, row in rows); rights = sorted(row.rfind(1) for _, row in rows)
        k = len(rows) // 20  # ignore the outermost 5% of rows' extremes
        w = rights[-1 - k] - lefts[k] + 1; h = rows[-1 - k][0] - rows[k][0] + 1
        yield max(0, w) * h / (cw * ch), m.count(1) / (cw * ch)
    if p.wait():
        raise RuntimeError('ffmpeg could not measure the frames')

def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument('video'); a.add_argument('--sheet'); a.add_argument('--first')
    a.add_argument('--still', type=float, default=0.5, help='mean abs luma change (0-255) below which a frame counts as near-still')
    a.add_argument('--max-hold', type=float, default=1.6); a.add_argument('--max-end', type=float, default=2.5)
    a.add_argument('--first-change', type=float, default=0.43)
    a.add_argument('--expect', help='spec to verify, e.g. 1920x1080@30:20')
    o = a.parse_args()
    try:
        fps, dur, w, h, exact = probe(o.video)
    except (subprocess.CalledProcessError, KeyError, IndexError, ValueError, ZeroDivisionError):
        sys.exit(f'{o.video}: not a readable video')

    diffs, means, prev = [], [], None
    for b in frames(o.video):
        means.append(sum(b) / len(b))
        diffs.append(0.0 if prev is None else sum(abs(x - y) for x, y in zip(b, prev)) / len(b))
        prev = b
    n = len(diffs)
    if n < 2:
        sys.exit(f'{o.video}: {n} readable frame(s), too short to measure')
    fail = []
    if exact and n < 0.95 * dur * fps:
        fail.append(f'decode: only {n} of ~{round(dur * fps)} frames decode (a truncated or corrupt file)')

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

    warn, run, rate = [], 0, 10  # sampled at 10 fps; ponytail: luma edges only, colour-on-colour of equal brightness reads as empty
    try:
        cover = list(coverage(o.video, rate))
    except RuntimeError as e:
        cover = []; warn.append(f'sparse: not measured ({e})')
    if exact and cover and len(cover) < 0.95 * dur * rate:
        warn.append(f'sparse: measured only {len(cover) / rate:.1f} s of {dur:.1f} s')
    for i, (c, _) in enumerate(cover + [(1.0, 0)]):
        if c < 0.25:
            run += 1
        else:
            end_card = i == len(cover) and run / rate <= max(o.max_end, 0.15 * dur)  # a logo lockup may close the film
            if run / rate > 0.5 and not end_card:
                least = min(x for x, _ in cover[i - run:i])
                warn.append(f'sparse: {run / rate:.1f} s from {(i - run) / rate:.1f} s where the content fits in {least:.0%} of the frame (want >= 25%)')
            run = 0

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

    for x in warn:
        print('WARN', x)
    for f in fail:
        print('FAIL', f)
    print('PASS' if not fail else f'{len(fail)} check(s) failed')
    sys.exit(1 if fail else 0)


if __name__ == '__main__':
    main()
