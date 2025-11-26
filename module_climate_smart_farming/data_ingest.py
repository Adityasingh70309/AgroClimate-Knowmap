from .utils import read_csv

def ingest(cfg):
    return {k: read_csv(v) for k,v in cfg['inputs'].items()}
