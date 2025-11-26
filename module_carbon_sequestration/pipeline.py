from .utils import load_config, new_id, save_jsonl, ensure_dir
from .data_ingest import ingest_all
from .carbon_engine import rule_based, scenarios, PRACTICE_FACTORS
from .neo4j_mapper import CarbonNeo4jMapper
from .ml_model import SimpleCarbonRegressor
import csv

def build_rows(cfg):
    data = ingest_all(cfg)
    soil = data.get('soil')
    if soil is None or soil.empty:
        return []
    merged = soil.copy()
    for name in ['climate','biomass','management']:
        df = data.get(name)
        if df is not None and not df.empty:
            merged = merged.merge(df, on='location', how='left')
    for col in ['rainfall','temperature','biomass']:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)
    if 'practice' in merged.columns:
        merged['practice'] = merged['practice'].fillna('baseline')
    rows = []
    practices = cfg['engine']['scenario_practices']
    cf = cfg['engine'].get('carbon_unit_factor',3.67)
    # preliminary pass to collect rows and compute baseline/scenarios
    for _,row in merged.iterrows():
        d = row.to_dict(); d['id']=new_id(); d['practice']=d.get('practice','baseline') or 'baseline'
        rule_val = rule_based(d, cf)
        baseline_rate, scen = scenarios(d, practices, cf)
        rows.append({
            'id': d['id'], 'location': d.get('location'), 'soc': d.get('soc'),
            'rainfall': d.get('rainfall'), 'temperature': d.get('temperature'), 'biomass': d.get('biomass'),
            'current_practice': d['practice'], 'practice_factor': PRACTICE_FACTORS.get(d['practice'],0),
            'rule_sequestration': rule_val, 'baseline_rate': baseline_rate, 'scenarios': scen
        })
    # Fit simple ML model and add predictions
    ml = SimpleCarbonRegressor(); ml.fit(rows)
    preds = ml.predict(rows)
    for r,p in zip(rows,preds):
        r['ml_predicted_rate'] = p
    return rows

def run_pipeline(cfg_path='agrobase/module_carbon_sequestration/config.yaml'):
    cfg = load_config(cfg_path)
    rows = build_rows(cfg)
    results_csv = cfg['output']['results_csv']; ensure_dir(results_csv)
    with open(results_csv,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['id','location','soc','rainfall','temperature','biomass','current_practice','practice_factor','rule_sequestration','baseline_rate','scenarios'])
        for r in rows:
            w.writerow([r.get(k) for k in ['id','location','soc','rainfall','temperature','biomass','current_practice','practice_factor','rule_sequestration','baseline_rate','scenarios']])
    save_jsonl(rows, cfg['output']['log_jsonl'])
    if cfg['neo4j'].get('enabled'):
        try:
            mapper = CarbonNeo4jMapper(cfg['neo4j']['uri'], cfg['neo4j']['user'], cfg['neo4j']['password'])
            mapper.map(rows); mapper.close()
        except Exception:
            pass
    return rows

if __name__=='__main__':
    out=run_pipeline(); print('Rows:',len(out))
