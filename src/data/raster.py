"""Raster acquisition, validation, mosaicking, and clipping utilities."""
from pathlib import Path
import gzip
import math
import numpy as np

def validate_raster(path: str | Path, bounds=None) -> dict:
    import rasterio
    with rasterio.open(path) as src:
        result={'path':str(path),'width':src.width,'height':src.height,'crs':str(src.crs),'resolution':src.res,'nodata':src.nodata,'bounds':tuple(src.bounds),'count':src.count}
        if bounds:
            minx,miny,maxx,maxy=bounds; b=src.bounds; result['covers_bounds']=b.left<=minx and b.bottom<=miny and b.right>=maxx and b.top>=maxy
        return result
def srtm_tiles_for_bounds(bounds):
    minx,miny,maxx,maxy=bounds; return [f'N{lat:02d}E{lon:03d}' for lat in range(math.floor(miny),math.ceil(maxy)) for lon in range(math.floor(minx),math.ceil(maxx))]
def download_srtm_tiles(destination='data/raw/srtm',tiles=None,timeout=(30,600)):
    import requests
    out=Path(destination); out.mkdir(parents=True,exist_ok=True); tiles=tiles or ['N27E088','N27E089','N28E088','N28E089']; results=[]
    for tile in tiles:
        url=f'https://s3.amazonaws.com/elevation-tiles-prod/skadi/{tile[:3]}/{tile}.hgt.gz'; dest=out/(tile+'.hgt.gz')
        with requests.get(url,stream=True,timeout=timeout) as r:
            r.raise_for_status()
            with dest.open('wb') as f:
                for chunk in r.iter_content(1024*1024): f.write(chunk)
        with gzip.open(dest,'rb') as f: header=f.read(2)
        if header != b'\x00\x00': raise ValueError(f'Invalid SRTM gzip payload: {dest}')
        results.append(dest)
    return results
def hgt_to_geotiff(hgt_gz,destination):
    import rasterio
    from rasterio.transform import from_origin
    p=Path(hgt_gz); tile=p.name[:7]; lat=int(tile[1:3]); lon=int(tile[4:7]); lat0=lat if tile[0]=='N' else -lat; lon0=lon if tile[3]=='E' else -lon
    with gzip.open(p,'rb') as f: raw=f.read()
    n=int(math.sqrt(len(raw)//2)); arr=np.frombuffer(raw,dtype='>i2').reshape(n,n); transform=from_origin(lon0+1,lat0+1,1/(n-1),1/(n-1)); out=Path(destination); out.parent.mkdir(parents=True,exist_ok=True)
    with rasterio.open(out,'w',driver='GTiff',height=n,width=n,count=1,dtype='int16',crs='EPSG:4326',transform=transform,nodata=-32768,compress='deflate') as dst: dst.write(arr,1)
    return out
def mosaic_and_clip(tile_paths,boundary_path,destination='data/processed/sikkim_dem.tif'):
    import geopandas as gpd, rasterio
    from rasterio.mask import mask
    from rasterio.merge import merge
    datasets=[rasterio.open(p) for p in tile_paths]; mosaic,transform=merge(datasets); boundary=gpd.read_file(boundary_path).to_crs(datasets[0].crs); profile=datasets[0].profile.copy(); profile.update(height=mosaic.shape[1],width=mosaic.shape[2],transform=transform)
    temp=Path(destination).with_suffix('.mosaic.tif'); temp.parent.mkdir(parents=True,exist_ok=True)
    with rasterio.open(temp,'w',**profile) as dst: dst.write(mosaic)
    with rasterio.open(temp) as src: clipped,ct=mask(src,boundary.geometry,crop=True,nodata=src.nodata); profile=src.profile.copy(); profile.update(height=clipped.shape[1],width=clipped.shape[2],transform=ct)
    out=Path(destination); 
    with rasterio.open(out,'w',**profile) as dst: dst.write(clipped)
    for d in datasets: d.close()
    return out
