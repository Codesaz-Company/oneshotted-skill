---
name: oneshotted
description: "Make premium motion graphics and short videos with code (Remotion, HyperFrames, GSAP, Three.js, canvas), grounded in real references. Use whenever the user wants a launch video, promo, product or feature video, explainer, kinetic typography, logo reveal, social clip, animated demo or any animation built with code, or asks to improve, critique or speed up one, even if they only say \"make a video about X\". Pulls real pieces and the exact prompts behind them from the Oneshotted library (5,000+ motion pieces made by AI agents), turns them into a plan with a beat sheet, builds, renders, and measures the render before calling it done."
license: "MIT AND Apache-2.0 (complete terms in LICENSE.txt)"
compatibility: "Needs ffmpeg/ffprobe and Python 3 (standard library only). Remotion needs Node 18+ and Chromium; HyperFrames needs Node and Chromium. The library steps need a free Oneshotted account: sign in once with `python3 scripts/library.py login`, or set ONESHOTTED_API_KEY (https://oneshotted.io/mcp-docs). Without either, skip step 2 and say so."
---

# oneshotted

You are directing a short film, not decorating a web page. Every film starts from real references (what already worked, made by an AI agent, with the prompt that made it), and nothing is done until the render has been measured and looked at.

The library is the edge: other skills give you rules; this one also gives you evidence. Use it.

## The bar

- **Moving from frame 0.** Something visibly changes within the first 0.4 s (median 0.1 s in top launch films) and the idea reads by 2 s. A still title card, a fade from black or "Introducing..." loses the viewer on a feed in under a second.
- **One idea, told in pictures.** It reads with the sound off; words confirm what the picture already said.
- **Real material beats decoration.** The product's own UI, real footage, real numbers. Never placeholder cards or fake metrics.
- **Every frame looks chosen.** Nothing floating alone in black, no half-built states, nothing clipped, body text at least 28 px at 1080p.
- **Motion has weight.** Eased in, eased out, lands and rests. Nothing just fades through black.

## Hard bans (unless the user's brand uses it: then the brand wins, write it in BRIEF.md)

- Words: eyebrow/kicker labels above a headline, "Introducing...", stacked taglines, text walls, filler captions, fake metrics, lorem ipsum.
- Colour: neon glows and bloom, purple-to-blue or any multi-hue gradient, glassmorphism.
- Decoration: sparkles standing for "AI", particles, confetti, lens flares, code rain, emoji and stock icons.
- Motion: bouncy overshoot on anything that isn't landing, camera shake, RGB split, a slow first second.

## Which reference to read when

| Step | Read |
|---|---|
| 3 Plan | `references/taste.md` (A, B, K groups) |
| 4 Build | `references/motion.md` (guardrails, build/breathe/resolve, determinism, truth list) |
| 6 Review | `references/critic.md` (prompts for a fresh critic) and search `references/taste.md` by ID or word |

The full catalogue with fixes is `references/taste.md`. Search it rather than reading it whole (`grep -n -i 'glow' references/taste.md`).

## Workflow

Every step writes a file; every gate is a check you actually run.

### 1. Brief → `BRIEF.md`
If the request names the subject, the format and the length, infer the rest and write your assumptions down. Otherwise ask at most 3 questions: what it is in one line, the format and length, where it will be shown. Defaults: 16:9 1920x1080, 30 fps (60 when UI or text moves a lot), 15-30 s for a promo, 6-12 s for a loop. Copy the hard bans into BRIEF.md: it is the review contract.

### 2. References from the library → `research/refs.md` (the step other skills don't have)
Find what already worked for this kind of piece, and the prompt that made it. If the script says you're not signed in, ask the user to run `python3 scripts/library.py login` once (it opens their browser; they sign in or make a free account and press Allow), or to set ONESHOTTED_API_KEY. Never ask them to paste a key into the chat.

```bash
python3 scripts/library.py search "product launch kinetic typography" --limit 8   # 2-4 searches, different angles
python3 scripts/library.py recipe <id>        # the exact prompt, tags, duration, credit
python3 scripts/library.py frames <id> --count 3 --out research/frames   # then Read the JPGs
python3 scripts/library.py similar <id>       # widen from the best one: pieces that look alike
```

- Budget: at most 4 searches and 8 recipe/frames calls (the free plan has 30 a day). Pick 2-3 references; don't survey 20.
- **Only verified owner prompts.** Search returns only pieces whose creator quoted the exact prompt on X and whose prompt was reviewed as a full reference (not a two-word "go all out"). It never shows reconstructed or "likely" prompts. `similar` marks each result `usable` or `style reference only`. A style reference can be looked at (`search --any`, `frames`), but never quote or adapt a prompt it doesn't have.
- **Borrow the mechanism, not the surface.** Take a reference's structure, pacing, transitions and technique; never its copy, colours or brand. Keep the creator credited.
- Write `research/refs.md`: for each reference, title, @creator, link, and what you take from it (pacing, type, transitions, palette, structure), plus one thing you reject and why. Credit them in the final message.
- If the library is unavailable (no key, a limit reached), say so and continue from the rules here.
- **Gate:** refs.md exists with 2-3 credited references and what each contributes. Take no more than 15 minutes on this step; the film matters more than the survey.

### 3. Plan → `PLAN.md`
- One sentence: what the viewer should remember.
- One device: an object, shape or colour that carries through every beat.
- One accent colour with one meaning, used on at most ~8% of pixels.
- A beat sheet: `| frames | picture | copy | motion |`, one idea per beat, a beat every 1.5-3 s, a visible change at least every 0.5-0.7 s. Beat 1 starts at frame 0 already moving and holds the strongest picture in the film.
- Copy: few words per beat, no line longer than ~6 words, total words within ~20 for a 20 s film.
- **Gate:** the beat sheet's first row starts at frame 0 with motion; nothing in it is a hard ban.

### 4. Build
- Start coding within your first few turns of this step. Read the engine's API only for the call you're about to use; don't tour the codebase.
- Everything is a function of the frame: no CSS animations or transitions, no Math.random or Date.now in render code (renders must repeat). Translate with `transform`, not left/top. Clamp every interpolation.
- One easing family (fast-out, slow-settle, e.g. cubic-bezier(.2,.8,.2,1)), named once and reused.
- System fonts or locally bundled fonts only; no network fonts in renders.
- Typecheck (`npx tsc --noEmit` for Remotion) before every render.

### 5. Render and measure
```bash
python3 scripts/check.py out/video.mp4 --sheet out/qa/sheet.jpg --first out/qa/first.jpg
```
It fails a still opening (nothing moves by 0.43 s, or a held first second), a dead hold over 1.6 s, black frames, single-frame flashes, and a file that doesn't match the spec (`--expect 1920x1080@30:20` checks size, fps and length), and writes a contact sheet plus a strip of the first 3 s. Then **Read both images** and judge every tile against the bar and the bans. Fix what the script finds before asking anyone's opinion.

### 6. Review rounds: the builder never grades its own work
Send the render to a **fresh** subagent with the full-film critic prompt in `references/critic.md` (it sees only the pixels, BRIEF.md and the beat sheet). Fix its top changes, re-render, re-run check.py, then send the verification prompt: every earlier finding comes back FIXED / PARTLY / STILL PRESENT, ending in SHIP or ONE MORE PASS. At most 3 rounds. If you can't spawn a subagent, do the same review yourself from the images only, writing findings with taste.md IDs before reading your own code.

### 7. Deliver
The video, the contact sheet, and a short note: the references used (with @creators and links), what changed in review, and anything not verified.

## Pitfalls seen in real builds

- **Planning forever.** Agents at maximum effort have spent hours researching and never written code. Keep steps 2-3 under ~20 minutes and start building.
- **Rate limits mid-build.** Keep BRIEF.md, refs.md and PLAN.md current so a fresh session can resume from the files.
- **The first-second problem.** A title card, a slow fade or a pull-back that starts from black fails the check every time. Open on the hero material already in motion.
- **Text on busy footage.** Put a dark plate or gradient behind headlines over video walls; check legibility on the contact sheet at 480 px wide.

## Credit

The workflow, the bans and the measured first-second and hold norms build on Cinetic by Leonxlnx (https://github.com/Leonxlnx/cinetic, MIT). The references come from Oneshotted (https://oneshotted.io): always credit the creators you used.
