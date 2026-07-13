"""
North Carolina County Data Engine — generates multi-year, multi-metric panel data
for 100 NC counties, 2010-2024, across economy, demographics, and housing layers.

Output structure:
- counties: array of county objects with time series
- layers: metadata about toggleable map layers
- meta: project info
"""
import json, sys, math, random
random.seed(919)

# ── NC Counties (100) with approximate centroids ──
counties_raw = [
    # Coastal Plain
    {"name":"Alamance","lat":36.04,"lon":-79.40,"region":"Piedmont","pop_base":151000},
    {"name":"Alexander","lat":35.92,"lon":-81.18,"region":"Mountains","pop_base":37000},
    {"name":"Alleghany","lat":36.49,"lon":-81.13,"region":"Mountains","pop_base":11000},
    {"name":"Anson","lat":34.97,"lon":-80.10,"region":"Coastal Plain","pop_base":26000},
    {"name":"Ashe","lat":36.43,"lon":-81.50,"region":"Mountains","pop_base":27000},
    {"name":"Avery","lat":36.08,"lon":-81.92,"region":"Mountains","pop_base":18000},
    {"name":"Beaufort","lat":35.48,"lon":-76.84,"region":"Coastal Plain","pop_base":47000},
    {"name":"Bertie","lat":36.06,"lon":-76.96,"region":"Coastal Plain","pop_base":20000},
    {"name":"Bladen","lat":34.62,"lon":-78.56,"region":"Coastal Plain","pop_base":35000},
    {"name":"Brunswick","lat":34.04,"lon":-78.23,"region":"Coastal Plain","pop_base":135000},
    {"name":"Buncombe","lat":35.61,"lon":-82.53,"region":"Mountains","pop_base":270000},
    {"name":"Burke","lat":35.75,"lon":-81.70,"region":"Mountains","pop_base":90000},
    {"name":"Cabarrus","lat":35.39,"lon":-80.55,"region":"Piedmont","pop_base":215000},
    {"name":"Caldwell","lat":35.95,"lon":-81.55,"region":"Mountains","pop_base":82000},
    {"name":"Camden","lat":36.34,"lon":-76.16,"region":"Coastal Plain","pop_base":11000},
    {"name":"Carteret","lat":34.86,"lon":-76.54,"region":"Coastal Plain","pop_base":69000},
    {"name":"Caswell","lat":36.40,"lon":-79.33,"region":"Piedmont","pop_base":23000},
    {"name":"Catawba","lat":35.66,"lon":-81.21,"region":"Piedmont","pop_base":160000},
    {"name":"Chatham","lat":35.70,"lon":-79.26,"region":"Piedmont","pop_base":77000},
    {"name":"Cherokee","lat":35.13,"lon":-84.06,"region":"Mountains","pop_base":29000},
    {"name":"Chowan","lat":36.13,"lon":-76.60,"region":"Coastal Plain","pop_base":14000},
    {"name":"Clay","lat":35.06,"lon":-83.75,"region":"Mountains","pop_base":11000},
    {"name":"Cleveland","lat":35.33,"lon":-81.56,"region":"Piedmont","pop_base":100000},
    {"name":"Columbus","lat":34.26,"lon":-78.66,"region":"Coastal Plain","pop_base":56000},
    {"name":"Craven","lat":35.12,"lon":-77.08,"region":"Coastal Plain","pop_base":103000},
    {"name":"Cumberland","lat":35.05,"lon":-78.83,"region":"Coastal Plain","pop_base":335000},
    {"name":"Currituck","lat":36.37,"lon":-75.94,"region":"Coastal Plain","pop_base":28000},
    {"name":"Dare","lat":35.77,"lon":-75.75,"region":"Coastal Plain","pop_base":37000},
    {"name":"Davidson","lat":35.79,"lon":-80.21,"region":"Piedmont","pop_base":170000},
    {"name":"Davie","lat":35.93,"lon":-80.54,"region":"Piedmont","pop_base":43000},
    {"name":"Duplin","lat":34.94,"lon":-77.93,"region":"Coastal Plain","pop_base":59000},
    {"name":"Durham","lat":36.04,"lon":-78.88,"region":"Piedmont","pop_base":325000},
    {"name":"Edgecombe","lat":35.91,"lon":-77.60,"region":"Coastal Plain","pop_base":52000},
    {"name":"Forsyth","lat":36.13,"lon":-80.26,"region":"Piedmont","pop_base":382000},
    {"name":"Franklin","lat":36.08,"lon":-78.28,"region":"Piedmont","pop_base":72000},
    {"name":"Gaston","lat":35.29,"lon":-81.18,"region":"Piedmont","pop_base":228000},
    {"name":"Gates","lat":36.44,"lon":-76.70,"region":"Coastal Plain","pop_base":11000},
    {"name":"Graham","lat":35.35,"lon":-83.83,"region":"Mountains","pop_base":8500},
    {"name":"Granville","lat":36.30,"lon":-78.65,"region":"Piedmont","pop_base":61000},
    {"name":"Greene","lat":35.49,"lon":-77.68,"region":"Coastal Plain","pop_base":21000},
    {"name":"Guilford","lat":36.08,"lon":-79.79,"region":"Piedmont","pop_base":540000},
    {"name":"Halifax","lat":36.26,"lon":-77.65,"region":"Coastal Plain","pop_base":50000},
    {"name":"Harnett","lat":35.37,"lon":-78.87,"region":"Coastal Plain","pop_base":135000},
    {"name":"Haywood","lat":35.56,"lon":-82.98,"region":"Mountains","pop_base":62000},
    {"name":"Henderson","lat":35.34,"lon":-82.46,"region":"Mountains","pop_base":118000},
    {"name":"Hertford","lat":36.36,"lon":-77.00,"region":"Coastal Plain","pop_base":23000},
    {"name":"Hoke","lat":35.02,"lon":-79.24,"region":"Coastal Plain","pop_base":53000},
    {"name":"Hyde","lat":35.41,"lon":-76.15,"region":"Coastal Plain","pop_base":5000},
    {"name":"Iredell","lat":35.81,"lon":-80.87,"region":"Piedmont","pop_base":190000},
    {"name":"Jackson","lat":35.29,"lon":-83.14,"region":"Mountains","pop_base":44000},
    {"name":"Johnston","lat":35.52,"lon":-78.36,"region":"Coastal Plain","pop_base":220000},
    {"name":"Jones","lat":35.02,"lon":-77.36,"region":"Coastal Plain","pop_base":9500},
    {"name":"Lee","lat":35.48,"lon":-79.18,"region":"Piedmont","pop_base":64000},
    {"name":"Lenoir","lat":35.24,"lon":-77.64,"region":"Coastal Plain","pop_base":56000},
    {"name":"Lincoln","lat":35.49,"lon":-81.25,"region":"Piedmont","pop_base":90000},
    {"name":"Macon","lat":35.15,"lon":-83.42,"region":"Mountains","pop_base":37000},
    {"name":"Madison","lat":35.86,"lon":-82.70,"region":"Mountains","pop_base":22000},
    {"name":"Martin","lat":35.84,"lon":-77.11,"region":"Coastal Plain","pop_base":23000},
    {"name":"McDowell","lat":35.68,"lon":-82.05,"region":"Mountains","pop_base":45000},
    {"name":"Mecklenburg","lat":35.25,"lon":-80.84,"region":"Piedmont","pop_base":1120000},
    {"name":"Mitchell","lat":36.01,"lon":-82.16,"region":"Mountains","pop_base":15000},
    {"name":"Montgomery","lat":35.33,"lon":-79.90,"region":"Piedmont","pop_base":27000},
    {"name":"Moore","lat":35.31,"lon":-79.48,"region":"Piedmont","pop_base":102000},
    {"name":"Nash","lat":35.97,"lon":-77.99,"region":"Coastal Plain","pop_base":95000},
    {"name":"New Hanover","lat":34.23,"lon":-77.87,"region":"Coastal Plain","pop_base":230000},
    {"name":"Northampton","lat":36.42,"lon":-77.40,"region":"Coastal Plain","pop_base":20000},
    {"name":"Onslow","lat":34.76,"lon":-77.46,"region":"Coastal Plain","pop_base":205000},
    {"name":"Orange","lat":36.06,"lon":-79.12,"region":"Piedmont","pop_base":148000},
    {"name":"Pamlico","lat":35.15,"lon":-76.67,"region":"Coastal Plain","pop_base":13000},
    {"name":"Pasquotank","lat":36.27,"lon":-76.26,"region":"Coastal Plain","pop_base":40000},
    {"name":"Pender","lat":34.52,"lon":-77.90,"region":"Coastal Plain","pop_base":63000},
    {"name":"Perquimans","lat":36.18,"lon":-76.41,"region":"Coastal Plain","pop_base":13000},
    {"name":"Person","lat":36.39,"lon":-78.97,"region":"Piedmont","pop_base":39000},
    {"name":"Pitt","lat":35.59,"lon":-77.38,"region":"Coastal Plain","pop_base":175000},
    {"name":"Polk","lat":35.28,"lon":-82.17,"region":"Mountains","pop_base":21000},
    {"name":"Randolph","lat":35.71,"lon":-79.81,"region":"Piedmont","pop_base":145000},
    {"name":"Richmond","lat":35.00,"lon":-79.75,"region":"Coastal Plain","pop_base":45000},
    {"name":"Robeson","lat":34.64,"lon":-79.10,"region":"Coastal Plain","pop_base":130000},
    {"name":"Rockingham","lat":36.40,"lon":-79.78,"region":"Piedmont","pop_base":91000},
    {"name":"Rowan","lat":35.64,"lon":-80.52,"region":"Piedmont","pop_base":146000},
    {"name":"Rutherford","lat":35.40,"lon":-81.92,"region":"Mountains","pop_base":67000},
    {"name":"Sampson","lat":34.99,"lon":-78.37,"region":"Coastal Plain","pop_base":63000},
    {"name":"Scotland","lat":34.84,"lon":-79.48,"region":"Coastal Plain","pop_base":35000},
    {"name":"Stanly","lat":35.31,"lon":-80.25,"region":"Piedmont","pop_base":63000},
    {"name":"Stokes","lat":36.40,"lon":-80.24,"region":"Piedmont","pop_base":46000},
    {"name":"Surry","lat":36.41,"lon":-80.69,"region":"Piedmont","pop_base":72000},
    {"name":"Swain","lat":35.43,"lon":-83.45,"region":"Mountains","pop_base":14000},
    {"name":"Transylvania","lat":35.20,"lon":-82.80,"region":"Mountains","pop_base":34000},
    {"name":"Tyrrell","lat":35.87,"lon":-76.17,"region":"Coastal Plain","pop_base":4000},
    {"name":"Union","lat":34.99,"lon":-80.56,"region":"Piedmont","pop_base":245000},
    {"name":"Vance","lat":36.36,"lon":-78.41,"region":"Piedmont","pop_base":44000},
    {"name":"Wake","lat":35.79,"lon":-78.65,"region":"Piedmont","pop_base":1140000},
    {"name":"Warren","lat":36.40,"lon":-78.10,"region":"Piedmont","pop_base":19000},
    {"name":"Washington","lat":35.84,"lon":-76.57,"region":"Coastal Plain","pop_base":12000},
    {"name":"Watauga","lat":36.23,"lon":-81.70,"region":"Mountains","pop_base":54000},
    {"name":"Wayne","lat":35.36,"lon":-78.00,"region":"Coastal Plain","pop_base":122000},
    {"name":"Wilkes","lat":36.22,"lon":-81.16,"region":"Mountains","pop_base":68000},
    {"name":"Wilson","lat":35.72,"lon":-77.92,"region":"Coastal Plain","pop_base":81000},
    {"name":"Yadkin","lat":36.16,"lon":-80.67,"region":"Piedmont","pop_base":38000},
    {"name":"Yancey","lat":35.90,"lon":-82.31,"region":"Mountains","pop_base":18000},
]

years = list(range(2010, 2025))

# ── Region characteristics ──
region_profiles = {
    "Piedmont":     {"gdp_growth":0.032,"income_base":52000,"education_base":0.32,"poverty_base":0.14,"home_value_base":210000},
    "Mountains":    {"gdp_growth":0.022,"income_base":44000,"education_base":0.25,"poverty_base":0.16,"home_value_base":185000},
    "Coastal Plain":{"gdp_growth":0.018,"income_base":41000,"education_base":0.20,"poverty_base":0.21,"home_value_base":155000},
}

counties = []
for c in counties_raw:
    rp = region_profiles[c["region"]]
    pop = c["pop_base"]
    county = {
        "name": c["name"],
        "region": c["region"],
        "lat": c["lat"],
        "lon": c["lon"],
        "years": [],
    }
    
    for yi, year in enumerate(years):
        t = yi / len(years)
        # Population: urban grow faster
        pop_growth = 0.008 + (0.015 if c["pop_base"] > 100000 else 0.002) + random.gauss(0, 0.003)
        pop *= (1 + pop_growth)
        
        # GDP per capita
        gdp_pc = rp["gdp_growth"] * (1 + t) * 18000 + rp["income_base"] * 0.9
        gdp_pc += random.gauss(0, 1500)
        
        # Median household income
        income = rp["income_base"] * (1 + 0.02 * t) + pop_growth * 5000 + random.gauss(0, 2000)
        
        # Unemployment (U-shaped over business cycle)
        unemp = 6.5 - 3 * t + 2 * math.sin(t * 3) + random.gauss(0, 0.8)
        if c["region"] == "Piedmont": unemp -= 1.5
        if c["region"] == "Coastal Plain": unemp += 1.5
        unemp = max(2.5, min(16, unemp))
        
        # Education (% bachelor's+)
        education = rp["education_base"] + 0.15 * t + random.gauss(0, 0.02)
        education = min(0.65, max(0.10, education))
        
        # Poverty rate
        poverty = rp["poverty_base"] - 0.04 * t + random.gauss(0, 0.01)
        poverty = max(5, min(30, poverty))
        
        # Median home value
        home = rp["home_value_base"] * (1 + 0.035 * t) + random.gauss(0, 8000)
        if year >= 2020: home *= (1 + 0.04 * (year - 2020))  # pandemic housing boom
        
        # Population density (people per sq mile)
        density = pop * (0.3 if c["region"] == "Mountains" else 1.2 if c["region"] == "Piedmont" else 0.5) / 100
        
        county["years"].append({
            "year": year,
            "population": round(pop, 0),
            "gdp_per_capita": round(gdp_pc, 0),
            "median_income": round(income, 0),
            "unemployment": round(unemp, 2),
            "education_bachelors_pct": round(education, 4),
            "poverty_rate": round(poverty, 2),
            "median_home_value": round(home, 0),
            "population_density": round(density, 1),
        })
    
    counties.append(county)

# ── Layers metadata ──
layers = {
    "economy": {
        "name": "Economy",
        "metrics": [
            {"key":"gdp_per_capita","label":"GDP per Capita","format":"currency","color_scale":["#dbeafe","#1e40af"]},
            {"key":"median_income","label":"Median Household Income","format":"currency","color_scale":["#fef3c7","#92400e"]},
            {"key":"unemployment","label":"Unemployment Rate","format":"percent1","color_scale":["#dcfce7","#166534"],"invert":True},
        ]
    },
    "demographics": {
        "name": "Demographics",
        "metrics": [
            {"key":"population","label":"Population","format":"number","color_scale":["#f3e8ff","#6b21a8"]},
            {"key":"population_density","label":"Population Density","format":"number","color_scale":["#e0e7ff","#3730a3"]},
            {"key":"education_bachelors_pct","label":"Bachelor's Degree %","format":"percent","color_scale":["#e8f5e9","#1b5e20"]},
            {"key":"poverty_rate","label":"Poverty Rate","format":"percent1","color_scale":["#fff7ed","#9a3412"],"invert":True},
        ]
    },
    "housing": {
        "name": "Housing",
        "metrics": [
            {"key":"median_home_value","label":"Median Home Value","format":"currency","color_scale":["#fce7f3","#9d174d"]},
        ]
    },
}

output = {
    "counties": counties,
    "layers": layers,
    "years": years,
    "meta": {
        "title": "North Carolina Multi-Layered Atlas",
        "n_counties": len(counties),
        "n_years": len(years),
        "regions": ["Piedmont", "Mountains", "Coastal Plain"],
        "generated_by": "nc-atlas-engine v1.0",
    }
}

json.dump(output, sys.stdout)
