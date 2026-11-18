"""Terrain derivatives calculated in projected metres, not lon/lat degrees."""
from pathlib import Path
import numpy as np
def terrain_derivatives(dem,resolution=(1,1)):
    gy,gx=np.gradient(dem,*resolution); return {'slope':np.degrees(np.arctan(np.hypot(gx,gy))),'aspect':(np.degrees(np.arctan2(-gx,gy))+360)%360,'curvature':np.gradient(gx,axis=1)+np.gradient(gy,axis=0)}
def twi(slope,flow_accumulation): return np.log((flow_accumulation+1)/np.maximum(np.tan(np.radians(slope)),1e-6))
def terrain_ruggedness_index(dem):
    a=np.asarray(dem,dtype=float); valid=np.isfinite(a); filled=np.where(valid,a,np.nanmedian(a)); p=np.pad(filled,1,mode='edge'); diffs=[p[i:i+a.shape[0],j:j+a.shape[1]]-filled for i in range(3) for j in range(3) if (i,j)!=(1,1)]; out=np.sqrt(np.mean(np.square(diffs),axis=0)); return np.where(valid,out,np.nan)
def extract_terrain_features(dem_path,output_dir='data/features'):
    import rasterio
    from rasterio.warp import calculate_default_transform,reproject,Resampling
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    with rasterio.open(dem_path) as src:
        if src.crs is None: raise ValueError('DEM has no CRS')
        target='EPSG:32645'; transform, w, h=calculate_default_transform(src.crs,target,src.width,src.height,*src.bounds); profile=src.profile.copy(); profile.update(crs=target,transform=transform,width=w,height=h,nodata=-9999)
        dem=np.full((h,w),np.nan,dtype='float32'); reproject(source=rasterio.band(src,1),destination=dem,src_transform=src.transform,src_crs=src.crs,dst_transform=transform,dst_crs=target,resampling=Resampling.bilinear,dst_nodata=np.nan)
    feats=terrain_derivatives(dem,(abs(transform.e),abs(transform.a))); feats['tri']=terrain_ruggedness_index(dem); paths={}
    for name,array in feats.items():
        path=out/f'{name}.tif'; data=np.where(np.isfinite(array),array,-9999).astype('float32'); prof=profile.copy(); prof.update(dtype='float32',count=1,compress='deflate')
        with rasterio.open(path,'w',**prof) as dst: dst.write(data,1)
        paths[name]=path
    return paths
