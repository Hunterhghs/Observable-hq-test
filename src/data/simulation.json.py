"""
Clean Industry Transition Simulator — generates multi-scenario panel data
for 15 countries × 25 years × 3 scenarios.

Output: JSON with full time series for animated simulation.
"""
import json, sys, math, random
random.seed(1337)

# ── Parameters ──
countries = [
    {"id":"DE","name":"Germany","region":"Western Europe","base_clean":0.12,"base_gdp":2.2,"green_ambition":0.9},
    {"id":"FR","name":"France","region":"Western Europe","base_clean":0.14,"base_gdp":1.8,"green_ambition":0.8},
    {"id":"UK","name":"United Kingdom","region":"Western Europe","base_clean":0.10,"base_gdp":2.0,"green_ambition":0.85},
    {"id":"DK","name":"Denmark","region":"Western Europe","base_clean":0.18,"base_gdp":0.35,"green_ambition":0.95},
    {"id":"PL","name":"Poland","region":"Central Europe","base_clean":0.05,"base_gdp":0.55,"green_ambition":0.5},
    {"id":"CZ","name":"Czech Republic","region":"Central Europe","base_clean":0.07,"base_gdp":0.25,"green_ambition":0.55},
    {"id":"SK","name":"Slovakia","region":"Central Europe","base_clean":0.06,"base_gdp":0.12,"green_ambition":0.6},
    {"id":"HU","name":"Hungary","region":"Central Europe","base_clean":0.05,"base_gdp":0.18,"green_ambition":0.55},
    {"id":"RO","name":"Romania","region":"Eastern Europe","base_clean":0.03,"base_gdp":0.28,"green_ambition":0.45},
    {"id":"BG","name":"Bulgaria","region":"Eastern Europe","base_clean":0.03,"base_gdp":0.08,"green_ambition":0.4},
    {"id":"CN","name":"China","region":"East Asia","base_clean":0.04,"base_gdp":12.0,"green_ambition":0.7},
    {"id":"IN","name":"India","region":"South Asia","base_clean":0.06,"base_gdp":4.0,"green_ambition":0.6},
    {"id":"US","name":"United States","region":"North America","base_clean":0.11,"base_gdp":13.0,"green_ambition":0.55},
    {"id":"BR","name":"Brazil","region":"South America","base_clean":0.09,"base_gdp":2.0,"green_ambition":0.65},
    {"id":"ZA","name":"South Africa","region":"Africa","base_clean":0.04,"base_gdp":0.4,"green_ambition":0.5},
]

scenarios = {
    "baseline": {
        "name": "Baseline",
        "desc": "Current policies continue — gradual transition",
        "color": "#8888aa",
        "annual_growth": 0.025,
        "policy_push": 0.0,
        "tech_cost_decay": 0.03,
    },
    "green_transition": {
        "name": "Green Transition",
        "desc": "Accelerated policy + technology — rapid clean industry growth",
        "color": "#72d2c0",
        "annual_growth": 0.045,
        "policy_push": 0.025,
        "tech_cost_decay": 0.06,
    },
    "fossil_lockin": {
        "name": "Fossil Lock-In",
        "desc": "Continued fossil investment — slow, uneven transition",
        "color": "#ff6b6b",
        "annual_growth": 0.012,
        "policy_push": -0.01,
        "tech_cost_decay": 0.015,
    },
}

years = list(range(2000, 2026))
output = {"countries": [], "scenarios": list(scenarios.keys()), "years": years, "meta": {}}

for c in countries:
    country_data = {"id": c["id"], "name": c["name"], "region": c["region"], "scenarios": {}}
    
    for sc_key, sc in scenarios.items():
        sc_data = {"name": sc["name"], "color": sc["color"], "years": []}
        clean_pct = c["base_clean"]
        emissions_base = c["base_gdp"] * 0.5  # emissions intensity
        gdp = c["base_gdp"]
        
        for yi, year in enumerate(years):
            t = yi / len(years)  # normalized time 0→1
            
            # GDP grows with some variation
            gdp *= (1 + 0.025 + random.gauss(0, 0.008))
            
            # Clean industry adoption: logistic-ish curve
            ambition_effect = c["green_ambition"] * sc["policy_push"] * t
            tech_effect = sc["tech_cost_decay"] * t * (1 + t)
            base_adoption = sc["annual_growth"] * (1 + 3 * t)  # accelerates over time
            noise = random.gauss(0, 0.008)
            
            # S-curve: slower start, acceleration, then saturation
            s_curve = 1 / (1 + math.exp(-8 * (t - 0.35)))
            clean_pct += (base_adoption + ambition_effect + tech_effect + noise)
            caps = {"baseline": 0.72, "green_transition": 0.90, "fossil_lockin": 0.45}
            clean_pct = min(caps.get(sc_key, 0.72), max(0.02, clean_pct))
            
            # Emissions: rise with GDP, fall with clean industry
            emissions_intensity = emissions_base * (1 - clean_pct * 0.7) * (1 + 0.01 * yi)
            emissions = gdp * emissions_intensity * 0.3
            # In green scenario, emissions fall after 2015
            if sc_key == "green_transition" and year > 2015:
                emissions *= (1 - 0.03 * (year - 2015))
            if sc_key == "fossil_lockin" and year > 2010:
                emissions *= (1 + 0.01 * (year - 2010))
            
            # Jobs in clean industry
            clean_jobs = clean_pct * gdp * 0.15 + random.gauss(0, 0.02)
            fossil_jobs = (1 - clean_pct) * gdp * 0.08 + random.gauss(0, 0.01)
            
            # Energy mix
            renewables = clean_pct * 0.7 + 0.05 * t
            nuclear = 0.15 - 0.03 * t if sc_key != "green_transition" else 0.2
            fossil = 1 - renewables - nuclear
            
            sc_data["years"].append({
                "year": year,
                "clean_industry_pct": round(clean_pct, 4),
                "gdp_trillion": round(gdp, 2),
                "emissions_mt": round(emissions, 1),
                "clean_jobs_m": round(max(0, clean_jobs), 2),
                "fossil_jobs_m": round(max(0, fossil_jobs), 2),
                "energy_renewables": round(renewables, 3),
                "energy_nuclear": round(nuclear, 3),
                "energy_fossil": round(fossil, 3),
                "region": c["region"],
            })
        
        country_data["scenarios"][sc_key] = sc_data
    
    output["countries"].append(country_data)

# ── Global aggregates ──
output["global"] = {}
for sc_key in scenarios:
    output["global"][sc_key] = {"name": scenarios[sc_key]["name"], "color": scenarios[sc_key]["color"], "years": []}
    for yi, year in enumerate(years):
        total_gdp = sum(c["scenarios"][sc_key]["years"][yi]["gdp_trillion"] for c in output["countries"])
        total_emissions = sum(c["scenarios"][sc_key]["years"][yi]["emissions_mt"] for c in output["countries"])
        total_clean_jobs = sum(c["scenarios"][sc_key]["years"][yi]["clean_jobs_m"] for c in output["countries"])
        total_fossil_jobs = sum(c["scenarios"][sc_key]["years"][yi]["fossil_jobs_m"] for c in output["countries"])
        weighted_clean = sum(
            c["scenarios"][sc_key]["years"][yi]["clean_industry_pct"] * c["scenarios"][sc_key]["years"][yi]["gdp_trillion"]
            for c in output["countries"]
        ) / total_gdp if total_gdp > 0 else 0
        
        output["global"][sc_key]["years"].append({
            "year": year,
            "clean_industry_pct": round(weighted_clean, 4),
            "gdp_trillion": round(total_gdp, 1),
            "emissions_mt": round(total_emissions, 0),
            "clean_jobs_m": round(total_clean_jobs, 1),
            "fossil_jobs_m": round(total_fossil_jobs, 1),
        })

output["meta"] = {
    "title": "Clean Industry Transition Simulator",
    "subtitle": "15 countries · 2000–2025 · 3 scenarios",
    "scenario_descriptions": {k: v["desc"] for k, v in scenarios.items()},
    "n_countries": len(countries),
    "n_years": len(years),
    "generated_by": "convergence-engine simulation v1.0",
}

json.dump(output, sys.stdout)
