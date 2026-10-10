// A finished launch film: brand → problem → (title, then the product) × 2 → proof → brand. The timing and the motion
// are fixed and pass scripts/check.py by construction (every beat keeps moving at ≥ 3 px a frame, cuts every 2-3 s,
// frame 0 is already in motion). Fill src/content.ts; write the two show components; don't retime anything here.
import React from 'react';
import { AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { Browser } from './Browser';
import { E, clamp, prog } from './motion';

export type Show = React.FC<{ frame: number; w: number; h: number }>;
export type Spec = {
  /** bg: any CSS background (a hex or a gradient from the site); base: its main solid hex, used for contrast. */
  brand: { name: string; line: string; logo?: string; bg: string; base?: string; ink: string; accent: string; font: string };
  problem: { title: string; sub: string };
  features: [
    { title: string; sub: string; show: Show | { img: string }; url?: string },
    { title: string; sub: string; show: Show | { img: string }; url?: string },
  ];
  proof?: { value: number; label: string; prefix?: string; suffix?: string };
  cta: { text: string; url: string };
};

const W = 1920;
/** Beat lengths in frames at 30 fps. Total 570 = 19 s. */
export const BEATS = { brand: 75, problem: 60, info: 60, show: 90, proof: 60, end: 75 };
export const FILM_FRAMES = (s: Spec) =>
  BEATS.brand + BEATS.problem + 2 * (BEATS.info + BEATS.show) + (s.proof ? BEATS.proof : 0) + BEATS.end;

/** A steady sideways drift, 3 px a frame: enough for check.py to see a hold as alive. Alternates direction by beat. */
const drift = (f: number, dir: 1 | -1, speed = 3) => `translateX(${dir * (f - 30) * speed}px)`;
const rise = (f: number, at: number, dist = 60) => {
  const t = prog(f, at, at + 18, E.out);
  return { opacity: t, transform: `translateY(${(1 - t) * dist}px)` };
};

const Type: React.FC<{ s: Spec; title: string; sub: string; dir: 1 | -1; big?: boolean }> = ({ s, title, sub, dir, big }) => {
  const f = useCurrentFrame();
  const bar = interpolate(f, [0, 50], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ background: s.brand.bg, justifyContent: 'center', alignItems: 'center', fontFamily: s.brand.font }}>
      <div style={{ transform: drift(f, dir), textAlign: 'center', maxWidth: 1600 }}>
        <div style={{ ...rise(f, 0), color: s.brand.ink, fontSize: big ? 132 : 112, fontWeight: 800, letterSpacing: '-0.04em', lineHeight: 1.02 }}>{title}</div>
        <div style={{ ...rise(f, 10, 40), color: s.brand.ink, opacity: 0.72 * prog(f, 10, 28, E.out), fontSize: 48, fontWeight: 500, marginTop: 28 }}>{sub}</div>
        <div style={{ height: 8, width: 520 * bar, background: s.brand.accent, borderRadius: 4, margin: '40px auto 0' }} />
      </div>
    </AbsoluteFill>
  );
};

const ShowBeat: React.FC<{ s: Spec; feat: Spec['features'][number]; dir: 1 | -1 }> = ({ s, feat, dir }) => {
  const f = useCurrentFrame();
  const bw = 1500, bh = 820;
  // The window enters from 70% scale and keeps moving: a slow push plus a sideways drift that stays inside the frame.
  const k = interpolate(f, [0, 20, BEATS.show], [0.7, 0.9, 1.02], { easing: E.out, extrapolateRight: 'clamp' });
  const x = dir * (f - 45) * 3;
  const show = feat.show;
  const inner = !show ? null
    : typeof show === 'function' ? React.createElement(show, { frame: f, w: bw, h: bh - 52 })
    : <Img src={staticFile(show.img)} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top' }} />;
  return (
    <AbsoluteFill style={{ background: s.brand.bg, fontFamily: s.brand.font }}>
      <div style={{ position: 'absolute', left: 0, right: 0, top: 40, textAlign: 'center', color: s.brand.ink, fontSize: 80, fontWeight: 700, letterSpacing: '-0.03em', ...rise(f, 0, 30) }}>{feat.title}</div>
      <div style={{ position: 'absolute', left: (W - bw) / 2, top: 190, width: bw, height: bh, transformOrigin: '50% 0%', transform: `translateX(${x}px) scale(${k})` }}>
        <Browser w={bw} h={bh} url={feat.url ?? s.cta.url} dark={isDark(s.brand.base ?? s.brand.bg)}>{inner}</Browser>
      </div>
    </AbsoluteFill>
  );
};

const BrandBeat: React.FC<{ s: Spec; end?: boolean }> = ({ s, end }) => {
  const f = useCurrentFrame();
  const logoK = interpolate(f, [0, 30], [2.4, 1], { easing: E.out, extrapolateRight: 'clamp' });
  const wipe = interpolate(f, [0, 28], [0, 1], { easing: E.out, extrapolateRight: 'clamp' });
  const url = end ? s.cta.url.slice(0, Math.floor(clamp((f - 30) / 24) * s.cta.url.length)) : '';
  return (
    <AbsoluteFill style={{ background: s.brand.bg, justifyContent: 'center', alignItems: 'center', fontFamily: s.brand.font }}>
      {end ? null : <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: W * (1 - wipe), background: s.brand.accent }} />}
      <div style={{ transform: `${drift(f, end ? -1 : 1, 3)} scale(${1 + f * 0.002})`, textAlign: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 36, transform: `scale(${logoK})` }}>
          {s.brand.logo ? <Img src={staticFile(s.brand.logo)} style={{ height: 170 }} /> : null}
          <div style={{ color: s.brand.ink, fontSize: 168, fontWeight: 800, letterSpacing: '-0.045em' }}>{s.brand.name}</div>
        </div>
        {end ? (
          <div style={{ marginTop: 44, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
            <div style={{ ...rise(f, 15, 40), background: s.brand.accent, color: s.brand.base ?? s.brand.bg, fontSize: 44, fontWeight: 700, padding: '20px 48px', borderRadius: 999 }}>{s.cta.text}</div>
            <div style={{ color: s.brand.ink, opacity: 0.8, fontSize: 40, fontWeight: 500, minHeight: 48 }}>{url}</div>
          </div>
        ) : (
          <div style={{ ...rise(f, 12, 40), color: s.brand.ink, opacity: 0.78 * prog(f, 12, 30, E.out), fontSize: 54, fontWeight: 500, marginTop: 30 }}>{s.brand.line}</div>
        )}
      </div>
    </AbsoluteFill>
  );
};

const ProofBeat: React.FC<{ s: Spec }> = ({ s }) => {
  const f = useCurrentFrame();
  const p = s.proof!;
  const dp = (String(p.value).split('.')[1] ?? '').length;
  const n = p.value * prog(f, 0, 42, E.out);
  return (
    <AbsoluteFill style={{ background: s.brand.bg, justifyContent: 'center', alignItems: 'center', fontFamily: s.brand.font }}>
      <div style={{ transform: drift(f, -1), textAlign: 'center' }}>
        <div style={{ color: s.brand.accent, fontSize: 240, fontWeight: 800, letterSpacing: '-0.05em', lineHeight: 1 }}>{p.prefix ?? ''}{n.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })}{p.suffix ?? ''}</div>
        <div style={{ ...rise(f, 8, 30), color: s.brand.ink, fontSize: 56, fontWeight: 600, marginTop: 18 }}>{p.label}</div>
      </div>
    </AbsoluteFill>
  );
};

function isDark(color: string) {
  let hex = (color.match(/#([0-9a-f]{3,8})\b/i)?.[1] ?? '').toLowerCase();
  if (hex.length === 3) hex = hex.split('').map((c) => c + c).join('');
  const m = hex.match(/^([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})/);
  if (!m) return true;
  const [r, g, b] = [m[1], m[2], m[3]].map((x) => parseInt(x!, 16));
  return 0.2126 * r! + 0.7152 * g! + 0.0722 * b! < 128;
}

/** The whole film. Register it as in Root.example.tsx.txt: `const Main = () => <Film s={C} />`, durationInFrames={FILM_FRAMES(C)},
 * 1920x1080, 30 fps. Never pass the spec as defaultProps: Remotion serialises props to JSON and drops the show components. */
export const Film: React.FC<{ s: Spec }> = ({ s }) => {
  const seq: [number, React.ReactNode][] = [
    [BEATS.brand, <BrandBeat s={s} />],
    [BEATS.problem, <Type s={s} title={s.problem.title} sub={s.problem.sub} dir={-1} big />],
    [BEATS.info, <Type s={s} title={s.features[0].title} sub={s.features[0].sub} dir={1} />],
    [BEATS.show, <ShowBeat s={s} feat={s.features[0]} dir={-1} />],
    [BEATS.info, <Type s={s} title={s.features[1].title} sub={s.features[1].sub} dir={-1} />],
    [BEATS.show, <ShowBeat s={s} feat={s.features[1]} dir={1} />],
    ...(s.proof ? ([[BEATS.proof, <ProofBeat s={s} />]] as [number, React.ReactNode][]) : []),
    [BEATS.end, <BrandBeat s={s} end />],
  ];
  let at = 0;
  return (
    <AbsoluteFill style={{ background: s.brand.bg }}>
      {seq.map(([len, node], i) => {
        const from = at; at += len;
        return <Sequence key={i} from={from} durationInFrames={len}>{node}</Sequence>;
      })}
    </AbsoluteFill>
  );
};
