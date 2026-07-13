---
theme: dashboard
toc: false
---

<div class="page-hero">
  <h1>Regression Diagnostics</h1>
  <p>Beta convergence, sigma convergence, and club decomposition across three development eras</p>
</div>

```js
const data = await FileAttachment("./data/convergence.json").json();
```

<div class="grid grid-cols-3" style="margin-bottom: 1.5rem;">
  ${data.metrics.map(m => `
  <div class="card" style="text-align: center;">
    <div style="font-size: 1.8rem; font-weight: 800; color: #72d2c0;">${m.era}</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.3rem; margin-top: 0.8rem;">
      <div><div class="metric-label">β</div><div style="font-weight: 700;">${(m.beta_convergence * 1e6).toFixed(2)}</div></div>
      <div><div class="metric-label">σ</div><div style="font-weight: 700;">${m.sigma_convergence.toFixed(3)}</div></div>
      <div><div class="metric-label">CV</div><div style="font-weight: 700;">${m.cv.toFixed(3)}</div></div>
    </div>
  </div>
  `).join("")}
</div>

<div class="grid grid-cols-2">
  <div class="card">
    <h3 style="margin-top:0;">Beta Convergence: Growth vs Initial GDP</h3>
    <p style="color: var(--muted); font-size: 0.85rem;">Negative slope = convergence (poorer regions grow faster)</p>
    <div id="beta-chart"></div>
  </div>
  <div class="card">
    <h3 style="margin-top:0;">Sigma Convergence: Dispersion Over Time</h3>
    <p style="color: var(--muted); font-size: 0.85rem;">Declining σ = reduced inequality across regions</p>
    <div id="sigma-chart"></div>
  </div>
</div>

<div class="grid grid-cols-2" style="margin-top: 1.5rem;">
  <div class="card">
    <h3 style="margin-top:0;">Club Convergence: Within vs Total Variance</h3>
    <p style="color: var(--muted); font-size: 0.85rem;">Club ratio = within-club variance / total variance</p>
    <div id="club-chart"></div>
  </div>
  <div class="card">
    <h3 style="margin-top:0;">GDP Growth Distribution</h3>
    <p style="color: var(--muted); font-size: 0.85rem;">Distribution of growth rates by era — rightward shift = convergence</p>
    <div id="growth-dist-chart"></div>
  </div>
</div>

```js
import * as Plot from "npm:@observablehq/plot";

// Beta convergence: each era, growth vs initial GDP
const betaData = [];
data.regions.forEach(r => {
  // Era 0: initial GDP is era 0 GDP, growth is era 0 growth
  betaData.push({region: r.name, era: r.eras[0].era, initial_gdp: r.eras[0].gdp_per_capita / 1000, growth: r.eras[0].growth_rate * 100, club: r.club});
  betaData.push({region: r.name, era: r.eras[1].era, initial_gdp: r.eras[1].gdp_per_capita / 1000, growth: r.eras[1].growth_rate * 100, club: r.club});
  betaData.push({region: r.name, era: r.eras[2].era, initial_gdp: r.eras[2].gdp_per_capita / 1000, growth: r.eras[2].growth_rate * 100, club: r.club});
});

const betaContainer = document.getElementById("beta-chart");
betaContainer.appendChild(
  Plot.plot({
    width: betaContainer.clientWidth,
    height: 320,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "GDP per capita (thousands $)", grid: true },
    y: { label: "↑ Growth rate (%)", grid: true },
    color: { legend: true, label: "Era" },
    marks: [
      Plot.dot(betaData, {x: "initial_gdp", y: "growth", stroke: "era", fill: "era", opacity: 0.7}),
      Plot.linearRegressionY(betaData, {x: "initial_gdp", y: "growth", stroke: "era", strokeWidth: 2}),
    ]
  })
);

// Sigma convergence
const sigmaContainer = document.getElementById("sigma-chart");
sigmaContainer.appendChild(
  Plot.plot({
    width: sigmaContainer.clientWidth,
    height: 320,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "Era" },
    y: { label: "↑ Sigma (σ)", grid: true },
    marks: [
      Plot.line(data.metrics, {x: "era", y: "sigma_convergence", stroke: "#ff6b6b", strokeWidth: 3}),
      Plot.dot(data.metrics, {x: "era", y: "sigma_convergence", fill: "#ff6b6b", r: 6}),
      Plot.text(data.metrics, {x: "era", y: "sigma_convergence", text: d => d.sigma_convergence.toFixed(3), dy: -15, fill: "#ff6b6b", fontSize: 13, fontWeight: "bold"}),
      Plot.ruleY([0]),
    ]
  })
);

// Club convergence
const clubContainer = document.getElementById("club-chart");
const clubData = data.metrics.map(m => ({
  era: m.era,
  "Within-Club σ²": Math.sqrt(m.within_club_variance) / 1000,
  "Total σ²": Math.sqrt(m.total_variance) / 1000,
}));
clubContainer.appendChild(
  Plot.plot({
    width: clubContainer.clientWidth,
    height: 320,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "Era" },
    y: { label: "↑ Standard Deviation (thousands $)", grid: true },
    color: { legend: true, label: "Component" },
    marks: [
      Plot.line(clubData, {x: "era", y: "Total σ²", stroke: "#ff6b6b", strokeWidth: 2.5}),
      Plot.dot(clubData, {x: "era", y: "Total σ²", fill: "#ff6b6b", r: 5}),
      Plot.line(clubData, {x: "era", y: "Within-Club σ²", stroke: "#72d2c0", strokeWidth: 2.5}),
      Plot.dot(clubData, {x: "era", y: "Within-Club σ²", fill: "#72d2c0", r: 5}),
      Plot.ruleY([0]),
    ]
  })
);

// Growth distribution by era
const growthDistContainer = document.getElementById("growth-dist-chart");
const growthData = data.regions.flatMap(r => r.eras.map(e => ({era: e.era, growth: e.growth_rate * 100})));
growthDistContainer.appendChild(
  Plot.plot({
    width: growthDistContainer.clientWidth,
    height: 320,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "↑ Growth rate (%)", grid: true },
    y: { label: "Density" },
    color: { legend: true, label: "Era" },
    marks: [
      Plot.density(growthData, {x: "growth", stroke: "era", strokeWidth: 2.5, fill: "era", fillOpacity: 0.15}),
    ]
  })
);
```
