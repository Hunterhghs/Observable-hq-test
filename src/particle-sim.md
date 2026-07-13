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
</style>

<div class="page-hero">
  <h1>⚛️ 3D Economic Particle Simulator</h1>
  <p>2,500 economic entities · 7 sectors · 2000–2025 · 3D point cloud · Playable simulation</p>
</div>

<div id="sim-bar">
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Scenario:</span>
  <button class="sc-active" data-sc="0">Baseline</button>
  <button data-sc="1">Tech Boom</button>
  <button data-sc="2">Restructuring</button>
  <span style="width:1px;height:22px;background:#e5e7eb;margin:0 0.25rem;"></span>
  <button id="btn-play-sim">▶ Play</button>
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Year:</span>
  <input type="range" id="year-slider-sim" min="0" max="25" value="0" step="1">
  <span id="year-big">2000</span>
  <span style="font-size:0.75rem;color:#6b7280;">Speed:</span>
  <select id="speed-select">
    <option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option><option value="4">4×</option>
  </select>
</div>

<div class="grid grid-cols-4" style="margin-bottom:0.75rem;" id="particle-stats"></div>

<div class="grid grid-cols-4" style="gap:0.75rem;">
  <div class="card" style="grid-column:span 3; padding:0; overflow:hidden; background:#f8f9fb; position:relative;">
    <div id="particle-container" style="width:100%;height:540px;"></div>
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
const $ = id => document.getElementById(id);

// ── Generate particle data inline (fast, no download) ──
const N = 2500;
const YEARS = 26; // 2000-2025
const sectors = [
  {name:"Technology",color:"#4269d0",cx:0.70,cy:0.70,cz:0.50,count:0.22,growth:0.045},
  {name:"Manufacturing",color:"#e6a817",cx:0.30,cy:0.40,cz:0.60,count:0.20,growth:0.022},
  {name:"Finance",color:"#10b981",cx:0.60,cy:0.50,cz:0.30,count:0.13,growth:0.030},
  {name:"Healthcare",color:"#8b5cf6",cx:0.50,cy:0.30,cz:0.70,count:0.15,growth:0.040},
  {name:"Energy",color:"#dc3545",cx:0.40,cy:0.60,cz:0.40,count:0.10,growth:0.020},
  {name:"Consumer",color:"#f59e0b",cx:0.50,cy:0.50,cz:0.50,count:0.12,growth:0.025},
  {name:"RealEstate",color:"#ec4899",cx:0.30,cy:0.30,cz:0.30,count:0.08,growth:0.020},
];

// Seeded random
let seed = 2024;
function rand() { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }
function gauss() { let u=0,v=0; while(u===0)u=rand(); while(v===0)v=rand(); return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v); }

// Build entities
const entities = [];
let eid = 0;
sectors.forEach(s => {
  const n = Math.round(N * s.count);
  for (let i = 0; i < n; i++) {
    entities.push({
      id: eid++, sector: s.name, color: s.color,
      x0: Math.max(0.02,Math.min(0.98,s.cx+gauss()*0.15)),
      y0: Math.max(0.02,Math.min(0.98,s.cy+gauss()*0.15)),
      z0: Math.max(0.02,Math.min(0.98,s.cz+gauss()*0.12)),
      baseGDP: 10**(1.5+rand()*2.5),
      growth: s.growth,
      innov: rand()*0.3,
    });
  }
});

// Scenario modifiers
const scMods = [
  {name:"Baseline",mod:1.0,drift:0.003},
  {name:"Tech Boom",mod:1.6,drift:0.005},
  {name:"Restructuring",mod:0.7,drift:0.008},
];

// Precompute all positions for fast switching
const positions = {}; // positions[sc][yearIdx][entityIdx] = {x,y,z,size,color}
scMods.forEach((sm, sc) => {
  positions[sc] = [];
  for (let y = 0; y < YEARS; y++) {
    const t = y / YEARS;
    const frame = [];
    const allGDPs = [];
    entities.forEach(e => {
      const gdp = e.baseGDP * (1 + e.growth * sm.mod * (1 + 0.3*Math.sin(t*5)))**y;
      allGDPs.push(gdp);
    });
    const maxG = Math.max(...allGDPs);
    const minG = Math.min(...allGDPs);
    entities.forEach((e, i) => {
      const gdp = allGDPs[i];
      const gNorm = Math.log(gdp/minG) / Math.log(maxG/minG);
      const drift = sm.drift * t * 10;
      const x = Math.max(0.01,Math.min(0.99,e.x0+gauss()*drift));
      const y = Math.max(0.01,Math.min(0.99,e.y0+gauss()*drift));
      const z = Math.max(0.01,Math.min(0.99,e.z0+gauss()*drift*0.7));
      const size = 0.005 + gNorm * 0.03;
      const bc = new THREE.Color(e.color);
      bc.multiplyScalar(0.35 + gNorm * 0.65);
      frame.push({x,y,z,size,color:bc,gdp,innov:e.innov+gauss()*0.005*y});
    });
    positions[sc].push(frame);
  }
});

// ── 3D Scene ──
const container = $("particle-container");
const W = container.clientWidth || 800;
const H = 540;
container.style.height = H + "px";

const scene = new THREE.Scene();
scene.background = new THREE.Color("#f8f9fb");
const camera = new THREE.PerspectiveCamera(50, W / H, 0.3, 12);
camera.position.set(0.85, 0.75, 2.3);
camera.lookAt(0.5, 0.5, 0.5);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.08;
controls.autoRotate = true; controls.autoRotateSpeed = 0.2;
controls.target.set(0.5, 0.5, 0.5);

// Lighting
scene.add(new THREE.AmbientLight(0x8899bb, 2.5));
const sun = new THREE.DirectionalLight(0xffffff, 1.8);
sun.position.set(2, 3, 2); scene.add(sun);

// Bounding box
const boxLine = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1, 1, 1)),
  new THREE.LineBasicMaterial({color:0xd1d5db,transparent:true,opacity:0.35})
);
boxLine.position.set(0.5, 0.5, 0.5);
scene.add(boxLine);

// Grid
const grid = new THREE.GridHelper(1.2, 10, 0xe5e7eb, 0xf3f4f6);
grid.position.set(0.5, 0, 0.5); scene.add(grid);

// ── Points for ALL particles ──
const pointGeom = new THREE.BufferGeometry();
const pointPositions = new Float32Array(N * 3);
const pointColors = new Float32Array(N * 3);
pointGeom.setAttribute("position", new THREE.BufferAttribute(pointPositions, 3));
pointGeom.setAttribute("color", new THREE.BufferAttribute(pointColors, 3));

// Create a circle sprite texture
const canvas = document.createElement("canvas");
canvas.width = 32; canvas.height = 32;
const ctx = canvas.getContext("2d");
const gradient = ctx.createRadialGradient(16,16,0,16,16,16);
gradient.addColorStop(0,"rgba(255,255,255,1)");
gradient.addColorStop(0.3,"rgba(255,255,255,0.8)");
gradient.addColorStop(0.7,"rgba(255,255,255,0.1)");
gradient.addColorStop(1,"rgba(255,255,255,0)");
ctx.fillStyle = gradient; ctx.fillRect(0,0,32,32);
const spriteTex = new THREE.CanvasTexture(canvas);

const pointsMat = new THREE.PointsMaterial({
  size: 0.035, map: spriteTex,
  vertexColors: true, blending: THREE.NormalBlending,
  depthWrite: false, transparent: true, opacity: 0.85,
});
const points = new THREE.Points(pointGeom, pointsMat);
scene.add(points);

// ── State ──
let sc = 0, yearIdx = 0, playing = false, speed = 1, playTimer = null;

function updatePoints() {
  const frame = positions[sc][yearIdx];
  for (let i = 0; i < N; i++) {
    const p = frame[i];
    pointPositions[i*3] = p.x;
    pointPositions[i*3+1] = p.y;
    pointPositions[i*3+2] = p.z;
    pointColors[i*3] = p.color.r;
    pointColors[i*3+1] = p.color.g;
    pointColors[i*3+2] = p.color.b;
  }
  pointGeom.attributes.position.needsUpdate = true;
  pointGeom.attributes.color.needsUpdate = true;
}

// ── Stats ──
function updateStats() {
  const frame = positions[sc][yearIdx];
  const totalGDP = frame.reduce((s,p)=>s+p.gdp,0);
  const avgInnov = frame.reduce((s,p)=>s+p.innov,0)/N;
  const sectorGDPs = {};
  entities.forEach((e,i) => {
    sectorGDPs[e.sector] = (sectorGDPs[e.sector]||0) + frame[i].gdp;
  });
  const totalS = Object.values(sectorGDPs).reduce((a,b)=>a+b,0);

  $("particle-stats").innerHTML = [
    `<div class="card" style="text-align:center;"><span class="metric-value accent">${N.toLocaleString()}</span><div class="metric-label">Entities</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#4269d0;">$${(totalGDP/1000).toFixed(1)}B</span><div class="metric-label">Total GDP</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#059669;">${(avgInnov*100).toFixed(1)}%</span><div class="metric-label">Avg Innovation</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#e6a817;">${Object.keys(sectorGDPs).length}</span><div class="metric-label">Active Sectors</div></div>`,
  ].join("");

  $("sector-legend").innerHTML = sectors.map(s =>
    `<div style="display:flex;align-items:center;gap:0.4rem;padding:0.15rem 0;font-size:0.78rem;">
      <span style="width:10px;height:10px;border-radius:2px;background:${s.color};display:inline-block;"></span>${s.name}
    </div>`).join("");

  $("sector-shares").innerHTML = Object.entries(sectorGDPs).sort((a,b)=>b[1]-a[1]).map(([s,v]) =>
    `<div style="margin-bottom:0.2rem;">
      <div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-bottom:0.1rem;">
        <span>${s}</span><span style="font-weight:700;">${(v/totalS*100).toFixed(0)}%</span>
      </div>
      <div style="height:4px;background:#f3f4f6;border-radius:2px;">
        <div style="width:${(v/totalS*100).toFixed(0)}%;height:100%;background:${sectors.find(x=>x.name===s)?.color||'#ccc'};border-radius:2px;"></div>
      </div>
    </div>`).join("");

  // Top entities
  const ranked = entities.map((e,i) => ({...e,gdp:frame[i].gdp,innov:frame[i].innov})).sort((a,b)=>b.gdp-a.gdp);
  $("top-entities").innerHTML = ranked.slice(0,5).map((e,i) =>
    `<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;">
      <span><b>${i+1}.</b> <span style="color:${e.color};">●</span> #${e.id}</span>
      <span style="font-weight:700;">$${e.gdp.toFixed(0)}M</span></div>`).join("");

  $("top-innovation").innerHTML = [...ranked].sort((a,b)=>b.innov-a.innov).slice(0,5).map((e,i) =>
    `<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;">
      <span><b>${i+1}.</b> <span style="color:${e.color};">●</span> #${e.id}</span>
      <span style="font-weight:700;">${(e.innov*100).toFixed(1)}%</span></div>`).join("");

  // Gini
  const giniDiv = $("gini-chart"); giniDiv.innerHTML = "";
  const giniData = [];
  for (let y = 0; y < YEARS; y++) {
    const gdps = positions[sc][y].map(p=>p.gdp).sort((a,b)=>a-b);
    const n = gdps.length, sum = gdps.reduce((a,b)=>a+b,0);
    const gini = sum>0 ? gdps.reduce((s,g,i)=>s+(2*i-n-1)*g,0)/(n*sum) : 0;
    giniData.push({year:2000+y, gini});
  }
  giniDiv.appendChild(Plot.plot({
    width:giniDiv.clientWidth, height:160,
    style:{background:"transparent",color:"#374151",fontSize:"11px"},
    marginLeft:45,marginRight:10,marginTop:5,marginBottom:30,
    x:{label:null,grid:true}, y:{label:"Gini",grid:true},
    marks: [
      Plot.areaY(giniData,{x:"year",y:"gini",fill:"#4269d0",fillOpacity:0.1}),
      Plot.line(giniData,{x:"year",y:"gini",stroke:"#4269d0",strokeWidth:2}),
      Plot.ruleX([2000+yearIdx],{stroke:"#dc3545",strokeOpacity:0.6,strokeWidth:2}),
      Plot.dot([giniData[yearIdx]],{x:"year",y:"gini",fill:"#dc3545",r:4}),
    ]
  }));
}

// ── Render ──
function renderAll() {
  $("year-big").textContent = 2000 + yearIdx;
  $("year-slider-sim").value = yearIdx;
  updatePoints();
  updateStats();
  $("btn-play-sim").textContent = playing ? "⏸ Pause" : "▶ Play";
  $("btn-play-sim").className = playing ? "playing" : "";
}

// ── Controls ──
$("btn-play-sim").onclick = () => {
  playing = !playing;
  if (playing) { function t(){if(!playing)return;yearIdx=(yearIdx+1)%YEARS;renderAll();playTimer=setTimeout(t,500/speed);} t(); }
  else clearTimeout(playTimer);
  renderAll();
};
$("year-slider-sim").oninput = () => { yearIdx = +$("year-slider-sim").value; renderAll(); };
$("speed-select").onchange = () => { speed = +$("speed-select").value; };
document.querySelectorAll("#sim-bar button[data-sc]").forEach(b => {
  b.onclick = () => {
    document.querySelectorAll("#sim-bar button[data-sc]").forEach(x=>x.classList.remove("sc-active"));
    b.classList.add("sc-active"); sc = +b.dataset.sc; renderAll();
  };
});
document.addEventListener("keydown", e => {
  if (e.code==="Space"&&document.activeElement===document.body){e.preventDefault();$("btn-play-sim").click();}
  if (e.code==="ArrowRight"&&!playing){yearIdx=Math.min(YEARS-1,yearIdx+1);renderAll();}
  if (e.code==="ArrowLeft"&&!playing){yearIdx=Math.max(0,yearIdx-1);renderAll();}
});

// ── Init ──
renderAll();
(function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);})();
```
