import json
from pathlib import Path
import pandas as pd
from src.data.boundary import validate_geojson,extract_sikkim_boundary
from src.data.inventory import filter_to_boundary

def test_boundary_validation_and_extraction(tmp_path):
    p=tmp_path/'india.geojson'; data={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'shapeName':'Sikkim'},'geometry':{'type':'Polygon','coordinates':[[[88,27],[89,27],[89,28],[88,28],[88,27]]]}}]}; p.write_text(json.dumps(data))
    assert validate_geojson(p)['features']==1
    out=extract_sikkim_boundary(p,tmp_path/'sikkim.geojson'); assert validate_geojson(out)['crs']=='EPSG:4326'

def test_inventory_clipping():
    b=Path('data/processed/sikkim_boundary.geojson')
    if not b.exists(): return
    df=filter_to_boundary(pd.DataFrame({'latitude':[27.53,30.0],'longitude':[88.5,88.5],'source_id':['a','b']}),b)
    assert list(df.source_id)==['a']
