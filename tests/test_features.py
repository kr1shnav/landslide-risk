from src.data.preprocessing import demo_features,FEATURES
def test_demo_schema():
    d=demo_features(10); assert set(FEATURES).issubset(d.columns); assert len(d)==10
