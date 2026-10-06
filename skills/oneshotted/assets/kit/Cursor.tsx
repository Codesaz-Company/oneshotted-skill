// A stage-prop pointer: big enough to read on a phone (~44x60 at 1080p), moved only by transform.
// Adapted from Cinetic (src/fx/Cursor.tsx), Copyright (c) 2026 Leonxlnx, MIT License: see LICENSE-cinetic.txt
// next to this file. Modified: larger default scale, colour prop. Size guidance from product-launch-motion (MIT).
import React from 'react';
import { mix } from './motion';

type Pt = { x: number; y: number };

export const Cursor: React.FC<{ x: number; y: number; press?: number; scale?: number; opacity?: number; ink?: string }> = ({
  x, y, press = 0, scale = 1.5, opacity = 1, ink = '#0b0b0f',
}) => (
  <div style={{ position: 'absolute', left: 0, top: 0, opacity, transformOrigin: '0 0',
    transform: `translate(${x}px, ${y}px) scale(${scale * (1 - 0.12 * press)})`, filter: 'drop-shadow(0 4px 8px rgba(0,0,0,0.35))' }}>
    <svg width={30} height={42} viewBox="0 0 30 42" style={{ position: 'absolute', left: -3, top: -2 }}>
      <path d="M3 2 L3 33 L10.2 26.4 L15 38 L20.2 35.8 L15.4 24.4 L25 24.4 Z" fill={ink} stroke="#fff" strokeWidth={2.4} strokeLinejoin="round" />
    </svg>
  </div>
);

/** Point on a bowed path from a to b at eased progress t: hands never move in straight lines. */
export const cursorArc = (a: Pt, b: Pt, t: number, bow = 0.2): Pt => {
  const cx = (a.x + b.x) / 2 - (b.y - a.y) * bow;
  const cy = (a.y + b.y) / 2 + (b.x - a.x) * bow;
  return { x: mix(mix(a.x, cx, t), mix(cx, b.x, t), t), y: mix(mix(a.y, cy, t), mix(cy, b.y, t), t) };
};

/** Click press 0..1 for Cursor's `press`: down over 4 f from `at`, back over the next 8 f. */
export const pressAt = (frame: number, at: number) => {
  const t = frame - at;
  if (t <= 0 || t >= 12) return 0;
  return t < 4 ? t / 4 : 1 - (t - 4) / 8;
};
