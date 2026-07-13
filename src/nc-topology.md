---
theme: dashboard
toc: false
---

<style>
  #topo-bar { display:flex; align-items:center; gap:0.75rem; padding:0.75rem 1rem; background:#fff; border:1px solid #e5e7eb; border-radius:10px; margin-bottom:0.75rem; flex-wrap:wrap; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
  #topo-bar button, #topo-bar select { padding:0.4rem 0.9rem; border-radius:6px; border:1px solid #d1d5db; background:#fff; font-size:0.85rem; font-family:inherit; cursor:pointer; color:#374151; }
  #topo-bar button:hover, #topo-bar select:hover { border-color:#4269d0; }
  #topo-bar button.active { background:#e8edf8; border-color:#4269d0; color:#4269d0; font-weight:600; }
  #topo-bar button.playing { background:#fef2f2; border-color:#dc3545; color:#dc3545; }
  #year-big-t { font-size:2rem; font-weight:900; color:#4269d0; font-variant-numeric:tabular-nums; min-width:60px; text-align:center; }
  #topo-bar input[type=range] { -webkit-appearance:none; height:5px; background:#e5e7eb; border-radius:3px; width:160px; }
  #topo-bar input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; width:16px; height:16px; background:#4269d0; border-radius:50%; cursor:pointer; }
  #topo-tooltip { position:absolute; display:none; background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:0.6rem 0.9rem; font-size:0.85rem; box-shadow:0 4px 16px rgba(0,0,0,0.1); color:#2c2c3a; pointer-events:none; z-index:10; white-space:nowrap; }
  #topo-tooltip b { color:#4269d0; }
</style>

<div class="page-hero">
  <h1>🏔️ NC 3D Socioeconomic Topology</h1>
  <p>100 North Carolina counties extruded in 3D · Height = economic metric · Color = growth · 2010–2024</p>
</div>

<div id="topo-bar">
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Metric:</span>
  <select id="metric-select-t">
    <option value="gdp_per_capita">GDP per Capita</option>
    <option value="median_income">Median Income</option>
    <option value="population">Population</option>
    <option value="median_home_value">Median Home Value</option>
  </select>
  <span style="width:1px;height:22px;background:#e5e7eb;margin:0 0.25rem;"></span>
  <button id="btn-play-t">▶ Play</button>
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Year:</span>
  <input type="range" id="year-slider-t" min="0" max="14" value="14" step="1">
  <span id="year-big-t">2024</span>
  <span style="font-size:0.75rem;color:#6b7280;">Speed:</span>
  <select id="speed-select-t">
    <option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option>
  </select>
</div>

<div class="grid grid-cols-4" style="margin-bottom:0.75rem;" id="topo-stats"></div>

<div class="grid grid-cols-4" style="gap:0.75rem;">
  <div class="card" style="grid-column:span 3; padding:0; overflow:hidden; position:relative; background:#f0f2f5;">
    <div id="topo-container" style="width:100%;height:560px;cursor:grab;">
      <div id="topo-tooltip"></div>
    </div>
  </div>
  <div class="card" style="padding:0.75rem;">
    <h3 style="font-size:0.9rem;margin:0 0 0.5rem 0;">Top Counties</h3>
    <div id="topo-rank"></div>
    <h3 style="font-size:0.9rem;margin:1rem 0 0.5rem 0;">Bottom Counties</h3>
    <div id="topo-rank-btm"></div>
  </div>
</div>

```js
import * as THREE from "npm:three";
const ncData = await FileAttachment("./data/nc-counties.json").json();
const $ = id => document.getElementById(id);

// ── Load GeoJSON ──
const usTopo = await fetch("https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json").then(r => r.json());
const topoClient = await import("npm:topojson-client");
const ncGeo = topoClient.feature(usTopo, usTopo.objects.counties);
ncGeo.features = ncGeo.features.filter(f => f.id && String(f.id).startsWith("37"));

// ── Map county name → data ──
function cleanName(n) { return (n||"").replace(/ County$/i,"").toLowerCase(); }
const dataByName = {};
ncData.counties.forEach(c => { dataByName[c.name.toLowerCase()] = c; });

// ── Compute bounds for scaling ──
let minLon=Infinity,maxLon=-Infinity,minLat=Infinity,maxLat=-Infinity;
ncGeo.features.forEach(f => {
  if (f.geometry.type === "Polygon") {
    f.geometry.coordinates[0].forEach(([lon,lat]) => {
      if(lon<minLon)minLon=lon;if(lon>maxLon)maxLon=lon;
      if(lat<minLat)minLat=lat;if(lat>maxLat)maxLat=lat;
    });
  } else if (f.geometry.type === "MultiPolygon") {
    f.geometry.coordinates.forEach(poly => {
      poly[0].forEach(([lon,lat]) => {
        if(lon<minLon)minLon=lon;if(lon>maxLon)maxLon=lon;
        if(lat<minLat)minLat=lat;if(lat>maxLat)maxLat=lat;
      });
    });
  }
});
const pad = 0.3;
minLon-=pad;maxLon+=pad;minLat-=pad;maxLat+=pad;
const scaleX = 10 / (maxLon-minLon);
const scaleZ = 8 / (maxLat-minLat);

function project(lon, lat) {
  return { x: (lon-minLon)*scaleX - 5, z: (lat-minLat)*scaleZ - 4 };
}

// ── Scene ──
const container = $("topo-container");
const W = container.clientWidth||900, H = 560;
container.style.height = H+"px";

const scene = new THREE.Scene();
scene.background = new THREE.Color("#f0f2f5");
const camera = new THREE.PerspectiveCamera(45, W/H, 0.5, 40);
camera.position.set(0, 6, 10);
camera.lookAt(0, 0.5, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(W, H);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
container.appendChild(renderer.domElement);

// Manual rotation
let rotX=0.35,rotY=0,autoRot=true,isDrag=false,lx=0,ly=0;
container.addEventListener("mousedown",e=>{isDrag=true;lx=e.clientX;ly=e.clientY;container.style.cursor="grabbing";});
window.addEventListener("mouseup",()=>{isDrag=false;container.style.cursor="grab";});
window.addEventListener("mousemove",e=>{if(!isDrag)return;rotY+=(e.clientX-lx)*.005;rotX+=(e.clientY-ly)*.005;rotX=Math.max(.05,Math.min(1.4,rotX));lx=e.clientX;ly=e.clientY;});
container.addEventListener("wheel",e=>{e.preventDefault();camera.position.multiplyScalar(1+e.deltaY*.001);camera.position.clampLength(5,25);},{passive:false});

// Lighting
scene.add(new THREE.AmbientLight(0xffffff, 1.8));
const sun = new THREE.DirectionalLight(0xffffff, 2.5);
sun.position.set(8, 12, 5); sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.near=0.5;sun.shadow.camera.far=50;
sun.shadow.camera.left=-8;sun.shadow.camera.right=8;
sun.shadow.camera.top=8;sun.shadow.camera.bottom=-8;
scene.add(sun);
const fill = new THREE.DirectionalLight(0x8899cc, 0.6);
fill.position.set(-3,2,-3);scene.add(fill);

// Base plane
const planeGeom = new THREE.PlaneGeometry(12, 10);
const planeMat = new THREE.MeshStandardMaterial({ color:0xe8ebf0, roughness:0.9 });
const plane = new THREE.Mesh(planeGeom, planeMat);
plane.rotation.x = -Math.PI/2;
plane.position.set(0, -0.05, 0);
plane.receiveShadow = true;
scene.add(plane);

// ── Build county blocks ──
const countyGroup = new THREE.Group();
const countyMeshes = [];
const extrudedMap = new Map(); // name → mesh

let currentMetric = "gdp_per_capita";
let currentYear = 14;

function getMetric(c, yearIdx, metric) {
  if (!c || !c.years || !c.years[yearIdx]) return 0;
  return c.years[yearIdx][metric] || 0;
}

function getColor(value, min, max) {
  if (max===min) return new THREE.Color("#4269d0");
  const t = (value-min)/(max-min);
  const c = new THREE.Color();
  c.setHSL(0.58 - t*0.5, 0.7, 0.3 + t*0.45);
  return c;
}

function rebuildCountyBlocks() {
  // Remove old
  while(countyGroup.children.length>0) countyGroup.remove(countyGroup.children[0]);
  countyMeshes.length = 0;
  extrudedMap.clear();

  // Compute metric range
  let minVal=Infinity,maxVal=-Infinity;
  ncGeo.features.forEach(f => {
    const name = cleanName(f.properties?.name||"");
    const c = dataByName[name];
    if (!c) return;
    const v = getMetric(c, currentYear, currentMetric);
    if (v<minVal) minVal=v;
    if (v>maxVal) maxVal=v;
  });
  if (minVal===maxVal) maxVal=minVal+1;

  // Create extruded shapes
  ncGeo.features.forEach(f => {
    const name = cleanName(f.properties?.name||"");
    const c = dataByName[name];
    if (!c) return;
    const v = getMetric(c, currentYear, currentMetric);
    const t = (v-minVal)/(maxVal-minVal);
    const height = 0.1 + t*2.2; // extrusion depth
    
    const shapes = [];
    const addPoly = (coords) => {
      const shape = new THREE.Shape();
      coords.forEach(([lon,lat], i) => {
        const p = project(lon, lat);
        if (i===0) shape.moveTo(p.x, p.z);
        else shape.lineTo(p.x, p.z);
      });
      shapes.push(shape);
    };

    if (f.geometry.type === "Polygon") {
      addPoly(f.geometry.coordinates[0]);
    } else if (f.geometry.type === "MultiPolygon") {
      f.geometry.coordinates.forEach(poly => addPoly(poly[0]));
    }

    shapes.forEach(shape => {
      const extrudeSettings = { depth: height, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 2 };
      const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      geom.translate(0, 0, -height/2); // center on z
      geom.rotateX(-Math.PI/2); // lay flat on xz plane
      
      const color = getColor(v, minVal, maxVal);
      const mat = new THREE.MeshStandardMaterial({
        color, roughness:0.4, metalness:0.1,
        flatShading: false,
      });
      const mesh = new THREE.Mesh(geom, mat);
      mesh.position.y = height/2;
      mesh.castShadow = true; mesh.receiveShadow = true;
      mesh.userData = { name: f.properties?.name||name, value:v, metric:currentMetric };
      countyGroup.add(mesh);
      countyMeshes.push(mesh);
      extrudedMap.set(name, mesh);
    });
  });
  
  scene.add(countyGroup);
}

// ── Raycaster ──
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const tooltip = $("topo-tooltip");

container.addEventListener("mousemove", e => {
  if (isDrag) return;
  const rect = container.getBoundingClientRect();
  mouse.x = ((e.clientX-rect.left)/rect.width)*2-1;
  mouse.y = -((e.clientY-rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(countyMeshes);
  if (hits.length>0) {
    const d = hits[0].object.userData;
    tooltip.style.display="block";
    tooltip.style.left=(e.clientX-rect.left+15)+"px";
    tooltip.style.top=(e.clientY-rect.top-15)+"px";
    const fmt = currentMetric.includes("income")||currentMetric.includes("gdp")||currentMetric.includes("home")?"$"+d.value.toLocaleString():d.value.toLocaleString();
    tooltip.innerHTML=`<b>${d.name}</b><br>${currentMetric.replace(/_/g," ")}: ${fmt}`;
    container.style.cursor="pointer";
  } else { tooltip.style.display="none"; container.style.cursor=isDrag?"grabbing":"grab"; }
});

// ── Stats ──
function updateStats() {
  const vals = [];
  ncGeo.features.forEach(f => {
    const c = dataByName[cleanName(f.properties?.name||"")];
    if (c) vals.push({name:cleanName(f.properties?.name||""), val:getMetric(c,currentYear,currentMetric)});
  });
  vals.sort((a,b)=>b.val-a.val);
  const avg = vals.reduce((s,v)=>s+v.val,0)/vals.length;
  const maxV = vals[0]?.val||0, minV = vals[vals.length-1]?.val||0;
  const fmt = (v) => currentMetric.includes("income")||currentMetric.includes("gdp")||currentMetric.includes("home")?"$"+v.toLocaleString():v.toLocaleString();

  $("topo-stats").innerHTML = [
    `<div class="card" style="text-align:center;"><span class="metric-value accent">${ncData.meta.n_counties}</span><div class="metric-label">Counties</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#4269d0;">${fmt(avg)}</span><div class="metric-label">Average</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#059669;">${fmt(maxV)}</span><div class="metric-label">Maximum</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#dc3545;">${fmt(minV)}</span><div class="metric-label">Minimum</div></div>`,
  ].join("");

  $("topo-rank").innerHTML = vals.slice(0,5).map((d,i)=>`<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;"><span><b>${i+1}.</b> ${d.name}</span><span style="font-weight:700;color:#4269d0;">${fmt(d.val)}</span></div>`).join("");
  $("topo-rank-btm").innerHTML = vals.slice(-5).reverse().map((d,i)=>`<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;"><span><b>${vals.length-4+i}.</b> ${d.name}</span><span style="font-weight:700;color:#dc3545;">${fmt(d.val)}</span></div>`).join("");
}

// ── Build initial ──
rebuildCountyBlocks();
updateStats();

// ── Metric change ──
$("metric-select-t").onchange = () => {
  currentMetric = $("metric-select-t").value;
  rebuildCountyBlocks();
  updateStats();
};

// ── Playback ──
let playing=false,speed=1,timer=null;
function tick(){currentYear=(currentYear+1)%15;renderAll();if(playing)timer=setTimeout(tick,500/speed);}
function renderAll(){
  $("year-big-t").textContent=2010+currentYear;$("year-slider-t").value=currentYear;
  rebuildCountyBlocks();updateStats();
  $("btn-play-t").textContent=playing?"⏸ Pause":"▶ Play";
  $("btn-play-t").className=playing?"playing":"";
}
$("btn-play-t").onclick=()=>{playing=!playing;if(playing){if(currentYear>=14)currentYear=0;tick();}else clearTimeout(timer);renderAll();};
$("year-slider-t").oninput=()=>{currentYear=+$("year-slider-t").value;renderAll();};
$("speed-select-t").onchange=()=>{speed=+$("speed-select-t").value;};
document.addEventListener("keydown",e=>{if(e.code==="Space"&&document.activeElement===document.body){e.preventDefault();$("btn-play-t").click();}});

// ── Init ──
renderAll();

// ── Animate ──
(function animate(){
  requestAnimationFrame(animate);
  if(autoRot&&!isDrag)rotY+=.002;
  const r=camera.position.length();
  camera.position.x=r*Math.sin(rotY)*Math.cos(rotX);
  camera.position.y=r*Math.sin(rotX);
  camera.position.z=r*Math.cos(rotY)*Math.cos(rotX);
  camera.lookAt(0,0.6,0);
  renderer.render(scene,camera);
})();
```
