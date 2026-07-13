export default {
  root: "src",
  title: "Convergence Engine — H Heuristics",
  pages: [
    { name: "Home", path: "/" },
    { name: "Innovation Diffusion", path: "/innovation-diffusion" },
    { name: "NC Topology", path: "/nc-topology" },
    { name: "Particle Sim", path: "/particle-sim" },
    { name: "NC Atlas", path: "/nc-atlas" },
    { name: "Clean Industry Sim", path: "/clean-industry-sim" },
    { name: "3D Globe", path: "/globe" },
    { name: "3D Surface", path: "/convergence-surface" },
    { name: "Map View", path: "/convergence-map" },
    { name: "Regression", path: "/regression-panel" },
    { name: "D-Coefficient", path: "/d-coefficient" }
  ],
  theme: "dashboard",
  toc: false,
  head: `<style>
    :root {
      --bg: #f8f9fb;
      --card-bg: #ffffff;
      --text: #2c2c3a;
      --muted: #6b7280;
      --accent: #4269d0;
      --accent-light: #e8edf8;
      --accent2: #2e5bb8;
      --warn: #dc3545;
      --gold: #e6a817;
      --border: #e5e7eb;
      --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    }
    body { background: var(--bg); color: var(--text); font-family: 'Source Serif 4', serif; }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      box-shadow: var(--shadow);
      padding: 1.25rem;
    }
    h1, h2, h3 { color: #1a1a2e; font-weight: 700; }
    h1 { font-size: 2rem; letter-spacing: -0.03em; }
    h2 { font-size: 1.4rem; }
    h3 { font-size: 1.1rem; margin-top: 0; }
    .metric-value { font-size: 2rem; font-weight: 800; line-height: 1.1; }
    .metric-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
    .accent { color: var(--accent); }
    .warn { color: var(--warn); }
    .gold { color: var(--gold); }
    .page-hero { text-align: center; padding: 2.5rem 0 1.5rem; }
    .page-hero h1 { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em; color: #1a1a2e; }
    .page-hero p { color: var(--muted); max-width: 650px; margin: 0.5rem auto 0; font-size: 1.05rem; line-height: 1.6; }
    .muted { color: var(--muted); font-size: 0.85rem; }
    nav a { color: var(--muted); font-size: 0.9rem; }
    nav a:hover, nav a[aria-current] { color: var(--accent); font-weight: 600; }
    .grid { gap: 1rem; }
    .btn {
      display: inline-flex; align-items: center; gap: 0.4rem;
      padding: 0.5rem 1.2rem; border-radius: 6px; font-size: 0.9rem; font-weight: 600;
      border: 1px solid var(--border); background: #fff; color: var(--text);
      cursor: pointer; transition: all 0.15s; font-family: inherit;
    }
    .btn:hover { border-color: var(--accent); color: var(--accent); }
    .btn-primary { background: var(--accent); color: #fff; border-color: var(--accent); }
    .btn-primary:hover { background: var(--accent2); }
    .btn-active { background: var(--accent-light); border-color: var(--accent); color: var(--accent); }
  </style>`
};
