# Motion: the guardrails agents break without being told

Read before Step 4 (build). Adapted and modified from HyperFrames' `motion-principles.md` (https://github.com/heygen-com/hyperframes, Copyright 2026 HeyGen, Inc., Apache-2.0) and Cinetic's craft rules (https://github.com/Leonxlnx/cinetic, MIT).

## Guardrails
- **Vary the ease.** At most 2 moves in a scene share an ease. Pick it like an adverb: a fast decelerating out-curve reads confident, a sine in-out dreamy, a spring playful (and only on a true landing).
- **Vary the speed.** The slowest scene is at least 3× slower than the fastest. Fast 0.15-0.3 s for energy, 0.3-0.5 s for most content, 0.5-0.8 s for weight, 0.8-2 s for cinematic moves. Duration grows with distance (~0.35 s + 1.35 ms per px).
- **Vary the direction.** Not everything rises 30 px while fading in: from the side, from scale, from a mask, from the object that caused it.
- **Vary the rhythm.** Each scene gets its own stagger; in a group the first item lands on the beat and the rest follow 0-3 frames apart.
- **One ambient motion per scene, or none.** Not a slow zoom on every scene. Stillness after motion is a tool.
- **Directions are not optional.** Entrances decelerate (`out`), exits accelerate (`in`), moves between positions use `inOut`. Agents get this backwards.

## Scene structure: build, breathe, resolve
- **Build (0-30%)**: elements enter, staggered; don't dump everything on frame 1.
- **Breathe (30-70%)**: the content is readable and alive with one ambient motion.
- **Resolve (70-100%)**: a decisive exit or a hand-off to the next scene; exits are faster than entrances.

The film's first scene is the exception: it is already in its breathe phase at frame 0, so the hook moves from the first frame.

## Transitions carry meaning
- Hard cut = "wake up", a change of register. Use it in the hook.
- Match cut or morph = "this continues": the same object, shape or colour carries across.
- Crossfade = "drift": rare, and never through black.
- Each transition type at most twice per film, plus one signature move.

## Determinism (renders must repeat)
- Everything is a function of the frame: no CSS transitions or keyframes, no wall clock, no unseeded random, no infinite repeats.
- Translate with `transform`, never left/top (whole-pixel stairs).
- Clamp every interpolation at both ends.
- No network at render time: fonts and media are local files.

## The truth list
Every number, name and claim on screen comes from the brief, the product, or a cited source. Anything illustrative is labelled as such. Adapted from product-launch-motion (https://github.com/AbubakrChan/product-launch-motion, MIT).
