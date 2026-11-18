import argparse,json
from pathlib import Path
import joblib
from sklearn.model_selection import train_test_split,GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
try:
    from xgboost import XGBClassifier
except ImportError:
    XGBClassifier=None
from src.data.preprocessing import FEATURES,demo_features,load_inventory
from src.models.evaluate import metrics
def train(inventory=None,out='models'):
    df=load_inventory(inventory) if inventory else demo_features(); missing=[x for x in FEATURES if x not in df]
    if missing: raise ValueError('Missing feature columns: '+', '.join(missing))
    y=df['label'].astype(int); X=df[FEATURES]
    if {'latitude','longitude'} <= set(df.columns):
        groups=(df['latitude'].round(1).astype(str)+'_'+df['longitude'].round(1).astype(str)).to_numpy(); train_idx,test_idx=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=42).split(X,y,groups)); a,b,c,d=X.iloc[train_idx],X.iloc[test_idx],y.iloc[train_idx],y.iloc[test_idx]
    else: a,b,c,d=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
    models={'logistic_regression':make_pipeline(SimpleImputer(),StandardScaler(),LogisticRegression(max_iter=1000,class_weight='balanced',random_state=42)),'random_forest':make_pipeline(SimpleImputer(),RandomForestClassifier(n_estimators=150,random_state=42,class_weight='balanced'))}
    if XGBClassifier is not None: models['xgboost']=make_pipeline(SimpleImputer(),XGBClassifier(n_estimators=100,max_depth=4,learning_rate=.08,eval_metric='logloss',random_state=42,scale_pos_weight=max(1,(y==0).sum()/max((y==1).sum(),1))))
    Path(out).mkdir(exist_ok=True); result={}
    for name,m in models.items():
        m.fit(a,c); pred=m.predict(b); result[name]=metrics(d,pred,m.predict_proba(b)[:,1]); joblib.dump(m,Path(out)/(name+'.joblib'))
    Path('reports').mkdir(exist_ok=True); Path('reports/model_metrics.json').write_text(json.dumps({'mode':'DEMONSTRATION' if inventory is None else 'REAL_INVENTORY','models':result},indent=2)); return result
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--inventory'); args=p.parse_args(); print(json.dumps(train(args.inventory),indent=2))
