---
theme: dashboard
toc: false
---

<div class="page-hero">
  <h1>Regression Diagnostics</h1>
  <p>Beta convergence · Sigma convergence · Club decomposition · Growth distributions — across three eras</p>
</div>

<div class="grid grid-cols-3" style="margin-bottom: 1.5rem;" id="metric-cards"></div>

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Beta Convergence</h3>
    <p class="muted">Growth rate vs initial GDP — negative slope = poorer regions grow faster</p>
    <div id="beta-chart"></div>
  </div>
  <div class="card">
    <h3>Sigma Convergence</h3>
    <p class="muted">Standard deviation of log GDP — decline = reduced inequality</p>
    <div id="sigma-chart"></div>
  </div>
</div>

<div class="grid grid-cols-2" style="margin-top: 1.5rem;">
  <div class="card">
    <h3>Club Variance Decomposition</h3>
    <p class="muted">Within-club vs total standard deviation — convergence within tiers</p>
    <div id="club-chart"></div>
  </div>
  <div class="card">
    <h3>Growth Rate Distribution</h3>
    <p class="muted">Distribution of growth rates by era — rightward shift with convergence</p>
    <div id="growth-chart"></div>
  </div>
</div>

```js
import * as Plot from "npm:@observablehq/plot";
const data = await FileAttachment("./data/convergence.json").json();
const $ = id => document.getElementById(id);

// ── Metric cards ──
const cardsDiv = $("metric-cards");
data.metrics.forEach(m => {
  const c = document.createElement("div");
  c.className = "card";
  c.style.textAlign = "center";
  c.innerHTML = `
    <div style="font-size:1.3rem;font-weight:700;color:#72d2c0;margin-bottom:0.5rem;">${m.era}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.3rem;">
      <div><div class="metric-label">β (×10⁶)</div><span style="font-weight:700;">${(m.beta_convergence * 1e6).toFixed(1)}</span></div>
      <div><div class="metric-label">σ</div><span style="font-weight:700;">${m.sigma_convergence.toFixed(3)}</span></div>
      <div><div class="metric-label">CV</div><span style="font-weight:700;">${m.cv.toFixed(3)}</span></div>
    </div>`;
  cardsDiv.appendChild(c);
});

// ── Beta Convergence ──
const betaData = data.regions.flatMap(r =>
  r.eras.map(e => ({ region: r.name, era: e.era, gdp: e.gdp_per_capita / 1000, growth: e.growth_rate * 100, club: r.club }))
);
$("beta-chart").appendChild(
  Plot.plot({
    width: $("beta-chart").clientWidth,
    height: 340,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 55,
    x: { label: "GDP per capita ($k)", grid: true },
    y: { label: "Growth rate (%)", grid: true },
    color: { legend: true, label: "Era" },
    marks: [
      Plot.dot(betaData, { x: "gdp", y: "growth", stroke: "era", fill: "era", fillOpacity: 0.5, r: 4 }),
      Plot.linearRegressionY(betaData, { x: "gdp", y: "growth", stroke: "era", strokeWidth: 2.5 }),
      Plot.ruleY([0], { stroke: "#ffffff22" }),
    ]
  })
);

// ── Sigma Convergence ──
$("sigma-chart").appendChild(
  Plot.plot({
    width: $("sigma-chart").clientWidth,
    height: 340,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 55,
    x: { label: null, padding: 0.4 },
    y: { label: "Sigma (σ log GDP)", grid: true },
    marks: [
      Plot.areaY(data.metrics, { x: "era", y1: d => data.metrics[0].sigma_convergence, y2: "sigma_convergence", fill: "#ff6b6b", fillOpacity: 0.1 }),
      Plot.line(data.metrics, { x: "era", y: "sigma_convergence", stroke: "#ff6b6b", strokeWidth: 3.5, curve: "catmull-rom" }),
      Plot.dot(data.metrics, { x: "era", y: "sigma_convergence", fill: "#ff6b6b", r: 8 }),
      Plot.text(data.metrics, { x: "era", y: "sigma_convergence", text: d => d.sigma_convergence.toFixed(3), dy: -20, fill: "#ff6b6b", fontSize: 16, fontWeight: "bold" }),
      Plot.ruleY([0]),
    ]
  })
);

// ── Club Variance ──
const clubDecompData = data.metrics.map(m => ({
  era: m.era,
  "Within-Club": Math.sqrt(m.within_club_variance) / 1000,
  "Between-Club": (Math.sqrt(m.total_variance) - Math.sqrt(m.within_club_variance)) / 1000,
}));
const clubFlat = clubDecompData.flatMap(d => [
  { era: d.era, component: "Between-Club", value: d["Between-Club"] },
  { era: d.era, component: "Within-Club", value: d["Within-Club"] },
]);
$("club-chart").appendChild(
  Plot.plot({
    width: $("club-chart").clientWidth,
    height: 340,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 55,
    x: { label: "Era", padding: 0.3 },
    y: { label: "Std Dev ($k)", grid: true },
    color: { legend: true, label: "Component", range: ["#ff6b6b", "#72d2c0"] },
    marks: [
      Plot.barY(clubFlat, { x: "era", y: "value", fill: "component" }),
      Plot.ruleY([0]),
    ]
  })
);

// ── Growth Distribution ──
const growthData = data.regions.flatMap(r =>
  r.eras.map(e => ({ era: e.era, growth: e.growth_rate * 100, region: r.name }))
);
$("growth-chart").appendChild(
  Plot.plot({
    width: $("growth-chart").clientWidth,
    height: 340,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 55,
    x: { label: "Growth rate (%)", grid: true },
    y: { label: "Density", ticks: [] },
    color: { legend: true, label: "Era" },
    marks: [
      Plot.density(growthData, { x: "growth", stroke: "era", strokeWidth: 2.5, fill: "era", fillOpacity: 0.1 }),
      Plot.ruleX([growthData.reduce((s, d) => s + d.growth, 0) / growthData.length], { stroke: "#ffffff44", strokeDasharray: "4,4" }),
    ]
  })
);
```
