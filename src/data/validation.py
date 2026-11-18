from pathlib import Path
from typing import Any
import pandas as pd
from src.data.preprocessing import clean_inventory

def validate_inventory(path: str | Path) -> dict[str, Any]:
    p=Path(path)
    if not p.exists(): raise FileNotFoundError(p)
    if p.suffix.lower()=='.csv':
        df=pd.read_csv(p); cols={c.lower() for c in df.columns}
        if not {'latitude','longitude'} <= cols: raise ValueError('CSV needs latitude and longitude columns')
        df, report=clean_inventory(df)
        return {'path':str(p),'records':len(df),**report,'crs':'EPSG:4326','columns':list(df.columns)}
    import geopandas as gpd
    g=gpd.read_file(p)
    if g.crs is None: raise ValueError('Spatial file has no CRS')
    g, report=clean_inventory(g)
    return {'path':str(p),'records':len(g),**report,'crs':str(g.crs),'columns':list(g.columns)}
