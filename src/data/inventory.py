"""Real inventory ingestion; no synthetic records are created here."""
from pathlib import Path
import json
import pandas as pd
from shapely.geometry import Point, shape

def load_inventory(path: str | Path) -> pd.DataFrame:
    p=Path(path)
    if p.suffix.lower()=='.csv':
        df=pd.read_csv(p); df.columns=[str(c).strip().lower() for c in df.columns]
        if not {'latitude','longitude'} <= set(df.columns): raise ValueError('CSV requires latitude and longitude')
        return df
    if p.suffix.lower() in {'.geojson','.json'}:
        data=json.loads(p.read_text(encoding='utf-8')); rows=[]
        for f in data.get('features',[]):
            g=shape(f['geometry']); point=g if g.geom_type=='Point' else g.centroid
            row={str(k).lower():v for k,v in f.get('properties',{}).items()}; row.update(latitude=point.y,longitude=point.x); rows.append(row)
        return pd.DataFrame(rows)
    import geopandas as gpd
    g=gpd.read_file(p).to_crs(4326); out=pd.DataFrame(g.drop(columns='geometry')); out.columns=[str(c).lower() for c in out.columns]; out['latitude']=g.geometry.y; out['longitude']=g.geometry.x; return out

def filter_to_boundary(df: pd.DataFrame, boundary_path: str | Path) -> pd.DataFrame:
    data=json.loads(Path(boundary_path).read_text(encoding='utf-8'))
    boundary=shape(data['features'][0]['geometry'])
    keep=[boundary.covers(Point(float(x),float(y))) for x,y in zip(df['longitude'],df['latitude'])]
    out=df.loc[keep].copy().reset_index(drop=True); out.attrs['input_records']=len(df); out.attrs['records_in_sikkim']=len(out); return out
