---
theme: dashboard
toc: false
---

<style>
  #usm-bar { display:flex; align-items:center; gap:0.75rem; padding:0.75rem 1rem; background:#fff; border:1px solid #e5e7eb; border-radius:10px; margin-bottom:0.75rem; flex-wrap:wrap; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
  #usm-bar button, #usm-bar select { padding:0.4rem 0.9rem; border-radius:6px; border:1px solid #d1d5db; background:#fff; font-size:0.85rem; font-family:inherit; cursor:pointer; color:#374151; }
  #usm-bar button:hover, #usm-bar select:hover { border-color:#4269d0; }
  #usm-bar button.act { background:#e8edf8; border-color:#4269d0; color:#4269d0; font-weight:600; }
  #usm-bar button.playing { background:#fef2f2; border-color:#dc3545; color:#dc3545; }
  #usm-year { font-size:2rem; font-weight:900; color:#4269d0; font-variant-numeric:tabular-nums; min-width:60px; text-align:center; }
  #usm-bar input[type=range] { -webkit-appearance:none; height:5px; background:#e5e7eb; border-radius:3px; width:180px; }
  #usm-bar input[type=range]::-webkit-slider-thumb { -webkit-appearance:none; width:16px; height:16px; background:#4269d0; border-radius:50%; cursor:pointer; }
  .usm-tooltip { background:#fff !important; border:1px solid #e5e7eb !important; border-radius:6px !important; color:#2c2c3a !important; font-family:'Source Serif 4',serif !important; padding:0.4rem 0.7rem !important; box-shadow:0 2px 8px rgba(0,0,0,0.1) !important; }
</style>

<div class="page-hero">
  <h1>🗺️ US County Economic Map</h1>
  <p>3,000+ counties · choropleth overlay · GDP per capita · color by industry or growth · 2010–2024</p>
</div>

<div id="usm-bar">
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Color:</span>
  <button class="act" data-c="sector">Industry</button>
  <button data-c="growth">Growth Rate</button>
  <button data-c="gdp">GDP/capita</button>
  <span style="width:1px;height:22px;background:#e5e7eb;margin:0 0.25rem;"></span>
  <button id="btn-play-usm">▶ Play</button>
  <span style="font-weight:700;color:#1a1a2e;font-size:0.85rem;">Year:</span>
  <input type="range" id="yr-slider-usm" min="0" max="14" value="14" step="1">
  <span id="usm-year">2024</span>
  <span style="font-size:0.75rem;color:#6b7280;">Speed:</span>
  <select id="spd-usm"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="2">2×</option></select>
</div>

<div class="grid grid-cols-5" style="margin-bottom:0.75rem;" id="usm-stats"></div>

<div class="grid grid-cols-4" style="gap:0.75rem;">
  <div class="card" style="grid-column:span 3; padding:0; overflow:hidden;">
    <div id="usm-map" style="width:100%;height:560px;"></div>
  </div>
  <div class="card" style="padding:0.75rem;">
    <h3 style="font-size:0.9rem;margin:0 0 0.5rem 0;">Legend</h3>
    <div id="usm-legend"></div>
    <h3 style="font-size:0.9rem;margin:1rem 0 0.5rem 0;">Top 10 Counties</h3>
    <div id="usm-top"></div>
  </div>
</div>

```js
import * as L from "npm:leaflet";
const $ = id => document.getElementById(id);

// ── Load GeoJSON ──
const topoClient = await import("npm:topojson-client");
const usTopo = await fetch("https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json").then(r => r.json());
const usGeo = topoClient.feature(usTopo, usTopo.objects.counties);

// ── Generate economic data ──
let seed=777;function rnd(){seed=(seed*16807)%2147483647;return(seed-1)/2147483646;}
const sectors=[
  {n:"Technology",c:"#4269d0"},{n:"Manufacturing",c:"#e6a817"},{n:"Finance",c:"#10b981"},
  {n:"Healthcare",c:"#8b5cf6"},{n:"Energy",c:"#dc3545"},{n:"Agriculture",c:"#65a30d"},
  {n:"Tourism",c:"#f59e0b"},{n:"Government",c:"#64748b"},
];
usGeo.features.forEach((f,i)=>{
  f.properties._sector=Math.floor(rnd()*sectors.length);
  f.properties._baseGDP=10**(2.5+rnd()*1.5);
  f.properties._growth=.005+rnd()*.04;
  f.properties._name=(f.properties?.name||`County #${i}`).replace(/ County$/i,"");
});

// ── Map ──
const map=L.map($("usm-map"),{zoomControl:true,attributionControl:false}).setView([39,-96],4);
L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",{attribution:"© CARTO",maxZoom:12}).addTo(map);

let geoLayer,yr=14,playing=false,speed=1,timer=null,colorMode="sector";
const years=15;

function getGDP(f){return f.properties._baseGDP*(1+f.properties._growth)**yr;}

function renderMap(){
  if(geoLayer)map.removeLayer(geoLayer);

  // Compute ranges
  let minG=Infinity,maxG=-Infinity,minGr=Infinity,maxGr=-Infinity;
  usGeo.features.forEach(f=>{
    const g=getGDP(f);if(g<minG)minG=g;if(g>maxG)maxG=g;
    if(f.properties._growth<minGr)minGr=f.properties._growth;
    if(f.properties._growth>maxGr)maxGr=f.properties._growth;
  });
  if(minG===maxG)maxG=minG+1;

  geoLayer=L.geoJSON(usGeo,{
    style:f=>{
      const gdp=getGDP(f);
      const gNorm=Math.log(gdp/minG)/Math.log(maxG/minG);
      let fill;
      if(colorMode==="sector"){
        fill=sectors[f.properties._sector].c;
      }else if(colorMode==="growth"){
        const gn=(f.properties._growth-minGr)/(maxGr-minGr||1);
        
        fill=`hsl(${Math.round(200-gn*200)},${Math.round(50+gn*30)}%,${Math.round(30+gn*30)}%)`;
      }else{
        fill=`hsl(${Math.round(220-gNorm*180)},${Math.round(40+gNorm*40)}%,${Math.round(25+gNorm*40)}%)`;
      }
      return {fillColor:fill,weight:.5,opacity:1,color:"#fff",fillOpacity:.85};
    },
    onEachFeature:(f,layer)=>{
      const gdp=getGDP(f);
      layer.bindTooltip(`<b>${f.properties._name}</b><br>GDP/cap: $${gdp.toLocaleString()}<br>Sector: ${sectors[f.properties._sector].n}<br>Growth: ${(f.properties._growth*100).toFixed(1)}%`,{sticky:true,className:"usm-tooltip",direction:"top"});
      layer.on({mouseover:e=>{e.target.setStyle({weight:2,color:"#4269d0"});e.target.bringToFront();},mouseout:e=>{geoLayer.resetStyle(e.target);}});
    },
  }).addTo(map);

  // Stats
  const allG=usGeo.features.map(f=>getGDP(f));
  const avg=allG.reduce((a,b)=>a+b,0)/allG.length;
  const secCnt={};usGeo.features.forEach(f=>{secCnt[f.properties._sector]=(secCnt[f.properties._sector]||0)+1;});
  $("usm-year").textContent=2010+yr;$("yr-slider-usm").value=yr;
  $("usm-stats").innerHTML=[
    `<div class="card" style="text-align:center;"><span class="metric-value accent">${usGeo.features.length.toLocaleString()}</span><div class="metric-label">Counties</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#4269d0;">$${(avg/1000).toFixed(1)}k</span><div class="metric-label">Avg GDP/cap</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#10b981;">$${(Math.max(...allG)/1000).toFixed(1)}k</span><div class="metric-label">Maximum</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#dc3545;">$${(Math.min(...allG)/1000).toFixed(1)}k</span><div class="metric-label">Minimum</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#e6a817;">${Object.keys(secCnt).length}</span><div class="metric-label">Sectors</div></div>`,
  ].join("");
  $("usm-legend").innerHTML=sectors.map(s=>`<div style="display:flex;align-items:center;gap:.4rem;padding:.15rem 0;font-size:.78rem;"><span style="width:10px;height:10px;border-radius:2px;background:${s.c};display:inline-block;"></span>${s.n}</div>`).join("");
  const ranked=usGeo.features.map(f=>({name:f.properties._name,gdp:getGDP(f)})).sort((a,b)=>b.gdp-a.gdp);
  $("usm-top").innerHTML=ranked.slice(0,10).map((c,i)=>`<div style="display:flex;justify-content:space-between;padding:.12rem 0;font-size:.75rem;border-bottom:1px solid #f3f4f6;"><span><b>${i+1}.</b> ${c.name}</span><span style="font-weight:700;color:#4269d0;">$${(c.gdp/1000).toFixed(0)}k</span></div>`).join("");
}

// ── Controls ──
function tick(){yr=(yr+1)%years;renderMap();if(playing)timer=setTimeout(tick,500/speed);}
$("btn-play-usm").onclick=()=>{playing=!playing;if(playing)tick();else clearTimeout(timer);$("btn-play-usm").textContent=playing?"⏸ Pause":"▶ Play";$("btn-play-usm").className=playing?"playing":"";};
$("yr-slider-usm").oninput=()=>{yr=+$("yr-slider-usm").value;renderMap();};
$("spd-usm").onchange=()=>{speed=+$("spd-usm").value;};
document.querySelectorAll("#usm-bar button[data-c]").forEach(b=>{b.onclick=()=>{document.querySelectorAll("#usm-bar button[data-c]").forEach(x=>x.classList.remove("act"));b.classList.add("act");colorMode=b.dataset.c;renderMap();};});
document.addEventListener("keydown",e=>{if(e.code==="Space"&&document.activeElement===document.body){e.preventDefault();$("btn-play-usm").click();}});

// ── Init ──
renderMap();
setTimeout(()=>map.invalidateSize(),200);
```
