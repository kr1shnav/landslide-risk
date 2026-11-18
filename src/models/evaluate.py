from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,confusion_matrix
def metrics(y,p,prob=None):
    out={'accuracy':accuracy_score(y,p),'precision':precision_score(y,p,zero_division=0),'recall':recall_score(y,p,zero_division=0),'f1':f1_score(y,p,zero_division=0),'confusion_matrix':confusion_matrix(y,p).tolist()}
    if prob is not None and len(set(y))>1: out['roc_auc']=roc_auc_score(y,prob)
    return out
