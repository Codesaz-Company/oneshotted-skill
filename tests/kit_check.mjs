// Self-check for assets/kit/motion.ts maths without Remotion: node --experimental-strip-types tests/kit_check.mjs
// (Node 22+). Stubs remotion's interpolate/Easing so the pure functions can be imported.
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const here = dirname(fileURLToPath(import.meta.url));
const d = mkdtempSync(join(tmpdir(), 'kit-'));
mkdirSync(join(d, 'node_modules/remotion'), { recursive: true });
writeFileSync(join(d, 'node_modules/remotion/package.json'), '{"name":"remotion","type":"module","main":"index.js"}');
writeFileSync(join(d, 'node_modules/remotion/index.js'), `
export const Easing = { bezier: () => (t) => t };
export const interpolate = (x, [a, b], [c, e]) => { if (!(b > a)) throw new Error('inputRange must be strictly monotonically increasing'); const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return c + (e - c) * t; };`);
writeFileSync(join(d, 'motion.ts'), readFileSync(join(here, '../skills/oneshotted/assets/kit/motion.ts'), 'utf8').replace("import type React from 'react';\n", ''));
const m = await import(pathToFileURL(join(d, 'motion.ts')).href);

// camera() transform and toScreen agree
const s = { ax: 300, ay: 200, sx: 960, sy: 540, k: 2.5 };
const T = (p) => ({ x: s.sx + s.k * (p.x - s.ax), y: s.sy + s.k * (p.y - s.ay) }); // translate(sx,sy) scale(k) translate(-ax,-ay)
for (const p of [{ x: 0, y: 0 }, { x: 300, y: 200 }, { x: 1600, y: 1000 }]) assert.deepEqual(m.toScreen(s, p), T(p));
assert.match(m.camera(s).transform, /translate\(960px, 540px\) scale\(2.5\) translate\(-300px, -200px\)/);
// prog: zero-length range is a step, never a throw
assert.equal(m.prog(5, 10, 10), 0); assert.equal(m.prog(10, 10, 10), 1); assert.equal(m.prog(15, 10, 20), 0.5);
// track: hold before/after, interpolate between, same-frame keys cut
const A = { ax: 0, ay: 0, sx: 0, sy: 0, k: 1 }, B = { ax: 100, ay: 0, sx: 0, sy: 0, k: 4 }, C = { ax: 500, ay: 0, sx: 0, sy: 0, k: 1 };
assert.deepEqual(m.track(-5, [[0, A], [10, B]]), A);
assert.deepEqual(m.track(99, [[0, A], [10, B]]), B);
assert.equal(m.track(5, [[0, A], [10, B]], m.E.linear).k, 2); // log-space: halfway between 1 and 4 is 2
assert.deepEqual(m.track(9, [[0, A], [10, A], [10, C]]), A);
assert.deepEqual(m.track(10, [[0, A], [10, A], [10, C]]), C);
assert.throws(() => m.track(0, []), /no keys/);
assert.throws(() => m.track(5, [[10, A], [0, B]]), /sorted/);
// frameRect: the rect's centre lands on screen centre at the requested fill; zero size is safe
const r = { x: 640, y: 520, w: 320, h: 90 }, f = m.frameRect(r, 1920, 1080, 0.5);
assert.deepEqual(m.toScreen(f, { x: r.x + r.w / 2, y: r.y + r.h / 2 }), { x: 960, y: 540 });
assert.equal(r.w * f.k, 960);
assert.ok(Number.isFinite(m.frameRect({ x: 0, y: 0, w: 0, h: 0 }, 1920, 1080).k));
console.log('kit_check: all ok');
