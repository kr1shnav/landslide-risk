import pytest
from src.models.predict import feature_row,validate_prediction_inputs

def valid(): return {'latitude':27.53,'longitude':88.5,'elevation':1800,'slope':25,'aspect':180,'rainfall_1d':20,'rainfall_3d':45,'rainfall_7d':100}
def test_prediction_feature_row(): assert feature_row(valid()).shape==(1,13)
@pytest.mark.parametrize('key,value',[('slope',91),('aspect',361),('elevation',-1),('latitude',30)])
def test_prediction_validation(key,value):
    values=valid(); values[key]=value
    with pytest.raises(ValueError): validate_prediction_inputs(values)
