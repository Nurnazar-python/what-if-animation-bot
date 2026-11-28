import React from 'react';
import { defineEpisode, Timeline, LookDef } from '../../engine';
import timeline from './timeline.json';
import { S1, S2, S3, S4, S5 } from './shots';

const powerLook: LookDef = {
  grade: (lv) => `saturate(${1 - 0.3 * lv})`,
  jitter: 3,
};

export const FlyTest = defineEpisode('FlyTest', {
  timeline: timeline as Timeline,
  shots: { S1, S2, S3, S4, S5 },
  looks: { power: powerLook },
});
