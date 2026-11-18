import joblib
import pandas as pd
from src.data.preprocessing import FEATURES
from src.data.preprocessing import demo_features

def validate_prediction_inputs(values):
    required=['latitude','longitude','elevation','slope','aspect','rainfall_1d','rainfall_3d','rainfall_7d']
    missing=[k for k in required if k not in values or values[k] is None]
    if missing: raise ValueError('Missing inputs: '+', '.join(missing))
    if not 27.0 <= float(values['latitude']) <= 28.3: raise ValueError('Latitude is outside the Sikkim input range')
    if not 87.8 <= float(values['longitude']) <= 89.1: raise ValueError('Longitude is outside the Sikkim input range')
    if not 0 <= float(values['slope']) <= 90: raise ValueError('Slope must be between 0 and 90 degrees')
    if not 0 <= float(values['aspect']) <= 360: raise ValueError('Aspect must be between 0 and 360 degrees')
    for k in ['elevation','rainfall_1d','rainfall_3d','rainfall_7d']:
        if float(values[k]) < 0: raise ValueError(f'{k} cannot be negative')
    return True

def feature_row(values):
    validate_prediction_inputs(values)
    row={f:0.0 for f in FEATURES}; row.update({k:float(values[k]) for k in ['elevation','slope','aspect','rainfall_1d','rainfall_3d','rainfall_7d']})
    row.update({'curvature':0.0,'twi':0.0,'landcover':float(values.get('landcover',0)),'soil':float(values.get('soil',0)),'distance_river':float(values.get('distance_river',0)),'distance_road':float(values.get('distance_road',0)),'ndvi':float(values.get('ndvi',0))})
    return pd.DataFrame([row])

def predict(features,model_path='models/random_forest.joblib'):
    return float(joblib.load(model_path).predict_proba(features[FEATURES])[:,1][0])
