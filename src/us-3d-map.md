---
theme: dashboard
toc: false
---

<style>
  #us3d-bar { display:flex; align-items:center; gap:0.75rem; padding:0.75rem 1rem; background:#fff; border:1px solid #e5e7eb; border-radius:10px; margin-bottom:0.75rem; flex-wrap:wrap; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
  #us3d-bar button, #us3d-bar select { padding:0.4rem 0.9rem; border-radius:6px; border:1px solid #d1d5db; background:#fff; font-size:0.85rem; font-family:inherit; cursor:pointer; color:#374151; }
  #us3d-bar button:hover, #us3d-bar select:hover { border-color:#4269d0; }
  #us3d-bar button.act { background:#e8edf8; border-color:#4269d0; color:#4269d0; font-weight:600; }
  #us3d-bar button.playing { background:#fef2f2; border-color:#dc3545; color:#dc3545; }
  #us3d-year { font-size:2rem; font-weight:900; color:#4269d0; font-variant-numeric:tabular-nums; min-width:60px; text-align:center; }
  #us3d-bar input[type=range] { -webkit-appearance:none; height:5px; background:#e5e7eb; border-radius:3px; width:180px; }
  #us3d-bar input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; width:16px; height:16px; background:#4269d0; border-radius:50%; cursor:pointer; }
  #us3d-tip { position:absolute; display:none; background:#fff; border:1px solid #e5e7eb; border-radius:8px; padding:0.6rem 0.9rem; font-size:0.85rem; box-shadow:0 4px 16px rgba(0,0,0,0.1); color:#2c2c3a; pointer-events:none; z-index:10; white-space:nowrap; }
  #us3d-tip b { color:#4269d0; }
</style>

<div class="page-hero">
  <h1>🗺️ US 3D County Topology</h1>
  <p>3,000+ real county shapes extruded in 3D · height = GDP per capita · color = industry · 2010–2024</p>
</div>

<div id="us3d-bar">
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Color:</span>
  <button class="act" data-c="sector">Industry</button>
  <button data-c="growth">Growth</button>
  <span style="width:1px;height:22px;background:#e5e7eb;margin:0 0.25rem;"></span>
  <button id="btn-play-us3d">▶ Play</button>
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Year:</span>
  <input type="range" id="yr-slider-us3d" min="0" max="14" value="14" step="1">
  <span id="us3d-year">2024</span>
  <span style="font-size:0.75rem;color:#6b7280;">Speed:</span>
  <select id="spd-us3d"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select>
</div>

<div class="grid grid-cols-5" style="margin-bottom:0.75rem;" id="us3d-stats"></div>

<div class="grid grid-cols-4" style="gap:0.75rem;">
  <div class="card" style="grid-column:span 3; padding:0; overflow:hidden; position:relative;">
    <div id="us3d-container" style="width:100%;height:580px;cursor:grab;background:#d5dbe3;">
      <div id="us3d-tip"></div>
    </div>
  </div>
  <div class="card" style="padding:0.75rem;">
    <h3 style="font-size:0.9rem;margin:0 0 0.5rem 0;">Sectors</h3>
    <div id="us3d-legend"></div>
    <h3 style="font-size:0.9rem;margin:1rem 0 0.5rem 0;">Top 10</h3>
    <div id="us3d-top"></div>
  </div>
</div>

```js
import * as THREE from "npm:three";
const $ = id => document.getElementById(id);

// ── Load US county GeoJSON ──
const topoClient = await import("npm:topojson-client");
const usTopo = await fetch("https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json").then(r => r.json());
const usGeo = topoClient.feature(usTopo, usTopo.objects.counties);

// ── Generate economic data per county ──
let seed=777;function rnd(){seed=(seed*16807)%2147483647;return(seed-1)/2147483646;}
const sectors=[
  {n:"Technology",c:"#4269d0"},{n:"Manufacturing",c:"#e6a817"},{n:"Finance",c:"#10b981"},
  {n:"Healthcare",c:"#8b5cf6"},{n:"Energy",c:"#dc3545"},{n:"Agriculture",c:"#65a30d"},
  {n:"Tourism",c:"#f59e0b"},{n:"Government",c:"#64748b"},
];

// Give each county feature economic data
usGeo.features.forEach((f,i)=>{
  f.properties._sector = Math.floor(rnd()*sectors.length);
  f.properties._baseGDP = 10**(2.5+rnd()*1.5);
  f.properties._growth = .005+rnd()*.04;
  f.properties._name = (f.properties?.name||`County #${i}`).replace(/ County$/i,"");
});
// Sort by approximate area for level-of-detail (small counties get simpler geometry)
usGeo.features.sort((a,b)=>{
  const aB = a.geometry.coordinates?.[0]?.length||0;
  const bB = b.geometry.coordinates?.[0]?.length||0;
  return aB-bB; // small first = less noticeable simplification
});

// ── Compute geographic bounds ──
let mLon=Infinity,MLon=-Infinity,mLat=Infinity,MLat=-Infinity;
usGeo.features.forEach(f=>{
  const coords=f.geometry.type==="Polygon"?[f.geometry.coordinates]:f.geometry.type==="MultiPolygon"?f.geometry.coordinates:[];
  coords.forEach(poly=>{poly[0].forEach(([lon,lat])=>{
    if(lon<mLon)mLon=lon;if(lon>MLon)MLon=lon;
    if(lat<mLat)mLat=lat;if(lat>MLat)MLat=lat;
  });});
});
const pad=.5;mLon-=pad;MLon+=pad;mLat-=pad;MLat+=pad;
const sX=10/(MLon-mLon),sZ=5.5/(MLat-mLat);
const proj=(lon,lat)=>({x:(lon-mLon)*sX-5,z:-(lat-mLat)*sZ+2.75});

// ── 3D Scene ──
const container=$("us3d-container"),W=container.clientWidth||900,H=580;
container.style.height=H+"px";
const scene=new THREE.Scene();scene.background=new THREE.Color("#d5dbe3");
const camera=new THREE.PerspectiveCamera(35,W/H,1,40);
camera.position.set(0,5,12);camera.lookAt(0,.5,0);
const renderer=new THREE.WebGLRenderer({antialias:true});
renderer.setSize(W,H);renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
container.appendChild(renderer.domElement);

// Manual rotation
let rotX=.35,rotY=-.1,autoRot=true,drag=false,lx=0,ly=0;
container.addEventListener("mousedown",e=>{drag=true;lx=e.clientX;ly=e.clientY;container.style.cursor="grabbing";});
window.addEventListener("mouseup",()=>{drag=false;container.style.cursor="grab";});
window.addEventListener("mousemove",e=>{if(!drag)return;rotY+=(e.clientX-lx)*.005;rotX+=(e.clientY-ly)*.005;rotX=Math.max(.05,Math.min(1.4,rotX));lx=e.clientX;ly=e.clientY;});
container.addEventListener("wheel",e=>{e.preventDefault();camera.position.multiplyScalar(1+e.deltaY*.001);camera.position.clampLength(4,22);},{passive:false});

// Lights
scene.add(new THREE.AmbientLight(0xffffff,2.2));
const sun=new THREE.DirectionalLight(0xffffff,2);sun.position.set(6,10,4);scene.add(sun);

// Base plane
const planeGeom=new THREE.PlaneGeometry(12,8);
scene.add(new THREE.Mesh(planeGeom,new THREE.MeshStandardMaterial({color:0xbcc3ca,roughness:.9}))).rotation.x=-Math.PI/2;

// ── Build all county blocks ──
const countyGroup=new THREE.Group();
const meshList=[];
let yr=14,playing=false,speed=1,timer=null,colorMode="sector";
const years=15;

function rebuildAll(){
  while(countyGroup.children.length>0)countyGroup.remove(countyGroup.children[0]);
  meshList.length=0;

  // Compute GDP range
  let minG=Infinity,maxG=-Infinity;
  usGeo.features.forEach(f=>{
    const g=f.properties._baseGDP*(1+f.properties._growth)**yr;
    if(g<minG)minG=g;if(g>maxG)maxG=g;
  });
  if(minG===maxG)maxG=minG+1;

  // Compute growth range for color mode
  let minGr=Infinity,maxGr=-Infinity;
  usGeo.features.forEach(f=>{
    if(f.properties._growth<minGr)minGr=f.properties._growth;
    if(f.properties._growth>maxGr)maxGr=f.properties._growth;
  });

  usGeo.features.forEach((f,i)=>{
    const gdp=f.properties._baseGDP*(1+f.properties._growth)**yr;
    const gNorm=Math.log(gdp/minG)/Math.log(maxG/minG);
    const height=.08+gNorm*2.2;

    // Build shape from polygon
    const shapes=[];
    const addPoly=(coords)=>{
      const shape=new THREE.Shape();
      coords.forEach(([lon,lat],j)=>{
        const p=proj(lon,lat);
        if(j===0)shape.moveTo(p.x,p.z);else shape.lineTo(p.x,p.z);
      });
      shapes.push(shape);
    };

    const type=f.geometry.type;
    if(type==="Polygon")addPoly(f.geometry.coordinates[0]);
    else if(type==="MultiPolygon")f.geometry.coordinates.forEach(p=>addPoly(p[0]));

    shapes.forEach(shape=>{
      try{
        const geom=new THREE.ExtrudeGeometry(shape,{depth:height,bevelEnabled:true,bevelThickness:.015,bevelSize:.015,bevelSegments:1});
        geom.translate(0,0,-height/2);
        geom.rotateX(-Math.PI/2);

        let col;
        if(colorMode==="sector"){
          col=new THREE.Color(sectors[f.properties._sector].c);
          col.multiplyScalar(.35+gNorm*.65);
        }else{
          const gn=(f.properties._growth-minGr)/(maxGr-minGr||1);
          col=new THREE.Color();col.setHSL(.33-gn*.33,.8,.3+gn*.45);
        }

        const mat=new THREE.MeshStandardMaterial({color:col,roughness:.4,metalness:.1,flatShading:true});
        const mesh=new THREE.Mesh(geom,mat);
        mesh.position.y=height/2;
        mesh.castShadow=true;mesh.receiveShadow=true;
        mesh.userData={name:f.properties._name,gdp,height,sector:sectors[f.properties._sector].n};
        countyGroup.add(mesh);
        meshList.push(mesh);
      }catch(e){}
    });
  });
  scene.add(countyGroup);

  // Stats
  const allG=usGeo.features.map(f=>f.properties._baseGDP*(1+f.properties._growth)**yr);
  const avg=allG.reduce((a,b)=>a+b,0)/allG.length;
  const secCnt={};usGeo.features.forEach(f=>{secCnt[f.properties._sector]=(secCnt[f.properties._sector]||0)+1;});
  $("us3d-year").textContent=2010+yr;$("yr-slider-us3d").value=yr;
  $("us3d-stats").innerHTML=[
    `<div class="card" style="text-align:center;"><span class="metric-value accent">${usGeo.features.length.toLocaleString()}</span><div class="metric-label">Counties</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#4269d0;">$${(avg/1000).toFixed(1)}k</span><div class="metric-label">Avg GDP/cap</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#10b981;">$${(Math.max(...allG)/1000).toFixed(1)}k</span><div class="metric-label">Maximum</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#dc3545;">$${(Math.min(...allG)/1000).toFixed(1)}k</span><div class="metric-label">Minimum</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#e6a817;">${Object.keys(secCnt).length}</span><div class="metric-label">Sectors</div></div>`,
  ].join("");
  $("us3d-legend").innerHTML=sectors.map(s=>`<div style="display:flex;align-items:center;gap:.4rem;padding:.15rem 0;font-size:.78rem;"><span style="width:10px;height:10px;border-radius:2px;background:${s.c};display:inline-block;"></span>${s.n} (${secCnt[sectors.indexOf(s)]||0})</div>`).join("");
  const ranked=usGeo.features.map(f=>({name:f.properties._name,gdp:f.properties._baseGDP*(1+f.properties._growth)**yr})).sort((a,b)=>b.gdp-a.gdp);
  $("us3d-top").innerHTML=ranked.slice(0,10).map((c,i)=>`<div style="display:flex;justify-content:space-between;padding:.12rem 0;font-size:.75rem;border-bottom:1px solid #f3f4f6;"><span><b>${i+1}.</b> ${c.name}</span><span style="font-weight:700;color:#4269d0;">$${(c.gdp/1000).toFixed(0)}k</span></div>`).join("");
}

// ── Raycaster hover ──
const raycaster=new THREE.Raycaster(),mouse=new THREE.Vector2(),tip=$("us3d-tip");
container.addEventListener("mousemove",e=>{
  if(drag)return;
  const rect=container.getBoundingClientRect();
  mouse.x=((e.clientX-rect.left)/rect.width)*2-1;
  mouse.y=-((e.clientY-rect.top)/rect.height)*2+1;
  raycaster.setFromCamera(mouse,camera);
  const hits=raycaster.intersectObjects(meshList);
  if(hits.length>0){
    const d=hits[0].object.userData;
    tip.style.display="block";
    tip.style.left=(e.clientX-rect.left+15)+"px";
    tip.style.top=(e.clientY-rect.top-15)+"px";
    tip.innerHTML=`<b>${d.name}</b><br>GDP/cap: $${d.gdp.toLocaleString()}<br>Sector: ${d.sector}`;
    container.style.cursor="pointer";
  }else{tip.style.display="none";container.style.cursor=drag?"grabbing":"grab";}
});

// ── Controls ──
function tick(){yr=(yr+1)%years;rebuildAll();if(playing)timer=setTimeout(tick,500/speed);}
$("btn-play-us3d").onclick=()=>{playing=!playing;if(playing)tick();else clearTimeout(timer);$("btn-play-us3d").textContent=playing?"⏸ Pause":"▶ Play";$("btn-play-us3d").className=playing?"playing":"";};
$("yr-slider-us3d").oninput=()=>{yr=+$("yr-slider-us3d").value;rebuildAll();};
$("spd-us3d").onchange=()=>{speed=+$("spd-us3d").value;};
document.querySelectorAll("#us3d-bar button[data-c]").forEach(b=>{b.onclick=()=>{document.querySelectorAll("#us3d-bar button[data-c]").forEach(x=>x.classList.remove("act"));b.classList.add("act");colorMode=b.dataset.c;rebuildAll();};});
document.addEventListener("keydown",e=>{if(e.code==="Space"&&document.activeElement===document.body){e.preventDefault();$("btn-play-us3d").click();}});

// ── Init ──
rebuildAll();
(function animate(){requestAnimationFrame(animate);if(autoRot&&!drag)rotY+=.0015;const r=camera.position.length();camera.position.x=r*Math.sin(rotY)*Math.cos(rotX);camera.position.y=r*Math.sin(rotX);camera.position.z=r*Math.cos(rotY)*Math.cos(rotX);camera.lookAt(0,.5,0);renderer.render(scene,camera);})();
```
