def compute_risk(row, weights):
    # Example simplistic scoring using climate params
    drought = max(0, 1 - (row.get('rainfall',0)/800))
    flood = max(0, (row.get('rainfall',0)-900)/300)
    heat = max(0, (row.get('temperature',0)-28)/10)
    pest = 0.3  # placeholder static risk
    score = (drought*weights['drought'] + flood*weights['flood'] + heat*weights['heat'] + pest*weights['pest'])
    level = 'Low' if score < 0.25 else 'Moderate' if score < 0.5 else 'High'
    return score, level
