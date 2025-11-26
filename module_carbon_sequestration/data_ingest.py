import pandas as pd, os

def read_csv(path):
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)

def ingest_all(cfg):
    return {k: read_csv(v) for k,v in cfg['inputs'].items() if k != 'rules'}
