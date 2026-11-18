"""Acquire and use an administrative Sikkim boundary."""
from pathlib import Path
import json
import requests
from shapely.geometry import shape, mapping, Point

GEBOUNDARIES_API = 'https://www.geoboundaries.org/api/current/gbOpen/IND/ADM1/'

def acquire_india_adm1_boundary(destination: str | Path = 'data/raw/india_adm1.geojson') -> Path:
    dest = Path(destination); dest.parent.mkdir(parents=True, exist_ok=True)
    metadata = requests.get(GEBOUNDARIES_API, timeout=30); metadata.raise_for_status()
    url = metadata.json()['gjDownloadURL']
    # GitHub's normal raw URL can return a Git-LFS pointer. The media URL
    # requests the actual object and is streamed to avoid partial memory reads.
    url = url.replace('https://github.com/', 'https://media.githubusercontent.com/media/').replace('/raw/', '/')
    with requests.get(url, stream=True, timeout=(30, 600)) as response:
        response.raise_for_status()
        head = next(response.iter_content(256), b'')
        if head.startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise ValueError('Downloaded Git-LFS pointer instead of GeoJSON content')
        with dest.open('wb') as f:
            f.write(head)
            for chunk in response.iter_content(1024 * 1024): f.write(chunk)
    validate_geojson(dest)
    return dest

def validate_geojson(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if data.get('type') != 'FeatureCollection' or not data.get('features'):
        raise ValueError('Expected a non-empty GeoJSON FeatureCollection')
    geometries = [shape(f['geometry']) for f in data['features']]
    if not all(g.is_valid and not g.is_empty for g in geometries):
        raise ValueError('Boundary contains empty or invalid geometries')
    minx, miny, maxx, maxy = geometries[0].bounds
    for g in geometries[1:]:
        x1,y1,x2,y2=g.bounds; minx,miny,maxx,maxy=min(minx,x1),min(miny,y1),max(maxx,x2),max(maxy,y2)
    return {'features':len(geometries), 'bounds':(minx,miny,maxx,maxy), 'crs':data.get('crs', {}).get('properties', {}).get('name', 'EPSG:4326')}

def extract_sikkim_boundary(india_path: str | Path, destination: str | Path = 'data/processed/sikkim_boundary.geojson') -> Path:
    data=json.loads(Path(india_path).read_text(encoding='utf-8'))
    features=[f for f in data['features'] if any(str(v).casefold()=='sikkim' for v in f.get('properties',{}).values())]
    if not features: raise ValueError('Sikkim was not found in the boundary file')
    out=Path(destination); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({'type':'FeatureCollection','features':features,'crs':{'type':'name','properties':{'name':'EPSG:4326'}}}),encoding='utf-8')
    validate_geojson(out)
    return out

def clip_inventory_to_sikkim(inventory_path: str | Path, boundary_path: str | Path, destination: str | Path | None = None):
    import geopandas as gpd
    points = gpd.read_file(inventory_path).to_crs(4326)
    boundary = gpd.read_file(boundary_path).to_crs(4326)
    clipped = gpd.sjoin(points, boundary[['geometry']], predicate='within', how='inner').drop(columns=['index_right'], errors='ignore')
    if destination:
        out = Path(destination); out.parent.mkdir(parents=True, exist_ok=True); clipped.to_file(out, driver='GeoJSON')
    return clipped
