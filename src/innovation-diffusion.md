---
theme: dashboard
toc: false
---

<style>
  #diff-bar { display:flex; align-items:center; gap:0.75rem; padding:0.75rem 1rem; background:#fff; border:1px solid #e5e7eb; border-radius:10px; margin-bottom:0.75rem; flex-wrap:wrap; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
  #diff-bar button, #diff-bar select { padding:0.4rem 0.9rem; border-radius:6px; border:1px solid #d1d5db; background:#fff; font-size:0.85rem; font-family:inherit; cursor:pointer; color:#374151; }
  #diff-bar button:hover, #diff-bar select:hover { border-color:#4269d0; }
  #diff-bar button.speed-active { background:#e8edf8; border-color:#4269d0; color:#4269d0; font-weight:600; }
  #diff-bar button.playing { background:#fef2f2; border-color:#dc3545; color:#dc3545; }
  #year-disp { font-size:2rem; font-weight:900; color:#4269d0; font-variant-numeric:tabular-nums; min-width:60px; text-align:center; }
  #diff-bar input[type=range] { -webkit-appearance:none; height:5px; background:#e5e7eb; border-radius:3px; width:200px; }
  #diff-bar input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; width:16px; height:16px; background:#4269d0; border-radius:50%; cursor:pointer; }
</style>

<div class="page-hero">
  <h1>💡 Innovation Diffusion Landscape</h1>
  <p>5,000 innovation events · Bass diffusion dynamics · 5 technology sectors · 1995–2025 · 3D spatial clustering over time</p>
</div>

<div id="diff-bar">
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Speed:</span>
  <button class="speed-active" data-sp="0.5">0.5×</button>
  <button data-sp="1">1×</button>
  <button data-sp="2">2×</button>
  <button data-sp="4">4×</button>
  <span style="width:1px;height:22px;background:#e5e7eb;margin:0 0.25rem;"></span>
  <button id="btn-play-d">▶ Play</button>
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Year:</span>
  <input type="range" id="year-slider-d" min="0" max="30" value="0" step="1">
  <span id="year-disp">1995</span>
  <span style="font-size:0.75rem;color:#6b7280;">Phase:</span>
  <span id="phase-label" style="font-weight:700;color:#4269d0;">Innovators</span>
</div>

<div class="grid grid-cols-5" style="margin-bottom:0.75rem;" id="diff-stats"></div>

<div class="grid grid-cols-4" style="gap:0.75rem;">
  <div class="card" style="grid-column:span 3; padding:0; overflow:hidden; background:#f8f9fb; position:relative;">
    <div id="diff-container" style="width:100%;height:540px;cursor:grab;"></div>
  </div>
  <div class="card" style="padding:0.75rem;">
    <h3 style="font-size:0.9rem;margin:0 0 0.5rem 0;">Sectors</h3>
    <div id="diff-legend"></div>
    <h3 style="font-size:0.9rem;margin:1rem 0 0.5rem 0;">Adoption by Sector</h3>
    <div id="diff-shares"></div>
  </div>
</div>

<div class="grid grid-cols-3" style="margin-top:0.75rem;">
  <div class="card"><h3 style="margin-top:0;">Adoption Curve (S-Curve)</h3><div id="adoption-chart"></div></div>
  <div class="card"><h3 style="margin-top:0;">Adoption by Region</h3><div id="region-chart"></div></div>
  <div class="card"><h3 style="margin-top:0;">Top Innovations by Impact</h3><div id="top-impact"></div></div>
</div>

```js
import * as THREE from "npm:three";
const $ = id => document.getElementById(id);

// ── Bass Diffusion Model ──
// N(t) = m * (1 - exp(-(p+q)*t)) / (1 + (q/p)*exp(-(p+q)*t))
// p = innovation coefficient (external influence)
// q = imitation coefficient (internal/word-of-mouth)
function bassAdoption(t, p, q, m) {
  const e = Math.exp(-(p+q)*t);
  return m * (1 - e) / (1 + (q/p)*e);
}

// ── Generate 5,000 innovation events ──
const N = 5000;
const YEARS = 31; // 1995-2025
const sectors = [
  {n:"AI & ML",c:"#4269d0",cx:0.15,cy:0.6,czBase:0.5,p:0.008,q:0.35,impactMul:2.5},
  {n:"Biotech",c:"#10b981",cx:0.35,cy:0.4,czBase:0.4,p:0.005,q:0.28,impactMul:2.0},
  {n:"Clean Energy",c:"#f59e0b",cx:0.55,cy:0.25,czBase:0.6,p:0.012,q:0.42,impactMul:1.8},
  {n:"Quantum",c:"#8b5cf6",cx:0.75,cy:0.7,czBase:0.3,p:0.003,q:0.22,impactMul:3.0},
  {n:"Robotics",c:"#dc3545",cx:0.9,cy:0.5,czBase:0.45,p:0.006,q:0.30,impactMul:2.2},
];
const regions = [
  {n:"North America",y:0.8},
  {n:"Europe",y:0.55},
  {n:"Asia-Pacific",y:0.3},
  {n:"Rest of World",y:0.05},
];

// Seeded PRNG
let seed=42;function rnd(){seed=(seed*16807)%2147483647;return(seed-1)/2147483646;}
function gauss(){let u=0,v=0;while(u===0)u=rnd();while(v===0)v=rnd();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}

// Assign each event a sector and region
const events=[];
for(let i=0;i<N;i++){
  const si=Math.floor(rnd()*sectors.length);
  const ri=Math.floor(rnd()*regions.length);
  const s=sectors[si],r=regions[ri];
  // Adoption year: when does this innovation cross the chasm?
  // Bass model gives the cumulative adoption curve; each event gets a random adoption time
  const adoptYear=5+rnd()*25; // year 0-25 of simulation → 1995-2020
  const impact=10**(1+rnd()*2.5)*s.impactMul; // economic impact
  const x0=s.cx+gauss()*0.12;
  const y0=r.y+gauss()*0.06;
  const z0=s.czBase+gauss()*0.08;
  events.push({id:i,sector:si,region:ri,color:s.c,adoptYear,impact,x0:Math.max(.02,Math.min(.98,x0)),y0:Math.max(.02,Math.min(.98,y0)),z0:Math.max(.05,Math.min(.95,z0))});
}

// ── 3D Scene ──
const container=$("diff-container"),W=container.clientWidth||900,H=540;
container.style.height=H+"px";
const scene=new THREE.Scene();scene.background=new THREE.Color("#f8f9fb");
const camera=new THREE.PerspectiveCamera(45,W/H,.3,15);
camera.position.set(.3,.7,1.8);camera.lookAt(.5,.4,.5);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(W,H);renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
container.appendChild(renderer.domElement);

// Manual rotation
let rotX=.4,rotY=-.5,autoRot=true,isDrag=false,lx=0,ly=0,baseDist=1.8;
container.addEventListener("mousedown",e=>{isDrag=true;lx=e.clientX;ly=e.clientY;container.style.cursor="grabbing";});
window.addEventListener("mouseup",()=>{isDrag=false;container.style.cursor="grab";});
window.addEventListener("mousemove",e=>{if(!isDrag)return;rotY+=(e.clientX-lx)*.005;rotX+=(e.clientY-ly)*.005;rotX=Math.max(.05,Math.min(1.4,rotX));lx=e.clientX;ly=e.clientY;});
container.addEventListener("wheel",e=>{e.preventDefault();camera.position.multiplyScalar(1+e.deltaY*.001);camera.position.clampLength(.8,6);},{passive:false});

// Lighting
scene.add(new THREE.AmbientLight(0x8899bb,2.5));
const sun=new THREE.DirectionalLight(0xffffff,1.8);sun.position.set(2,3,2);scene.add(sun);

// Bounding box
scene.add(new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1,1,1)),new THREE.LineBasicMaterial({color:0xd1d5db,transparent:true,opacity:.3}))).position.set(.5,.5,.5);

// Points
const ptGeom=new THREE.BufferGeometry();
const ptPos=new Float32Array(N*3),ptCol=new Float32Array(N*3),ptSizes=new Float32Array(N);
ptGeom.setAttribute("position",new THREE.BufferAttribute(ptPos,3));
ptGeom.setAttribute("color",new THREE.BufferAttribute(ptCol,3));

// Soft circle sprite
const cvs=document.createElement("canvas");cvs.width=32;cvs.height=32;
const ctx=cvs.getContext("2d"),grad=ctx.createRadialGradient(16,16,0,16,16,16);
grad.addColorStop(0,"rgba(255,255,255,1)");grad.addColorStop(.25,"rgba(255,255,255,.85)");grad.addColorStop(.6,"rgba(255,255,255,.15)");grad.addColorStop(1,"rgba(255,255,255,0)");
ctx.fillStyle=grad;ctx.fillRect(0,0,32,32);

const points=new THREE.Points(ptGeom,new THREE.PointsMaterial({size:.04,map:new THREE.CanvasTexture(cvs),vertexColors:true,blending:THREE.NormalBlending,depthWrite:false,transparent:true,opacity:.9}));
scene.add(points);

// ── State ──
let yr=5,playing=false,speed=1,timer=null;

function updatePoints(){
  let visible=0;
  for(let i=0;i<N;i++){
    const e=events[i];
    if(yr<e.adoptYear){
      // Not yet adopted — hide far away
      ptPos[i*3]=-10;ptPos[i*3+1]=-10;ptPos[i*3+2]=-10;
      ptCol[i*3]=0;ptCol[i*3+1]=0;ptCol[i*3+2]=0;
    } else {
      // Adopted — position with some drift over time
      const age=yr-e.adoptYear;
      const drift=gauss()*.003*age;
      const x=Math.max(.02,Math.min(.98,e.x0+drift));
      const y=Math.max(.02,Math.min(.98,e.y0+gauss()*.002*age));
      const z=Math.max(.05,Math.min(.95,e.z0+age*.008));
      ptPos[i*3]=x;ptPos[i*3+1]=y;ptPos[i*3+2]=z;
      const bc=new THREE.Color(e.color);
      const fade=Math.min(1,age*.15); // fade in over ~7 years
      bc.multiplyScalar(.3+.7*fade);
      ptCol[i*3]=bc.r;ptCol[i*3+1]=bc.g;ptCol[i*3+2]=bc.b;
      visible++;
    }
  }
  ptGeom.attributes.position.needsUpdate=true;
  ptGeom.attributes.color.needsUpdate=true;
  return visible;
}

function updateStats(){
  const visible=updatePoints();
  const adopted=events.filter(e=>yr>=e.adoptYear);
  const totalImpact=adopted.reduce((s,e)=>s+e.impact,0);
  const sectorCounts={};sectors.forEach((s,i)=>{sectorCounts[i]=adopted.filter(e=>e.sector===i).length;});
  const regionCounts={};regions.forEach((r,i)=>{regionCounts[i]=adopted.filter(e=>e.region===i).length;});
  const totAdopted=adopted.length;
  const pct=yr/YEARS;
  let phase="Innovators";
  if(pct>.16)phase="Early Adopters";
  if(pct>.34)phase="Early Majority";
  if(pct>.68)phase="Late Majority";
  if(pct>.84)phase="Laggards";

  $("phase-label").textContent=phase;
  $("year-disp").textContent=1995+yr;$("year-slider-d").value=yr;

  $("diff-stats").innerHTML=[
    `<div class="card" style="text-align:center;"><span class="metric-value accent">${totAdopted.toLocaleString()}</span><div class="metric-label">Adopted ({${(totAdopted/N*100).toFixed(0)}%})</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#4269d0;">$${(totalImpact/1e9).toFixed(1)}B</span><div class="metric-label">Total Impact</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#10b981;">${Object.keys(sectorCounts).filter(k=>sectorCounts[k]>0).length}</span><div class="metric-label">Active Sectors</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#8b5cf6;">${Object.keys(regionCounts).filter(k=>regionCounts[k]>0).length}</span><div class="metric-label">Active Regions</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#f59e0b;">${phase}</span><div class="metric-label">Diffusion Phase</div></div>`,
  ].join("");

  $("diff-legend").innerHTML=sectors.map(s=>`<div style="display:flex;align-items:center;gap:.4rem;padding:.15rem 0;font-size:.78rem;"><span style="width:10px;height:10px;border-radius:2px;background:${s.c};display:inline-block;"></span>${s.n}</div>`).join("");

  $("diff-shares").innerHTML=sectors.map((s,i)=>{
    const c=sectorCounts[i]||0,share=totAdopted>0?c/totAdopted*100:0;
    return `<div style="margin-bottom:.2rem;"><div style="display:flex;justify-content:space-between;font-size:.75rem;margin-bottom:.1rem;"><span>${s.n}</span><span style="font-weight:700;">${share.toFixed(0)}%</span></div><div style="height:4px;background:#f3f4f6;border-radius:2px;"><div style="width:${share.toFixed(0)}%;height:100%;background:${s.c};border-radius:2px;"></div></div></div>`;
  }).join("");

  // Adoption curve — simple HTML line
  const curveData=[];
  for(let y=0;y<YEARS;y++){curveData.push({year:1995+y,adopted:events.filter(e=>y>=e.adoptYear).length/N*100});}
  const aDiv=$("adoption-chart");aDiv.innerHTML="";
  const maxA=Math.max(...curveData.map(d=>d.adopted));
  const svgH=140,svgW=aDiv.clientWidth-20;
  const pts=curveData.map((d,i)=>`${(i/(YEARS-1))*svgW},${svgH-(d.adopted/maxA)*svgH}`).join(" ");
  const yrX=(yr/(YEARS-1))*svgW;
  aDiv.innerHTML=`<svg width="${svgW}" height="${svgH+30}" style="overflow:visible;">
    <polyline points="${pts}" fill="none" stroke="#4269d0" stroke-width="2.5"/>
    <line x1="${yrX}" y1="0" x2="${yrX}" y2="${svgH}" stroke="#dc3545" stroke-width="2" stroke-dasharray="4,3" opacity="0.6"/>
    <circle cx="${yrX}" cy="${svgH-(curveData[yr].adopted/maxA)*svgH}" r="4" fill="#dc3545"/>
    <text x="${svgW}" y="12" fill="#9ca3af" font-size="9" text-anchor="end">Innovators</text>
    <text x="${svgW}" y="${svgH*.84}" fill="#9ca3af" font-size="9" text-anchor="end">Early Adopters</text>
    <text x="${svgW}" y="${svgH*.5}" fill="#9ca3af" font-size="9" text-anchor="end">Early Majority</text>
    <text x="${svgW}" y="${svgH*.32}" fill="#9ca3af" font-size="9" text-anchor="end">Late Maj.</text>
    <text x="${svgW}" y="${svgH*.16}" fill="#9ca3af" font-size="9" text-anchor="end">Laggards</text>
  </svg>`;

  // Region chart — simple HTML bars
  const rDiv=$("region-chart");rDiv.innerHTML="";
  const maxR=Math.max(...Object.values(regionCounts),1);
  regions.forEach((r,i)=>{const v=regionCounts[i]||0,pct=v/maxR*100;rDiv.innerHTML+=`<div style="margin-bottom:6px;"><div style="display:flex;justify-content:space-between;font-size:.75rem;margin-bottom:2px;"><span>${r.n}</span><span style="font-weight:700;color:#4269d0;">${v.toLocaleString()}</span></div><div style="height:6px;background:#f3f4f6;border-radius:3px;"><div style="width:${pct}%;height:100%;background:#4269d0;border-radius:3px;"></div></div></div>`;});

  // Top impact
  const top=adopted.sort((a,b)=>b.impact-a.impact).slice(0,5);
  $("top-impact").innerHTML=top.map((e,i)=>`<div style="display:flex;justify-content:space-between;padding:.2rem 0;font-size:.8rem;border-bottom:1px solid #f3f4f6;"><span><b>${i+1}.</b> <span style="color:${e.color};">●</span> #${e.id}</span><span style="font-weight:700;">$${(e.impact/1e6).toFixed(0)}M</span></div>`).join("");
}

// ── Playback ──
let tickFn=()=>{yr=(yr+1)%YEARS;updateStats();$("btn-play-d").textContent=playing?"⏸ Pause":"▶ Play";$("btn-play-d").className=playing?"playing":"";if(playing)timer=setTimeout(tickFn,500/speed);};
$("btn-play-d").onclick=()=>{playing=!playing;if(playing)tickFn();else clearTimeout(timer);updateStats();};
$("year-slider-d").oninput=()=>{yr=+$("year-slider-d").value;updateStats();};
document.querySelectorAll("#diff-bar button[data-sp]").forEach(b=>{b.onclick=()=>{document.querySelectorAll("#diff-bar button[data-sp]").forEach(x=>x.classList.remove("speed-active"));b.classList.add("speed-active");speed=+b.dataset.sp;};});
document.addEventListener("keydown",e=>{if(e.code==="Space"&&document.activeElement===document.body){e.preventDefault();$("btn-play-d").click();}});

// ── Init ──
updateStats();

// ── Animate ──
(function animate(){requestAnimationFrame(animate);if(autoRot&&!isDrag)rotY+=.002;const r=camera.position.length();camera.position.x=r*Math.sin(rotY)*Math.cos(rotX);camera.position.y=r*Math.sin(rotX);camera.position.z=r*Math.cos(rotY)*Math.cos(rotX);camera.lookAt(.5,.4,.5);renderer.render(scene,camera);})();
```
