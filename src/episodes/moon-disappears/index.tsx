import React from 'react';
import { defineEpisode, Timeline, LookDef, HudChip, Dial } from '../../engine';
import timeline from './timeline.json';
import { Sh1, Sh2, Sh3, Sh4, Sh5, Sh6, Sh7, Sh8 } from './shots';

const powerLook: LookDef = {
  grade: (lv) => `contrast(${1 + lv * 0.2}) brightness(${1 - lv * 0.1})`,
  jitter: 2,
  Overlay: ({ f, lv, p }) => (
    <>
      <HudChip label="LUNAR DECAY" icon="moon" f={f} />
      <Dial p={p} readout="0.00G" />
    </>
  ),
};

export const MoonDisappears = defineEpisode('MoonDisappears', {
  timeline: timeline as Timeline,
  shots: { Sh1, Sh2, Sh3, Sh4, Sh5, Sh6, Sh7, Sh8 },
  looks: { power: powerLook },
});
