import React from 'react';
import { Hero, Study, Desk, Rooftop, Mug, Cat, camT, kf, basePose, poseAt, LOOKS, TitleCard, ShotProps } from '../../engine';
const PIP = LOOKS.pipHood;

// Simple reusable shot: Pip in the study. Each is a pure function of its own clock t.
const SimpleShot: React.FC<ShotProps & { set?: 'study' | 'rooftop'; prop?: 'mug' | 'cat' | 'none' }> = ({ t, set = 'study', prop = 'none' }) => {
  const pose = poseAt(t, [{ f: 0, p: basePose }]);
  const scale = kf(t, [[0, 0.9], [40, 1.0]]);
  return (
    <g transform={camT(960, 545, scale)}>
      {set === 'rooftop' ? <Rooftop t={t} /> : <Study t={t} />}
      <Hero look={PIP} pose={pose} />
      {prop === 'mug' && <Mug x={1120} y={700} rot={0} f={t} />}
      {prop === 'cat' && <Cat x={900} y={640} mood="alert" f={t} />}
    </g>
  );
};

export const S1: React.FC<ShotProps> = ({ t }) => <SimpleShot t={t} />;

export const S2: React.FC<ShotProps> = ({ t }) => <SimpleShot t={t} />;

export const S3: React.FC<ShotProps> = ({ t }) => <SimpleShot t={t} />;

export const S4: React.FC<ShotProps> = ({ t }) => <SimpleShot t={t} />;

export const S5: React.FC<ShotProps> = ({ t }) => <SimpleShot t={t} />;
