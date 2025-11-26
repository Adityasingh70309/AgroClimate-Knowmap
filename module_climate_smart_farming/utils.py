import os, json, uuid, yaml, datetime, pandas as pd

def load_config(path):
    with open(path,'r',encoding='utf-8') as f: return yaml.safe_load(f)

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def save_jsonl(records, path):
    ensure_dir(path)
    with open(path,'a',encoding='utf-8') as f:
        for r in records: f.write(json.dumps(r)+'\n')

def new_id(): return str(uuid.uuid4())

def read_csv(path):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame()
