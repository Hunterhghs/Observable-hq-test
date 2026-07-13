---
theme: dashboard
toc: false
---

<div class="page-hero">
  <h1>3D Convergence Surface</h1>
  <p>GDP per capita across 47 regions and 3 eras — drag to rotate, scroll to zoom, right-drag to pan</p>
</div>

<div class="card" style="padding: 0; overflow: hidden; background: #050510;">
  <div id="surface-container" style="width: 100%; min-height: 550px;"></div>
</div>

<div class="grid grid-cols-2" style="margin-top: 1rem;">
  <div class="card" id="era-legend" style="text-align:center; padding:1rem;"></div>
  <div class="card" id="height-legend" style="text-align:center; padding:1rem;"></div>
</div>

```js
import * as THREE from "npm:three";
import { OrbitControls } from "npm:three/examples/jsm/controls/OrbitControls.js";
const data = await FileAttachment("./data/convergence.json").json();

const container = document.getElementById("surface-container");
const W = container.clientWidth;
const H = Math.min(580, W * 0.72);
container.style.height = H + "px";

// ── Scene ──
const scene = new THREE.Scene();
scene.background = new THREE.Color("#050510");
scene.fog = new THREE.FogExp2("#050510", 0.0008);

const camera = new THREE.PerspectiveCamera(48, W / H, 0.8, 60);
camera.position.set(7, 8, 12);
camera.lookAt(1.5, -0.5, 2);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.25;
controls.target.set(1.5, -0.5, 2);
controls.maxPolarAngle = Math.PI * 0.7;

// ── Lighting ──
scene.add(new THREE.AmbientLight(0x1a1a40, 1.5));
const sun = new THREE.DirectionalLight(0xffeedd, 3.5);
sun.position.set(10, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
sun.shadow.camera.near = 0.5;
sun.shadow.camera.far = 50;
sun.shadow.camera.left = -10;
sun.shadow.camera.right = 10;
sun.shadow.camera.top = 10;
sun.shadow.camera.bottom = -10;
scene.add(sun);
const rim = new THREE.DirectionalLight(0x4269d0, 1.2);
rim.position.set(-5, 3, -4);
scene.add(rim);

// ── Stars background ──
const starsGeom = new THREE.BufferGeometry();
const starVerts = [];
for (let i = 0; i < 400; i++) {
  starVerts.push((Math.random()-0.5)*30, (Math.random()-0.5)*20 + 3, (Math.random()-0.5)*25);
}
starsGeom.setAttribute("position", new THREE.Float32BufferAttribute(starVerts, 3));
const starsMat = new THREE.PointsMaterial({ color: 0x8899cc, size: 0.04, transparent: true, opacity: 0.6 });
scene.add(new THREE.Points(starsGeom, starsMat));

// ── Base grid ──
scene.add(new THREE.GridHelper(12, 16, 0x1a1a3a, 0x0a0a1a));

// ── Sort regions by avg GDP ──
const regions = [...data.regions].sort((a, b) => {
  const aAvg = a.eras.reduce((s, e) => s + e.gdp_per_capita, 0) / 3;
  const bAvg = b.eras.reduce((s, e) => s + e.gdp_per_capita, 0) / 3;
  return aAvg - bAvg;
});
const nRegions = regions.length;
const nEras = 3;
const allGDPs = regions.flatMap(r => r.eras.map(e => e.gdp_per_capita));
const minGDP = Math.min(...allGDPs);
const maxGDP = Math.max(...allGDPs);
const gdpRange = maxGDP - minGDP;

// ── Surface geometry ──
const surfWidth = 2.8;
const surfDepth = 7.5;
const surfGeom = new THREE.PlaneGeometry(surfWidth, surfDepth, nEras - 1, nRegions - 1);
surfGeom.rotateX(-Math.PI / 2);
const pos = surfGeom.attributes.position;
const surfColors = [];

for (let i = 0; i < nRegions; i++) {
  for (let j = 0; j < nEras; j++) {
    const idx = i * nEras + j;
    const gdp = regions[i].eras[j].gdp_per_capita;
    const t = (gdp - minGDP) / gdpRange;
    const z = t * 5.5 - 1.5;
    pos.setZ(idx, z);
    const c = new THREE.Color();
    c.setHSL(0.58 - t * 0.55, 0.85, 0.22 + t * 0.45);
    surfColors.push(c.r, c.g, c.b);
  }
}
surfGeom.setAttribute("color", new THREE.Float32BufferAttribute(surfColors, 3));
surfGeom.computeVertexNormals();

const surfMat = new THREE.MeshStandardMaterial({
  vertexColors: true,
  side: THREE.DoubleSide,
  roughness: 0.35,
  metalness: 0.15,
});
const surface = new THREE.Mesh(surfGeom, surfMat);
surface.position.set(1.5, 0, 0);
surface.receiveShadow = true;
surface.castShadow = true;
scene.add(surface);

// ── Wireframe ──
const wireMat = new THREE.MeshBasicMaterial({ color: 0x334466, wireframe: true, transparent: true, opacity: 0.12 });
const wire = new THREE.Mesh(surfGeom, wireMat);
wire.position.copy(surface.position);
scene.add(wire);

// ── Data point markers ──
const dotGeom = new THREE.SphereGeometry(0.05, 10, 10);
for (let i = 0; i < nRegions; i++) {
  for (let j = 0; j < nEras; j++) {
    const gdp = regions[i].eras[j].gdp_per_capita;
    const t = (gdp - minGDP) / gdpRange;
    const z = t * 5.5 - 1.5;
    const x = (j - 1) * (surfWidth / 2);
    const y = (i - nRegions / 2) * (surfDepth / nRegions);
    const c = new THREE.Color();
    c.setHSL(0.58 - t * 0.55, 0.9, 0.35 + t * 0.5);
    const mat = new THREE.MeshStandardMaterial({ color: c, roughness: 0.2, metalness: 0.4, emissive: c, emissiveIntensity: 0.4 });
    const dot = new THREE.Mesh(dotGeom, mat);
    dot.position.set(x + 1.5, z + 0.08, y);
    dot.castShadow = true;
    scene.add(dot);
  }
}

// ── Era label sprites ──
data.parameters.eras.forEach((era, j) => {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 96;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#bcd4ff";
  ctx.font = "bold 36px 'Source Serif 4', serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(era.name, 256, 48);
  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthTest: false }));
  sprite.position.set((j - 1) * (surfWidth / 2) + 1.5, 5, -(nRegions / 2) * (surfDepth / nRegions) - 0.8);
  sprite.scale.set(2.5, 0.5, 1);
  scene.add(sprite);
});

// ── Legends ──
document.getElementById("era-legend").innerHTML = `
  <div class="metric-label">Eras (X Axis)</div>
  <div style="display:flex;gap:1.5rem;justify-content:center;margin-top:0.4rem;font-size:0.9rem;">
    ${data.parameters.eras.map(e => `<span style="color:#bcd4ff;">◆ ${e.name}<br><span style="color:var(--muted);">${e.year_start}–${e.year_end}</span></span>`).join("")}
  </div>`;
document.getElementById("height-legend").innerHTML = `
  <div class="metric-label">GDP per Capita (Height + Color)</div>
  <div style="display:flex;align-items:center;justify-content:center;gap:0.5rem;margin-top:0.4rem;">
    <span style="color:#ff6b6b;">$${(minGDP/1000).toFixed(0)}k</span>
    <div style="width:180px;height:10px;border-radius:5px;background:linear-gradient(90deg,#1a3a5c,#1a6b5c,#5aaa5c,#c0d840,#ffcc00);"></div>
    <span style="color:#ffd93d;">$${(maxGDP/1000).toFixed(0)}k</span>
  </div>`;

// ── Animate ──
const clock = new THREE.Clock();
(function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.1);
  controls.update();
  renderer.render(scene, camera);
})();
```
