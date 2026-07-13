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
    <div id="particle-container" style="width:100%;height:540px;cursor:grab;"></div>
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
import * as Plot from "npm:@observablehq/plot";
const $ = id => document.getElementById(id);

// ── Generate particles inline ──
const N = 2500, YEARS = 26;
const sectors = [
  {n:"Technology",c:"#4269d0",cx:0.70,cy:0.70,cz:0.50,pct:0.22,g:0.045},
  {n:"Manufacturing",c:"#e6a817",cx:0.30,cy:0.40,cz:0.60,pct:0.20,g:0.022},
  {n:"Finance",c:"#10b981",cx:0.60,cy:0.50,cz:0.30,pct:0.13,g:0.030},
  {n:"Healthcare",c:"#8b5cf6",cx:0.50,cy:0.30,cz:0.70,pct:0.15,g:0.040},
  {n:"Energy",c:"#dc3545",cx:0.40,cy:0.60,cz:0.40,pct:0.10,g:0.020},
  {n:"Consumer",c:"#f59e0b",cx:0.50,cy:0.50,cz:0.50,pct:0.12,g:0.025},
  {n:"RealEstate",c:"#ec4899",cx:0.30,cy:0.30,cz:0.30,pct:0.08,g:0.020},
];
let seed=2024; function rnd(){seed=(seed*16807)%2147483647;return(seed-1)/2147483646;}
function gauss(){let u=0,v=0;while(u===0)u=rnd();while(v===0)v=rnd();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}

const entities=[];
let eid=0;
sectors.forEach(s=>{const n=Math.round(N*s.pct);for(let i=0;i<n;i++)entities.push({id:eid++,sector:s.n,color:s.c,x0:Math.max(.02,Math.min(.98,s.cx+gauss()*.15)),y0:Math.max(.02,Math.min(.98,s.cy+gauss()*.15)),z0:Math.max(.02,Math.min(.98,s.cz+gauss()*.12)),baseGDP:10**(1.5+rnd()*2.5),growth:s.g,innov:rnd()*.3});});

const scMods=[{mod:1,drift:.003},{mod:1.6,drift:.005},{mod:.7,drift:.008}];
const positions=[[],[],[]];
scMods.forEach((sm,si)=>{for(let y=0;y<YEARS;y++){const t=y/YEARS,frame=[],allGDPs=entities.map(e=>e.baseGDP*(1+e.growth*sm.mod*(1+.3*Math.sin(t*5)))**y);const maxG=Math.max(...allGDPs),minG=Math.min(...allGDPs);entities.forEach((e,i)=>{const g=allGDPs[i],gNorm=Math.log(g/minG)/Math.log(maxG/minG),drift=sm.drift*t*10,x=Math.max(.01,Math.min(.99,e.x0+gauss()*drift)),y=Math.max(.01,Math.min(.99,e.y0+gauss()*drift)),z=Math.max(.01,Math.min(.99,e.z0+gauss()*drift*.7)),size=.005+gNorm*.03,bc=new THREE.Color(e.color);bc.multiplyScalar(.35+gNorm*.65);frame.push({x,y,z,size,color:bc,gdp:g,innov:e.innov+gauss()*.005*y});});positions[si].push(frame);}});

// ── Scene ──
const container=$("particle-container"),W=container.clientWidth||800,H=540;
container.style.height=H+"px";
const scene=new THREE.Scene();scene.background=new THREE.Color("#f8f9fb");
const camera=new THREE.PerspectiveCamera(50,W/H,.3,12);
camera.position.set(.85,.75,2.3);camera.lookAt(.5,.5,.5);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(W,H);renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
container.appendChild(renderer.domElement);

// Manual rotation (no OrbitControls)
let rotX=0,rotY=0,autoRotate=true,isDragging=false,lastX=0,lastY=0;
container.addEventListener("mousedown",e=>{isDragging=true;lastX=e.clientX;lastY=e.clientY;container.style.cursor="grabbing";});
window.addEventListener("mouseup",()=>{isDragging=false;container.style.cursor="grab";});
window.addEventListener("mousemove",e=>{if(!isDragging)return;rotY+=(e.clientX-lastX)*.005;rotX+=(e.clientY-lastY)*.005;rotX=Math.max(-1.2,Math.min(1.2,rotX));lastX=e.clientX;lastY=e.clientY;});
container.addEventListener("wheel",e=>{e.preventDefault();camera.position.multiplyScalar(1+e.deltaY*.001);camera.position.clampLength(1,5);},{passive:false});

// Lighting
scene.add(new THREE.AmbientLight(0x8899bb,2.5));
const sun=new THREE.DirectionalLight(0xffffff,1.8);sun.position.set(2,3,2);scene.add(sun);

// Bounding box
scene.add(new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1,1,1)),new THREE.LineBasicMaterial({color:0xd1d5db,transparent:true,opacity:.35}))).position.set(.5,.5,.5);
const grid=new THREE.GridHelper(1.2,10,0xe5e7eb,0xf3f4f6);grid.position.set(.5,0,.5);scene.add(grid);

// Points
const ptGeom=new THREE.BufferGeometry();
const ptPos=new Float32Array(N*3),ptCol=new Float32Array(N*3);
ptGeom.setAttribute("position",new THREE.BufferAttribute(ptPos,3));
ptGeom.setAttribute("color",new THREE.BufferAttribute(ptCol,3));
const cvs=document.createElement("canvas");cvs.width=32;cvs.height=32;
const ctx=cvs.getContext("2d"),grad=ctx.createRadialGradient(16,16,0,16,16,16);
grad.addColorStop(0,"rgba(255,255,255,1)");grad.addColorStop(.3,"rgba(255,255,255,.8)");grad.addColorStop(.7,"rgba(255,255,255,.1)");grad.addColorStop(1,"rgba(255,255,255,0)");
ctx.fillStyle=grad;ctx.fillRect(0,0,32,32);
const points=new THREE.Points(ptGeom,new THREE.PointsMaterial({size:.035,map:new THREE.CanvasTexture(cvs),vertexColors:true,blending:THREE.NormalBlending,depthWrite:false,transparent:true,opacity:.85}));
scene.add(points);

// ── State ──
let sc=0,yr=0,playing=false,speed=1,timer=null;

function updatePoints(){
  const f=positions[sc][yr];
  for(let i=0;i<N;i++){const p=f[i];ptPos[i*3]=p.x;ptPos[i*3+1]=p.y;ptPos[i*3+2]=p.z;ptCol[i*3]=p.color.r;ptCol[i*3+1]=p.color.g;ptCol[i*3+2]=p.color.b;}
  ptGeom.attributes.position.needsUpdate=true;ptGeom.attributes.color.needsUpdate=true;
}

function updateStats(){
  const f=positions[sc][yr],totGDP=f.reduce((s,p)=>s+p.gdp,0),avgInn=f.reduce((s,p)=>s+p.innov,0)/N;
  const sGDP={};entities.forEach((e,i)=>{sGDP[e.sector]=(sGDP[e.sector]||0)+f[i].gdp;});
  const totS=Object.values(sGDP).reduce((a,b)=>a+b,0);

  $("particle-stats").innerHTML=[
    `<div class="card" style="text-align:center;"><span class="metric-value accent">${N.toLocaleString()}</span><div class="metric-label">Entities</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#4269d0;">$${(totGDP/1000).toFixed(1)}B</span><div class="metric-label">Total GDP</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#059669;">${(avgInn*100).toFixed(1)}%</span><div class="metric-label">Avg Innovation</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#e6a817;">${Object.keys(sGDP).length}</span><div class="metric-label">Active Sectors</div></div>`,
  ].join("");

  $("sector-legend").innerHTML=sectors.map(s=>`<div style="display:flex;align-items:center;gap:0.4rem;padding:0.15rem 0;font-size:0.78rem;"><span style="width:10px;height:10px;border-radius:2px;background:${s.c};display:inline-block;"></span>${s.n}</div>`).join("");
  $("sector-shares").innerHTML=Object.entries(sGDP).sort((a,b)=>b[1]-a[1]).map(([s,v])=>`<div style="margin-bottom:0.2rem;"><div style="display:flex;justify-content:space-between;font-size:0.75rem;margin-bottom:0.1rem;"><span>${s}</span><span style="font-weight:700;">${(v/totS*100).toFixed(0)}%</span></div><div style="height:4px;background:#f3f4f6;border-radius:2px;"><div style="width:${(v/totS*100).toFixed(0)}%;height:100%;background:${sectors.find(x=>x.n===s)?.c||'#ccc'};border-radius:2px;"></div></div></div>`).join("");

  const ranked=entities.map((e,i)=>({...e,gdp:f[i].gdp,innov:f[i].innov})).sort((a,b)=>b.gdp-a.gdp);
  $("top-entities").innerHTML=ranked.slice(0,5).map((e,i)=>`<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;"><span><b>${i+1}.</b> <span style="color:${e.color};">●</span> #${e.id}</span><span style="font-weight:700;">$${e.gdp.toFixed(0)}M</span></div>`).join("");
  $("top-innovation").innerHTML=[...ranked].sort((a,b)=>b.innov-a.innov).slice(0,5).map((e,i)=>`<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;"><span><b>${i+1}.</b> <span style="color:${e.color};">●</span> #${e.id}</span><span style="font-weight:700;">${(e.innov*100).toFixed(1)}%</span></div>`).join("");

  const giniDiv=$("gini-chart");giniDiv.innerHTML="";
  const gd=[];for(let y=0;y<YEARS;y++){const gdps=positions[sc][y].map(p=>p.gdp).sort((a,b)=>a-b),n=gdps.length,s=gdps.reduce((a,b)=>a+b,0);gd.push({year:2000+y,gini:s>0?gdps.reduce((a,g,i)=>a+(2*i-n-1)*g,0)/(n*s):0});}
  giniDiv.appendChild(Plot.plot({width:giniDiv.clientWidth,height:160,style:{background:"transparent",color:"#374151",fontSize:"11px"},marginLeft:45,marginRight:10,marginTop:5,marginBottom:30,x:{label:null,grid:true},y:{label:"Gini",grid:true},marks:[Plot.areaY(gd,{x:"year",y:"gini",fill:"#4269d0",fillOpacity:.1}),Plot.line(gd,{x:"year",y:"gini",stroke:"#4269d0",strokeWidth:2}),Plot.ruleX([2000+yr],{stroke:"#dc3545",strokeOpacity:.6,strokeWidth:2}),Plot.dot([gd[yr]],{x:"year",y:"gini",fill:"#dc3545",r:4})]}));
}

function renderAll(){
  $("year-big").textContent=2000+yr;$("year-slider-sim").value=yr;
  updatePoints();updateStats();
  $("btn-play-sim").textContent=playing?"⏸ Pause":"▶ Play";
  $("btn-play-sim").className=playing?"playing":"";
}

$("btn-play-sim").onclick=()=>{
  playing=!playing;
  if(playing){function t(){if(!playing)return;yr=(yr+1)%YEARS;renderAll();timer=setTimeout(t,500/speed);}t();}
  else clearTimeout(timer);
  renderAll();
};
$("year-slider-sim").oninput=()=>{yr=+$("year-slider-sim").value;renderAll();};
$("speed-select").onchange=()=>{speed=+$("speed-select").value;};
document.querySelectorAll("#sim-bar button[data-sc]").forEach(b=>{b.onclick=()=>{document.querySelectorAll("#sim-bar button[data-sc]").forEach(x=>x.classList.remove("sc-active"));b.classList.add("sc-active");sc=+b.dataset.sc;renderAll();};});
document.addEventListener("keydown",e=>{if(e.code==="Space"&&document.activeElement===document.body){e.preventDefault();$("btn-play-sim").click();}if(e.code==="ArrowRight"&&!playing){yr=Math.min(YEARS-1,yr+1);renderAll();}if(e.code==="ArrowLeft"&&!playing){yr=Math.max(0,yr-1);renderAll();}});

// ── Render loop ──
renderAll();
(function animate(){
  requestAnimationFrame(animate);
  if(autoRotate&&!isDragging)rotY+=.003;
  const r=2.3;camera.position.x=r*Math.sin(rotY)*Math.cos(rotX);
  camera.position.y=r*Math.sin(rotX);
  camera.position.z=r*Math.cos(rotY)*Math.cos(rotX);
  camera.lookAt(.5,.5,.5);
  renderer.render(scene,camera);
})();
```
