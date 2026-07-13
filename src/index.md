---
theme: dashboard
toc: false
---

<div class="page-hero">
  <h1>Convergence Engine</h1>
  <p>Advanced economic convergence modeling · 47 European regions · 1985–2023 · Three development eras</p>
</div>

<div class="grid grid-cols-4" style="margin-bottom: 1.5rem;" id="kpi-row"></div>

<div class="grid grid-cols-3" style="margin-bottom: 1.5rem;" id="era-cards"></div>

<div class="grid grid-cols-2">
  <div class="card">
    <h3>Convergence Trajectory</h3>
    <p class="muted">D-Coefficient (convergence) vs Gini (inequality) across eras</p>
    <div id="trajectory-chart"></div>
  </div>
  <div class="card">
    <h3>GDP Distribution by Era</h3>
    <p class="muted">Kernel density of GDP per capita — rightward shift = growth with convergence</p>
    <div id="distribution-chart"></div>
  </div>
</div>

<div class="grid grid-cols-2" style="margin-top: 1.5rem;">
  <div class="card">
    <h3>Regional GDP Rankings</h3>
    <p class="muted">Top and bottom performers across eras</p>
    <div id="rankings-chart"></div>
  </div>
  <div class="card">
    <h3>Convergence Clubs</h3>
    <p class="muted">GDP trajectory by development club (0 = poorest, 3 = richest)</p>
    <div id="clubs-chart"></div>
  </div>
</div>

<div style="text-align: center; margin-top: 2.5rem; color: var(--muted); font-size: 0.8rem;">
  H Heuristics · Convergence Engine v2.0 · Observable Pro · Python + THREE.js + Plot
</div>

```js
import * as Plot from "npm:@observablehq/plot";
const data = await FileAttachment("./data/convergence.json").json();

// ── Helper ──
function $(id) { return document.getElementById(id); }
function card(html) { const d = document.createElement("div"); d.className = "card"; d.style.textAlign = "center"; d.innerHTML = html; return d; }

// ── KPI Row ──
const kpiRow = $("kpi-row");
const dFinal = data.metrics[2].d_coefficient;
const giniDrop = data.metrics[0].gini - data.metrics[2].gini;
const sigmaDrop = data.metrics[0].sigma_convergence - data.metrics[2].sigma_convergence;
const meanGrowth = (data.metrics[2].mean_gdp / data.metrics[0].mean_gdp - 1) * 100;
[
  [`<span class="metric-value accent">${data.meta.n_regions}</span><div class="metric-label">Regions Tracked</div>`, ""],
  [`<span class="metric-value gold">+${dFinal.toFixed(3)}</span><div class="metric-label">D-Coefficient (Final)</div>`, ""],
  [`<span class="metric-value" style="color:#72d2c0;">${giniDrop.toFixed(3)}</span><div class="metric-label">Gini Reduction (Δ)</div>`, ""],
  [`<span class="metric-value" style="color:#ff6b6b;">${sigmaDrop.toFixed(3)}</span><div class="metric-label">Sigma Reduction (Δ)</div>`, ""],
].forEach(([html]) => kpiRow.appendChild(card(html)));

// ── Era Cards ──
const eraRow = $("era-cards");
data.metrics.forEach(m => {
  const eraCard = document.createElement("div");
  eraCard.className = "card";
  eraCard.innerHTML = `
    <div style="font-size:1.4rem;font-weight:700;color:#72d2c0;margin-bottom:0.5rem;">${m.era}</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;">
      <div><div class="metric-label">D-Coeff</div><span style="font-weight:700;font-size:1.1rem;">${m.d_coefficient.toFixed(3)}</span></div>
      <div><div class="metric-label">Sigma σ</div><span style="font-weight:700;font-size:1.1rem;">${m.sigma_convergence.toFixed(3)}</span></div>
      <div><div class="metric-label">Mean GDP</div><span style="font-weight:700;font-size:1.1rem;">$${(m.mean_gdp/1000).toFixed(1)}k</span></div>
      <div><div class="metric-label">CV</div><span style="font-weight:700;font-size:1.1rem;">${m.cv.toFixed(3)}</span></div>
    </div>`;
  eraRow.appendChild(eraCard);
});

// ── Trajectory Chart ──
$("trajectory-chart").appendChild(
  Plot.plot({
    width: $("trajectory-chart").clientWidth,
    height: 300,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 50,
    x: { label: null, padding: 0.3 },
    y: { grid: true, label: null },
    color: { legend: true, legendX: 0.02, legendY: 0.98 },
    marks: [
      Plot.line(data.metrics, {x:"era",y:"d_coefficient",stroke:"#72d2c0",strokeWidth:3}),
      Plot.dot(data.metrics, {x:"era",y:"d_coefficient",fill:"#72d2c0",r:6}),
      Plot.text(data.metrics, {x:"era",y:"d_coefficient",text:d=>d.d_coefficient.toFixed(3),dy:-16,fill:"#72d2c0",fontSize:14,fontWeight:"bold"}),
      Plot.line(data.metrics, {x:"era",y:"gini",stroke:"#ff6b6b",strokeWidth:2.5}),
      Plot.dot(data.metrics, {x:"era",y:"gini",fill:"#ff6b6b",r:5}),
      Plot.text(data.metrics, {x:"era",y:"gini",text:d=>d.gini.toFixed(3),dy:16,fill:"#ff6b6b",fontSize:13}),
    ]
  })
);

// ── Distribution ──
const distData = data.regions.flatMap(r => r.eras.map(e => ({era:e.era,gdp:e.gdp_per_capita/1000})));
$("distribution-chart").appendChild(
  Plot.plot({
    width: $("distribution-chart").clientWidth,
    height: 300,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 50,
    x: { label: "GDP per capita (thousands $)", grid: true },
    y: { label: null, ticks: [] },
    color: { legend: true, label: "Era", legendX: 0.98, legendY: 0.98, legendAnchor: "top-right" },
    marks: [
      Plot.density(distData, {x:"gdp",stroke:"era",strokeWidth:2.5,fill:"era",fillOpacity:0.12}),
    ]
  })
);

// ── Rankings ──
const rankData = data.regions
  .map(r => ({name:r.name, era0:r.eras[0].gdp_per_capita/1000, era2:r.eras[2].gdp_per_capita/1000, change:(r.eras[2].gdp_per_capita/r.eras[0].gdp_per_capita-1)*100}))
  .sort((a,b) => b.change - a.change);
$("rankings-chart").appendChild(
  Plot.plot({
    width: $("rankings-chart").clientWidth,
    height: 350,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 120,
    marginRight: 40,
    x: { grid: true, label: "GDP per capita ($k)", transform: d => d*1000 },
    y: { label: null },
    marks: [
      Plot.barX(rankData, {x:"era0",y:"name",fill:"#ff6b6b",fillOpacity:0.5, sort:{y:"x"}}),
      Plot.barX(rankData, {x:"era2",y:"name",fill:"#72d2c0",fillOpacity:0.7, sort:{y:"x"}}),
      Plot.ruleX([0]),
    ]
  })
);

// ── Clubs ──
const clubNames = {0:"Club 0 (Poorest)",1:"Club 1",2:"Club 2",3:"Club 3 (Richest)"};
const clubData = data.regions.flatMap(r => {
  const avg = r.eras.reduce((s,e)=>s+e.gdp_per_capita,0)/3;
  return r.eras.map(e => ({club:clubNames[r.club],era:e.era,gdp:e.gdp_per_capita/1000,region:r.name}));
});
$("clubs-chart").appendChild(
  Plot.plot({
    width: $("clubs-chart").clientWidth,
    height: 350,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 50,
    x: { label: "Era", padding: 0.4 },
    y: { label: "GDP per capita ($k)", grid: true },
    color: { legend: true, label: "Club", scheme: "turbo" },
    marks: [
      Plot.line(clubData, Plot.groupZ({x:"era",y:"gdp",stroke:"club"}, {stroke:"club",strokeWidth:2.5})),
      Plot.dot(clubData, Plot.groupZ({x:"era",y:"gdp",fill:"club"}, {fill:"club",r:5})),
    ]
  })
);
```
