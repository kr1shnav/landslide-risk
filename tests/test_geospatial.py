import json
from pathlib import Path
import pandas as pd
from src.data.boundary import validate_geojson,extract_sikkim_boundary
from src.data.inventory import filter_to_boundary
from src.features.terrain import terrain_derivatives,terrain_ruggedness_index

def test_boundary_validation_and_extraction(tmp_path):
    p=tmp_path/'india.geojson'; data={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'shapeName':'Sikkim'},'geometry':{'type':'Polygon','coordinates':[[[88,27],[89,27],[89,28],[88,28],[88,27]]]}}]}; p.write_text(json.dumps(data))
    assert validate_geojson(p)['features']==1
    out=extract_sikkim_boundary(p,tmp_path/'sikkim.geojson'); assert validate_geojson(out)['crs']=='EPSG:4326'

def test_inventory_clipping():
    b=Path('data/processed/sikkim_boundary.geojson')
    if not b.exists(): return
    df=filter_to_boundary(pd.DataFrame({'latitude':[27.53,30.0],'longitude':[88.5,88.5],'source_id':['a','b']}),b)
    assert list(df.source_id)==['a']

def test_slope_and_aspect_calculation():
    dem=[[0,1,2],[0,1,2],[0,1,2]]
    out=terrain_derivatives(dem,(1,1))
    assert out['slope'].shape==(3,3)
    assert (out['slope']>0).all()
    assert ((out['aspect']>=0)&(out['aspect']<=360)).all()

def test_tri_shape_and_nodata_safe():
    import numpy as np
    tri=terrain_ruggedness_index(np.array([[1.,2.,3.],[2.,np.nan,4.],[3.,4.,5.]]))
    assert tri.shape==(3,3)
