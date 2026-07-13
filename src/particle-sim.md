---
theme: dashboard
toc: false
---

<style>
  #sim-bar { display:flex; align-items:center; gap:0.75rem; padding:0.75rem 1rem; background:#fff; border:1px solid #e5e7eb; border-radius:10px; margin-bottom:0.75rem; flex-wrap:wrap; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
  #sim-bar button, #sim-bar select { padding:0.4rem 0.9rem; border-radius:6px; border:1px solid #d1d5db; background:#fff; font-size:0.85rem; font-family:inherit; cursor:pointer; color:#374151; }
  #sim-bar button:hover, #sim-bar select:hover { border-color:#4269d0; }
  #sim-bar button.sc-active { background:#e8edf8; border-color:#4269d0; color:#4269d0; font-weight:600; }
  #sim-bar button.playing { background:#fef2f2; border-color:#dc3545; color:#dc3545; }
  #year-big { font-size:2.2rem; font-weight:900; color:#4269d0; font-variant-numeric:tabular-nums; min-width:70px; text-align:center; }
  #sim-bar input[type=range] { -webkit-appearance:none; height:5px; background:#e5e7eb; border-radius:3px; width:180px; }
  #sim-bar input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; width:16px; height:16px; background:#4269d0; border-radius:50%; cursor:pointer; }
  #particle-tooltip { position:absolute; display:none; background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:0.6rem 0.9rem; font-size:0.85rem; box-shadow:0 4px 16px rgba(0,0,0,0.1); color:#2c2c3a; pointer-events:none; z-index:10; white-space:nowrap; }
  #particle-tooltip b { color:#4269d0; }
</style>

<div class="page-hero">
  <h1>⚛️ 3D Economic Particle Simulator</h1>
  <p>2,500 economic entities · 7 sectors · 2000–2025 · 3D point cloud · Playable simulation</p>
</div>

<div id="sim-bar">
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Scenario:</span>
  <button class="sc-active" data-sc="baseline">Baseline</button>
  <button data-sc="tech_boom">Tech Boom</button>
  <button data-sc="restructuring">Restructuring</button>
  <span style="width:1px;height:22px;background:#e5e7eb;margin:0 0.25rem;"></span>
  <button id="btn-play-sim">▶ Play</button>
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Year:</span>
  <input type="range" id="year-slider-sim" min="0" max="25" value="0" step="1">
  <span id="year-big">2000</span>
  <span style="font-size:0.75rem;color:#6b7280;">Speed:</span>
  <select id="speed-select">
    <option value="0.5">0.5×</option>
    <option value="1" selected>1×</option>
    <option value="2">2×</option>
    <option value="4">4×</option>
  </select>
</div>

<div class="grid grid-cols-4" style="margin-bottom:0.75rem;" id="particle-stats"></div>

<div class="grid grid-cols-4" style="gap:0.75rem;">
  <div class="card" style="grid-column:span 3; padding:0; overflow:hidden; background:#f8f9fb; position:relative;">
    <div id="particle-container" style="width:100%;height:540px;">
      <div id="particle-tooltip"></div>
    </div>
  </div>
  <div class="card" style="padding:0.75rem;">
    <h3 style="font-size:0.9rem;margin:0 0 0.5rem 0;">Sectors</h3>
    <div id="sector-legend"></div>
    <h3 style="font-size:0.9rem;margin:1rem 0 0.5rem 0;">GDP Share</h3>
    <div id="sector-shares"></div>
  </div>
</div>

<div class="grid grid-cols-3" style="margin-top:0.75rem;">
  <div class="card"><h3 style="margin-top:0;">Top Entities by GDP</h3><div id="top-entities"></div></div>
  <div class="card"><h3 style="margin-top:0;">Innovation Leaders</h3><div id="top-innovation"></div></div>
  <div class="card"><h3 style="margin-top:0;">Gini Trajectory</h3><div id="gini-chart"></div></div>
</div>

```js
import * as THREE from "npm:three";
import { OrbitControls } from "npm:three/examples/jsm/controls/OrbitControls.js";
import * as Plot from "npm:@observablehq/plot";
const data = await FileAttachment("./data/particles.json").json();
const $ = id => document.getElementById(id);

// ── State ──
let scenario = "baseline";
let yearIdx = 0;
let playing = false;
let speed = 1;
let playTimer = null;
const nYears = data.years.length;

// ── 3D Scene ──
const container = $("particle-container");
const W = container.clientWidth;
const H = 540;
container.style.height = H + "px";

const scene = new THREE.Scene();
scene.background = new THREE.Color("#f8f9fb");
scene.fog = new THREE.Fog("#f8f9fb", 2.5, 6);

const camera = new THREE.PerspectiveCamera(50, W / H, 0.3, 12);
camera.position.set(0.8, 0.7, 2.2);
camera.lookAt(0.5, 0.5, 0.5);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.2;
controls.target.set(0.5, 0.5, 0.5);
controls.minDistance = 0.8;
controls.maxDistance = 5;

// Lighting
scene.add(new THREE.AmbientLight(0x8899bb, 2.5));
const sun = new THREE.DirectionalLight(0xffffff, 2);
sun.position.set(2, 3, 2);
scene.add(sun);

// Bounding box wireframe
const boxGeom = new THREE.BoxGeometry(1, 1, 1);
const boxEdges = new THREE.EdgesGeometry(boxGeom);
const boxLine = new THREE.LineSegments(boxEdges, new THREE.LineBasicMaterial({ color: 0xd1d5db, transparent: true, opacity: 0.4 }));
boxLine.position.set(0.5, 0.5, 0.5);
scene.add(boxLine);

// Grid on floor
const gridHelper = new THREE.GridHelper(1.2, 10, 0xe5e7eb, 0xf3f4f6);
gridHelper.position.set(0.5, 0, 0.5);
scene.add(gridHelper);

// ── InstancedMesh for particles ──
const MAX_INSTANCES = data.entities.length;
const sphereGeom = new THREE.SphereGeometry(0.012, 6, 6);
const sphereMat = new THREE.MeshStandardMaterial({ roughness: 0.3, metalness: 0.1 });
const instancedMesh = new THREE.InstancedMesh(sphereGeom, sphereMat, MAX_INSTANCES);
instancedMesh.castShadow = true;
instancedMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
scene.add(instancedMesh);

// Dummy matrix and color
const dummy = new THREE.Object3D();
const tempColor = new THREE.Color();

// ── Raycaster for hover ──
const raycaster = new THREE.Raycaster();
raycaster.params.Points.threshold = 0.03;
const mouse = new THREE.Vector2();
const tooltip = $("particle-tooltip");
let hoveredEntity = null;

container.addEventListener("mousemove", (e) => {
  const rect = container.getBoundingClientRect();
  mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObject(instancedMesh);
  
  if (intersects.length > 0) {
    const instanceId = intersects[0].instanceId;
    if (instanceId !== undefined && instanceId < MAX_INSTANCES) {
      const entity = data.entities[instanceId];
      const ts = entity.scenarios[scenario][yearIdx];
      tooltip.style.display = "block";
      tooltip.style.left = (e.clientX - rect.left + 15) + "px";
      tooltip.style.top = (e.clientY - rect.top - 15) + "px";
      tooltip.innerHTML = `<b>Entity #${entity.id}</b> · ${entity.sector}<br>GDP: $${ts.gdp_m.toLocaleString()}M · Emp: ${ts.employees.toLocaleString()}<br>Innovation: ${(ts.innovation*100).toFixed(1)}%`;
      container.style.cursor = "pointer";
      hoveredEntity = instanceId;
    }
  } else {
    tooltip.style.display = "none";
    container.style.cursor = "grab";
    hoveredEntity = null;
  }
});

// ── Render particles for current year ──
function renderParticles() {
  const ts = data.entities.map(e => e.scenarios[scenario][yearIdx]);
  const maxGDP = Math.max(...ts.map(t => t.gdp_m));
  const minGDP = Math.min(...ts.map(t => t.gdp_m));
  
  data.entities.forEach((entity, i) => {
    const t = entity.scenarios[scenario][yearIdx];
    const x = t.x;
    const y = t.y;
    const z = t.z;
    
    // Size by GDP (log scale for better distribution)
    const gdpNorm = Math.log(t.gdp_m / minGDP) / Math.log(maxGDP / minGDP);
    const size = 0.005 + gdpNorm * 0.025;
    
    dummy.position.set(x, y, z);
    dummy.scale.setScalar(size);
    dummy.updateMatrix();
    instancedMesh.setMatrixAt(i, dummy.matrix);
    
    // Color by sector with brightness by GDP
    const baseColor = new THREE.Color(entity.color);
    const brightness = 0.4 + gdpNorm * 0.6;
    tempColor.copy(baseColor).multiplyScalar(brightness);
    instancedMesh.setColorAt(i, tempColor);
  });
  
  instancedMesh.instanceMatrix.needsUpdate = true;
  if (instancedMesh.instanceColor) instancedMesh.instanceColor.needsUpdate = true;
}

// ── UI Updates ──
function renderStats() {
  const agg = data.aggregates[scenario].years[yearIdx];
  $("particle-stats").innerHTML = [
    `<div class="card" style="text-align:center;"><span class="metric-value accent">${data.meta.n_entities.toLocaleString()}</span><div class="metric-label">Entities</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#4269d0;">$${agg.total_gdp_b.toFixed(1)}B</span><div class="metric-label">Total GDP</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#059669;">${agg.total_emp_m.toFixed(1)}M</span><div class="metric-label">Total Employment</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#e6a817;">${(agg.avg_innovation*100).toFixed(1)}%</span><div class="metric-label">Avg Innovation</div></div>`,
  ].join("");
  
  // Sector legend
  $("sector-legend").innerHTML = data.sectors.map(s =>
    `<div style="display:flex;align-items:center;gap:0.4rem;padding:0.15rem 0;font-size:0.78rem;">
      <span style="width:10px;height:10px;border-radius:2px;background:${data.sector_colors[s]};display:inline-block;"></span>${s}
    </div>`
  ).join("");
  
  // Sector shares
  const sd = agg.sector_gdps;
  const total = Object.values(sd).reduce((a,b)=>a+b,0);
  $("sector-shares").innerHTML = Object.entries(sd).sort((a,b)=>b[1]-a[1]).map(([s,v]) =>
    `<div style="margin-bottom:0.2rem;">
      <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-bottom:0.1rem;">
        <span>${s}</span><span style="font-weight:700;">${(v/total*100).toFixed(0)}%</span>
      </div>
      <div style="height:4px;background:#f3f4f6;border-radius:2px;">
        <div style="width:${(v/total*100).toFixed(0)}%;height:100%;background:${data.sector_colors[s]};border-radius:2px;"></div>
      </div>
    </div>`
  ).join("");
  
  // Top entities
  const sorted = data.entities.map(e => ({...e, ts: e.scenarios[scenario][yearIdx]})).sort((a,b) => b.ts.gdp_m - a.ts.gdp_m);
  $("top-entities").innerHTML = sorted.slice(0, 5).map((e, i) =>
    `<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;">
      <span><b>${i+1}.</b> <span style="color:${e.color};">●</span> #${e.id}</span>
      <span style="font-weight:700;">$${e.ts.gdp_m.toFixed(0)}M</span>
    </div>`
  ).join("");
  
  // Innovation leaders
  const innovSorted = [...data.entities.map(e => ({...e, ts: e.scenarios[scenario][yearIdx]}))].sort((a,b) => b.ts.innovation - a.ts.innovation);
  $("top-innovation").innerHTML = innovSorted.slice(0, 5).map((e, i) =>
    `<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;">
      <span><b>${i+1}.</b> <span style="color:${e.color};">●</span> #${e.id}</span>
      <span style="font-weight:700;">${(e.ts.innovation*100).toFixed(1)}%</span>
    </div>`
  ).join("");
  
  // Gini chart
  const giniDiv = $("gini-chart");
  giniDiv.innerHTML = "";
  const giniData = data.aggregates[scenario].years.map(y => ({year: y.year, gini: y.gini}));
  giniDiv.appendChild(Plot.plot({
    width: giniDiv.clientWidth,
    height: 160,
    style: {background:"transparent",color:"#374151",fontSize:"11px"},
    marginLeft: 45, marginRight: 10, marginTop: 5, marginBottom: 30,
    x: {label:null, grid:true},
    y: {label:"Gini", grid:true},
    marks: [
      Plot.areaY(giniData, {x:"year",y:"gini",fill:"#4269d0",fillOpacity:0.1}),
      Plot.line(giniData, {x:"year",y:"gini",stroke:"#4269d0",strokeWidth:2}),
      Plot.ruleX([data.years[yearIdx]], {stroke:"#dc3545",strokeOpacity:0.6,strokeWidth:2}),
      Plot.dot([giniData[yearIdx]], {x:"year",y:"gini",fill:"#dc3545",r:4}),
    ]
  }));
}

// ── Playback ──
function tick() {
  yearIdx = (yearIdx + 1) % nYears;
  renderAll();
  if (playing) playTimer = setTimeout(tick, 500 / speed);
}

function renderAll() {
  $("year-big").textContent = data.years[yearIdx];
  $("year-slider-sim").value = yearIdx;
  renderParticles();
  renderStats();
  updateButtons();
}

function updateButtons() {
  $("btn-play-sim").textContent = playing ? "⏸ Pause" : "▶ Play";
  $("btn-play-sim").className = playing ? "playing" : "";
}

// ── Controls ──
$("btn-play-sim").onclick = () => {
  playing = !playing;
  if (playing) tick();
  else clearTimeout(playTimer);
  updateButtons();
};
$("year-slider-sim").oninput = () => { yearIdx = parseInt($("year-slider-sim").value); renderAll(); };
$("speed-select").onchange = () => { speed = parseFloat($("speed-select").value); };

document.querySelectorAll("#sim-bar button[data-sc]").forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll("#sim-bar button[data-sc]").forEach(b => b.classList.remove("sc-active"));
    btn.classList.add("sc-active");
    scenario = btn.dataset.sc;
    renderAll();
  };
});

// Keyboard
document.addEventListener("keydown", e => {
  if (e.code === "Space" && document.activeElement === document.body) { e.preventDefault(); $("btn-play-sim").click(); }
  if (e.code === "ArrowRight" && !playing) { yearIdx = Math.min(nYears-1, yearIdx+1); renderAll(); }
  if (e.code === "ArrowLeft" && !playing) { yearIdx = Math.max(0, yearIdx-1); renderAll(); }
});

// ── Init ──
renderAll();
(function animate() { requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); })();
```
