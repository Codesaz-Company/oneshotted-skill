# Motion: the guardrails agents break without being told

Read before building by hand (step 5); the template film (step 4) already follows it. Adapted and modified from HyperFrames' `motion-principles.md` and motion doctrine (https://github.com/heygen-com/hyperframes, Copyright 2026 HeyGen, Inc., Apache-2.0) and Cinetic's craft rules (https://github.com/Leonxlnx/cinetic, MIT). The timing, camera, logo, cut and choreography sections draw on motion-design-skill (LottieFiles, MIT), motion-design-skills (iart.ai, MIT), animate (cth9191, MIT), claude-motion (whaleyxbt, MIT), motion-graphics-skills (Charlie Hills, MIT), klik-anim-skill-creation (t3knobox, no licence, used with the author's permission, in our own words) and hyperframes-student-kit (Nate Herk, MIT). Licences in `LICENSES/`.

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

---

# Further detail (search when the beat needs it)

## Timing by distance and personality
- **Pick a personality and keep it** (quick / standard / slow): premium 350 / 500 / 800 ms, corporate 200 / 300 / 450 ms, energetic 100 / 180 / 300 ms. Scale each by distance: 50 px ×0.8, 100 px ×1.0, 200 px ×1.3, 400 px ×1.6, full frame ×1.8-2.0. An exit takes 65-75% of its entrance (a 0.8 s entrance, a 0.55 s exit).
- **Nothing travels more than a third of the frame** without a keyframe in between.
- **Reading time decides the copy, not the beat length.** A line needs about `0.25 s + characters / 17` on screen. A 2-3 s beat holds a title and a short subtitle; if the copy needs longer, cut words. The hold stays alive (one ambient move, never a freeze: `scripts/check.py` fails a still 1.6 s).
- Leave 100-200 ms of stillness after something resolves; that's a rest, not a dead hold.

## Choreography
- Elements reacting to one trigger start within 50 ms of each other; a group follows its leader 0-3 frames apart (the guardrail above); a whole stagger stays under 500 ms.
- Counter-motion: the background drifts 20-30% of the hero's move, the other way.
- A faint ghost of the start state (an outline where the card began) lets the eye follow a change. A shared title travels; it is never duplicated.

## Camera
- **One camera move per beat;** a push takes 0.8-2 s. Interpolate zoom in log space, so it doesn't speed up as it closes in.
- **Know the moves.** Truck and pedestal (sliding the camera) give parallax; pan and tilt (turning it) don't. Zoom scales the picture; a dolly moves the camera through depth. Pair them (truck with pan, pedestal with tilt). Keep pans within ~6° and tilts within ~5° in 2.5D.
- **Parallax layers:** background 0.1-0.3×, middle 0.5-0.7×, foreground 1.0-1.5×.
- **A whip pan** is 10-14 frames; **rack focus** crossfades blur between depth planes over 12-20 frames; a dolly zoom (camera moves in while the subject's scale is held constant) once per film at most.
- Scale about the thing being clicked, so it stays put during a push. Music-driven speed is accumulated over time, never `frame × rate` (that jumps when the rate changes).

## Cuts need a reason
Every cut answers "why now": next step, matched position, shape morph, iris (2-4 frames), scale through (5-20×), point of view, cause and effect, time skip, or callback. Across a cut keep the **vector**: same axis, same direction, matched speed, cut mid-motion on both sides, with mirrored eases (the outgoing move accelerates with `E.exit`, the incoming one decelerates with `E.out`). One dominant direction per film; other directions mean something. Morphs cost ~1.2 s each: three at most under 30 s, and the bridge object is ≥ 200 px at the boundary.

## Logos
One technique per logo: draw it, build it or morph it.

| Move | Duration | Ease (the kit's `E`) |
|---|---|---|
| Stroke draw-on | 0.6-1.0 s | `E.whip` |
| Mask wipe | 0.5-0.8 s | `E.out` |
| Build-on | 0.4-0.6 s | `E.out` |
| Morph | 0.6-1.0 s | `E.whip` |
| Settle | 0.12-0.20 s, scale 1.04 → 1.00 | `E.soft` |

The whole reveal fits the brand beat: ≤ ~1.2 s, so the name and one-line description resolve by ~2 s. Order symbol → accents → wordmark (a build-on's letters land within 0.5 s together); hold the settled mark ≥ 0.4 s; clearspace equals the cap height; never stretch, skew or squash it. With a sound logo, the settle lands on its peak. For SVG strokes, `pathLength="1"` lets one dash value draw every path.

## Type in motion
- Display type: tracking −0.03 to −0.05 em; real weight contrast (300 against 900), not 400 against 600. For a 9:16 reel, go larger than the 16:9 minimums: body ≥ 32 px, titles ≥ 90 px.
- Give every text slot a character limit and every card a duration range in PLAN.md: it stops overflow and text walls before they're built.

## Colour and finish
- Interpolate colour in OKLCH (`linear-gradient(in oklch, …)`), not sRGB, which goes muddy in the middle.
- Lift the darkest tone off pure black. No grain or animated texture: it defeats `scripts/check.py` (a frozen frame with grain never reads as still). A vignette, if the brand uses one, stays around 0.15. No `mix-blend-mode` in an overlay track (it has turned whole renders white).
- Tag the file `-color_primaries bt709 -color_trc bt709 -colorspace bt709`; never judge colour in QuickTime (it applies a different gamma).

## Loops
The last frame flows into the first in position **and** speed (`seek(0)` matches `seek(duration)`), so the seam is invisible. Keep the middle alive (no still over 1.6 s), and check the frame just before the end against frame 0.

