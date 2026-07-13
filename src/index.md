---
theme: dashboard
toc: false
---

<div class="page-hero">
  <h1>Convergence Engine</h1>
  <p>Advanced economic convergence modeling across 47 European regions · 1985–2023 · Three development eras</p>
</div>

```js
const data = await FileAttachment("./data/convergence.json").json();
```

<div class="grid grid-cols-4" style="margin-bottom: 1.5rem;">
  <div class="card" style="text-align: center;">
    <div class="metric-value accent">${data.meta.n_regions}</div>
    <div class="metric-label">Regions Tracked</div>
  </div>
  <div class="card" style="text-align: center;">
    <div class="metric-value gold">${data.meta.n_eras}</div>
    <div class="metric-label">Development Eras</div>
  </div>
  <div class="card" style="text-align: center;">
    <div class="metric-value" style="color: #72d2c0;">${data.metrics[2].d_coefficient.toFixed(3)}</div>
    <div class="metric-label">Latest D-Coefficient</div>
  </div>
  <div class="card" style="text-align: center;">
    <div class="metric-value warn">${(data.metrics[0].gini - data.metrics[2].gini).toFixed(3)}</div>
    <div class="metric-label">Gini Reduction (Δ)</div>
  </div>
</div>

<div class="grid grid-cols-2">
  <div class="card">
    <h3 style="margin-top: 0;">Convergence Trajectory</h3>
    <div id="trajectory-chart"></div>
  </div>
  <div class="card">
    <h3 style="margin-top: 0;">GDP Distribution by Era</h3>
    <div id="distribution-chart"></div>
  </div>
</div>

<div class="grid grid-cols-3" style="margin-top: 1.5rem;">
  ${data.metrics.map(m => `
  <div class="card">
    <h3 style="margin-top: 0; color: #72d2c0;">${m.era}</h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
      <div><div class="metric-label">D-Coefficient</div><div style="font-size: 1.3rem; font-weight: 700;">${m.d_coefficient.toFixed(3)}</div></div>
      <div><div class="metric-label">Sigma (σ)</div><div style="font-size: 1.3rem; font-weight: 700;">${m.sigma_convergence.toFixed(3)}</div></div>
      <div><div class="metric-label">Mean GDP</div><div style="font-size: 1.3rem; font-weight: 700;">$${(m.mean_gdp/1000).toFixed(1)}k</div></div>
      <div><div class="metric-label">CV</div><div style="font-size: 1.3rem; font-weight: 700;">${m.cv.toFixed(3)}</div></div>
      <div><div class="metric-label">Club Ratio</div><div style="font-size: 1.3rem; font-weight: 700;">${m.club_ratio.toFixed(3)}</div></div>
      <div><div class="metric-label">Gini</div><div style="font-size: 1.3rem; font-weight: 700;">${m.gini.toFixed(3)}</div></div>
    </div>
  </div>
  `).join("")}
</div>

<div style="text-align: center; margin-top: 2rem; color: var(--muted); font-size: 0.8rem;">
  H Heuristics · Convergence Engine v1.0 · Observable Pro · Built with Python & THREE.js
</div>

```js
import * as Plot from "npm:@observablehq/plot";

// Trajectory chart
const trajData = data.metrics;
const trajContainer = document.getElementById("trajectory-chart");
trajContainer.appendChild(
  Plot.plot({
    width: trajContainer.clientWidth,
    height: 250,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "Era", tickRotate: 0 },
    y: { grid: true },
    color: { legend: true, range: ["#ff6b6b", "#ffd93d", "#72d2c0"] },
    marks: [
      Plot.line(trajData, {x: "era", y: "d_coefficient", stroke: "#72d2c0", strokeWidth: 2.5}),
      Plot.dot(trajData, {x: "era", y: "d_coefficient", fill: "#72d2c0", r: 5}),
      Plot.line(trajData, {x: "era", y: "gini", stroke: "#ff6b6b", strokeWidth: 2}),
      Plot.dot(trajData, {x: "era", y: "gini", fill: "#ff6b6b", r: 4}),
      Plot.text(trajData, {x: "era", y: "d_coefficient", text: d => d.d_coefficient.toFixed(2), dy: -12, fill: "#72d2c0", fontSize: 11}),
      Plot.text(trajData, {x: "era", y: "gini", text: d => d.gini.toFixed(2), dy: 14, fill: "#ff6b6b", fontSize: 11}),
    ]
  })
);

// Distribution chart
const distContainer = document.getElementById("distribution-chart");
const distData = data.regions.flatMap(r => r.eras.map(e => ({region: r.name, era: e.era, gdp: e.gdp_per_capita / 1000})));
distContainer.appendChild(
  Plot.plot({
    width: distContainer.clientWidth,
    height: 250,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "GDP per capita (thousands)", grid: true },
    y: { label: "↑ Frequency" },
    color: { legend: true },
    marks: [
      Plot.rectY(distData, Plot.binX({y: "count"}, {x: "gdp", fill: "era", opacity: 0.6, thresholds: 20})),
      Plot.ruleY([0]),
    ]
  })
);
```
