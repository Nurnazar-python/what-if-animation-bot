import React from 'react';
import { defineEpisode, Timeline, LookDef, ParticleBurst, HudChip, Dial, FONT } from '../../engine';
import timeline from './timeline.json';
import { Sh1, Sh2, Sh3, Sh4, Sh5, Sh6, Sh7, Sh8, Sh9, Sh10, Sh11 } from './shots';

// The power's look: while gravity reverses, objects float, particles drift up, a GRAVITY chip blinks
// and a counter counts down from 10.
const gravityLook: LookDef = {
  grade: (lv) => `saturate(${1 - 0.3 * lv}) contrast(${1 + 0.15 * lv}) hue-rotate(${18 * lv}deg)`,
  jitter: 3,
  Overlay: ({ f, p, n }) => {
    const secs = 10 * (1 - p);
    const read = `${String(Math.floor(secs)).padStart(2, '0')}.${String(Math.floor((secs % 1) * 100)).padStart(2, '0')}`;
    return (
      <g>
        <ParticleBurst f={f} count={30} />
        <HudChip f={f} label="GRAVITY" icon="arrow-up" />
        <Dial p={1 - p} readout={read} />
        <text x={1820} y={1010} textAnchor="end" fontFamily={FONT.ui} fontSize={28} fill="#A0D0FF" opacity={0.6}>
          {`TAKE ${n + 2}`}
        </text>
      </g>
    );
  },
};

export const gravityReversed = defineEpisode('GravityReversed', {
  timeline: timeline as Timeline,
  shots: { Sh1, Sh2, Sh3, Sh4, Sh5, Sh6, Sh7, Sh8, Sh9, Sh10, Sh11 },
  looks: { gravity: gravityLook },
});