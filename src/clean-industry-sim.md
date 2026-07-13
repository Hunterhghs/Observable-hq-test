---
theme: dashboard
toc: false
---

<style>
  #sim-controls { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.25rem; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; margin-bottom: 1rem; flex-wrap: wrap; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
  #sim-controls button { background: #fff; border: 1px solid #d1d5db; color: #374151; padding: 0.5rem 1.2rem; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-family: inherit; transition: all 0.15s; font-weight: 600; }
  #sim-controls button:hover { border-color: #4269d0; color: #4269d0; background: #f0f4ff; }
  #sim-controls button.active { background: #e8edf8; border-color: #4269d0; color: #4269d0; }
  #sim-controls button.playing { background: #fef2f2; border-color: #dc3545; color: #dc3545; }
  #year-display { font-size: 2.8rem; font-weight: 900; color: #4269d0; font-variant-numeric: tabular-nums; min-width: 110px; text-align: center; }
  #sim-controls input[type=range] { -webkit-appearance: none; height: 6px; background: #e5e7eb; border-radius: 3px; flex: 1; min-width: 200px; }
  #sim-controls input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 20px; height: 20px; background: #4269d0; border-radius: 50%; cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.15); }
  .bar-race-row { display: flex; align-items: center; margin-bottom: 1px; transition: all 0.3s ease; }
  .bar-race-label { width: 130px; text-align: right; padding-right: 0.8rem; font-size: 0.85rem; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #374151; }
  .bar-race-track { flex: 1; height: 26px; background: #f3f4f6; border-radius: 4px; overflow: hidden; position: relative; }
  .bar-race-fill { height: 100%; border-radius: 4px; transition: width 0.3s ease, background 0.3s ease; display: flex; align-items: center; padding-left: 0.5rem; font-size: 0.75rem; font-weight: 700; color: #fff; }
  .bar-race-value { width: 70px; padding-left: 0.6rem; font-size: 0.85rem; font-weight: 700; font-variant-numeric: tabular-nums; color: #374151; }
  .metric-big { font-size: 2rem; font-weight: 800; }
  .scenario-tabs { display: flex; gap: 0.4rem; }
  .scenario-tab { padding: 0.35rem 1rem; border-radius: 6px; cursor: pointer; font-size: 0.85rem; font-weight: 600; border: 1px solid #d1d5db; background: #fff; color: #6b7280; transition: all 0.2s; }
  .scenario-tab:hover { border-color: #9ca3af; color: #374151; }
  .scenario-tab.sel-baseline { background: #f3f4f6; border-color: #6b7280; color: #374151; }
  .scenario-tab.sel-green { background: #ecfdf5; border-color: #10b981; color: #059669; }
  .scenario-tab.sel-fossil { background: #fef2f2; border-color: #dc3545; color: #dc2626; }
</style>

<div class="page-hero">
  <h1>🏭 Clean Industry Transition Simulator</h1>
  <p>Interactive simulation · 15 countries · 2000–2025 · Play, pause, switch scenarios</p>
</div>

<div id="sim-controls">
  <div class="scenario-tabs" id="scenario-tabs"></div>
  <button id="btn-play">▶ Play</button>
  <button id="btn-slower" style="font-size:0.8rem;">⏪</button>
  <button id="btn-faster" style="font-size:0.8rem;">⏩</button>
  <span style="color:var(--muted);font-size:0.8rem;">Speed: <span id="speed-label">1×</span></span>
  <div id="year-display">2000</div>
</div>

<div class="grid grid-cols-4" style="margin-bottom: 1rem;" id="global-metrics"></div>

<div class="grid grid-cols-3" style="gap: 1rem;">
  <div class="card" style="grid-column: span 2; padding: 0.5rem;">
    <h3 style="margin:0 0 0.5rem 0; padding: 0 0.8rem;">Clean Industry Adoption by Country</h3>
    <div id="bar-race" style="padding: 0 0.5rem;"></div>
  </div>
  <div class="card">
    <h3 style="margin-top:0;">Trajectory</h3>
    <p class="muted" style="font-size:0.8rem;">Selected scenario — global average</p>
    <div id="trajectory-mini"></div>
  </div>
</div>

<div class="grid grid-cols-3" style="margin-top: 1rem;">
  <div class="card">
    <h3 style="margin-top:0;">Energy Mix</h3>
    <div id="energy-chart"></div>
  </div>
  <div class="card">
    <h3 style="margin-top:0;">Jobs Transition</h3>
    <div id="jobs-chart"></div>
  </div>
  <div class="card">
    <h3 style="margin-top:0;">Emissions vs GDP</h3>
    <div id="emissions-chart"></div>
  </div>
</div>

```js
import * as Plot from "npm:@observablehq/plot";
const data = await FileAttachment("./data/simulation.json").json();
const $ = id => document.getElementById(id);

// ── State ──
let scenario = "baseline";
let yearIdx = 0;
let playing = false;
let speed = 1;
let animFrame = null;
const nYears = data.years.length;

const scenarioColors = {
  baseline: "#aaaacc",
  green_transition: "#72d2c0",
  fossil_lockin: "#ff6b6b",
};
const scenarioClasses = {
  baseline: "sel-baseline",
  green_transition: "sel-green",
  fossil_lockin: "sel-fossil",
};

// ── Scenario Tabs ──
function renderTabs() {
  $("scenario-tabs").innerHTML = Object.entries(data.global).map(([k, v]) =>
    `<div class="scenario-tab ${k === scenario ? scenarioClasses[k] : ''}" data-scenario="${k}" style="border-left: 3px solid ${v.color};">${v.name}</div>`
  ).join("");
  document.querySelectorAll(".scenario-tab").forEach(tab => {
    tab.onclick = () => { scenario = tab.dataset.scenario; renderAll(); };
  });
}

// ── Global Metrics ──
function renderMetrics() {
  const g = data.global[scenario].years[yearIdx];
  $("global-metrics").innerHTML = [
    [`<span class="metric-value" style="color:#72d2c0;">${(g.clean_industry_pct*100).toFixed(1)}%</span><div class="metric-label">Clean Industry Share</div>`],
    [`<span class="metric-value" style="color:#ff6b6b;">${(g.emissions_mt/1000).toFixed(1)}</span><div class="metric-label">Emissions (Gt CO₂)</div>`],
    [`<span class="metric-value gold">${g.clean_jobs_m.toFixed(1)}M</span><div class="metric-label">Clean Jobs</div>`],
    [`<span class="metric-value" style="color:#aaa;">$${g.gdp_trillion.toFixed(1)}T</span><div class="metric-label">Global GDP</div>`],
  ].map(([html]) => `<div class="card" style="text-align:center;">${html}</div>`).join("");
}

// ── Bar Race ──
function renderBarRace() {
  const countries = data.countries
    .map(c => ({ name: c.name, region: c.region, pct: c.scenarios[scenario].years[yearIdx].clean_industry_pct }))
    .sort((a, b) => b.pct - a.pct);
  
  const maxPct = Math.max(0.05, ...countries.map(c => c.pct));
  const barRace = $("bar-race");
  barRace.innerHTML = "";
  
  countries.forEach((c, i) => {
    const row = document.createElement("div");
    row.className = "bar-race-row";
    const widthPct = (c.pct / maxPct) * 100;
    const hue = 160 - c.pct * 120;
    const color = `hsl(${Math.max(0, hue)}, 65%, ${50 + c.pct * 20}%)`;
    row.innerHTML = `
      <div class="bar-race-label">${c.name}</div>
      <div class="bar-race-track">
        <div class="bar-race-fill" style="width:${widthPct}%;background:${color};">${i < 3 ? c.name.substring(0,3).toUpperCase() : ''}</div>
      </div>
      <div class="bar-race-value">${(c.pct*100).toFixed(1)}%</div>`;
    barRace.appendChild(row);
  });
  
  // Trajectory mini chart
  const trajData = data.global[scenario].years.map(y => ({ year: y.year, clean: y.clean_industry_pct * 100 }));
  const trajDiv = $("trajectory-mini");
  trajDiv.innerHTML = "";
  trajDiv.appendChild(
    Plot.plot({
      width: trajDiv.clientWidth,
      height: 200,
      style: { background: "transparent", color: "#374151", fontSize: "11px" },
      marginLeft: 45, marginRight: 10, marginTop: 5, marginBottom: 30,
      x: { label: null, grid: true },
      y: { label: "% Clean", grid: true },
      marks: [
        Plot.areaY(trajData, { x: "year", y: "clean", fill: scenarioColors[scenario], fillOpacity: 0.15 }),
        Plot.line(trajData, { x: "year", y: "clean", stroke: scenarioColors[scenario], strokeWidth: 2.5 }),
        Plot.ruleX([data.years[yearIdx]], { stroke: "#374151", strokeOpacity: 0.3, strokeWidth: 2 }),
        Plot.dot([trajData[yearIdx]], { x: "year", y: "clean", fill: "#4269d0", r: 5 }),,
      ]
    })
  );
}

// ── Charts ──
function renderCharts() {
  const sc = data.global[scenario].years[yearIdx];
  const countries = data.countries.map(c => {
    const y = c.scenarios[scenario].years[yearIdx];
    return { ...y, name: c.name, region: c.region };
  });

  // Energy mix
  const eDiv = $("energy-chart");
  eDiv.innerHTML = "";
  const energyData = countries.map(c => ({ name: c.name, Renewables: c.energy_renewables, Nuclear: c.energy_nuclear, Fossil: c.energy_fossil }));
  const energyFlat = energyData.flatMap(d => [
    { name: d.name, source: "Renewables", share: d.Renewables },
    { name: d.name, source: "Nuclear", share: d.Nuclear },
    { name: d.name, source: "Fossil", share: d.Fossil },
  ]);
  eDiv.appendChild(
    Plot.plot({
      width: eDiv.clientWidth,
      height: 220,
      style: { background: "transparent", color: "#374151", fontSize: "11px" },
      marginLeft: 80, marginRight: 10,
      x: { label: null, percent: true },
      y: { label: null },
      color: { legend: true, range: ["#72d2c0", "#ffd93d", "#ff6b6b"] },
      marks: [
        Plot.barX(energyFlat, Plot.stackX({ y: "name", x: "share", fill: "source", order: "source", sort: { y: "x", reverse: true } })),
      ]
    })
  );

  // Jobs
  const jDiv = $("jobs-chart");
  jDiv.innerHTML = "";
  const jobsSorted = [...countries].sort((a, b) => b.clean_jobs_m - a.clean_jobs_m).slice(0, 10);
  jDiv.appendChild(
    Plot.plot({
      width: jDiv.clientWidth,
      height: 220,
      style: { background: "transparent", color: "#374151", fontSize: "11px" },
      marginLeft: 80, marginRight: 10,
      x: { label: "Jobs (millions)", grid: true },
      y: { label: null },
      marks: [
        Plot.barX(jobsSorted, { x: "clean_jobs_m", y: "name", fill: "#72d2c0", fillOpacity: 0.8, sort: { y: "x" } }),
        Plot.barX(jobsSorted, { x: "fossil_jobs_m", y: "name", fill: "#ff6b6b", fillOpacity: 0.5, sort: { y: "x" } }),
      ]
    })
  );

  // Emissions vs GDP
  const emDiv = $("emissions-chart");
  emDiv.innerHTML = "";
  emDiv.appendChild(
    Plot.plot({
      width: emDiv.clientWidth,
      height: 220,
      style: { background: "transparent", color: "#374151", fontSize: "11px" },
      marginLeft: 50, marginBottom: 35,
      x: { label: "GDP ($T)", grid: true },
      y: { label: "Emissions (Mt CO₂)", grid: true },
      marks: [
        Plot.dot(countries, { x: "gdp_trillion", y: "emissions_mt", fill: scenarioColors[scenario], r: 8, fillOpacity: 0.7 }),
        Plot.text(countries, { x: "gdp_trillion", y: "emissions_mt", text: d => d.name.substring(0, 3), dy: -14, fill: "#c8c8d4", fontSize: 9 }),
      ]
    })
  );
}

// ── Playback ──
function tick() {
  if (yearIdx < nYears - 1) {
    yearIdx++;
  } else {
    yearIdx = 0;
  }
  renderAll();
  if (playing) {
    animFrame = setTimeout(tick, 400 / speed);
  }
}

function renderAll() {
  $("year-display").textContent = data.years[yearIdx];
  renderMetrics();
  renderBarRace();
  renderCharts();
  renderTabs();
  $("btn-play").textContent = playing ? "⏸ Pause" : "▶ Play";
  $("btn-play").className = playing ? "playing" : "";
  $("speed-label").textContent = speed + "×";
}

// ── Controls ──
$("btn-play").onclick = () => {
  playing = !playing;
  if (playing) {
    if (yearIdx >= nYears - 1) yearIdx = 0;
    tick();
  } else {
    clearTimeout(animFrame);
  }
  renderAll();
};

$("btn-faster").onclick = () => {
  speed = Math.min(8, speed * 2);
  renderAll();
};

$("btn-slower").onclick = () => {
  speed = Math.max(0.25, speed / 2);
  renderAll();
};

// Keyboard controls
document.addEventListener("keydown", e => {
  if (e.code === "Space") { e.preventDefault(); $("btn-play").click(); }
  if (e.code === "ArrowRight") { if (!playing) { yearIdx = Math.min(nYears - 1, yearIdx + 1); renderAll(); } }
  if (e.code === "ArrowLeft") { if (!playing) { yearIdx = Math.max(0, yearIdx - 1); renderAll(); } }
});

// ── Init ──
renderAll();
```
