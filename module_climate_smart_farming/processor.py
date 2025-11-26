import pandas as pd

def merge_tables(data):
    climate = data.get('climate'); soil = data.get('soil'); crops = data.get('crops')
    if climate is None or climate.empty: return pd.DataFrame()
    df = climate.copy()
    if soil is not None and not soil.empty: df = df.merge(soil, on='location', how='left')
    if crops is not None and not crops.empty: df = df.merge(crops, on='location', how='left')
    return df.fillna('')
