---
theme: dashboard
toc: false
---

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

<div class="page-hero">
  <h1>Geographic Convergence Map</h1>
  <p>Spatial distribution of GDP per capita — hover for details, use dropdown to switch eras</p>
</div>

<div class="card" style="padding: 0; overflow: hidden; background: #0a0a0f;">
  <div id="map-container" style="width: 100%; height: 540px;"></div>
</div>

<div class="grid grid-cols-4" style="margin-top: 1rem;" id="map-stats"></div>

```js
import * as L from "npm:leaflet";
const data = await FileAttachment("./data/convergence.json").json();
const $ = id => document.getElementById(id);

// ── Map ──
const map = L.map($("map-container"), {
  center: [50, 14],
  zoom: 4,
  zoomControl: true,
  attributionControl: false,
});

L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
  attribution: "© CARTO",
  maxZoom: 10,
}).addTo(map);

function getColor(gdp, min, max) {
  const t = (gdp - min) / (max - min);
  if (t < 0.2) return "#ff4444";
  if (t < 0.4) return "#ff8844";
  if (t < 0.6) return "#ffcc44";
  if (t < 0.8) return "#44cc88";
  return "#44aacc";
}

function getRadius(gdp, min, max) {
  const t = (gdp - min) / (max - min);
  return 6 + t * 18;
}

let markers = [];
let currentEra = 2;

function renderEra(idx) {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  const gdps = data.regions.map(r => r.eras[idx].gdp_per_capita);
  const minG = Math.min(...gdps);
  const maxG = Math.max(...gdps);

  data.regions.forEach(r => {
    const e = r.eras[idx];
    const color = getColor(e.gdp_per_capita, minG, maxG);
    const radius = getRadius(e.gdp_per_capita, minG, maxG);

    const circle = L.circleMarker([r.lat, r.lon], {
      radius, fillColor: color, color: "#ffffff18", weight: 1.5,
      fillOpacity: 0.88,
    }).addTo(map);

    circle.bindTooltip(
      `<div style="font-family:'Source Serif 4',serif;font-size:0.9rem;">
        <b style="font-size:1rem;">${r.name}</b><br>
        GDP/cap: <b>$${e.gdp_per_capita.toLocaleString()}</b><br>
        Growth: <b>${(e.growth_rate*100).toFixed(1)}%</b><br>
        Club: <b>${r.club}</b>
      </div>`,
      { direction: "top", offset: [0, -radius - 2], className: "map-tooltip" }
    );

    circle.on("mouseover", function() { this.setStyle({ weight: 3, color: "#fff" }); this.bringToFront(); });
    circle.on("mouseout", function() { this.setStyle({ weight: 1.5, color: "#ffffff18" }); });

    markers.push(circle);
  });
  updateStats(idx, minG, maxG);
}

function updateStats(idx, minG, maxG) {
  const m = data.metrics[idx];
  const statsRow = $("map-stats");
  statsRow.innerHTML = "";
  [
    [`<span class="metric-value accent">${m.era}</span><div class="metric-label">Current View</div>`, ""],
    [`<span class="metric-value gold">${m.mean_gdp.toLocaleString()}</span><div class="metric-label">Mean GDP/cap ($)</div>`, ""],
    [`<span class="metric-value" style="color:#72d2c0;">${m.d_coefficient.toFixed(3)}</span><div class="metric-label">D-Coefficient</div>`, ""],
    [`<span class="metric-value" style="color:#ff6b6b;">${m.gini.toFixed(3)}</span><div class="metric-label">Gini Coefficient</div>`, ""],
  ].forEach(([html]) => {
    const card = document.createElement("div");
    card.className = "card";
    card.style.textAlign = "center";
    card.innerHTML = html;
    statsRow.appendChild(card);
  });
}

renderEra(2);
setTimeout(() => map.invalidateSize(), 200);

// ── Era selector ──
const selDiv = document.createElement("div");
selDiv.style.cssText = "position:absolute;top:12px;right:12px;z-index:1000;";
selDiv.innerHTML = `<select id="era-select" style="background:#12121a;color:#c8c8d4;border:1px solid #2a2a4e;padding:0.5rem 1rem;border-radius:6px;font-size:0.95rem;font-family:'Source Serif 4',serif;cursor:pointer;">
  <option value="0">Pre-Transition (1985–1995)</option>
  <option value="1">Transition (1995–2008)</option>
  <option value="2" selected>Integration (2008–2023)</option>
</select>`;
$("map-container").style.position = "relative";
$("map-container").appendChild(selDiv);

$("era-select").addEventListener("change", e => {
  currentEra = parseInt(e.target.value);
  renderEra(currentEra);
});
```

<style>
.map-tooltip {
  background: #12121a !important;
  border: 1px solid #2a2a4e !important;
  border-radius: 8px !important;
  color: #c8c8d4 !important;
  font-family: 'Source Serif 4', serif !important;
  font-size: 0.85rem !important;
  padding: 0.5rem 0.8rem !important;
  box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
}
.leaflet-control-zoom a { background: #12121a !important; color: #c8c8d4 !important; border-color: #2a2a4e !important; }
</style>
```
