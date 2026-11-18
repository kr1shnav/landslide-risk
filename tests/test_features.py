from src.data.preprocessing import demo_features,FEATURES,remove_duplicates
def test_demo_schema():
    d=demo_features(10); assert set(FEATURES).issubset(d.columns); assert len(d)==10

def test_duplicate_removal_preserves_first_record():
    import pandas as pd
    d=pd.DataFrame({'latitude':[27.5,27.5,27.6],'longitude':[88.5,88.5,88.6],'label':[1,1,0]})
    cleaned=remove_duplicates(d)
    assert len(cleaned)==2
    assert cleaned.attrs['duplicates_removed']==1
    assert cleaned.iloc[0]['label']==1
