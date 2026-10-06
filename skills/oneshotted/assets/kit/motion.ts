// Motion tokens and helpers for Remotion. Adapted from Cinetic (src/lib/anim.ts, src/lib/camera.ts),
// Copyright (c) 2026 Leonxlnx, MIT License: see LICENSE-cinetic.txt next to this file.
// Modified: trimmed to what a launch film uses; adds track() and frameRect().
import type React from 'react';
import { Easing, interpolate } from 'remotion';

export type Ease = (t: number) => number;

/** Easing tokens, named for how they feel. Entrances decelerate, exits accelerate; only the camera eases both ways. */
export const E = {
  out: Easing.bezier(0.16, 1, 0.3, 1), // arrivals and reveals
  soft: Easing.bezier(0.22, 1, 0.36, 1), // gentle settles
  exit: Easing.bezier(0.55, 0.055, 0.675, 0.19), // exits into a cut
  whip: Easing.bezier(0.6, 0, 0.15, 1), // feature-to-feature moves
  cam: Easing.bezier(0.48, 0.1, 0, 0.9), // camera: slow start, long settle
  ui: Easing.bezier(0.4, 0, 0.2, 1), // small UI state changes
  type: Easing.bezier(0.5, 1, 0.89, 1), // eased typing
  linear: (t: number) => t,
};

export const clamp = (v: number, lo = 0, hi = 1) => Math.min(hi, Math.max(lo, v));
export const mix = (a: number, b: number, t: number) => a + (b - a) * t;
/** Log-space mix for scale: a zoom never seems to accelerate. */
export const lmix = (a: number, b: number, t: number) => Math.exp(mix(Math.log(a), Math.log(b), t));
/** Clamped 0..1 progress between two frames. */
export const prog = (frame: number, from: number, to: number, ease: Ease = E.out) =>
  to <= from ? (frame >= to ? 1 : 0) : interpolate(frame, [from, to], [0, 1], { easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
/** Start offset of item i of n spread over `span` frames. */
export const stagger = (i: number, n: number, span: number) => (n > 1 ? (span * i) / (n - 1) : 0);
/** Deterministic pseudo-random in [0,1) (Math.random breaks repeatable renders). */
export const rand = (seed: number | string) => {
  const s = String(seed);
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619);
  h ^= h >>> 16; h = Math.imul(h, 2246822507); h ^= h >>> 13;
  return (h >>> 0) / 4294967296;
};

/** A framing: world point (ax, ay) sits at screen point (sx, sy) at scale k. */
export type Shot = { ax: number; ay: number; sx: number; sy: number; k: number };
/** Blend two shots: anchors linearly, scale in log space, so the subject travels straight at an even zoom rate. */
export const lc = (A: Shot, B: Shot, t: number): Shot => ({
  ax: mix(A.ax, B.ax, t), ay: mix(A.ay, B.ay, t), sx: mix(A.sx, B.sx, t), sy: mix(A.sy, B.sy, t), k: lmix(A.k, B.k, t),
});
/**
 * Camera through a list of keyed shots: [[frame, shot], ...] sorted by frame. Between keys it moves on `ease`
 * (default E.cam); before the first and after the last it holds. Two keys on the same frame are a hard cut.
 * Add life to a hold with `breath`.
 */
export const track = (frame: number, keys: [number, Shot][], ease: Ease = E.cam): Shot => {
  const first = keys[0];
  if (!first) throw new Error('track(): no keys');
  for (let i = 1; i < keys.length; i++) if (keys[i]![0] < keys[i - 1]![0]) throw new Error('track(): keys must be sorted by frame');
  if (frame < first[0]) return first[1];
  let cur = first[1];
  for (let i = 1; i < keys.length; i++) {
    const [f0, a] = keys[i - 1]!; const [f1, b] = keys[i]!;
    if (frame < f1) return f1 === f0 ? a : lc(a, b, prog(frame, f0, f1, ease));
    cur = b;
  }
  return cur;
};
/** Multiply k by this inside a hold: a slow push (+2.5% over the hold). */
export const breath = (frame: number, from: number, to: number, amount = 0.025) => 1 + amount * prog(frame, from, to, E.linear);
/** Style for the world container. Lay the world out at left 0, top 0 in world px; all movement is this one transform. */
export const camera = (s: Shot): React.CSSProperties => ({
  position: 'absolute', left: 0, top: 0, transformOrigin: '0 0',
  transform: `translate(${s.sx}px, ${s.sy}px) scale(${Math.max(1e-4, s.k)}) translate(${-s.ax}px, ${-s.ay}px)`,
});
/** Screen position of a world point under a shot: where to draw a cursor or a label that tracks the product. */
export const toScreen = (s: Shot, p: { x: number; y: number }) => ({ x: s.sx + (p.x - s.ax) * s.k, y: s.sy + (p.y - s.ay) * s.k });
/**
 * Shot that frames the rect {x, y, w, h} (world px) to fill `fill` of the frame width (or height, whichever binds),
 * centred at (cx, cy) on screen. The main tool for "push in on this button / this row".
 */
export const frameRect = (r: { x: number; y: number; w: number; h: number }, W: number, H: number, fill = 0.8, cx = W / 2, cy = H / 2): Shot => {
  const k = Math.min((W * fill) / Math.max(1, r.w), (H * fill) / Math.max(1, r.h));
  return { ax: r.x + r.w / 2, ay: r.y + r.h / 2, sx: cx, sy: cy, k };
};
