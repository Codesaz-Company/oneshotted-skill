# Taste: the tells of cheap or generated motion, and their fixes

Search this during review; cite the ID when you flag something ("K1: 2.2 s title card before anything moves"). Numbers are measured norms at 1080p, starting points rather than law: move them with a written reason. Adapted with credit from Cinetic's taste catalogue (https://github.com/Leonxlnx/cinetic, MIT, `references/taste-and-slop.md`, `references/craft-rules.md`), plus what we learned building real promos.

## Opening and pacing (the most common failures)
- **K1 Weak hook.** A fade from black, raw UI with no name, a static title card, or 1-2 s of near-still frame first. A muted feed reads it as a stalled player. **Fix:** in a product film, open on the brand alone: the logo, name and one-line description, big and moving from frame 0, on the brand's background, with no UI before ~3 s; first visible change by 0.1-0.4 s. `scripts/check.py` fails the still part.
- **K2 Dead holds.** More than ~1.6 s with no visible life mid-film. **Fix:** every hold builds (a slow push, a counter, a reveal); one designed stillness per film, on the key claim.
- **K3 Cramming.** 17 scenes in 30 s, or 3 features in 5 s. **Fix:** 8-12 beats per 30 s; one idea per beat.
- **K4 Flat energy.** Same intensity throughout. **Fix:** an early peak in the hook, a short lull around 60-70%, the biggest peak around 80%, then a calm brand end card of 2-3 s.
- **K5 Slow middle.** A product demo with only small typing for 5-10 s. **Fix:** cut it to the result, or move the camera with the action.

## Concept
- **A1 Feature tour.** Screen, screen, screen, logo: nothing explained, nothing to remember. **Fix:** brand → the problem → feature pairs (a title and subtitle, then the screen that proves it) that resolve it → proof → brand, carried by one idea.
- **A2 Borrowed props.** Rocket, lightbulb, globe with arcs, up-and-right chart, floating phone, sparkles for AI, shield for security. **Fix:** build every image from the subject's own objects (its UI, its footage, its numbers).
- **A3 A style posing as an idea.** "Bold, kinetic, minimal, 3D." **Fix:** write the one-sentence idea and the device first; the style follows.
- **A4 Frames that contradict the promise.** A strike-through over the tagline, overlapping tiles in an "everything fits" shot. **Fix:** read each key frame literally as a paused still.
- **A5 Dead end card.** Fades to black, sits static for 3 s, or the last frame has no name. **Fix:** a 2-3 s brand end card (logo, name, call to action, URL) that builds slightly; the final frame works as the poster.

## Copy
- **B1 Landing-page grammar.** "Introducing…", tiny all-caps micro labels, three taglines stacked at once. **Fix:** one title and one subtitle per beat, large; hierarchy from size and order of appearance. (A title with a subtitle is the information beat, not this.)
- **B2 Stock phrasing.** Seamless, unlock, supercharge, AI-powered, next-gen, "the future of", exclamation marks. **Fix:** plain statements in the subject's own words, ending in a period.
- **B3 Over budget.** More than ~35 words per 30 s, more than ~6 words per line, more than 2 lines on screen. **Fix:** cut adjectives, then whole lines.
- **B4 Text nobody can read.** Under ~28 px at 1080p, or on screen shorter than ~0.4 s + 0.2 s per word. **Fix:** bigger, longer, or drop it.

## Layout
- **E1 The SaaS layout.** Text left and a small UI card right for beat after beat, or everything centred and floating in black. **Fix:** in show beats the product is large (40-70% of the frame); type anchored to a line or the lower third; vary the layout beat to beat.
- **E2 Voids and no margins.** 20% of the frame empty, or text within 80 px of the edge. **Fix:** fill the frame; safe margins ≥ 80 px.
- **E3 Text over busy footage.** Headlines unreadable over a video wall. **Fix:** a dark plate, a gradient, or a calmer moment for the line.
- **E4 Cropped verticals.** A 9:16 cut out of the 16:9 master. **Fix:** re-lay the vertical as its own composition.

## Motion
- **F1 The default entrance.** Everything fades in, or rises 30 px while fading. **Fix:** one reveal per role with physical entrances: a mask sweep, a scale from the source, a morph.
- **F2 Uniform timing.** Every move 0.4-0.5 s on one curve. **Fix:** duration grows with distance (~0.35 s + 1.35 ms per px); the slowest move ≥ 3× the fastest.
- **F3 Bounce everywhere.** Elastic or overshoot on every card. **Fix:** eased or critically damped by default; overshoot of 1-7% only on a true landing, at most twice.
- **F4 Easing the wrong way.** Ease-in entrances, ease-out exits. **Fix:** entrances decelerate, exits accelerate.
- **F5 Everything moving at once.** Idle bobbing, pulsing badges, ambient zoom on every scene. **Fix:** one hero motion plus at most 2 supporting ones.
- **F6 Stall, then lurch.** A move eases to rest, then the next starts at full speed. **Fix:** overlap consecutive moves, or start the next one on a zero-slope curve.

## Transitions
- **G1 Crossfade by default,** or fades through black. **Fix:** a match cut, a morph of the container, a camera move that carries across.
- **G2 Presets.** Glitch, RGB split, light leak, film burn, swirl, flash to white. **Fix:** motivated transitions only, each type at most twice.
- **G3 Velocity mismatch at a cut.** **Fix:** the outgoing shot accelerates into the cut; the incoming one decelerates out of it.

## Colour and finish
- **D1 Neon, glow and bloom; purple-to-blue or multi-hue gradients; glassmorphism.** **Fix:** one flat accent with one meaning; opaque surfaces with one soft dark shadow. **Exception:** the product's own look. If its site uses a gradient background or a glow, the film uses it the same way (see BRIEF.md's Brand look).
- **D2 Accent everywhere.** **Fix:** ~5-8% of pixels, one full-frame flood at most.
- **D3 Banding** on dark gradients. **Fix:** static grain at 4-8% over everything, or a dithered image.
- **L1 Pops and ghost frames.** A frame that flashes for one frame. **Fix:** `scripts/check.py` finds them; never animate CSS blur on a promoted layer.
- **L2 Pixel-snap stairs.** Slow moves stepping in whole pixels. **Fix:** move with `transform` only, never left/top.
