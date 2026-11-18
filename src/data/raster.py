from pathlib import Path
import numpy as np

def validate_raster(path: str | Path, bounds: tuple[float,float,float,float] | None=None) -> dict:
    import rasterio
    with rasterio.open(path) as src:
        result={'path':str(path),'width':src.width,'height':src.height,'crs':str(src.crs),'resolution':src.res,'nodata':src.nodata,'bounds':tuple(src.bounds),'count':src.count}
        if bounds:
            minx,miny,maxx,maxy=bounds; b=src.bounds
            result['covers_bounds']=b.left<=minx and b.bottom<=miny and b.right>=maxx and b.top>=maxy
        return result

def download_srtm_tiles(destination: str | Path='data/raw/srtm', tiles=('N27E088','N27E089','N28E088','N28E089')):
    import requests
    out=Path(destination); out.mkdir(parents=True,exist_ok=True); results=[]
    for tile in tiles:
        ns=tile[:3]; url=f'https://s3.amazonaws.com/elevation-tiles-prod/skadi/{ns}/{tile}.hgt.gz'; dest=out/(tile+'.hgt.gz')
        with requests.get(url,stream=True,timeout=(30,300)) as r:
            r.raise_for_status()
            with dest.open('wb') as f:
                for chunk in r.iter_content(1024*1024): f.write(chunk)
        results.append(dest)
    return results
