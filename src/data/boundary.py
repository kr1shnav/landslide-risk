"""Acquire and use an administrative Sikkim boundary."""
from pathlib import Path
import requests

GEBOUNDARIES_API = 'https://www.geoboundaries.org/api/current/gbOpen/IND/ADM1/'

def acquire_india_adm1_boundary(destination: str | Path = 'data/raw/india_adm1.geojson') -> Path:
    dest = Path(destination); dest.parent.mkdir(parents=True, exist_ok=True)
    metadata = requests.get(GEBOUNDARIES_API, timeout=30); metadata.raise_for_status()
    url = metadata.json()['gjDownloadURL']
    response = requests.get(url, timeout=120); response.raise_for_status()
    dest.write_bytes(response.content)
    return dest

def extract_sikkim_boundary(india_path: str | Path, destination: str | Path = 'data/processed/sikkim_boundary.geojson') -> Path:
    import geopandas as gpd
    g = gpd.read_file(india_path)
    name_columns = [c for c in g.columns if c.lower() in {'shape_name','name','name_1','statename'}]
    if not name_columns: raise ValueError('Could not identify state-name column in boundary file')
    col = name_columns[0]
    sikkim = g[g[col].astype(str).str.casefold().eq('sikkim')].copy()
    if sikkim.empty: raise ValueError('Sikkim was not found in the boundary file')
    sikkim = sikkim.to_crs(4326)
    out = Path(destination); out.parent.mkdir(parents=True, exist_ok=True); sikkim.to_file(out, driver='GeoJSON')
    return out

def clip_inventory_to_sikkim(inventory_path: str | Path, boundary_path: str | Path, destination: str | Path | None = None):
    import geopandas as gpd
    points = gpd.read_file(inventory_path).to_crs(4326)
    boundary = gpd.read_file(boundary_path).to_crs(4326)
    clipped = gpd.sjoin(points, boundary[['geometry']], predicate='within', how='inner').drop(columns=['index_right'], errors='ignore')
    if destination:
        out = Path(destination); out.parent.mkdir(parents=True, exist_ok=True); clipped.to_file(out, driver='GeoJSON')
    return clipped
