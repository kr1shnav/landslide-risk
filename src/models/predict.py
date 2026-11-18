import joblib
from src.data.preprocessing import FEATURES
def predict(features,model_path='models/random_forest.joblib'):
    return float(joblib.load(model_path).predict_proba(features[FEATURES])[:,1][0])
