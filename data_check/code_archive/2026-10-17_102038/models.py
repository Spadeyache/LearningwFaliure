"""Seed-grouped out-of-fold diagnostics. Training-only scaling and feature ranking."""
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from data import CHANNELS,FACTORS


def classifier():
    return make_pipeline(StandardScaler(),LogisticRegression(C=1.,max_iter=3000,class_weight='balanced',random_state=0))


def channel_rank(x,y):
    # x is episode x sampled-time x channel. Rank on the TRAINING fold only.
    mean=x.mean(axis=0);between=np.zeros_like(mean);within=np.zeros_like(mean)
    for label in np.unique(y):
        z=x[y==label];between+=len(z)*(z.mean(axis=0)-mean)**2
        within+=((z-z.mean(axis=0))**2).sum(axis=0)
    ratio=between/(within+1e-12)
    return np.argsort(-np.mean(ratio,axis=0))


def predict_cv(x,y,seeds,channels=None,top=None):
    if len(np.unique(seeds))<5 or len(np.unique(y))<2:
        return None
    pred=np.empty(len(y),dtype=y.dtype);folds=[];selected=[]
    for train,test in GroupKFold(5).split(x,y,seeds):
        if set(y[test])-set(y[train]):return None
        use=channel_rank(x[train],y[train])[:top] if top else (np.arange(x.shape[2]) if channels is None else np.array(channels))
        model=classifier();model.fit(x[train][:,:,use].reshape(len(train),-1),y[train])
        pred[test]=model.predict(x[test][:,:,use].reshape(len(test),-1))
        folds.append(dict(train_seeds=np.unique(seeds[train]).tolist(),test_seeds=np.unique(seeds[test]).tolist(),
                          accuracy=float(accuracy_score(y[test],pred[test]))))
        selected.append([CHANNELS[i] for i in use])
    return dict(pred=pred,accuracy=float(accuracy_score(y,pred)),balanced_accuracy=float(balanced_accuracy_score(y,pred)),
                folds=folds,selected_channels=selected)


def analyze(d):
    pure=np.flatnonzero(np.isin(d['single'],FACTORS)); labels=d['single'][pure]; seeds=d['seed'][pure]
    x=d['gap'][pure][:,::5,:]
    if not np.isfinite(x).all():raise ValueError('Classification requires complete reset-aligned gap windows')
    out={'indices':pure,'labels':labels,'groups':seeds,'features':x}
    out['channel_scores']=[predict_cv(x,labels,seeds,channels=[j]) for j in range(len(CHANNELS))]
    out['all']=predict_cv(x,labels,seeds)
    out['selected']=predict_cv(x,labels,seeds,top=5)
    out['counts']=[predict_cv(x,labels,seeds,top=k) for k in range(1,len(CHANNELS)+1)]
    out['classes']=np.array(FACTORS)
    out['confusion']=confusion_matrix(labels,out['selected']['pred'],labels=FACTORS)
    # Geometry-focused diagnostic uses paired mass/friction SINGLE-variable controls.
    dynamic=np.flatnonzero(np.isin(d['single'],['mass','object_friction']))
    out['dynamic']=predict_cv(d['gap'][dynamic][:,::5],d['single'][dynamic],d['seed'][dynamic])
    out['dynamic_indices']=dynamic
    failure=dynamic[~d['success'][dynamic]]
    out['dynamic_failures']=predict_cv(d['gap'][failure][:,::5],d['single'][failure],d['seed'][failure])
    # Causal history windows on the diagnostic nominal-lift clock. Missing
    # nominal lifts are excluded and explicitly counted, never substituted.
    finite=np.array([np.isfinite(r['nominal_lift_time']) for r in d['records']])
    eligible=pure[finite[pure]]
    time_scores=[]
    for end in [0,.25,.5,1,1.5,2,3]:
        use=(d['lift_time']>=0)&(d['lift_time']<=end+1e-8)
        if not use.any():use[np.argmin(abs(d['lift_time']))]=True
        xx=d['lift_gap'][eligible][:,use,:][:,::2,:]
        valid=np.isfinite(xx).all(axis=(1,2));ix=eligible[valid]
        result=predict_cv(xx[valid],d['single'][ix],d['seed'][ix])
        time_scores.append(dict(time=end,n=len(ix),result=result))
    out['time_scores']=time_scores
    # PCA is an exploratory fit on singles only; combos are out-of-fit projections.
    scale=StandardScaler().fit(x.reshape(len(x),-1));pca=PCA(n_components=2,svd_solver='full')
    pca.fit(scale.transform(x.reshape(len(x),-1)))
    out['embedding']=pca.transform(scale.transform(d['gap'][:,::5,:].reshape(len(d['records']),-1)))
    out['pca_variance']=pca.explained_variance_ratio_
    # Independent binary membership detectors trained ONLY on singles + nominal.
    # Held-out-seed combinations are genuinely never in training.
    y=np.array([[f in r['active'] for f in FACTORS] for r in d['records']],int)
    combo=np.flatnonzero(d['single']=='mixed');prob=np.full((len(d['records']),len(FACTORS)),np.nan)
    feats=d['gap'][:,::5,:].reshape(len(d['records']),-1)
    for train,test in GroupKFold(5).split(feats,y,d['seed']):
        tr=train[d['single'][train]!='mixed'];te=test[d['single'][test]=='mixed']
        for j in range(len(FACTORS)):
            if len(np.unique(y[tr,j]))<2:continue
            model=classifier();model.fit(feats[tr],y[tr,j]);prob[te,j]=model.predict_proba(feats[te])[:,1]
    predicted=(prob[combo]>=.5).astype(int)
    precision,recall,f1,support=precision_recall_fscore_support(y[combo],predicted,average=None,zero_division=0)
    out['combo']=dict(indices=combo,prob=prob[combo],target=y[combo],pred=predicted,
        exact_match=float(np.mean((predicted==y[combo]).all(axis=1))),
        micro_f1=float(f1_score(y[combo],predicted,average='micro',zero_division=0)),
        macro_f1=float(f1_score(y[combo],predicted,average='macro',zero_division=0)),
        precision=precision,recall=recall,f1=f1,support=support)
    return out
