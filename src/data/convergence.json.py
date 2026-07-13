"""
Economic Convergence Engine — generates synthetic panel data for
convergence analysis across three development eras.

Outputs a JSON object with:
- regions: list of region objects with coordinates, era-level GDP, growth rates
- eras: era metadata
- convergence_metrics: D-coefficient, beta/sigma convergence per era
- scenario_parameters: adjustable model parameters
"""
import json, sys, math, random

random.seed(42)

# ── Scenario Parameters ──────────────────────────────────────────
params = {
    "n_regions": 48,
    "eras": [
        {"name": "Pre-Transition", "year_start": 1985, "year_end": 1995, "tech_growth": 0.008, "diffusion_rate": 0.12},
        {"name": "Transition",      "year_start": 1995, "year_end": 2008, "tech_growth": 0.018, "diffusion_rate": 0.25},
        {"name": "Integration",     "year_start": 2008, "year_end": 2023, "tech_growth": 0.022, "diffusion_rate": 0.35},
    ],
    "base_gdp": 2800,       # initial GDP per capita (lowest region)
    "gdp_spread": 18000,    # range from poorest to richest
    "noise": 0.08,          # random variation
    "convergence_clubs": 4, # number of convergence clubs
    "spatial_autocorr": 0.3 # spatial autocorrelation strength
}

# ── Region Generator ──────────────────────────────────────────────
regions_list = [
    # Western / Advanced
    {"id": "DE", "name": "Germany", "lat": 51.2, "lon": 10.4, "club": 3},
    {"id": "FR", "name": "France", "lat": 46.6, "lon": 2.2, "club": 3},
    {"id": "UK", "name": "United Kingdom", "lat": 55.4, "lon": -3.4, "club": 3},
    {"id": "AT", "name": "Austria", "lat": 47.5, "lon": 14.5, "club": 3},
    {"id": "CH", "name": "Switzerland", "lat": 46.8, "lon": 8.2, "club": 3},
    {"id": "NL", "name": "Netherlands", "lat": 52.1, "lon": 5.3, "club": 3},
    {"id": "BE", "name": "Belgium", "lat": 50.5, "lon": 4.5, "club": 3},
    {"id": "DK", "name": "Denmark", "lat": 55.7, "lon": 9.6, "club": 3},
    {"id": "SE", "name": "Sweden", "lat": 60.1, "lon": 18.6, "club": 3},
    {"id": "NO", "name": "Norway", "lat": 60.5, "lon": 8.5, "club": 3},
    {"id": "FI", "name": "Finland", "lat": 61.9, "lon": 25.7, "club": 2},
    {"id": "IT", "name": "Italy", "lat": 41.9, "lon": 12.5, "club": 2},
    {"id": "ES", "name": "Spain", "lat": 40.5, "lon": -3.7, "club": 2},
    {"id": "PT", "name": "Portugal", "lat": 39.4, "lon": -8.2, "club": 2},
    {"id": "IE", "name": "Ireland", "lat": 53.1, "lon": -8.2, "club": 3},
    {"id": "GR", "name": "Greece", "lat": 39.1, "lon": 21.8, "club": 1},
    # Central / Transition
    {"id": "PL", "name": "Poland", "lat": 52.0, "lon": 19.4, "club": 1},
    {"id": "CZ", "name": "Czech Republic", "lat": 49.8, "lon": 15.5, "club": 2},
    {"id": "SK", "name": "Slovakia", "lat": 48.7, "lon": 19.7, "club": 2},
    {"id": "HU", "name": "Hungary", "lat": 47.2, "lon": 19.5, "club": 1},
    {"id": "SI", "name": "Slovenia", "lat": 46.1, "lon": 14.8, "club": 2},
    {"id": "HR", "name": "Croatia", "lat": 45.1, "lon": 15.2, "club": 1},
    {"id": "EE", "name": "Estonia", "lat": 58.6, "lon": 25.0, "club": 2},
    {"id": "LV", "name": "Latvia", "lat": 56.9, "lon": 24.6, "club": 1},
    {"id": "LT", "name": "Lithuania", "lat": 55.2, "lon": 23.9, "club": 1},
    {"id": "RO", "name": "Romania", "lat": 45.9, "lon": 25.0, "club": 0},
    {"id": "BG", "name": "Bulgaria", "lat": 42.7, "lon": 25.5, "club": 0},
    {"id": "RS", "name": "Serbia", "lat": 44.0, "lon": 21.0, "club": 0},
    {"id": "BA", "name": "Bosnia & Herz.", "lat": 43.9, "lon": 17.7, "club": 0},
    {"id": "MK", "name": "North Macedonia", "lat": 41.6, "lon": 21.7, "club": 0},
    {"id": "AL", "name": "Albania", "lat": 41.2, "lon": 20.2, "club": 0},
    {"id": "ME", "name": "Montenegro", "lat": 42.7, "lon": 19.4, "club": 0},
    # Eastern / CIS
    {"id": "UA", "name": "Ukraine", "lat": 49.0, "lon": 31.4, "club": 0},
    {"id": "BY", "name": "Belarus", "lat": 53.9, "lon": 27.5, "club": 0},
    {"id": "MD", "name": "Moldova", "lat": 47.0, "lon": 28.9, "club": 0},
    {"id": "GE", "name": "Georgia", "lat": 42.3, "lon": 43.4, "club": 0},
    {"id": "AM", "name": "Armenia", "lat": 40.2, "lon": 44.5, "club": 0},
    {"id": "AZ", "name": "Azerbaijan", "lat": 40.4, "lon": 47.6, "club": 0},
    # Southern / Med
    {"id": "TR", "name": "Turkey", "lat": 39.1, "lon": 35.4, "club": 0},
    {"id": "CY", "name": "Cyprus", "lat": 35.1, "lon": 33.4, "club": 2},
    {"id": "MT", "name": "Malta", "lat": 35.9, "lon": 14.4, "club": 2},
    # Additional
    {"id": "IS", "name": "Iceland", "lat": 64.9, "lon": -19.0, "club": 3},
    {"id": "LU", "name": "Luxembourg", "lat": 49.6, "lon": 6.1, "club": 3},
    {"id": "AD", "name": "Andorra", "lat": 42.5, "lon": 1.5, "club": 3},
    {"id": "MC", "name": "Monaco", "lat": 43.7, "lon": 7.4, "club": 3},
    {"id": "SM", "name": "San Marino", "lat": 43.9, "lon": 12.5, "club": 2},
    {"id": "LI", "name": "Liechtenstein", "lat": 47.1, "lon": 9.5, "club": 3},
]

n = len(regions_list)

# ── Generate era-level data ──────────────────────────────────────
def club_base_gdp(club, era_idx):
    """Base GDP grows per club, with convergence over eras."""
    club_starts = {0: 2800, 1: 5500, 2: 9500, 3: 16000}
    # Convergence: poorer clubs catch up faster
    convergence_rates = {0: [0.035, 0.055, 0.065],
                         1: [0.025, 0.040, 0.045],
                         2: [0.018, 0.028, 0.030],
                         3: [0.012, 0.018, 0.020]}
    base = club_starts[club]
    for e in range(era_idx + 1):
        base *= (1 + convergence_rates[club][e]) ** 10
    return base

regions = []
for r in regions_list:
    region = {
        "id": r["id"],
        "name": r["name"],
        "lat": r["lat"],
        "lon": r["lon"],
        "club": r["club"],
        "eras": []
    }
    for e_idx, era in enumerate(params["eras"]):
        base = club_base_gdp(r["club"], e_idx)
        # Add spatial noise and individual variation
        spatial_factor = 1.0 + random.gauss(0, params["spatial_autocorr"])
        noise = 1.0 + random.gauss(0, params["noise"])
        gdp = base * spatial_factor * noise
        
        # Growth rate (higher for poorer regions — convergence)
        growth_noise = random.gauss(0, 0.005)
        growth = params["eras"][e_idx]["tech_growth"]
        # Convergence effect: poorer grow faster
        convergence_premium = max(0, (20000 - gdp) / 20000 * 0.03)
        growth += convergence_premium + growth_noise
        
        region["eras"].append({
            "era": era["name"],
            "era_idx": e_idx,
            "gdp_per_capita": round(gdp, 0),
            "growth_rate": round(growth, 4),
            "population": round(random.uniform(0.4, 80.0), 1),  # millions
        })
    regions.append(region)

# ── Convergence Metrics ──────────────────────────────────────────
import statistics

def compute_convergence_metrics(regions_list, era_idx):
    """Compute D-coefficient, beta, sigma convergence for an era."""
    gdps = [r["eras"][era_idx]["gdp_per_capita"] for r in regions_list]
    growths = [r["eras"][era_idx]["growth_rate"] for r in regions_list]
    clubs = [r["club"] for r in regions_list]
    
    n = len(gdps)
    mean_gdp = statistics.mean(gdps)
    mean_growth = statistics.mean(growths)
    std_gdp = statistics.stdev(gdps)
    std_growth = statistics.stdev(growths)
    min_gdp = min(gdps)
    max_gdp = max(gdps)
    
    # Sigma convergence: standard deviation of log GDP
    log_gdps = [math.log(g) for g in gdps]
    sigma = statistics.stdev(log_gdps)
    
    # Beta convergence: regress growth on initial GDP
    # beta < 0 means convergence (poorer grow faster)
    cov = sum((gdps[i] - mean_gdp) * (growths[i] - mean_growth) for i in range(n)) / n
    var_gdp = sum((g - mean_gdp) ** 2 for g in gdps) / n
    beta = cov / var_gdp if var_gdp > 0 else 0
    
    # D-coefficient: measure of distributional change
    # D = 1 - (Gini_t / Gini_t-1)  → D>0 means convergence
    sorted_gdps = sorted(gdps)
    cumsum = 0
    for i, g in enumerate(sorted_gdps):
        cumsum += g
    gini = 0
    cumsum2 = 0
    for i, g in enumerate(sorted_gdps):
        cumsum2 += g
        gini += (i + 1) * g
    gini = (2 * gini) / (n * cumsum) - (n + 1) / n if cumsum > 0 else 0
    
    # Club convergence: variance within clubs vs total
    club_groups = {}
    for i, c in enumerate(clubs):
        if c not in club_groups:
            club_groups[c] = []
        club_groups[c].append(gdps[i])
    within_var = 0
    for c, vals in club_groups.items():
        if len(vals) > 1:
            within_var += statistics.stdev(vals) ** 2
    within_var /= len(club_groups)
    total_var = std_gdp ** 2
    
    return {
        "era": params["eras"][era_idx]["name"],
        "era_idx": era_idx,
        "mean_gdp": round(mean_gdp, 0),
        "min_gdp": round(min_gdp, 0),
        "max_gdp": round(max_gdp, 0),
        "std_gdp": round(std_gdp, 0),
        "sigma_convergence": round(sigma, 4),
        "beta_convergence": round(beta, 8),
        "d_coefficient": round(1 - gini, 4),
        "gini": round(gini, 4),
        "within_club_variance": round(within_var, 0),
        "total_variance": round(total_var, 0),
        "club_ratio": round(within_var / total_var, 4) if total_var > 0 else 0,
        "n_regions": n,
        "cv": round(std_gdp / mean_gdp, 4),
    }

metrics = [compute_convergence_metrics(regions, e) for e in range(len(params["eras"]))]

# ── Output ───────────────────────────────────────────────────────
output = {
    "parameters": params,
    "regions": regions,
    "metrics": metrics,
    "meta": {
        "generated_by": "convergence-engine v1.0",
        "description": "Synthetic panel data for economic convergence analysis across 48 European regions",
        "n_regions": n,
        "n_eras": len(params["eras"]),
        "convergence_clubs": params["convergence_clubs"],
    }
}

json.dump(output, sys.stdout)
