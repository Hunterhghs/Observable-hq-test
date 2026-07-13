"""
Economic Particle Engine — generates 2,500 economic entities across 25 years × 3 scenarios.
Designed for high-density 3D point cloud visualization.

Each entity represents a firm/cluster with:
- 3D spatial coordinates (simulated economic space)
- Sector classification
- GDP contribution, employment, innovation index
- Growth trajectory over time
"""
import json, sys, math, random
random.seed(2024)

# ── Parameters ──
n_entities = 2500
years = list(range(2000, 2026))
sectors = [
    {"name":"Technology","color":"#4269d0","base_x":0.7,"base_y":0.7,"base_z":0.5,"count":0.22},
    {"name":"Manufacturing","color":"#e6a817","base_x":0.3,"base_y":0.4,"base_z":0.6,"count":0.20},
    {"name":"Finance","color":"#10b981","base_x":0.6,"base_y":0.5,"base_z":0.3,"count":0.13},
    {"name":"Healthcare","color":"#8b5cf6","base_x":0.5,"base_y":0.3,"base_z":0.7,"count":0.15},
    {"name":"Energy","color":"#dc3545","base_x":0.4,"base_y":0.6,"base_z":0.4,"count":0.10},
    {"name":"Consumer","color":"#f59e0b","base_x":0.5,"base_y":0.5,"base_z":0.5,"count":0.12},
    {"name":"Real Estate","color":"#ec4899","base_x":0.3,"base_y":0.3,"base_z":0.3,"count":0.08},
]

scenarios = {
    "baseline": {"name":"Baseline","desc":"Steady growth","growth_mod":1.0,"cluster_strength":0.6},
    "tech_boom": {"name":"Tech Boom","desc":"Technology-driven acceleration","growth_mod":1.6,"cluster_strength":0.8},
    "restructuring": {"name":"Restructuring","desc":"Sectoral shift from manufacturing to services","growth_mod":0.85,"cluster_strength":0.4},
}

# ── Entity generation ──
entities = []
sector_counts = {}
current_count = 0
for sector in sectors:
    count = int(n_entities * sector["count"])
    sector_counts[sector["name"]] = count
    
    for i in range(count):
        # Base 3D position in economic space (clustered by sector)
        cx = sector["base_x"]
        cy = sector["base_y"]
        cz = sector["base_z"]
        
        x = cx + random.gauss(0, 0.15)
        y = cy + random.gauss(0, 0.15)
        z = cz + random.gauss(0, 0.12)
        
        # Keep within bounds
        x = max(0.02, min(0.98, x))
        y = max(0.02, min(0.98, y))
        z = max(0.02, min(0.98, z))
        
        # Base economic metrics
        base_gdp = 10 ** random.uniform(1.5, 4.0)  # $30 to $10,000 million
        base_emp = int(10 ** random.uniform(1.0, 3.5))  # 10 to 3,000 employees
        base_innovation = random.betavariate(2, 5)  # skewed toward lower values
        
        entities.append({
            "id": current_count + i,
            "sector": sector["name"],
            "color": sector["color"],
            "x": round(x, 4),
            "y": round(y, 4),
            "z": round(z, 4),
            "base_gdp": round(base_gdp, 1),
            "base_emp": base_emp,
            "base_innovation": round(base_innovation, 4),
            "scenarios": {},
        })
    current_count += count

n_actual = len(entities)

# ── Generate time series per scenario ──
for sc_key, sc in scenarios.items():
    for entity in entities:
        sector_data = next(s for s in sectors if s["name"] == entity["sector"])
        
        # Sector-specific growth rates
        sector_growth = {
            "Technology":   0.065 if sc_key == "tech_boom" else 0.038,
            "Manufacturing":0.015 if sc_key == "restructuring" else 0.025,
            "Finance":      0.030,
            "Healthcare":   0.042,
            "Energy":       0.020 if sc_key == "tech_boom" else 0.028,
            "Consumer":     0.025,
            "Real Estate":  0.022,
        }.get(entity["sector"], 0.025)
        
        timeseries = []
        gdp = entity["base_gdp"]
        emp = entity["base_emp"]
        innov = entity["base_innovation"]
        
        for yi, year in enumerate(years):
            t = yi / len(years)
            
            # GDP growth with noise
            gdp_growth = sector_growth * sc["growth_mod"] * (1 + 0.3 * math.sin(t * 5))
            gdp *= (1 + gdp_growth + random.gauss(0, 0.02))
            
            # Employment with some decoupling from GDP
            emp *= (1 + gdp_growth * 0.6 + random.gauss(0, 0.015))
            emp = max(1, int(emp))
            
            # Innovation index (slow accumulation + jumps)
            innov += random.uniform(0, 0.015) * sc["growth_mod"]
            innov = min(1.0, innov)
            
            # 3D position drift (entities move in economic space over time)
            drift_x = x + random.gauss(0, 0.003) * t * 10 * sc["cluster_strength"]
            drift_y = y + random.gauss(0, 0.003) * t * 10 * sc["cluster_strength"]
            drift_z = z + random.gauss(0, 0.002) * t * 8
            drift_x = max(0.01, min(0.99, drift_x))
            drift_y = max(0.01, min(0.99, drift_y))
            drift_z = max(0.01, min(0.99, drift_z))
            
            timeseries.append({
                "year": year,
                "gdp_m": round(gdp, 1),
                "employees": emp,
                "innovation": round(innov, 4),
                "x": round(drift_x, 4),
                "y": round(drift_y, 4),
                "z": round(drift_z, 4),
            })
        
        entity["scenarios"][sc_key] = timeseries

# ── Aggregates ──
aggregates = {}
for sc_key, sc in scenarios.items():
    agg = {"years": []}
    for yi, year in enumerate(years):
        total_gdp = sum(e["scenarios"][sc_key][yi]["gdp_m"] for e in entities)
        total_emp = sum(e["scenarios"][sc_key][yi]["employees"] for e in entities)
        avg_innov = sum(e["scenarios"][sc_key][yi]["innovation"] for e in entities) / n_actual
        
        sector_gdps = {}
        for sector in sectors:
            sector_gdps[sector["name"]] = sum(
                e["scenarios"][sc_key][yi]["gdp_m"] for e in entities if e["sector"] == sector["name"]
            )
        
        # Gini of GDP distribution
        gdps_sorted = sorted(e["scenarios"][sc_key][yi]["gdp_m"] for e in entities)
        n = len(gdps_sorted)
        cumsum = sum(gdps_sorted)
        gini = sum((2*i - n - 1) * g for i, g in enumerate(gdps_sorted)) / (n * cumsum) if cumsum > 0 else 0
        
        agg["years"].append({
            "year": year,
            "total_gdp_b": round(total_gdp / 1000, 2),
            "total_emp_m": round(total_emp / 1_000_000, 2),
            "avg_innovation": round(avg_innov, 4),
            "gini": round(gini, 4),
            "sector_gdps": {k: round(v / 1000, 2) for k, v in sector_gdps.items()},
        })
    aggregates[sc_key] = agg

output = {
    "entities": entities,
    "aggregates": aggregates,
    "sectors": [s["name"] for s in sectors],
    "sector_colors": {s["name"]: s["color"] for s in sectors},
    "years": years,
    "scenarios": list(scenarios.keys()),
    "scenario_meta": {k: {"name": v["name"], "desc": v["desc"]} for k, v in scenarios.items()},
    "meta": {
        "n_entities": n_actual,
        "n_years": len(years),
        "total_data_points": n_actual * len(years) * len(scenarios),
        "generated_by": "economic-particle-engine v1.0",
    }
}

json.dump(output, sys.stdout)
