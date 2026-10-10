# kit: copy into the project's src/kit/

`cp -R <skill>/assets/kit src/kit` (Remotion). Nothing here is required; it is tested, so use it instead of writing
your own camera or cursor.

| File | What |
|---|---|
| `Film.tsx` | **the template film**: brand → problem → (title, product) × 2 → proof → brand, 19 s, motion that passes check.py. Fill `content.ts`; see `content.example.ts.txt`, `Root.example.tsx.txt`, `ExampleInbox.tsx` |
| `motion.ts` | easing tokens `E`, `prog`, `stagger`, `rand`, and the camera: `Shot`, `track` (keyed shots), `frameRect` (push in on a rect), `breath`, `camera()` style, `toScreen` |
| `Cursor.tsx` | a readable pointer (`Cursor`), bowed paths (`cursorArc`), clicks (`pressAt`) |
| `Browser.tsx` | `Browser` window chrome; `ScrollPlate` for a brief glimpse of a full-page screenshot |

The pattern for a product shot: rebuild the UI surface the beat needs as a component at video scale (the site's
font, colours, radii and real copy from the capture; body text ≥ 28 px), lay it out once inside a `Browser` (or a
phone frame) at, say, 1600x1000 world px, put that in a div with `style={camera(track(frame, keys))}`, and key shots
with `frameRect` on the thing that changes (the field being typed, the button being clicked, the result).
Screenshots from `research/capture/` are reference for the rebuild; a real screenshot can also be a show beat when it is
cropped to the part that matters, large, framed in a `Browser` or device, with its title on screen. What lost blind tests
was a camera touring full screenshots with no words.

Keep any image under 8000 px tall: Chromium renders a 16000 px one blank, without an error. Crop a long page
(`ffmpeg -i full-page.png -vf "crop=iw:min(ih\,8000):0:0" public/page.png`).

Credit: motion.ts and Cursor.tsx are adapted from Cinetic by Leonxlnx (MIT, `LICENSE-cinetic.txt`); keep that file
with them when you copy the kit.
