import React from 'react';
import {
  Hero, Cat, Mug, C, Pose, basePose, poseAt, kf, clamp, lerp, easeOut, easeIn, backOut, joints, toWorld, reachAngle, LEG_LEN, faceAt, LOOKS, HEAD,
  Foreground, camT, Sparkle, Tag, FocusRings, DizzyStars, TitleCard, walkPose, stepTop, hipGround,
  Study, Desk, Stairwell, Rooftop, Kid, S3, Glow, rnd, ShotProps,
} from '../../engine';

const PIP = LOOKS.pipHood;

export const Sh1: React.FC<ShotProps> = ({ t }) => {
  const cam = camT(t);
  return (
    <C f={t} cam={cam}>
      <Study t={t} />
      <Hero look={PIP} pose={basePose} face="neutral" t={t} />
      <Mug t={t} />
    </C>
  );
};

export const Sh2: React.FC<ShotProps> = ({ t }) => {
  const cam = camT(t);
  return (
    <C f={t} cam={cam}>
      <Desk t={t} />
      <Mug t={t} lift={easeOut(clamp(t / 22, 0, 1))} />
    </C>
  );
};

export const Sh3: React.FC<ShotProps> = ({ t }) => {
  const cam = camT(t);
  return (
    <C f={t} cam={cam}>
      <Rooftop t={t} />
      <Hero look={PIP} pose={basePose} face="surprise" t={t} />
    </C>
  );
};

export const Sh4: React.FC<ShotProps> = ({ t }) => {
  const cam = camT(t);
  return (
    <C f={t} cam={cam}>
      <Rooftop t={t} />
      <Sparkle f={t} count={5} />
    </C>
  );
};

export const Sh5: React.FC<ShotProps> = ({ t }) => {
  const cam = camT(t);
  return (
    <C f={t} cam={cam}>
      <Study t={t} />
      <Hero look={PIP} pose={basePose} face="neutral" t={t} />
      <Glow f={t} color="#112244" />
    </C>
  );
};

export const Sh6: React.FC<ShotProps> = ({ t, len }) => {
  const cam = camT(t);
  return (
    <C f={t} cam={cam}>
      <Study t={t} />
      <TitleCard lines={["WHAT IF THE MOON", "DISAPPEARED?"]} t={t} len={len} />
    </C>
  );
};

export const Sh7: React.FC<ShotProps> = ({ t }) => {
  const cam = camT(t);
  return (
    <C f={t} cam={cam}>
      <Rooftop t={t} />
      <FocusRings f={t} />
    </C>
  );
};

export const Sh8: React.FC<ShotProps> = ({ t }) => {
  const cam = camT(t);
  return (
    <C f={t} cam={cam}>
      <Study t={t} />
      <Hero look={PIP} pose={basePose} face="surprise" t={t} />
      <Tag text="AXIS WOBBLE" f={t} />
    </C>
  );
};
