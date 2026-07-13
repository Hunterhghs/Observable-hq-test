---
theme: dashboard
toc: false
---

<div class="page-hero">
  <h1>Geographic Convergence Map</h1>
  <p>Spatial distribution of GDP per capita and convergence clubs across Europe</p>
</div>

<div class="grid grid-cols-2" style="margin-bottom: 1rem;">
  <div class="card" style="text-align: center;">
    <div class="metric-label">Era Selector</div>
    <select id="era-select" style="background: #1a1a2e; color: #c8c8d4; border: 1px solid #2a2a4e; padding: 0.4rem 1rem; border-radius: 6px; font-size: 0.95rem; margin-top: 0.25rem;">
      <option value="0">Pre-Transition (1985-1995)</option>
      <option value="1">Transition (1995-2008)</option>
      <option value="2" selected>Integration (2008-2023)</option>
    </select>
  </div>
  <div class="card" style="text-align: center;">
    <div class="metric-label">Color Scale</div>
    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem; margin-top: 0.5rem;">
      <span style="color: #ff6b6b;">Low GDP</span>
      <div style="width: 120px; height: 12px; border-radius: 6px; background: linear-gradient(90deg, #ff6b6b, #ffd93d, #72d2c0, #4269d0);"></div>
      <span style="color: #4269d0;">High GDP</span>
    </div>
  </div>
</div>

<div class="card" style="padding: 0; overflow: hidden; background: #0a0a0f;">
  <div id="map-container" style="width: 100%; height: 520px;"></div>
</div>

```js
import * as L from "npm:leaflet";

const data = await FileAttachment("./data/convergence.json").json();

const container = document.getElementById("map-container");
const map = L.map(container).setView([50, 15], 4);

L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
  maxZoom: 10
}).addTo(map);

function getColor(gdp, maxGDP) {
  const t = gdp / maxGDP;
  if (t < 0.25) return "#ff6b6b";
  if (t < 0.5) return "#ff9f43";
  if (t < 0.75) return "#ffd93d";
  return "#72d2c0";
}

let markers = [];
let eraIdx = 2;

function renderEra(idx) {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  const eraGDPS = data.regions.map(r => r.eras[idx].gdp_per_capita);
  const maxGDP = Math.max(...eraGDPS);

  data.regions.forEach(r => {
    const e = r.eras[idx];
    const radius = Math.max(5, Math.sqrt(e.gdp_per_capita) * 0.25);
    const color = getColor(e.gdp_per_capita, maxGDP);

    const circle = L.circleMarker([r.lat, r.lon], {
      radius,
      fillColor: color,
      color: "#ffffff22",
      weight: 1,
      fillOpacity: 0.85,
    }).addTo(map);

    circle.bindTooltip(`<b>${r.name}</b><br>GDP/cap: $${e.gdp_per_capita.toLocaleString()}<br>Growth: ${(e.growth_rate*100).toFixed(1)}%<br>Club: ${r.club}`, {
      direction: "top",
      offset: [0, -radius],
      className: "map-tooltip",
    });

    markers.push(circle);
  });
}

renderEra(2);

document.getElementById("era-select").addEventListener("change", (e) => {
  eraIdx = parseInt(e.target.value);
  renderEra(eraIdx);
});

// Invalidate size after container is visible
setTimeout(() => map.invalidateSize(), 100);
```

<style>
.map-tooltip {
  background: #12121a !important;
  border: 1px solid #2a2a4e !important;
  border-radius: 6px !important;
  color: #c8c8d4 !important;
  font-family: 'Source Serif 4', serif !important;
  font-size: 0.85rem !important;
  padding: 0.4rem 0.7rem !important;
}
</style>
```
