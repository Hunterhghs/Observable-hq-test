---
theme: dashboard
toc: false
---

<div class="page-hero">
  <h1>D-Coefficient Explorer</h1>
  <p>Distributional convergence metric — Lorenz curves, Gini decomposition, and inequality diagnostics</p>
</div>

<div class="grid grid-cols-4" style="margin-bottom: 1.5rem;" id="d-kpi"></div>

<div class="grid grid-cols-2">
  <div class="card">
    <h3>D-Coefficient & Gini Trajectory</h3>
    <p class="muted">D → 1 = perfect convergence. Declining Gini = equalizing distribution.</p>
    <div id="d-gini-chart"></div>
  </div>
  <div class="card">
    <h3>Lorenz Curves by Era</h3>
    <p class="muted">Cumulative GDP share vs cumulative population — closer to diagonal = more equal</p>
    <div id="lorenz-chart"></div>
  </div>
</div>

<div class="grid grid-cols-2" style="margin-top: 1.5rem;">
  <div class="card">
    <h3>Inequality Decomposition</h3>
    <p class="muted">Between-club vs within-club variance shares — where does inequality come from?</p>
    <div id="decomp-chart"></div>
  </div>
  <div class="card">
    <h3>GDP Distribution Curves</h3>
    <p class="muted">Full distribution shape per era — rightward shift + narrowing = convergence</p>
    <div id="ridge-chart"></div>
  </div>
</div>

<div class="card" style="margin-top: 1.5rem;" id="insight-card"></div>

```js
import * as Plot from "npm:@observablehq/plot";
const data = await FileAttachment("./data/convergence.json").json();
const $ = id => document.getElementById(id);

// ── KPI ──
const kpi = $("d-kpi");
const dDelta = data.metrics[2].d_coefficient - data.metrics[0].d_coefficient;
const giniDelta = data.metrics[0].gini - data.metrics[2].gini;
const giniPct = ((1 - data.metrics[2].gini / data.metrics[0].gini) * 100).toFixed(1);
[
  [`<span class="metric-value" style="color:#72d2c0;">+${dDelta.toFixed(3)}</span><div class="metric-label">Δ D-Coefficient</div>`, ""],
  [`<span class="metric-value" style="color:#ff6b6b;">−${giniDelta.toFixed(3)}</span><div class="metric-label">Δ Gini</div>`, ""],
  [`<span class="metric-value gold">${giniPct}%</span><div class="metric-label">Inequality Reduction</div>`, ""],
  [`<span class="metric-value" style="color:#72d2c0;">Converging ✓</span><div class="metric-label">Status</div>`, ""],
].forEach(([html]) => { const c = document.createElement("div"); c.className="card"; c.style.textAlign="center"; c.innerHTML=html; kpi.appendChild(c); });

// ── D-Coefficient & Gini ──
$("d-gini-chart").appendChild(
  Plot.plot({
    width: $("d-gini-chart").clientWidth,
    height: 340,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 55, marginRight: 55,
    x: { label: null, padding: 0.4 },
    y: { grid: true, label: null },
    marks: [
      // D-coefficient
      Plot.areaY(data.metrics, { x: "era", y1: 0.55, y2: "d_coefficient", fill: "#72d2c0", fillOpacity: 0.12 }),
      Plot.line(data.metrics, { x: "era", y: "d_coefficient", stroke: "#72d2c0", strokeWidth: 3.5, curve: "catmull-rom" }),
      Plot.dot(data.metrics, { x: "era", y: "d_coefficient", fill: "#72d2c0", r: 7 }),
      Plot.text(data.metrics, { x: "era", y: "d_coefficient", text: d => `D: ${d.d_coefficient.toFixed(3)}`, dy: -18, fill: "#72d2c0", fontSize: 14, fontWeight: "bold" }),
      // Gini
      Plot.line(data.metrics, { x: "era", y: "gini", stroke: "#ff6b6b", strokeWidth: 3, curve: "catmull-rom" }),
      Plot.dot(data.metrics, { x: "era", y: "gini", fill: "#ff6b6b", r: 6 }),
      Plot.text(data.metrics, { x: "era", y: "gini", text: d => `Gini: ${d.gini.toFixed(3)}`, dy: 18, fill: "#ff6b6b", fontSize: 13 }),
      // Reference lines
      Plot.ruleY([1], { stroke: "#72d2c0", strokeOpacity: 0.2, strokeDasharray: "6,4" }),
      Plot.ruleY([0], { stroke: "#ff6b6b", strokeOpacity: 0.2, strokeDasharray: "6,4" }),
    ]
  })
);

// ── Lorenz Curves ──
const lorenzData = [];
data.metrics.forEach((m, ei) => {
  const gdps = data.regions.map(r => r.eras[ei].gdp_per_capita).sort((a, b) => a - b);
  const total = gdps.reduce((s, v) => s + v, 0);
  let cumPop = 0, cumGDP = 0;
  for (let i = 0; i < gdps.length; i++) {
    cumPop = (i + 1) / gdps.length;
    cumGDP += gdps[i] / total;
    lorenzData.push({ era: m.era, cumPop, cumGDP });
  }
});
$("lorenz-chart").appendChild(
  Plot.plot({
    width: $("lorenz-chart").clientWidth,
    height: 340,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 55, marginBottom: 40,
    x: { label: "Cumulative population share →", domain: [0, 1] },
    y: { label: "↑ Cumulative GDP share", domain: [0, 1] },
    color: { legend: true, label: "Era", legendX: 0.02, legendY: 0.98 },
    marks: [
      Plot.line([{x:0,y:0},{x:1,y:1}], { x:"x", y:"y", stroke: "#ffffff18", strokeWidth: 1.5, strokeDasharray: "6,4" }),
      Plot.text([{x:0.85,y:0.88}], { x:"x", y:"y", text: "Perfect equality", fill: "#ffffff30", fontSize: 10 }),
      Plot.line(lorenzData, { x: "cumPop", y: "cumGDP", stroke: "era", strokeWidth: 3, curve: "basis" }),
    ]
  })
);

// ── Decomposition ──
const decompData = data.metrics.map(m => ({
  era: m.era,
  between: 1 - m.club_ratio,
  within: m.club_ratio,
}));
const decompFlat = decompData.flatMap(d => [
  { era: d.era, component: "Between Clubs", share: d.between },
  { era: d.era, component: "Within Clubs", share: d.within },
]);
$("decomp-chart").appendChild(
  Plot.plot({
    width: $("decomp-chart").clientWidth,
    height: 340,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 55,
    x: { label: "Era", padding: 0.3 },
    y: { label: "Share of total variance", grid: true, percent: true },
    color: { legend: true, label: "Component", range: ["#4269d0", "#72d2c0"] },
    marks: [
      Plot.barY(decompFlat, Plot.stackY({ x: "era", y: "share", fill: "component", order: "component" })),
      Plot.text(decompFlat, Plot.stackY({
        x: "era", y: "share", fill: "component", order: "component",
        text: d => d.share > 0.06 ? `${(d.share*100).toFixed(0)}%` : "",
        fill: "#000", fontSize: 12, fontWeight: "bold",
      })),
      Plot.ruleY([0, 1]),
    ]
  })
);

// ── Ridge / Distribution ──
const ridgeData = data.regions.flatMap(r =>
  r.eras.map(e => ({ era: e.era, gdp: e.gdp_per_capita / 1000 }))
);
$("ridge-chart").appendChild(
  Plot.plot({
    width: $("ridge-chart").clientWidth,
    height: 340,
    style: { background: "transparent", color: "#c8c8d4", fontSize: "13px" },
    marginLeft: 55,
    x: { label: "GDP per capita ($k)", grid: true },
    y: { label: "Density", ticks: [] },
    color: { legend: true, label: "Era" },
    marks: [
      Plot.density(ridgeData, { x: "gdp", y: "era", stroke: "era", strokeWidth: 2, fill: "era", fillOpacity: 0.12, bandwidth: 2.5 }),
    ]
  })
);

// ── Insight ──
$("insight-card").innerHTML = `
  <h3 style="margin-top:0;">Key Insight</h3>
  <p style="color:#c8c8d4;line-height:1.8;font-size:1.05rem;">
    The D-Coefficient rises from <strong style="color:#ff6b6b;">${data.metrics[0].d_coefficient.toFixed(3)}</strong> 
    (Pre-Transition) to <strong style="color:#72d2c0;">${data.metrics[2].d_coefficient.toFixed(3)}</strong> 
    (Integration), confirming <strong style="color:#72d2c0;">strong convergence</strong> across ${data.meta.n_regions} European regions. 
    The Gini coefficient drops <strong style="color:#ff6b6b;">${giniPct}%</strong> from 
    <strong>${data.metrics[0].gini.toFixed(3)}</strong> to 
    <strong style="color:#72d2c0;">${data.metrics[2].gini.toFixed(3)}</strong>.
    The club decomposition shows that <strong style="color:#72d2c0;">within-club convergence</strong> accounts for 
    <strong>${(data.metrics[2].club_ratio*100).toFixed(0)}%</strong> of total variance in the Integration era — 
    regions within the same development tier are catching up to each other rapidly, 
    while structural differences between clubs persist.
  </p>`;
```
