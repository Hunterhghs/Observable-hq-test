---
theme: dashboard
toc: false
---

<style>
  #globe-container { position: relative; }
  #globe-tooltip {
    position: absolute; pointer-events: none; display: none;
    background: #fff; border: 1px solid #e5e7eb; border-radius: 8px;
    padding: 0.6rem 0.9rem; font-size: 0.85rem; box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    color: #2c2c3a; z-index: 10; white-space: nowrap;
  }
  #globe-tooltip b { color: #4269d0; }
</style>

<div class="page-hero">
  <h1>🌍 3D Global GDP Globe</h1>
  <p>Interactive 3D visualization — drag to rotate, scroll to zoom. Bar height = GDP per capita. Color = region.</p>
</div>

<div class="grid grid-cols-4" style="margin-bottom: 1rem;" id="globe-kpi"></div>

<div class="card" style="padding: 0; overflow: hidden;">
  <div id="globe-container" style="width: 100%; min-height: 600px;">
    <div id="globe-tooltip"></div>
  </div>
</div>

<div class="grid grid-cols-4" style="margin-top: 1rem;">
  <div class="card" style="text-align:center;">
    <div style="display:flex;align-items:center;gap:0.3rem;justify-content:center;">
      <span style="width:12px;height:12px;background:#4269d0;border-radius:3px;display:inline-block;"></span>
      <span style="font-size:0.8rem;font-weight:600;">Western Europe</span>
    </div>
  </div>
  <div class="card" style="text-align:center;">
    <div style="display:flex;align-items:center;gap:0.3rem;justify-content:center;">
      <span style="width:12px;height:12px;background:#e6a817;border-radius:3px;display:inline-block;"></span>
      <span style="font-size:0.8rem;font-weight:600;">Central Europe</span>
    </div>
  </div>
  <div class="card" style="text-align:center;">
    <div style="display:flex;align-items:center;gap:0.3rem;justify-content:center;">
      <span style="width:12px;height:12px;background:#dc3545;border-radius:3px;display:inline-block;"></span>
      <span style="font-size:0.8rem;font-weight:600;">Eastern Europe</span>
    </div>
  </div>
  <div class="card" style="text-align:center;">
    <div style="display:flex;align-items:center;gap:0.3rem;justify-content:center;">
      <span style="width:12px;height:12px;background:#10b981;border-radius:3px;display:inline-block;"></span>
      <span style="font-size:0.8rem;font-weight:600;">Rest of World</span>
    </div>
  </div>
</div>

```js
import * as THREE from "npm:three";
import { OrbitControls } from "npm:three/examples/jsm/controls/OrbitControls.js";
const data = await FileAttachment("./data/convergence.json").json();
const $ = id => document.getElementById(id);

// ── Region lookup ──
const regionMap = {
  DE:"Western Europe",FR:"Western Europe",UK:"Western Europe",AT:"Western Europe",
  CH:"Western Europe",NL:"Western Europe",BE:"Western Europe",DK:"Western Europe",
  SE:"Western Europe",NO:"Western Europe",IE:"Western Europe",IS:"Western Europe",
  LU:"Western Europe",AD:"Western Europe",MC:"Western Europe",LI:"Western Europe",
  FI:"Northern Europe",IT:"Southern Europe",ES:"Southern Europe",PT:"Southern Europe",
  GR:"Southern Europe",CY:"Southern Europe",MT:"Southern Europe",SM:"Southern Europe",
  PL:"Central Europe",CZ:"Central Europe",SK:"Central Europe",HU:"Central Europe",
  SI:"Central Europe",HR:"Central Europe",EE:"Central Europe",LV:"Central Europe",
  LT:"Central Europe",
  RO:"Eastern Europe",BG:"Eastern Europe",RS:"Eastern Europe",BA:"Eastern Europe",
  MK:"Eastern Europe",AL:"Eastern Europe",ME:"Eastern Europe",UA:"Eastern Europe",
  BY:"Eastern Europe",MD:"Eastern Europe",GE:"Eastern Europe",AM:"Eastern Europe",
  AZ:"Eastern Europe",TR:"Eastern Europe",
};
function getRegion(r) { return regionMap[r.id] || "Other"; }

// ── Container setup ──
const container = $("globe-container");
const W = container.clientWidth;
const H = Math.min(620, W * 0.75);
container.style.height = H + "px";

const scene = new THREE.Scene();
scene.background = new THREE.Color("#f8f9fb");

const camera = new THREE.PerspectiveCamera(42, W / H, 0.5, 30);
camera.position.set(0, 1.5, 8);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.25;
controls.minDistance = 3.5;
controls.maxDistance = 14;
controls.target.set(0, 0, 0);

// ── Lighting ──
scene.add(new THREE.AmbientLight(0x8899cc, 2.8));
const sun = new THREE.DirectionalLight(0xffffff, 3.5);
sun.position.set(5, 8, 5);
scene.add(sun);
const fill = new THREE.DirectionalLight(0x8899cc, 1.2);
fill.position.set(-3, 0, -2);
scene.add(fill);

// ── Globe sphere ──
const globeGeom = new THREE.SphereGeometry(2.2, 72, 54);
const globeMat = new THREE.MeshStandardMaterial({
  color: 0xe8edf4,
  roughness: 0.7,
  metalness: 0.05,
});
const globe = new THREE.Mesh(globeGeom, globeMat);
scene.add(globe);

// ── Latitude/longitude grid lines ──
const gridGroup = new THREE.Group();
// Lat lines
for (let lat = -60; lat <= 60; lat += 30) {
  const phi = (90 - lat) * Math.PI / 180;
  const r = 2.21 * Math.cos(phi);
  const y = 2.21 * Math.sin(phi);
  const circleGeom = new THREE.TorusGeometry(r, 0.005, 8, 64);
  const circle = new THREE.Mesh(circleGeom, new THREE.MeshBasicMaterial({ color: 0xccccdd, transparent: true, opacity: 0.3 }));
  circle.position.y = y;
  gridGroup.add(circle);
}
// Lon lines
for (let lon = 0; lon < 360; lon += 30) {
  const theta = lon * Math.PI / 180;
  const points = [];
  for (let i = 0; i <= 64; i++) {
    const phi = (i / 64) * Math.PI;
    points.push(new THREE.Vector3(
      2.21 * Math.sin(phi) * Math.cos(theta),
      2.21 * Math.cos(phi),
      2.21 * Math.sin(phi) * Math.sin(theta)
    ));
  }
  const lineGeom = new THREE.BufferGeometry().setFromPoints(points);
  gridGroup.add(new THREE.Line(lineGeom, new THREE.LineBasicMaterial({ color: 0xccccdd, transparent: true, opacity: 0.3 })));
}
scene.add(gridGroup);

// ── Country bars ──
const regionColors = {
  "Western Europe": "#4269d0",
  "Central Europe": "#e6a817",
  "Eastern Europe": "#dc3545",
  "East Asia": "#10b981",
  "South Asia": "#8b5cf6",
  "North America": "#3b82f6",
  "South America": "#f59e0b",
  "Africa": "#ef4444",
};

// Use integration-era GDP
const eraIdx = 2;
const maxGDP = Math.max(...data.regions.map(r => r.eras[eraIdx].gdp_per_capita));
const minGDP = Math.min(...data.regions.map(r => r.eras[eraIdx].gdp_per_capita));

const barGroup = new THREE.Group();
const bars = []; // for raycasting

data.regions.forEach(r => {
  const e = r.eras[eraIdx];
  const gdp = e.gdp_per_capita;
  const t = (gdp - minGDP) / (maxGDP - minGDP);
  const barHeight = 0.25 + t * 1.8;
  
  // Convert lat/lon to 3D position on sphere
  const lat = r.lat * Math.PI / 180;
  const lon = r.lon * Math.PI / 180;
  const radius = 2.22;
  const x = radius * Math.cos(lat) * Math.cos(lon);
  const y = radius * Math.sin(lat);
  const z = radius * Math.cos(lat) * Math.sin(lon);
  
  // Bar geometry
  const barGeom = new THREE.CylinderGeometry(0.04, 0.04, barHeight, 8);
  const region = getRegion(r);
  const color = regionColors[region] || "#4269d0";
  
  const barMat = new THREE.MeshStandardMaterial({
    color: new THREE.Color(color),
    roughness: 0.3,
    metalness: 0.2,
  });
  const bar = new THREE.Mesh(barGeom, barMat);
  
  // Position bar: base on sphere surface, pointing outward
  const dir = new THREE.Vector3(x, y, z).normalize();
  bar.position.copy(dir.clone().multiplyScalar(radius + barHeight / 2));
  
  // Orient bar to point outward from sphere
  const up = new THREE.Vector3(0, 1, 0);
  const quat = new THREE.Quaternion().setFromUnitVectors(up, dir);
  bar.setRotationFromQuaternion(quat);
  
  bar.userData = { name: r.name, gdp: gdp, region: region, color: color, dir: dir, radius: radius };
  barGroup.add(bar);
  bars.push(bar);
  
  // Small sphere at bar tip
  const tipGeom = new THREE.SphereGeometry(0.05, 8, 8);
  const tipMat = new THREE.MeshStandardMaterial({ color: new THREE.Color(color), roughness: 0.2, metalness: 0.3, emissive: new THREE.Color(color), emissiveIntensity: 0.2 });
  const tip = new THREE.Mesh(tipGeom, tipMat);
  tip.position.copy(dir.clone().multiplyScalar(radius + barHeight + 0.03));
  barGroup.add(tip);
});

scene.add(barGroup);

// ── Raycaster for hover ──
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const tooltip = $("globe-tooltip");

container.addEventListener("mousemove", (e) => {
  const rect = container.getBoundingClientRect();
  mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(bars);
  
  if (intersects.length > 0) {
    const obj = intersects[0].object;
    const d = obj.userData;
    tooltip.style.display = "block";
    tooltip.style.left = (e.clientX - rect.left + 15) + "px";
    tooltip.style.top = (e.clientY - rect.top - 15) + "px";
    tooltip.innerHTML = `<b>${d.name}</b><br>GDP/capita: $${d.gdp.toLocaleString()}<br>Region: ${d.region}`;
    container.style.cursor = "pointer";
  } else {
    tooltip.style.display = "none";
    container.style.cursor = "grab";
  }
});

// ── KPI cards ──
const metrics = data.metrics[2];
const eraGDPS = data.regions.map(r => r.eras[2].gdp_per_capita);
$("globe-kpi").innerHTML = [
  `<div class="card" style="text-align:center;"><span class="metric-value accent">${data.meta.n_regions}</span><div class="metric-label">Countries</div></div>`,
  `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#4269d0;">$${(metrics.mean_gdp/1000).toFixed(1)}k</span><div class="metric-label">Mean GDP/cap</div></div>`,
  `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#e6a817;">$${(Math.max(...eraGDPS)/1000).toFixed(1)}k</span><div class="metric-label">Maximum</div></div>`,
  `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#dc3545;">$${(Math.min(...eraGDPS)/1000).toFixed(1)}k</span><div class="metric-label">Minimum</div></div>`,
].join("");

// ── Animate ──
(function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
})();
```
