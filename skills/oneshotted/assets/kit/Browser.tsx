// A browser window to hold the product's rebuilt UI, plus a plate that scrolls a full-page screenshot for a
// brief glimpse of the real page. Rebuilt components are the hero; screenshots are reference and texture.
import React from 'react';
import { Img, staticFile } from 'remotion';

/** Window chrome around children, sized in world px. `dark` follows the site's theme. */
export const Browser: React.FC<{ w: number; h: number; url?: string; dark?: boolean; radius?: number; children: React.ReactNode }> = ({
  w, h, url, dark = false, radius = 18, children,
}) => {
  const bar = 52;
  return (
    <div style={{ width: w, height: h, borderRadius: radius, overflow: 'hidden', position: 'relative',
      background: dark ? '#0f1115' : '#fff', boxShadow: '0 40px 120px rgba(0,0,0,0.35), 0 0 0 1px rgba(127,127,127,0.18)' }}>
      <div style={{ height: bar, display: 'flex', alignItems: 'center', gap: 10, padding: '0 20px',
        background: dark ? '#1a1d24' : '#f3f4f6', borderBottom: `1px solid ${dark ? '#262a33' : '#e5e7eb'}` }}>
        {['#ff5f57', '#febc2e', '#28c840'].map((c) => <div key={c} style={{ width: 14, height: 14, borderRadius: 7, background: c }} />)}
        {url ? <div style={{ marginLeft: 24, flex: 1, maxWidth: w * 0.5, height: 32, borderRadius: 8, background: dark ? '#0f1115' : '#fff',
          color: dark ? '#9ca3af' : '#4b5563', font: '500 18px system-ui, sans-serif', display: 'flex', alignItems: 'center', padding: '0 14px' }}>{url}</div> : null}
      </div>
      <div style={{ position: 'absolute', top: bar, left: 0, right: 0, bottom: 0, overflow: 'hidden' }}>{children}</div>
    </div>
  );
};

/**
 * A full-page screenshot (in public/) shown at width `w`, scrolled to `y` page px (at that width).
 * Drive `y` with prog()/E.cam for a deliberate scroll, never linear drift over the whole film.
 * Chromium paints nothing for an image taller than about 16000 px (no error, a blank frame), so crop a long
 * page to the part you show first, keeping it under 8000 px tall:
 *   ffmpeg -i full-page.png -vf "crop=iw:min(ih\,8000):0:0" public/page.png
 */
export const ScrollPlate: React.FC<{ src: string; w: number; y: number }> = ({ src, w, y }) => (
  <Img src={staticFile(src)} style={{ position: 'absolute', left: 0, top: 0, width: w, transformOrigin: '0 0', transform: `translateY(${-y}px)` }} />
);
