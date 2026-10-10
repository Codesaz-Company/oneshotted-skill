# The critic loop: the builder never grades its own work

A fresh agent that did not build the video judges only the rendered pixels, the brief and the plan. Asking the builder "is it good?" returns "yes" by construction. Adapted with credit from motion-video-kit's Gauntlet (https://github.com/echris6/motion-video-kit, MIT).

Send each prompt to a **fresh** subagent with your own reasoning left out. Fill the `<>` slots.

## Full-film critic
```
You are an independent, harsh critic of a short motion video. You did NOT build it; judge rendered pixels, not intentions.
Video: <path> (<seconds> s, <WxH>, <fps> fps). What it is for: <one line from BRIEF.md>.
Images to Read: the contact sheet <out/qa/sheet.jpg>, the first 3 seconds <out/qa/first.jpg>, and the product's own site
<research/capture/screenshots/contact-sheet.jpg or research/site.png>. The brief and its Brand look: <paste BRIEF.md>.
The beat sheet: <paste from PLAN.md>. check.py said: <paste its output>.
Report (under 500 words) to out/critic-1.md:
1. Would a founder post this as their launch video instead of what they'd get by asking a plain AI model? Why or why not, bluntly.
2. Structure (product, launch or promo film): do the first 2-3 s show the logo, name and one-line description on the brand's background, and do the last 2-3 s close on the brand? In the middle, is every product screen introduced by a title and subtitle, so a stranger knows what they're looking at? Name any screen shown without words. (For a sting, loop or type piece: is it composed and moving from frame 0?)
3. Brand: next to the site, would their team recognise it as theirs (background, colour, type, UI)?
4. Legibility and fill: any show beat where the product is small, unreadable or floating in empty space; any blank between beats. (Brand and information beats are large type on a designed background by design; judge them on size and composition, not fill.)
5. Any hard-ban pattern (except what BRIEF.md's Brand look says the brand itself uses), with timestamps.
6. The top 3 changes ranked by impact, concrete and implementable in code.
End with SHIP or FIX (FIX only for something broken: clipped, empty, off-brand, unreadable).
```

## Verification critic (later rounds)
```
You are an independent critic; you did NOT build this. New render: <path>. The previous report: out/critic-<n>.md.
For every item in its top changes and defects: FIXED / PARTLY / STILL PRESENT, with timestamps.
Then list any NEW defects (pops, clipped text, overlaps, dead holds, a slower first second).
Write under 400 words to out/critic-<n+1>.md, ending with SHIP or FIX (at most 3 fixes; FIX only for something broken).
```

## Plan critic (before building, optional for films over 20 s)
```
Review this plan for a <seconds> s video. You did not write it. Check: does it open and close on the brand (logo, name, one-line description, moving from frame 0); is every product screen introduced by a title and subtitle; does each beat have one job and a distinct picture; which beats are filler; is every claim on screen true
(the truth list); does it read on mute? Return ranked problems, one concrete fix each.
```

Stop at SHIP or after 2 rounds. Past that, fixes start fighting each other.

## Severity, so the top 3 are the right 3
Rank findings before choosing what to fix (tiers adapted and modified from motion-design-skill, LottieFiles, MIT). A film built from the template (`Film.tsx`) has fixed timing and motion: judge its content, brand, legibility and screens, not its drift or push.
- **Critical:** off-brand or unreadable frames; anything clipped or empty; linear easing on a move through space; a state change shown only by opacity; anything travelling more than a third of the frame with no keyframe between; a group stagger longer than 500 ms; a sound hit more than a frame off its picture.
- **Major:** a cut with no reason; two directions fighting across a cut; text held shorter than its reading time; more than one camera move in a beat.
- **Minor:** polish. Fix it only after everything above.

## Frames to pull before judging
Take one frame at every hero moment **and** one in the middle of every transition (`ffmpeg -ss <t> -i out/video.mp4 -frames:v 1 out/qa/t<t>.png`), plus the phone view: one frame a second at 360 px wide (`ffmpeg -i out/video.mp4 -vf "fps=1,scale=360:-1,tile=6x4" -frames:v 1 out/qa/phone.jpg`). Read them all.

