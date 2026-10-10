# Sound: music, effects, voice and captions, made and checked in code

Read only when the user asks for sound or voice-over (SKILL.md keeps films silent by default; a muted feed needs the picture to work alone). Sound follows the same timeline as the picture, so it can't drift. Adapted, with credit, from claude-motion (whaleyxbt, MIT), claude-motion-design (Howseen AI, MIT), claude-remotion-skill (haidrrrry, MIT), product-launch-motion (Abubakr Chan, MIT) and the music-motion ideas in klik-anim-skill-creation (t3knobox, no licence, used with the author's permission, in our own words). Licences in `LICENSES/`.

## One timeline for picture and sound
- Write every beat once, in seconds or as `b(n) = n × 60 / BPM`, in one `timeline.json` (or a constant the composition imports). Picture and sound cues both read it. A sound time typed in by hand is the bug.
- At 30 fps, frames per beat = `fps × 60 / BPM` (120 BPM → 15; 60 fps → 30). Reveals snap to a cue within 0.15 s.
- **A hit lands on the frame the picture lands, or one frame before** (≤ 33 ms at 30 fps). Viewers notice sound that comes early sooner than sound that comes late, so never lead by more than a frame. A riser builds into a cut; the hit is on it.
- Pick the tempo by mood: 60-80 BPM regal, 90-110 smooth, 115-123 confident, above 125 hype. Find the drop by energy per bar, then refine in 20-50 ms windows; never trust an automatic beat grid on its own.

## Effects made in code (no stock packs, no network)
- Synthesise effects with the standard library: a short noise burst through a falling filter (whoosh), a pitch-drop sine (pop), a 140 → 95 Hz falling sine with fast decay (kick or impact), a filtered noise swell (riser), a soft sine stack (pad). Seed any randomness so renders repeat. Write 16-bit WAV at 48 kHz.
- Typing: one click per character with ±4-6 ms jitter, not a metronome.
- **Restraint:** one riser and one impact per film, one musical key throughout, pan follows where the thing is on screen.
- Levels (linear gain): hero hits 0.25-0.35, supporting effects 0.08-0.2, a music pad ~0.03. Under a voice, the music bed sits ~18 dB down (about 0.13) and ducks further under a hero hit.

## Voice-over and word-locked cues
- Get word timings from Whisper (or the TTS's own timestamps) and drop words it hallucinated over silence.
- Cue each reveal to the start of its word: readable things lead the word by 0.02-0.06 s; hits land exactly on it; at most two cues per word.
- Film length = narration + 0.2-0.5 s tail + any transition padding. Write it before building.
- A sub-bass swell (1.7-1.8 s at 0.2) under the thesis and the call to action only, after ~0.3 s of near-silence.

## Captions
- Social cuts: 1-3 words per pop, or 3-7 for a karaoke line; each on screen ≥ 0.7 s, ≤ 17 characters per second, no 1-3 frame gaps between them. In Remotion, `@remotion/captions`' `createTikTokStyleCaptions({ combineTokensWithinMilliseconds: 1200 })` gives 2-4 word pages.
- Place them clear of the subject and inside the reel safe zone in `references/engines.md`. Hold times follow `references/motion.md`.

## Mastering
- Target −14 LUFS integrated with true peak ≤ −2 dBFS before AAC (the MP4 then stays under −1). A mix of short hits can't reach −14: add sustained sound (a bed, a pad), not more gain.
- Two-pass `loudnorm`, then `aresample=48000` (loudnorm outputs 192 kHz) and `alimiter=level=disabled` (otherwise it adds make-up gain). Verify with `ebur128=peak=true`.
- If an asset sits more than ~15 dB under the voice, no cue volume fixes it: level the asset itself (`volume=22dB,alimiter=level=disabled`), trimmed from its first transient, and measure against the voice stem.
- A video with no sound still gets a silent AAC track (`-f lavfi -i anullsrc=r=48000:cl=stereo -shortest`): some platforms reject files without audio.

## Check it
- Draw the waveform with a line at every beat (`ffmpeg -i out/video.mp4 -filter_complex "showwavespic=s=1920x240" -frames:v 1 out/qa/wave.png`, then mark the beat times). Every transient sits on a line or just after it; a hit between lines is a hand-typed time.
- Listen once at full speed and once with the picture off: the sound alone should tell where the cuts are.

## Skip from those sources
Elastic springs on everything, screen shake on the kick, glow pulses, drift on every idle element, and J/L-cuts (these films have no dialogue to carry across a cut): they break this skill's motion bans or don't apply.
