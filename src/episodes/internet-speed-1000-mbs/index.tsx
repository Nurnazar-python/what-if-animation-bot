import React from 'react';
import { defineEpisode, Timeline, LookDef, HudChip, Dial } from '../../engine';
import timeline from './timeline.json';
import { Sh1, Sh2, Sh3, Sh4, Sh5, Sh6, Sh7, Sh8 } from './shots';

const powerLook: LookDef = {
  grade: (lv) => `contrast(${1 + lv * 0.2}) saturate(${1 + lv * 0.3})`,
  jitter: 1.5,
  Overlay: ({ f, lv, p }) => (
    <>
      <HudChip label="GIGABIT SPEED" icon="bolt" f={f} />
      <Dial p={p} readout="1000 Mb/s" />
    </>
  ),
};

export const InternetSpeed1000Mbs = defineEpisode('InternetSpeed1000Mbs', {
  timeline: timeline as Timeline,
  shots: { Sh1, Sh2, Sh3, Sh4, Sh5, Sh6, Sh7, Sh8 },
  looks: { power: powerLook },
});
