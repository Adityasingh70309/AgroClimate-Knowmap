import pandas as pd
import re
from .utils import new_id

DEF_STRATEGY_FIELDS = ['practice','category','description','conditions']

def load_strategies(path):
    return pd.read_csv(path) if path and isinstance(path,str) and path.endswith('.csv') else pd.DataFrame()

def _eval_condition(cond, row):
    cond = cond.strip()
    if not cond: return True
    m = re.match(r"(\w+)\s*([<>=])\s*([A-Za-z0-9_.-]+)", cond)
    if not m: return True  # unknown condition, ignore
    key, op, val = m.groups()
    left = row.get(key)
    # Normalize types
    try:
        if isinstance(left, (int,float)) or re.match(r"^-?\d+(\.\d+)?$", str(val)):
            left = float(left)
            val_cmp = float(val)
        else:
            left = str(left)
            val_cmp = str(val)
    except Exception:
        return False
    if op == '<': return left < val_cmp
    if op == '>': return left > val_cmp
    if op == '=': return left == val_cmp
    return False

def recommend(row, catalog, top_n=3):
    matches = []
    crop = row.get('crop','').lower()
    risk_level = row.get('risk_level')
    for _,s in catalog.iterrows():
        base_score = 0.0
        explanation_parts = []
        # Evaluate conditions list (comma separated)
        cond_str = str(s.get('conditions',''))
        conditions = [c for c in cond_str.split(',') if c.strip()]
        if conditions:
            cond_results = [_eval_condition(c, row) for c in conditions]
            if all(cond_results):
                base_score += 0.4
                explanation_parts.append('conditions matched')
            else:
                # Skip if explicit conditions and not all satisfied
                continue
        # Crop keyword heuristic
        if crop and crop in str(s.get('description','')).lower():
            base_score += 0.3
            explanation_parts.append('crop keyword')
        # Risk level emphasis
        if risk_level == 'High':
            base_score += 0.2
            explanation_parts.append('high risk emphasis')
        elif risk_level == 'Moderate':
            base_score += 0.1
            explanation_parts.append('moderate risk emphasis')
        if base_score > 0:
            matches.append({
                'strategy_id': new_id(),
                'practice': s.get('practice'),
                'category': s.get('category'),
                'description': s.get('description'),
                'conditions': cond_str,
                'score': round(base_score,3),
                'explanation': '; '.join(explanation_parts) or 'heuristic match'
            })
    matches.sort(key=lambda x: x['score'], reverse=True)
    return matches[:top_n]
