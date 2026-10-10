import type { Show } from './Film';
import { E, prog, stagger } from './motion';
// A rebuilt product surface: rows arrive one by one, the selected row highlights, a reply types in.
export const ExampleInbox: Show = ({ frame, w, h }) => {
  const rows = ['Sara · Instagram · Is the sale on today?', 'Ahmed · Email · Can I change my order?', 'Lena · WhatsApp · Do you ship to Erbil?', 'Omar · Facebook · What are your hours?'];
  const reply = 'Yes! 20% off everything until Sunday.';
  const typed = reply.slice(0, Math.floor(prog(frame, 40, 80, E.linear) * reply.length));
  return (
    <div style={{ width: w, height: h, background: '#151821', color: '#fff', font: '500 30px system-ui, sans-serif', padding: 40, boxSizing: 'border-box' }}>
      {rows.map((r, i) => {
        const t = prog(frame, stagger(i, rows.length, 24), stagger(i, rows.length, 24) + 14, E.out);
        return <div key={r} style={{ opacity: t, transform: `translateX(${(1 - t) * 80}px)`, padding: '22px 26px', borderRadius: 16, marginBottom: 16, background: i === 0 && frame > 30 ? '#7c5cff' : '#1f2330' }}>{r}</div>;
      })}
      <div style={{ marginTop: 30, padding: '24px 26px', borderRadius: 16, background: '#0d0f14', minHeight: 40 }}>{typed}</div>
    </div>
  );
};
