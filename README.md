# oneshotted

An agent skill that makes your coding agent produce premium motion graphics and short videos with code (Remotion, HyperFrames, GSAP, Three.js), grounded in real references: 5,000+ pieces made by AI agents, with the exact prompts behind them, from [Oneshotted](https://oneshotted.io).

Other skills give the agent rules. This one also gives it evidence: before designing, it searches the library, reads the prompts and keyframes of 2-3 pieces that worked, plans a beat sheet, builds, renders, and measures the render (a still first second, dead holds, black frames and flashes fail) before it calls anything done.

## Install (one command)

```bash
curl -fsSL https://oneshotted.io/install.sh | sh
```

It installs the skill for your coding agents (Claude Code, Codex, Cursor and others the `skills` CLI supports), then opens your browser to sign in to Oneshotted (a free account works). That's it: ask your agent for a video. On a server or over SSH it skips the browser and tells you how to use an API key instead. Needs Python 3.9+; Node is optional.

Prefer to do it by hand?

```bash
npx skills add Codesaz-Company/oneshotted-skill -g     # install for your agents
python3 ~/.claude/skills/oneshotted/scripts/library.py login   # sign in once
```

Or skip the sign-in with an API key from https://oneshotted.io/mcp-docs: `export ONESHOTTED_API_KEY=osk_...`. Either way, calls count toward your Oneshotted account. Sign out with `library.py logout`, or disconnect "Oneshotted skill" on your dashboard.

Then ask your agent: "Make a launch video for https://your-product.com". Without a sign-in the skill still works; it skips the library step and says so.

## What's inside

- `skills/oneshotted/SKILL.md`: the workflow (capture the site, one library reference, plan as brand → explain → show → brand, style stills, build, measure, one review, deliver) and the hard bans.
- `skills/oneshotted/assets/kit/`: a tested Remotion camera, cursor and browser frame to copy into a project.
- `skills/oneshotted/scripts/library.py`: search the library (only pieces whose creator's own verified prompt is a full reference), read a piece's prompt, save its keyframes, find similar pieces. Standard-library Python.
- `skills/oneshotted/scripts/check.py`: measures a render (ffmpeg) and writes a contact sheet and a first-3-seconds strip to look at.
- `skills/oneshotted/references/`: the tells of cheap or generated motion, each with its fix.
- `evals/evals.json`: prompts and pass criteria to test the skill against.

## Credit

The workflow, bans and measured pacing norms build on [Cinetic](https://github.com/Leonxlnx/cinetic) by Leonxlnx (MIT); the critic loop on [motion-video-kit](https://github.com/echris6/motion-video-kit) (MIT); the motion guardrails on [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache-2.0); the truth list on [product-launch-motion](https://github.com/AbubakrChan/product-launch-motion) (MIT). The reference library is Oneshotted; the skill always credits the creators whose pieces it used.

For a product video the skill captures the product's site with the [HyperFrames](https://github.com/heygen-com/hyperframes) CLI (HeyGen, Apache-2.0), run with `npx` with telemetry and vision off. Its first run downloads a headless Chrome into `~/.cache/hyperframes`. The skill only runs it on a URL you gave it.

MIT licensed, with third-party portions under their own licenses (MIT, Apache-2.0): see LICENSE and LICENSES/.
