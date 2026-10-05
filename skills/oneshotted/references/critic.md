# The critic loop: the builder never grades its own work

A fresh agent that did not build the video judges only the rendered pixels, the brief and the plan. Asking the builder "is it good?" returns "yes" by construction. Adapted with credit from motion-video-kit's Gauntlet (https://github.com/echris6/motion-video-kit, MIT).

Send each prompt to a **fresh** subagent with your own reasoning left out. Fill the `<>` slots.

## Full-film critic (round 1)
```
You are an independent, harsh critic of a short motion video. You did NOT build it; judge rendered pixels, not intentions.
Video: <path> (<seconds> s, <WxH>, <fps> fps). What it is for: <one line from BRIEF.md>.
The brief and its hard bans: <paste BRIEF.md>. The plan: <paste the beat sheet from PLAN.md>.
Method: extract a contact sheet every 0.2 s and native frames at the first 3 s and around every cut
(ffmpeg into <scratch dir>), and look at every image. Run: python3 <skill>/scripts/check.py <path>.
Report (under 700 words) to <path>/critic-1.md:
1. The first 3 seconds: does something move at once, is the idea readable by 2 s, would you stop scrolling?
2. Per beat: what's on screen, % of the frame that is empty, problems ranked (cite IDs from references/taste.md).
3. Any hard-ban pattern on any frame, with its timestamp.
4. The top 5 changes ranked by impact, concrete and implementable in code.
End with SHIP or ONE MORE PASS. Be blunt; no padding.
```

## Verification critic (later rounds)
```
You are an independent critic; you did NOT build this. New render: <path>. The previous report: <path>/critic-<n>.md.
For every item in its top changes and defects: FIXED / PARTLY / STILL PRESENT, with timestamps.
Then list any NEW defects (pops, clipped text, overlaps, dead holds, a slower first second).
Write under 400 words to <path>/critic-<n+1>.md, ending with SHIP or ONE MORE PASS (at most 3 fixes).
```

## Plan critic (before building, optional for films over 20 s)
```
Review this plan for a <seconds> s video. You did not write it. Check: does frame 0 already move on the hero
material; does each beat have one job and a distinct picture; which beats are filler; is every claim on screen true
(the truth list); does it read on mute? Return ranked problems, one concrete fix each.
```

Stop after 3 rounds or at SHIP. Past that, fixes start fighting each other.
