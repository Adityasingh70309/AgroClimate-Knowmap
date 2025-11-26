PRACTICE_FACTORS = {
    'cover_cropping': 0.15,
    'agroforestry': 0.30,
    'residue_retention': 0.10,
    'reduced_tillage': 0.08,
    'baseline': 0.0
}

def rule_based(row, carbon_unit_factor=3.67):
    soc = float(row.get('soc', 0) or 0)
    biomass = float(row.get('biomass', 0) or 0)
    rainfall = float(row.get('rainfall', 0) or 0)
    temperature = float(row.get('temperature', 0) or 0)
    practice_factor = PRACTICE_FACTORS.get(row.get('practice','baseline'),0)
    base = soc*0.02 + biomass*0.01
    climate = (rainfall/1000.0)*0.05 - max(0.0, temperature-25.0)*0.01
    rate = base + climate
    if rate < 0: rate = 0
    return rate*(1+practice_factor)*carbon_unit_factor

def scenarios(base_row, practices, carbon_unit_factor=3.67):
    baseline_rate = rule_based({**base_row, 'practice':'baseline'}, carbon_unit_factor)/carbon_unit_factor
    out = []
    for p in practices:
        f = PRACTICE_FACTORS.get(p,0)
        out.append({'practice':p,'factor':f,'estimated_rate':baseline_rate*(1+f)*carbon_unit_factor})
    return baseline_rate*carbon_unit_factor, out
