# Engines: which one, how to render it, and how to keep renders repeatable

Read when building by hand (step 5). Pick the engine before writing code. Sources, adapted and modified: the engines' own docs and licences; HyperFrames' CLI and determinism docs (HeyGen, Apache-2.0); gsap-skills (GreenSock, MIT); claude-motion-design (Howseen AI, MIT); motion-graphics `motion-broll` (Bart, MIT); motion-dev-animations-skill (199 Biotechnologies, MIT); the HyperFrames notes in hyperframes-motion-reel-skill (Sunwood AI Labs, MIT); ideas from Remotion's agent skills (remotion-dev/skills, no licence, used with the authors' permission, in our own words). Licences in `LICENSES/`.

## Pick one

| Engine | Use it for | Start | Render | Licence |
|---|---|---|---|---|
| **Remotion** (default) | Product films: React, the template film and kit in `assets/kit/` and the typecheck gate all assume it. | `npx create-video@latest` | `npx remotion render src/index.ts Main out/video.mp4` | Free for individuals, non-profits and for-profit teams of **up to 3**; a paid Company License for **4 or more** (mention it in the final message if the user is a company). |
| **HyperFrames** | HTML/CSS films driven by GSAP, Lottie, Three or canvas, when the user wants plain HTML or the kit isn't needed. | `HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_NO_TELEMETRY=1 npx -y hyperframes@0.8.133 init my-video` (Node 22+, FFmpeg), then delete the `CLAUDE.md` and `AGENTS.md` it writes | `HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_NO_TELEMETRY=1 npx -y hyperframes@0.8.133 render --quality delivery` | Apache-2.0, no render fees |
| **GSAP in a page** | The best timeline, text and SVG control, driven through HyperFrames or Remotion. | `npm install gsap` | Through HyperFrames or Remotion, or the capture loop below | Free, commercial use included; not open source, so never copy GSAP itself into a skill or repo |
| **Lottie** | Crisp vector loops, icons, an After Effects hand-off. | `npm install lottie-web` (Remotion: `npm i @remotion/lottie lottie-web`) | Through Remotion or HyperFrames | MIT runtime; **each .json animation has its own licence**: record it |
| **Canvas + ffmpeg** | Generative or procedural pictures, no DOM, fastest. | nothing (browser canvas) | `ffmpeg -framerate 30 -i frames/%05d.png -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart out.mp4` | depends on the ffmpeg build |
| **Motion.dev** | Interactive web UI, not video. If you must, use the capture loop. | `npm install motion` | Capture loop only | MIT |

Don't mix two engines in one film. Always pin HyperFrames to one version and set `HYPERFRAMES_SKIP_SKILLS=1`: without it `init` installs skills globally into the user's agent config, and its `--skip-skills` flag is ignored.

## Repeatable renders, engine by engine
Every frame is a pure function of time (step 5). These are the ways each engine breaks it.

### Remotion
- Everything from `useCurrentFrame()`; `random('seed')`, never `Math.random`; local assets through `staticFile()`; durations from `fps` (`4 * fps`, not a bare 120); a composition sized from its media with `calculateMetadata` (`Math.ceil(seconds * fps)`).
- Put `premountFor={fps}` on `<Sequence>`, `<Series.Sequence>`, `<TransitionSeries.Sequence>` and `@remotion/media`'s `<Audio>`/`<Video>` so nothing pops in on its first frame (the older core `<Audio>`/`<Html5Video>` don't take it).
- Fonts: `loadFont({ family, url: staticFile(...), weight })` from `@remotion/fonts`, one call per weight; measure text only after it loads (`fitText({ text, withinWidth, fontFamily })`, then cap the size). `@remotion/google-fonts` fetches at render: prefer local files.
- Async assets (Lottie JSON, data) go through `useDelayRender()`: `delayRender()`, then `continueRender(handle)`, `cancelRender(err)` on failure.
- Scale with `interpolate(..., { output: 'perceptual-scale' })`; a push with no bounce is `Easing.spring({ damping: 200 })`. CSS and Tailwind animations don't render.
- GSAP only through `useGsapTimeline()` from `@remotion/gsap`: one paused master timeline. It blocks `play()`, `seek()`, callbacks, async builders, free `gsap.to()`, `"random(...)"` and tweens on plain objects (they freeze: nothing re-reads them after a seek).
- QA stills for a few frames: `npx remotion render Main out/qa --frames=<f1>,<f2>,<f3> --image-format=png`.

### HyperFrames
- Build `gsap.timeline({ paused: true })` and register it as `window.__timelines["<composition-id>"] = tl`, at the end of any async build (earlier, the render is blank). Bundle GSAP locally: its README loads it from a CDN, which breaks "no network at render".
- Silent failures seen in real builds:
  - a property set only on the `from` side of `fromTo` vanishes in parallel render workers (repeat it on `to`);
  - fonts in an external stylesheet aren't embedded (look for `Injected deterministic @font-face` in the log);
  - an `<audio>` without an `id` renders silent;
  - `data-duration`, `data-width` and `data-height` are read at compile time;
  - use `immediateRender: false` with a `gsap.set` before it;
  - a finite repeat is `Math.max(0, Math.floor(duration / cycle) - 1)` (floor, not ceil);
  - transforms do nothing on inline spans or zero-width elements; never tween `visibility` on a clip; no `<br>` in body text.
- Loop: `lint` while writing, then `check` with 0 findings (runtime errors, failed requests, overflow past 2 px, WCAG contrast; `--snapshots --at-transitions --frame-check`), then `render --quality delivery`. Compare its snapshot with frames pulled from the final MP4: they can differ. Motion intent can be checked from a `*.motion.json` sidecar (`appearsBy`, `before`, `staysInFrame`, `keepsMoving` with `maxStaticSec`).

### GSAP anywhere
Free `gsap.to()` and `delayedCall` run on the wall clock; `"random()"` and `stagger: { from: "random" }` are unseeded; callbacks fire out of order when seeking. Animate `opacity` (never `visibility`, so not `autoAlpha`, on clips). On stacked `from()`/`fromTo()` on one property, set `immediateRender: false` on the later ones. Line reveals: `SplitText.create(el, { type: "words, chars", mask: "lines" })`, splitting only what moves (in a page or HyperFrames; not inside `@remotion/gsap`).

### Lottie
`renderer: 'svg'`, `autoplay: false`, `rendererSettings: { progressiveLoad: false }`; seek with `goToAndStop(t × the file's own frame rate, true)` (After Effects fps is often not the video's); keep `setSubframe(true)`. Video layers aren't supported. The full player runs a file's expressions through `eval`: in a page, load third-party files with the light player (`lottie-web/build/player/lottie_light`); in Remotion (`@remotion/lottie` uses the full player) use only files you trust, or strip their expressions first.

### Motion.dev
`MotionGlobalConfig.useManualTiming = true`; per frame `const a = animate(...); a.pause(); a.time = t`. Declarative `<motion.div>` can't be seeked. Its springs default to `bounce: 0.3`, which overshoots: set `bounce: 0`.

## The capture loop (no Remotion, any page)
For a page driven by `seek(t)`, Playwright steps through frames into ffmpeg:
- Launch Chromium with `--deterministic-mode --run-all-compositor-stages-before-draw --disable-threaded-animation --font-render-hinting=none --force-color-profile=srgb`, at `deviceScaleFactor: 2` for sharp text.
- Before frame 0: `await document.fonts.ready` and load every font (or frame 0 paints in a fallback), pause `document.getAnimations()`.
- Per frame: `seek(f / fps)`, wait for two `requestAnimationFrame`s, screenshot, pipe to ffmpeg.
- Encode for the web: `-vf "scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p" -c:v libx264 -crf 16 -movflags +faststart`.

## Motion blur (only for fast moves, only if time allows)
Fast moves can look like stutter. Blur costs 4× the render time, so do it last and only when the critic flags stutter. Render 4 subframes per frame inside the open shutter, at t = f/fps + k/(fps × 8) for k = 0..3 (a 180° shutter that never reaches into the next frame), then:
`-vf "format=gbrap,tmix=frames=4:weights='1 1 1 1',select='eq(mod(n\,4)\,3)',setpts=N/30/TB,format=yuv420p" -r 30`.
Never blend across a hard cut: render the frames on either side of a cut without subframes. In Remotion, use `<CameraMotionBlur>`. Never put `will-change` on anything the camera scales: text goes soft.

## Springs
A spring may never bounce except on a true landing. Damping ratio ζ = damping / (2 × √(stiffness × mass)); ζ ≥ 1 never overshoots (with mass 1, stiffness 300 needs damping ≥ 35, 400 needs ≥ 40). A tab or indicator that moves can stretch: its leading edge on a stiffer spring than its trailing edge, both at ζ = 1.

## Other outputs
- Reel (9:16): keep text and logos between y 360 and y 1420 and out of the right 120 px; check with ffprobe for `h264`, `yuv420p`, `color_range=tv`, `bt709`, plus an audio track (silent if needed: `references/sound.md`).
- GIF: `ffmpeg -i out/video.mp4 -vf "fps=15,scale=900:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" out/preview.gif`.
- Transparent: `-c:v prores_ks -profile:v 4 -pix_fmt yuva444p10le` to a `.mov`.

## Ignore from those sources
`back.out(1.7)`, `elastic.out` and `bounce: 0.3` as defaults; fade-and-rise as the standard entrance; unseeded random; CDN scripts at render; sparkle icons; particle "premium" looks.
