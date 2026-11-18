from pathlib import Path
from typing import Any
import pandas as pd

def validate_inventory(path: str | Path) -> dict[str, Any]:
    p=Path(path)
    if not p.exists(): raise FileNotFoundError(p)
    if p.suffix.lower()=='.csv':
        df=pd.read_csv(p); cols={c.lower() for c in df.columns}
        if not {'latitude','longitude'} <= cols: raise ValueError('CSV needs latitude and longitude columns')
        return {'path':str(p),'records':len(df),'crs':'EPSG:4326','missing':int(df.isna().sum().sum()),'columns':list(df.columns)}
    import geopandas as gpd
    g=gpd.read_file(p)
    if g.crs is None: raise ValueError('Spatial file has no CRS')
    return {'path':str(p),'records':len(g),'crs':str(g.crs),'missing':int(g.isna().sum().sum()),'columns':list(g.columns)}
