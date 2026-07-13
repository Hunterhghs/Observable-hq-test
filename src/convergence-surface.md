---
theme: dashboard
toc: false
---

<div class="page-hero">
  <h1>3D Convergence Surface</h1>
  <p>GDP per capita across regions and eras — rotate, zoom, and pan to explore convergence patterns</p>
</div>

<div class="card" style="padding: 0; overflow: hidden; background: #0a0a0f;">
  <div id="surface-container" style="width: 100%; min-height: 520px;"></div>
</div>

<div class="grid grid-cols-3" style="margin-top: 1rem;">
  <div class="card" style="text-align: center;">
    <div class="metric-label">X Axis</div>
    <div style="font-weight: 600;">Era → Time</div>
  </div>
  <div class="card" style="text-align: center;">
    <div class="metric-label">Y Axis</div>
    <div style="font-weight: 600;">Region (sorted by GDP)</div>
  </div>
  <div class="card" style="text-align: center;">
    <div class="metric-label">Z Axis (Height)</div>
    <div style="font-weight: 600;">GDP per Capita ($)</div>
  </div>
</div>

```js
import * as THREE from "npm:three";
import { OrbitControls } from "npm:three/examples/jsm/controls/OrbitControls.js";

const data = await FileAttachment("./data/convergence.json").json();

const container = document.getElementById("surface-container");
const W = container.clientWidth;
const H = Math.min(520, W * 0.7);
container.style.height = H + "px";

const scene = new THREE.Scene();
scene.background = new THREE.Color("#0a0a0f");
scene.fog = new THREE.Fog("#0a0a0f", 20, 50);

const camera = new THREE.PerspectiveCamera(50, W / H, 0.5, 80);
camera.position.set(8, 9, 14);
camera.lookAt(1.5, -1, 2);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.3;
controls.target.set(1.5, -1, 3);

// Lighting
scene.add(new THREE.AmbientLight(0x303050, 2.5));
const key = new THREE.DirectionalLight(0xffffff, 2);
key.position.set(8, 12, 8);
scene.add(key);
const fill = new THREE.DirectionalLight(0x4269d0, 0.6);
fill.position.set(-4, 2, -2);
scene.add(fill);

// Base plane
const planeGeom = new THREE.PlaneGeometry(12, 10);
const planeMat = new THREE.MeshStandardMaterial({ color: 0x111122, roughness: 0.9, metalness: 0.1 });
const plane = new THREE.Mesh(planeGeom, planeMat);
plane.rotation.x = -Math.PI / 2;
plane.position.set(1.5, -3.5, 0);
plane.receiveShadow = true;
scene.add(plane);

// Grid
scene.add(new THREE.GridHelper(14, 14, 0x222244, 0x141428));

// Sort regions by GDP for Y axis
const regions = [...data.regions].sort((a, b) => {
  const avgA = a.eras.reduce((s, e) => s + e.gdp_per_capita, 0) / 3;
  const avgB = b.eras.reduce((s, e) => s + e.gdp_per_capita, 0) / 3;
  return avgA - avgB;
});

const nRegions = regions.length;
const nEras = 3;
const maxGDP = Math.max(...regions.flatMap(r => r.eras.map(e => e.gdp_per_capita)));

// Surface vertices
const cols = nEras;
const rows = nRegions;
const geometry = new THREE.PlaneGeometry(2.5, 7, cols - 1, rows - 1);
geometry.rotateX(-Math.PI / 2);
const positions = geometry.attributes.position;

for (let i = 0; i < rows; i++) {
  for (let j = 0; j < cols; j++) {
    const idx = (i * cols + j);
    const gdp = regions[i].eras[j].gdp_per_capita;
    const z = (gdp / maxGDP) * 6 - 2.5;
    positions.setZ(idx, z);
  }
}
geometry.computeVertexNormals();

// Color by height
const colors = [];
for (let i = 0; i < rows; i++) {
  for (let j = 0; j < cols; j++) {
    const gdp = regions[i].eras[j].gdp_per_capita;
    const t = gdp / maxGDP;
    const c = new THREE.Color();
    c.setHSL(0.6 - t * 0.55, 0.8, 0.25 + t * 0.4);
    colors.push(c.r, c.g, c.b);
  }
}
geometry.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));

const surfaceMat = new THREE.MeshStandardMaterial({
  vertexColors: true,
  side: THREE.DoubleSide,
  roughness: 0.4,
  metalness: 0.2,
  flatShading: false,
  transparent: true,
  opacity: 0.85,
});
const surface = new THREE.Mesh(geometry, surfaceMat);
surface.position.set(1.5, 0, 0);
surface.receiveShadow = true;
surface.castShadow = true;
scene.add(surface);

// Wireframe overlay
const wireMat = new THREE.MeshBasicMaterial({ color: 0x334466, wireframe: true, transparent: true, opacity: 0.15 });
const wireframe = new THREE.Mesh(geometry, wireMat);
wireframe.position.copy(surface.position);
scene.add(wireframe);

// Region labels (spheres at each point)
const labelGeom = new THREE.SphereGeometry(0.06, 8, 8);
for (let i = 0; i < rows; i++) {
  for (let j = 0; j < cols; j++) {
    const gdp = regions[i].eras[j].gdp_per_capita;
    const t = gdp / maxGDP;
    const z = (gdp / maxGDP) * 6 - 2.5;
    const x = (j - 1) * (2.5 / 2);
    const y = (i - rows / 2) * (7 / rows);
    const c = new THREE.Color();
    c.setHSL(0.6 - t * 0.55, 0.9, 0.3 + t * 0.5);
    const mat = new THREE.MeshStandardMaterial({ color: c, roughness: 0.2, metalness: 0.3, emissive: c, emissiveIntensity: 0.3 });
    const sphere = new THREE.Mesh(labelGeom, mat);
    sphere.position.set(x + 1.5, z + 0.1, y);
    scene.add(sphere);
  }
}

// Era labels
const eraNames = ["Pre-Transition", "Transition", "Integration"];
eraNames.forEach((name, j) => {
  const canvas = document.createElement("canvas");
  canvas.width = 256;
  canvas.height = 64;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#aaccff";
  ctx.font = "bold 24px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(name, 128, 40);
  const texture = new THREE.CanvasTexture(canvas);
  const spriteMat = new THREE.SpriteMaterial({ map: texture, transparent: true });
  const sprite = new THREE.Sprite(spriteMat);
  sprite.position.set((j - 1) * 1.25 + 1.5, 4.2, -(rows / 2) * (7 / rows) - 0.6);
  sprite.scale.set(2.5, 0.6, 1);
  scene.add(sprite);
});

// Animate
(function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
})();
```
