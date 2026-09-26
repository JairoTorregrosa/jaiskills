// Deterministic WebGPU scene for Remotion: TSL compute kernel, 60k sprites, domain-warped background,
// bloom and IGN dither, every value driven from useCurrentFrame() (never TSL `time`, which reads the wall clock).
// Tested with Remotion 4.0.529 + R3F 9.8 + three r186: `npx remotion render <id> --gl=angle`; a still and a
// 4-tab render of the same frame were byte-identical. Walkthrough in references/stack-3d-shaders.md.
// Plumbing, not a design reference: the neon-particle look is a test pattern, and the corner label
// (WebGPU vs WebGL2-fallback) is burned in on purpose to verify the backend. Remove it for real work.

import React, {useLayoutEffect, useMemo} from 'react';
import {useFrame, useThree} from '@react-three/fiber';
import {ThreeWebGPUCanvas} from '@remotion/three/webgpu';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import * as THREE from 'three/webgpu';
import {
  Fn, uniform, instancedArray, instanceIndex, hash, vec3, vec4, float, sin, cos, mix, color,
  shapeCircle, pass, uv, vec2, smoothstep, renderOutput, screenCoordinate, interleavedGradientNoise, mx_fractal_noise_float,
} from 'three/tsl';
import {bloom} from 'three/addons/tsl/display/BloomNode.js';

const N = 60_000;

const World: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {gl, scene, camera} = useThree();
  const renderer = gl as unknown as THREE.WebGPURenderer;

  // --- GPU resources, built once ---------------------------------------------------------------
  const sim = useMemo(() => {
    const uT = uniform(0);             // seconds = frame / fps, NEVER the TSL `time` node (wall clock)
    const pos = instancedArray(N, 'vec3');
    // Stateless compute: position is a pure function of (index, t) -> any frame, any order, same pixels.
    const kernel = Fn(() => {
      const i = instanceIndex;
      const r = hash(i).mul(2.2).add(0.3);
      const a = hash(i.add(7)).mul(6.2831853).add(uT.mul(0.25).div(r));
      const y = hash(i.add(13)).sub(0.5).mul(0.5);
      const p = vec3(cos(a).mul(r), y, sin(a).mul(r));
      const n = mx_fractal_noise_float(p.mul(0.9).add(uT.mul(0.15)));
      pos.element(i).assign(p.add(vec3(0, n.mul(0.35), 0)));
    })().compute(N);
    const mat = new THREE.SpriteNodeMaterial({transparent: true, depthWrite: false, blending: THREE.AdditiveBlending});
    mat.positionNode = pos.toAttribute();
    mat.scaleNode = float(0.018);
    mat.colorNode = mix(color('#ff7a2f'), color('#3fa9ff'), hash(instanceIndex.add(3)));
    mat.opacityNode = shapeCircle().mul(0.3);
    const sprites = new THREE.Sprite(mat);
    sprites.count = N;
    sprites.frustumCulled = false;
    // Domain-warped fbm backdrop (TSL), driven by the same frame-derived uniform.
    const p = uv().mul(3.0);
    const q = vec2(mx_fractal_noise_float(p.add(uT.mul(0.05))), mx_fractal_noise_float(p.add(vec2(5.2, 1.3))));
    const f = mx_fractal_noise_float(p.add(q.mul(4.0)), 4);
    const bgMat = new THREE.MeshBasicNodeMaterial();
    bgMat.colorNode = mix(color('#05060a'), color('#3a1a4a'), smoothstep(-0.3, 0.7, f));
    const bg = new THREE.Mesh(new THREE.PlaneGeometry(40, 22), bgMat);
    bg.position.z = -6;
    sprites.add(bg);
    return {uT, kernel, sprites};
  }, []);

  const post = useMemo(() => {
    const uFrame = uniform(0);
    const pipeline = new THREE.RenderPipeline(renderer);
    const scenePass = pass(scene, camera);
    const hdr = scenePass.getTextureNode('output');
    const lit = hdr.add(bloom(hdr, 0.35, 0.4, 0.7));
    const display = renderOutput(lit);                  // tone mapping + sRGB happen HERE
    const n = interleavedGradientNoise(screenCoordinate.xy.add(uFrame.mul(5.588238)));
    pipeline.outputColorTransform = false;              // we already called renderOutput()
    pipeline.outputNode = vec4(display.rgb.add(n.sub(0.5).mul(2.5 / 255)), 1); // dither + faint grain in display space
    return {pipeline, uFrame};
  }, [renderer, scene, camera]);

  useLayoutEffect(() => {
    renderer.toneMapping = THREE.NeutralToneMapping;
    scene.background = new THREE.Color('#05060a');
    const be = (renderer as any).backend;
    console.warn(`[gpu] backend=${be?.isWebGPUBackend ? 'WebGPU' : 'WebGL2 fallback'}`);
  }, [renderer, scene]);

  // frame -> uniforms (pure), then R3F's advance() runs the priority-1 callback below.
  sim.uT.value = frame / fps;
  post.uFrame.value = frame;
  camera.position.set(Math.sin(frame / 90) * 1.2, 1.1, 5.2 - frame * 0.01);
  camera.lookAt(0, 0, 0);

  useFrame(() => {
    renderer.compute(sim.kernel);
    post.pipeline.render();
  }, 1);

  return <primitive object={sim.sprites} />;
};

export const Scene: React.FC = () => {
  const {width, height} = useVideoConfig();
  const [backend, setBackend] = React.useState('?');
  return (
    <>
      <ThreeWebGPUCanvas width={width} height={height} camera={{fov: 35, position: [0, 1, 5]}}
        onCreated={(st: any) => setBackend(st.gl.backend?.isWebGPUBackend ? 'WebGPU' : 'WebGL2-fallback')}>
        <World />
      </ThreeWebGPUCanvas>
      <div style={{position: 'absolute', left: 12, top: 8, color: 'white', font: '16px monospace'}}>{backend}</div>
    </>
  );
};
