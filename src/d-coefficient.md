---
theme: dashboard
toc: false
---

<div class="page-hero">
  <h1>D-Coefficient Explorer</h1>
  <p>Distributional convergence metric — tracks how the shape of the GDP distribution evolves across eras</p>
</div>

```js
const data = await FileAttachment("./data/convergence.json").json();
```

<div class="grid grid-cols-3" style="margin-bottom: 1.5rem;">
  <div class="card" style="text-align: center;">
    <div class="metric-label">D-Coefficient Range</div>
    <div style="font-size: 1.5rem; font-weight: 700; margin-top: 0.3rem;">
      <span style="color: #ff6b6b;">${data.metrics[0].d_coefficient.toFixed(3)}</span>
      <span style="color: var(--muted); margin: 0 0.5rem;">→</span>
      <span style="color: #72d2c0;">${data.metrics[2].d_coefficient.toFixed(3)}</span>
    </div>
  </div>
  <div class="card" style="text-align: center;">
    <div class="metric-label">Total ΔD</div>
    <div class="metric-value gold" style="margin-top: 0.3rem;">+${(data.metrics[2].d_coefficient - data.metrics[0].d_coefficient).toFixed(3)}</div>
  </div>
  <div class="card" style="text-align: center;">
    <div class="metric-label">Convergence Status</div>
    <div style="font-size: 1.3rem; font-weight: 700; color: #72d2c0; margin-top: 0.3rem;">✓ Converging</div>
  </div>
</div>

<div class="grid grid-cols-2">
  <div class="card">
    <h3 style="margin-top:0;">D-Coefficient Trajectory</h3>
    <p style="color: var(--muted); font-size: 0.85rem;">D → 1.0 indicates perfect convergence. Rising D = reducing inequality.</p>
    <div id="d-coeff-chart"></div>
  </div>
  <div class="card">
    <h3 style="margin-top:0;">Gini Coefficient by Era</h3>
    <p style="color: var(--muted); font-size: 0.85rem;">Declining Gini = more equal distribution. Paired with D for full picture.</p>
    <div id="gini-chart"></div>
  </div>
</div>

<div class="grid grid-cols-2" style="margin-top: 1.5rem;">
  <div class="card">
    <h3 style="margin-top:0;">Lorenz Curves</h3>
    <p style="color: var(--muted); font-size: 0.85rem;">Cumulative GDP share vs cumulative population share. Closer to diagonal = more equal.</p>
    <div id="lorenz-chart"></div>
  </div>
  <div class="card">
    <h3 style="margin-top:0;">Decomposition: Between vs Within Clubs</h3>
    <p style="color: var(--muted); font-size: 0.85rem;">How much inequality comes from differences between clubs vs within them.</p>
    <div id="decomp-chart"></div>
  </div>
</div>

<div class="card" style="margin-top: 1.5rem;">
  <h3 style="margin-top:0;">Key Insight</h3>
  <p style="color: #c8c8d4; line-height: 1.7;">
    The D-Coefficient rises from <strong style="color: #ff6b6b;">${data.metrics[0].d_coefficient.toFixed(3)}</strong> 
    (Pre-Transition) to <strong style="color: #72d2c0;">${data.metrics[2].d_coefficient.toFixed(3)}</strong> 
    (Integration), confirming <strong style="color: #72d2c0;">strong convergence</strong> across European regions. 
    The Gini coefficient drops from <strong style="color: #ffd93d;">${data.metrics[0].gini.toFixed(3)}</strong> to 
    <strong style="color: #72d2c0;">${data.metrics[2].gini.toFixed(3)}</strong>, a 
    <strong style="color: #ff6b6b;">${((1 - data.metrics[2].gini / data.metrics[0].gini) * 100).toFixed(1)}%</strong> reduction in inequality.
    The club decomposition shows that <strong>within-club convergence</strong> dominates, suggesting that 
    regions within the same development tier are catching up to each other, while structural differences 
    between clubs persist.
  </p>
</div>

```js
import * as Plot from "npm:@observablehq/plot";

// D-Coefficient trajectory
const dContainer = document.getElementById("d-coeff-chart");
dContainer.appendChild(
  Plot.plot({
    width: dContainer.clientWidth,
    height: 300,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "Era" },
    y: { label: "↑ D-Coefficient", domain: [0.5, 0.85], grid: true },
    marks: [
      Plot.areaY(data.metrics, {x: "era", y1: 0.5, y2: "d_coefficient", fill: "#72d2c0", fillOpacity: 0.15}),
      Plot.line(data.metrics, {x: "era", y: "d_coefficient", stroke: "#72d2c0", strokeWidth: 3}),
      Plot.dot(data.metrics, {x: "era", y: "d_coefficient", fill: "#72d2c0", r: 7}),
      Plot.text(data.metrics, {x: "era", y: "d_coefficient", text: d => d.d_coefficient.toFixed(3), dy: -18, fill: "#72d2c0", fontSize: 15, fontWeight: "bold"}),
      Plot.ruleY([1], {stroke: "#72d2c0", strokeOpacity: 0.3, strokeDasharray: "4,4"}),
      Plot.text([1], {x: "Integration", y: 1.005, text: "Perfect Convergence", fill: "#72d2c0", fontSize: 10, textAnchor: "end"}),
    ]
  })
);

// Gini chart
const giniContainer = document.getElementById("gini-chart");
giniContainer.appendChild(
  Plot.plot({
    width: giniContainer.clientWidth,
    height: 300,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "Era" },
    y: { label: "↑ Gini Coefficient", domain: [0.15, 0.45], grid: true },
    marks: [
      Plot.areaY(data.metrics, {x: "era", y1: 0.45, y2: "gini", fill: "#ff6b6b", fillOpacity: 0.15}),
      Plot.line(data.metrics, {x: "era", y: "gini", stroke: "#ff6b6b", strokeWidth: 3}),
      Plot.dot(data.metrics, {x: "era", y: "gini", fill: "#ff6b6b", r: 7}),
      Plot.text(data.metrics, {x: "era", y: "gini", text: d => d.gini.toFixed(3), dy: -18, fill: "#ff6b6b", fontSize: 15, fontWeight: "bold"}),
      Plot.ruleY([0], {stroke: "#ff6b6b", strokeOpacity: 0.3, strokeDasharray: "4,4"}),
      Plot.text([0], {x: "Integration", y: 0.005, text: "Perfect Equality", fill: "#ff6b6b", fontSize: 10, textAnchor: "end"}),
    ]
  })
);

// Lorenz curves
const lorenzContainer = document.getElementById("lorenz-chart");
const lorenzData = [];
data.metrics.forEach((m, eraIdx) => {
  const gdps = data.regions.map(r => r.eras[eraIdx].gdp_per_capita).sort((a, b) => a - b);
  const total = gdps.reduce((s, v) => s + v, 0);
  let cumPop = 0, cumGDP = 0;
  gdps.forEach((g, i) => {
    cumPop = (i + 1) / gdps.length;
    cumGDP += g / total;
    lorenzData.push({era: m.era, cumPop, cumGDP});
  });
});
lorenzContainer.appendChild(
  Plot.plot({
    width: lorenzContainer.clientWidth,
    height: 300,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "Cumulative population share →", domain: [0, 1] },
    y: { label: "↑ Cumulative GDP share", domain: [0, 1] },
    color: { legend: true, label: "Era" },
    marks: [
      Plot.line([0, 1], [0, 1], {stroke: "#ffffff22", strokeWidth: 1, strokeDasharray: "4,4"}),
      Plot.line(lorenzData, {x: "cumPop", y: "cumGDP", stroke: "era", strokeWidth: 2.5}),
    ]
  })
);

// Decomposition
const decompContainer = document.getElementById("decomp-chart");
const decompData = data.metrics.map(m => ({
  era: m.era,
  "Between Clubs": 1 - m.club_ratio,
  "Within Clubs": m.club_ratio,
}));
decompContainer.appendChild(
  Plot.plot({
    width: decompContainer.clientWidth,
    height: 300,
    style: { background: "transparent", color: "#c8c8d4" },
    x: { label: "Era" },
    y: { label: "↑ Share of total variance", grid: true, percent: true },
    color: { legend: true, label: "Component", range: ["#4269d0", "#72d2c0"] },
    marks: [
      Plot.barY(decompData, Plot.stackY({x: "era", y: "Between Clubs", fill: "#4269d0", order: "color"})),
      Plot.barY(decompData, Plot.stackY({x: "era", y: "Within Clubs", fill: "#72d2c0", order: "color"})),
      Plot.text(decompData, Plot.stackY({
        x: "era", y: "Within Clubs",
        text: d => `${(d["Within Clubs"]*100).toFixed(0)}%`,
        fill: "#000", fontSize: 12, fontWeight: "bold",
        dy: -10,
      })),
      Plot.ruleY([0, 1]),
    ]
  })
);
```
