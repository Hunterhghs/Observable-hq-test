---
theme: dashboard
toc: false
---

<style>
  #nc-controls { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; margin-bottom: 0.75rem; flex-wrap: wrap; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
  #nc-controls select, #nc-controls button { padding: 0.4rem 0.9rem; border-radius: 6px; border: 1px solid #d1d5db; background: #fff; font-size: 0.85rem; font-family: inherit; cursor: pointer; color: #374151; }
  #nc-controls button:hover, #nc-controls select:hover { border-color: #4269d0; }
  #nc-controls button.layer-active { background: #e8edf8; border-color: #4269d0; color: #4269d0; font-weight: 600; }
  #nc-controls input[type=range] { -webkit-appearance: none; height: 5px; background: #e5e7eb; border-radius: 3px; width: 160px; }
  #nc-controls input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 16px; height: 16px; background: #4269d0; border-radius: 50%; cursor: pointer; }
  #year-badge { font-size: 1.4rem; font-weight: 800; color: #4269d0; min-width: 50px; text-align: center; }
  .info-panel { background:#fff; padding:0.8rem 1rem; border-radius:8px; border:1px solid #e5e7eb; font-size:0.85rem; }
  .info-panel b { color: #4269d0; }
  .legend-bar { display:flex; align-items:center; gap:0.3rem; font-size:0.75rem; color:#6b7280; }
  .legend-gradient { width:140px; height:10px; border-radius:5px; }
</style>

<div class="page-hero">
  <h1>🗺️ North Carolina Multi-Layered Atlas</h1>
  <p>100 counties · Economy · Demographics · Housing · 2010–2024 · Toggle layers, scrub time</p>
</div>

<div id="nc-controls">
  <span style="font-weight:700;color:#1a1a2e;font-size:0.9rem;">Layer:</span>
  <button class="layer-active" data-layer="economy" id="btn-economy">💰 Economy</button>
  <button data-layer="demographics" id="btn-demographics">👥 Demographics</button>
  <button data-layer="housing" id="btn-housing">🏠 Housing</button>
  <span style="width:1px;height:24px;background:#e5e7eb;margin:0 0.25rem;"></span>
  <span style="font-weight:700;color:#1a1a2e;font-size:0.9rem;">Metric:</span>
  <select id="metric-select"></select>
  <span style="width:1px;height:24px;background:#e5e7eb;margin:0 0.25rem;"></span>
  <span style="font-weight:700;color:#1a1a2e;font-size:0.9rem;">Year:</span>
  <button id="btn-prev">◀</button>
  <input type="range" id="year-slider" min="0" max="14" value="14" step="1">
  <span id="year-badge">2024</span>
  <button id="btn-next">▶</button>
  <button id="btn-play" style="font-size:0.8rem;">▶ Play</button>
</div>

<div class="grid grid-cols-3" style="gap:0.75rem; margin-bottom:0.75rem;" id="top-stats"></div>

<div class="grid grid-cols-4" style="gap:0.75rem;">
  <div class="card" style="grid-column:span 3; padding:0; overflow:hidden;">
    <div id="nc-map" style="width:100%;height:520px;"></div>
  </div>
  <div class="card" style="padding:0.75rem;">
    <h3 style="font-size:0.95rem;margin:0 0 0.5rem 0;">Top 5 Counties</h3>
    <div id="top-counties"></div>
    <h3 style="font-size:0.95rem;margin:1rem 0 0.5rem 0;">Bottom 5</h3>
    <div id="bottom-counties"></div>
  </div>
</div>

```js
import * as Plot from "npm:@observablehq/plot";
import * as L from "npm:leaflet";
import * as topojson from "npm:topojson-client";
const ncData = await FileAttachment("./data/nc-counties.json").json();
const $ = id => document.getElementById(id);

// ── Load US county TopoJSON → filter NC ──
const usTopo = await fetch("https://cdn.jsdelivr.net/npm/us-atlas@3/counties-10m.json").then(r => r.json());
const ncGeo = topojson.feature(usTopo, usTopo.objects.counties);
ncGeo.features = ncGeo.features.filter(f => f.id && String(f.id).startsWith("37"));

// ── Build county FIPS lookup ──
const fipsMap = {};
ncGeo.features.forEach(f => {
  const fips = String(f.id).slice(2); // strip "37"
  fipsMap[fips] = f;
});
// Map county names to FIPS (approximate)
const nameToFips = {};
ncData.counties.forEach(c => {
  // Find closest FIPS by matching county name to GeoJSON properties
  for (const [fips, feat] of Object.entries(fipsMap)) {
    if (feat.properties && feat.properties.name && feat.properties.name.toLowerCase() === c.name.toLowerCase()) {
      nameToFips[c.name] = fips;
      break;
    }
  }
});

// ── State ──
let currentLayer = "economy";
let currentMetric = "gdp_per_capita";
let currentYear = 14; // 2024
let playing = false;
let playTimer = null;
const nYears = ncData.years.length;

const metricInfo = {};
Object.entries(ncData.layers).forEach(([lk, lv]) => {
  lv.metrics.forEach(m => { metricInfo[m.key] = { ...m, layer: lk, layerName: lv.name }; });
});

// ── Map ──
const map = L.map($("nc-map"), { zoomControl: true, attributionControl: false }).setView([35.5, -79.5], 7);
L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
  attribution: "© CARTO", maxZoom: 12,
}).addTo(map);

let geoLayer;

function getCountyData(geoName, yearIdx) {
  // GeoJSON names are "Alamance County" — strip suffix
  const clean = geoName.replace(/ County$/i, "").toLowerCase();
  const c = ncData.counties.find(c => c.name.toLowerCase() === clean);
  if (!c) return null;
  return c.years[yearIdx];
}

function getColor(value, min, max, invert) {
  if (max === min) return "#4269d0";
  const t = invert ? 1 - (value - min) / (max - min) : (value - min) / (max - min);
  const clamped = Math.max(0, Math.min(1, t));
  // Blue gradient
  const r = Math.round(30 + (1 - clamped) * 195);
  const g = Math.round(60 + (1 - clamped) * 155);
  const b = Math.round(120 + clamped * 110);
  return `rgb(${r},${g},${b})`;
}

function formatValue(val, fmt) {
  if (fmt === "currency") return "$" + val.toLocaleString();
  if (fmt === "percent") return (val * 100).toFixed(1) + "%";
  if (fmt === "percent1") return val.toFixed(1) + "%";
  return val.toLocaleString();
}

function renderMap() {
  if (geoLayer) map.removeLayer(geoLayer);
  
  const mi = metricInfo[currentMetric];
  const values = [];
  
  ncGeo.features.forEach(f => {
    const name = f.properties?.name;
    const cd = getCountyData(name, currentYear);
    if (cd && cd[currentMetric] !== undefined) {
      f.properties._value = cd[currentMetric];
      values.push(cd[currentMetric]);
    } else {
      f.properties._value = null;
    }
  });
  
  const validVals = values.filter(v => v !== null);
  const minV = Math.min(...validVals);
  const maxV = Math.max(...validVals);
  const invert = mi.invert || false;
  
  geoLayer = L.geoJSON(ncGeo, {
    style: f => ({
      fillColor: f.properties._value != null ? getColor(f.properties._value, minV, maxV, invert) : "#e5e7eb",
      weight: 1,
      opacity: 1,
      color: "#fff",
      fillOpacity: 0.85,
    }),
    onEachFeature: (f, layer) => {
      const name = f.properties?.name || "";
      const cd = getCountyData(name, currentYear);
      if (cd) {
        layer.bindTooltip(
          `<div style="font-size:0.85rem;line-height:1.5;">
            <b style="font-size:0.95rem;">${cd.name || name}</b><br>
            ${mi.label}: <b>${formatValue(cd[currentMetric], mi.format)}</b><br>
            Population: ${cd.population.toLocaleString()}<br>
            Median Income: $${cd.median_income.toLocaleString()}
          </div>`,
          { sticky: true, className: "nc-tooltip", direction: "top" }
        );
      }
      layer.on({ mouseover: e => { e.target.setStyle({ weight: 2, color: "#4269d0" }); e.target.bringToFront(); },
                  mouseout: e => { geoLayer.resetStyle(e.target); } });
    },
  }).addTo(map);
  
  // Update legend
  updateLegend(minV, maxV, mi);
  updateRankings();
}

// ── Legend ──
function updateLegend(minV, maxV, mi) {
  const existing = document.querySelector(".map-legend");
  if (existing) existing.remove();
  const legend = L.control({ position: "bottomright" });
  legend.onAdd = () => {
    const div = L.DomUtil.create("div", "map-legend info-panel");
    div.innerHTML = `
      <div style="font-weight:700;margin-bottom:0.3rem;">${mi.label}</div>
      <div class="legend-bar">
        <span>${formatValue(minV, mi.format)}</span>
        <div class="legend-gradient" style="background:linear-gradient(90deg,rgb(225,215,215),rgb(30,60,230));"></div>
        <span>${formatValue(maxV, mi.format)}</span>
      </div>`;
    return div;
  };
  legend.addTo(map);
}

// ── Rankings ──
function updateRankings() {
  const mi = metricInfo[currentMetric];
  const data = ncData.counties.map(c => {
    const y = c.years[currentYear];
    return { name: c.name, value: y[currentMetric], region: c.region };
  }).filter(d => d.value != null);
  
  const sorted = [...data].sort((a, b) => mi.invert ? a.value - b.value : b.value - a.value);
  
  $("top-counties").innerHTML = sorted.slice(0, 5).map((d, i) =>
    `<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;">
      <span><b>${i+1}.</b> ${d.name}</span>
      <span style="font-weight:700;color:#4269d0;">${formatValue(d.value, mi.format)}</span>
    </div>`
  ).join("");
  
  $("bottom-counties").innerHTML = sorted.slice(-5).reverse().map((d, i) =>
    `<div style="display:flex;justify-content:space-between;padding:0.2rem 0;font-size:0.8rem;border-bottom:1px solid #f3f4f6;">
      <span><b>${sorted.length-4+i}.</b> ${d.name}</span>
      <span style="font-weight:700;color:#dc3545;">${formatValue(d.value, mi.format)}</span>
    </div>`
  ).join("");
}

// ── Update metric dropdown ──
function updateMetricSelect() {
  const sel = $("metric-select");
  const metrics = ncData.layers[currentLayer].metrics;
  sel.innerHTML = metrics.map(m => `<option value="${m.key}" ${m.key===currentMetric?'selected':''}>${m.label}</option>`).join("");
  currentMetric = sel.value;
}

// ── Top stats ──
function updateStats() {
  const vals = ncData.counties.map(c => c.years[currentYear][currentMetric]).filter(v => v != null);
  const total = vals.reduce((s, v) => s + v, 0);
  const avg = total / vals.length;
  const mi = metricInfo[currentMetric];
  $("top-stats").innerHTML = [
    `<div class="card" style="text-align:center;"><span class="metric-value accent">${ncData.meta.n_counties}</span><div class="metric-label">Counties</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#4269d0;">${formatValue(avg, mi.format)}</span><div class="metric-label">Average ${mi.label}</div></div>`,
    `<div class="card" style="text-align:center;"><span class="metric-value" style="color:#059669;">${formatValue(Math.max(...vals), mi.format)}</span><div class="metric-label">Maximum</div></div>`,
  ].join("");
}

// ── Layer buttons ──
document.querySelectorAll("#nc-controls button[data-layer]").forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll("#nc-controls button[data-layer]").forEach(b => b.classList.remove("layer-active"));
    btn.classList.add("layer-active");
    currentLayer = btn.dataset.layer;
    updateMetricSelect();
    renderAll();
  };
});

$("metric-select").onchange = () => { currentMetric = $("metric-select").value; renderAll(); };

// ── Year controls ──
$("year-slider").oninput = () => { currentYear = parseInt($("year-slider").value); renderAll(); };
$("btn-prev").onclick = () => { currentYear = Math.max(0, currentYear - 1); $("year-slider").value = currentYear; renderAll(); };
$("btn-next").onclick = () => { currentYear = Math.min(14, currentYear + 1); $("year-slider").value = currentYear; renderAll(); };
$("btn-play").onclick = () => {
  playing = !playing;
  $("btn-play").textContent = playing ? "⏸ Pause" : "▶ Play";
  $("btn-play").style.background = playing ? "#fef2f2" : "";
  if (playing) playTick();
  else clearTimeout(playTimer);
};
function playTick() {
  if (!playing) return;
  currentYear = (currentYear + 1) % nYears;
  $("year-slider").value = currentYear;
  renderAll();
  playTimer = setTimeout(playTick, 600);
}

// ── Render all ──
function renderAll() {
  $("year-badge").textContent = ncData.years[currentYear];
  updateStats();
  renderMap();
}

// ── Init ──
updateMetricSelect();
renderAll();
setTimeout(() => map.invalidateSize(), 200);
```

<style>
.nc-tooltip { background:#fff !important; border:1px solid #e5e7eb !important; border-radius:6px !important; color:#2c2c3a !important; font-family:'Source Serif 4',serif !important; padding:0.4rem 0.7rem !important; box-shadow:0 2px 8px rgba(0,0,0,0.1) !important; }
.leaflet-control-zoom a { background:#fff !important; color:#374151 !important; border-color:#e5e7eb !important; }
</style>
```
