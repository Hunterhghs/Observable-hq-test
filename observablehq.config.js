export default {
  root: "src",
  title: "Convergence Engine — H Heuristics",
  pages: [
    { name: "Home", path: "/" },
    { name: "Clean Industry Sim", path: "/clean-industry-sim" },
    { name: "3D Surface", path: "/convergence-surface" },
    { name: "Map View", path: "/convergence-map" },
    { name: "Regression", path: "/regression-panel" },
    { name: "D-Coefficient", path: "/d-coefficient" }
  ],
  theme: "dashboard",
  toc: false,
  head: `<style>
    :root {
      --bg: #0a0a0f;
      --card-bg: #12121a;
      --text: #c8c8d4;
      --muted: #6b6b7b;
      --accent: #72d2c0;
      --accent2: #4269d0;
      --warn: #ff6b6b;
      --gold: #ffd93d;
    }
    body { background: var(--bg); color: var(--text); font-family: 'Source Serif 4', serif; }
    .card { background: var(--card-bg); border: 1px solid #1a1a2e; border-radius: 10px; }
    h1, h2, h3 { color: #e8e8f0; }
    .metric-value { font-size: 2.2rem; font-weight: 800; }
    .metric-label { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }
    .accent { color: var(--accent); }
    .warn { color: var(--warn); }
    .gold { color: var(--gold); }
    .page-hero { text-align: center; padding: 2rem 0 1.5rem; }
    .page-hero h1 { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em; }
    .page-hero p { color: var(--muted); max-width: 600px; margin: 0.5rem auto 0; }
    nav a { color: var(--muted); }
    nav a:hover, nav a[aria-current] { color: var(--accent); }
  </style>`
};
