"""A–H figures; all labels describe interventions rather than proven causes."""
from pathlib import Path
import warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.stats import norm
from data import CHANNELS,UNITS,FACTORS,FACTOR_NAMES,factor_values

COLORS=dict(zip(FACTORS,plt.get_cmap('tab10').colors[:8]))
RULES=['none','miss','drop','slip','grasped_no_lift','goal_not_reached_or_not_static','lifted_then_lost_grasp']
RCOLORS=dict(zip(RULES,['#218c74','#c0392b','#d68910','#8e44ad','#2471a3','#707b7c','#b03a2e']))
DISPLAY={'none':'success','grasped_no_lift':'grasped, no lift','goal_not_reached_or_not_static':'goal/static not met'}
plt.rcParams.update({'font.size':9,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':110,'savefig.dpi':135})


def stats(a):
    good=np.isfinite(a);n=good.sum(axis=0);mean=np.nansum(a,axis=0)/np.maximum(n,1)
    sd=np.sqrt(np.nansum(np.where(good,(a-mean)**2,0),axis=0)/np.maximum(n,1))
    mean=np.where(n,mean,np.nan);sd=np.where(n,sd,np.nan)
    return mean,sd,n


def band(ax,x,a,label,color=None):
    if len(a)==0:return
    mean,sd,n=stats(a)
    ax.plot(x,mean,label=label,color=color,lw=1.5)
    ax.fill_between(x,mean-sd,mean+sd,color=color,alpha=.15)


def wilson(success):
    n=len(success)
    if n==0:return np.nan,0,0
    p=np.mean(success);z=1.96;den=1+z*z/n
    center=(p+z*z/(2*n))/den;half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return p,p-(center-half),(center+half)-p


def factor_axis(f,values):
    if f=='shape':return np.arange(len(values)),[str(v) for v in values]
    scale=1000 if f in ('mass','com') else (100 if f in ('size','goal_height') else 1)
    unit=' g' if f=='mass' else (' mm' if f=='com' else (' cm' if scale==100 else ''))
    return np.array(values)*scale,[f'{v*scale:g}{unit}' for v in values]


class Plotter:
    def __init__(self,d,m,out):self.d=d;self.m=m;self.out=Path(out);self.out.mkdir(parents=True,exist_ok=True);self.entries=[]
    def save(self,fig,name,title,note):
        fig.suptitle(title,fontsize=14)
        fig.text(.015,.008,note,fontsize=8,va='bottom',wrap=True)
        fig.tight_layout(rect=(0,.05,1,.95))
        path=self.out/(name+'.png');path.parent.mkdir(parents=True,exist_ok=True)
        fig.savefig(path);plt.close(fig)
        self.entries.append(dict(file=str(path.relative_to(self.out)),title=title,note=note))
        print('plot',name,flush=True)
    def label_channels(self,axes):
        for j,ax in enumerate(np.array(axes).flat):
            ax.set_title(CHANNELS[j].replace('_',' '));ax.set_ylabel(UNITS[j]);ax.axhline(0,c='.7',lw=.6);ax.grid(alpha=.15)
    def stack(self,ax,groups,labels,by='rule',horizontal=False):
        left=np.zeros(len(groups));values=self.d[by]
        for rule in RULES:
            frac=np.array([np.mean(values[g]==rule) if np.any(g) else 0 for g in groups])
            if not np.any(frac):continue
            kwargs=dict(label=DISPLAY.get(rule,rule),color=RCOLORS[rule])
            if horizontal:ax.barh(range(len(groups)),frac,left=left,**kwargs)
            else:ax.bar(range(len(groups)),frac,bottom=left,**kwargs)
            left+=frac
        if horizontal:ax.set_yticks(range(len(groups)),labels);ax.set_xlim(0,1)
        else:ax.set_xticks(range(len(groups)),labels,rotation=35,ha='right');ax.set_ylim(0,1)
        ax.legend(fontsize=8,ncol=2)

    def coverage(self):
        d=self.d;n=len(d['conditions']);rates=np.array([d['success'][d['condition']==i].mean() for i in range(n)])
        fig,ax=plt.subplots(figsize=(13,7));im=ax.imshow(rates.reshape(6,10),vmin=0,vmax=1,cmap='RdYlGn')
        for i,v in enumerate(rates):ax.text(i%10,i//10,f'C{i+1:02d}\n{v:.0%}\nn={(d["condition"]==i).sum()}',ha='center',va='center')
        ax.set_xticks([]);ax.set_yticks([]);fig.colorbar(im,ax=ax,label='Final success fraction')
        self.save(fig,'A01_condition_success','A1 · Success rate per physical condition','10 starts per condition. C01 is nominal. Full settings are in conditions.csv; rates are descriptive, not causal attribution.')
        fig,ax=plt.subplots(figsize=(15,19));groups=[d['condition']==i for i in range(n)]
        self.stack(ax,groups,[f'C{i+1:02d} {d["descriptions"][i]}' for i in range(n)],horizontal=True);ax.invert_yaxis();ax.set_xlabel('Fraction of 10 attempts')
        self.save(fig,'A02_condition_rule_mix','A2 · Rule-label mix per condition','Rule labels describe observed outcomes; zero slip labels do not mean zero transient slip events.')
        seeds=np.unique(d['seed']);matrix=np.array([[d['success'][(d['condition']==i)&(d['seed']==s)][0] for s in seeds] for i in range(n)])
        fig,(ax,bx)=plt.subplots(2,1,figsize=(12,15),gridspec_kw={'height_ratios':[5,1]})
        ax.imshow(matrix,cmap='RdYlGn',vmin=0,vmax=1,aspect='auto');ax.set_yticks(range(n),[f'C{i+1:02d}' for i in range(n)],fontsize=7);ax.set_xticks(range(len(seeds)),seeds);ax.set_ylabel('Physical condition')
        bx.bar(range(len(seeds)),matrix.mean(axis=0),color='#2471a3');bx.set_xticks(range(len(seeds)),seeds);bx.set_ylim(0,1);bx.set_ylabel('Success fraction');bx.set_xlabel('Starting seed (same across conditions)')
        self.save(fig,'A03_start_state_success','A3 · Outcome for every condition × starting state','Top: one success/failure per cell, not an estimated per-cell probability. Bottom: success across all 60 conditions for each start.')

    def variables(self):
        d=self.d;fig,axes=plt.subplots(2,4,figsize=(16,8))
        for f,name,ax in zip(FACTORS,FACTOR_NAMES,axes.flat):
            ids=np.flatnonzero(np.isin(d['single'],[f,'nominal']));levels=sorted(set(d['records'][i]['values'][f] for i in ids));x,ticks=factor_axis(f,levels)
            ss=[d['success'][[i for i in ids if d['records'][i]['values'][f]==v]] for v in levels]
            rates=np.array([wilson(s) for s in ss]);ax.errorbar(x,rates[:,0],yerr=rates[:,1:].T,marker='o',capsize=3,color=COLORS[f]);ax.set_xticks(x,ticks);ax.set_ylim(-.05,1.05);ax.set_title(name);ax.set_ylabel('Success fraction')
        self.save(fig,'B01_single_variable_success','B1 · Single-variable success curves','Nominal plus isolated shifts only; 10 matched seeds per point. Bars: 95% Wilson intervals (descriptive; pairing used in the experiment).')
        fig,axes=plt.subplots(1,3,figsize=(16,5))
        for ax,other in zip(axes,['object_friction','size','goal_height']):
            ix=[i for i,r in enumerate(d['records']) if set(r['active'])<=set(['mass',other])]
            a=sorted(set(d['records'][i]['values']['mass'] for i in ix));b=sorted(set(d['records'][i]['values'][other] for i in ix));mat=np.full((len(a),len(b)),np.nan)
            for j,v in enumerate(a):
                for k,w in enumerate(b):
                    g=[i for i in ix if d['records'][i]['values']['mass']==v and d['records'][i]['values'][other]==w]
                    if g:mat[j,k]=d['success'][g].mean()
                    ax.text(k,j,f'{mat[j,k]:.0%}\nn={len(g)}' if g else 'not sampled',ha='center',va='center',fontsize=8)
            im=ax.imshow(np.ma.masked_invalid(mat),vmin=0,vmax=1,cmap='RdYlGn');ax.set_yticks(range(len(a)),factor_axis('mass',a)[1]);ax.set_xticks(range(len(b)),factor_axis(other,b)[1]);ax.set_xlabel(other);ax.set_ylabel('Mass');ax.set_title('Mass × '+other)
        self.save(fig,'B02_pair_success','B2 · Pair interactions with other variables held nominal','Missing cells stay missing. Mixed episodes with additional changed factors are excluded; no averaging over geometry/COM confounds.')
        fig,axes=plt.subplots(2,3,figsize=(17,9))
        for col,other in enumerate(['object_friction','size','goal_height']):
            for row,direction in enumerate(['together','opposite']):
                ax=axes[row,col];family=f'{direction}:mass+{other}'
                combos=[(i,c) for i,c in enumerate(d['conditions']) if family in c['design_families'] and c['changed_properties']]
                for k,(ci,c) in enumerate(combos):
                    vals=factor_values(c);sets=[]
                    for active in [set(),{'mass'},{other},{'mass',other}]:
                        ids=[j for j,r in enumerate(d['records']) if set(r['active'])==active and all(r['values'][f]==vals[f] for f in active)]
                        sets.append(ids)
                    rates=[np.mean(d['success'][g]) if g else np.nan for g in sets]
                    ax.plot(range(4),rates,'o-',label=f"mass {vals['mass']*1000:g}g; {other}={vals[other]:g}")
                ax.set_xticks(range(4),['nominal','mass only',other+' only','combined'],rotation=20);ax.set_ylim(-.05,1.05);ax.set_title(f'{direction}: mass + {other}');ax.legend(fontsize=7)
        self.save(fig,'B03_direction_combinations','B3 · Do combined changes cancel or compound?','Same 10 seeds per point. Compare combination to each isolated shift; curves are descriptive and do not prove a unique failure cause.')
        fig,ax=plt.subplots(figsize=(13,6));self.stack(ax,[d['single']==f for f in FACTORS],FACTOR_NAMES);ax.set_ylabel('Fraction of isolated-shift episodes')
        self.save(fig,'B04_variable_rule_mix','B4 · Rule labels by changed variable','Single-variable shifts only; successful and failed attempts included. "Cause" here means experimental intervention, not identified mechanism.')

    def traces(self):
        d=self.d;fig,axes=plt.subplots(2,4,figsize=(16,8));js=[2,8,12,13,14,15,16,17]
        for ax,j in zip(axes.flat,js):
            for rule in np.unique(d['rule']):
                ix=np.flatnonzero(d['rule']==rule)
                for i in ix:ax.plot(d['time'],d['raw'][i,:,j],color=RCOLORS.get(rule,'gray'),alpha=.035,lw=.5,rasterized=True)
                ax.plot(d['time'],d['raw'][ix,:,j].mean(axis=0),color=RCOLORS.get(rule,'gray'),label=f'{DISPLAY.get(rule,rule)} n={len(ix)}')
            ax.set_title(CHANNELS[j]);ax.set_xlabel('Time from reset (s)');ax.set_ylabel(UNITS[j])
        axes.flat[0].legend(fontsize=6)
        self.save(fig,'C01_raw_outcome_traces','C1 · Raw measurement traces colored by final rule label','Thin lines: all episodes. Bold lines: outcome-group mean. These groups mix physical conditions; this is an exploratory view.')
        # Overview plus full mean ± SD traces for EVERY condition.
        rms=[]
        for ci in range(len(d['conditions'])):
            ix=np.flatnonzero(d['condition']==ci);a=d['lift_gap'][ix];mean,_,_=stats(a);rms.append(np.sqrt(np.nanmean(mean**2,axis=0)))
        rms=np.array(rms);scaled=rms/np.maximum(np.nanmax(rms,axis=0),1e-12)
        fig,ax=plt.subplots(figsize=(15,13));im=ax.imshow(scaled,aspect='auto',cmap='magma',vmin=0,vmax=1);ax.set_xticks(range(len(CHANNELS)),CHANNELS,rotation=65,ha='right');ax.set_yticks(range(len(rms)),[f'C{i+1:02d}' for i in range(len(rms))],fontsize=7);fig.colorbar(im,ax=ax,label='RMS mean gap / largest condition RMS in channel')
        self.save(fig,'C02_condition_gap_overview','C2 · Condition gap overview; individual trace pages linked below','Derived shifted − same-seed nominal; common nominal-lift clock. Relative/world orientation gaps use rotation vectors, not quaternion subtraction.')
        for ci,c in enumerate(d['conditions']):
            ix=np.flatnonzero(d['condition']==ci);fig,axes=plt.subplots(5,4,figsize=(15,15));self.label_channels(axes)
            for j,ax in enumerate(axes.flat):band(ax,d['lift_time'],d['lift_gap'][ix,:,j],None,'#2471a3');ax.set_xlabel('Seconds from nominal lift')
            self.save(fig,f'C02_conditions/C{ci+1:02d}',f'C2 · C{ci+1:02d}: {d["descriptions"][ci]}','Mean ± 1 SD across available matched seeds. 9/10 have nominal lift; no extrapolation outside observed times. See derived/gaps.npz masks.')
        fig,axes=plt.subplots(5,4,figsize=(15,15));self.label_channels(axes)
        for f in ['mass','object_friction']:
            ix=np.flatnonzero((d['single']==f)&~d['success']);n=sum(np.isfinite(d['records'][i]['nominal_lift_time']) for i in ix)
            for j,ax in enumerate(axes.flat):band(ax,d['lift_time'],d['lift_gap'][ix,:,j],f'{f}: {n}/{len(ix)} aligned failures',COLORS[f]);ax.set_xlabel('Seconds from nominal lift')
        axes.flat[0].legend(fontsize=7)
        self.save(fig,'C03_mass_friction_failures','C3 · Mass failures versus object-friction failures','Isolated interventions and failed episodes only. Mean ± 1 SD; conditioning on failure and nominal lifting changes the represented population.')
        fig,axes=plt.subplots(2,4,figsize=(16,8))
        for f,ax in zip(FACTORS,axes.flat):
            cis=sorted(set(d['condition'][d['single']==f]));colors=plt.get_cmap('viridis')(np.linspace(.2,.85,len(cis)))
            for ci,color in zip(cis,colors):
                ix=np.flatnonzero(d['condition']==ci);band(ax,d['lift_time'],d['lift_gap'][ix,:,2],d['descriptions'][ci],color)
            ax.set_title(f);ax.set_ylabel('Relative Z gap (m)');ax.set_xlabel('Seconds from nominal lift');ax.legend(fontsize=6)
        self.save(fig,'C04_actual_magnitude_traces','C4 · Signature scaling at the magnitudes actually collected','Requested ×0.5/×2/×4 series is unavailable. Mass: ×0.4/×5; object friction: ×0.25/×2.5. Other actual levels shown; mean ± 1 SD.')
        fig,axes=plt.subplots(len(CHANNELS),len(FACTORS),figsize=(22,32),sharex=True)
        for j in range(len(CHANNELS)):
            for k,f in enumerate(FACTORS):
                ax=axes[j,k];ix=np.flatnonzero(d['single']==f);band(ax,d['lift_time'],d['lift_gap'][ix,:,j],None,COLORS[f]);ax.axhline(0,c='.7',lw=.5)
                if j==0:ax.set_title(f)
                if k==0:ax.set_ylabel(CHANNELS[j]+'\n'+UNITS[j])
                if j==len(CHANNELS)-1:ax.set_xlabel('s from nominal lift')
                ax.tick_params(labelsize=6)
        self.save(fig,'C05_channels_by_variables','C5 · Channels × isolated interventions','Mean ± 1 SD; both magnitudes pooled, so opposite signed effects can cancel. Use individual-condition pages to inspect each level.')
        # A predefined, unit-aware effect threshold; not a significance claim.
        thresholds=np.array([.005]*3+[.1]*3+[.005]*3+[.1]*3+[.005,.005,.002,1,1,1,.02,.005])
        onset=np.full((len(CHANNELS),len(FACTORS)),np.nan)
        for k,f in enumerate(FACTORS):
            mean,_,count=stats(d['lift_gap'][d['single']==f]);above=(abs(mean)>thresholds)&(count>=3)
            for j in range(len(CHANNELS)):
                for i in range(len(d['lift_time'])-2):
                    if above[i:i+3,j].all():onset[j,k]=d['lift_time'][i];break
        self.divergence=dict(thresholds=thresholds,onset=onset)
        fig,ax=plt.subplots(figsize=(12,10));im=ax.imshow(np.ma.masked_invalid(onset),aspect='auto',cmap='viridis',vmin=-.25,vmax=4);ax.set_xticks(range(len(FACTORS)),FACTOR_NAMES,rotation=35,ha='right');ax.set_yticks(range(len(CHANNELS)),CHANNELS);fig.colorbar(im,ax=ax,label='First sustained threshold crossing (s from nominal lift)')
        for j in range(len(CHANNELS)):
            for k in range(len(FACTORS)):ax.text(k,j,f'{onset[j,k]:.2f}' if np.isfinite(onset[j,k]) else '—',ha='center',va='center',fontsize=7)
        self.save(fig,'C06_divergence_times','C6 · Exploratory time of divergence','First 3 consecutive samples beyond preset effect thresholds, ≥3 valid runs. Not a statistical alarm; thresholds saved in scores.json. — means not detected.')

    def measurements(self):
        d,m=self.d,self.m;scores=np.array([r['balanced_accuracy'] for r in m['channel_scores']]);order=np.argsort(scores)
        fig,ax=plt.subplots(figsize=(12,9));ax.barh(np.arange(len(CHANNELS)),scores[order],color='#2471a3');ax.set_yticks(range(len(CHANNELS)),np.array(CHANNELS)[order]);ax.axvline(1/len(FACTORS),c='black',ls='--',label='8-class chance');ax.set_xlim(0,1);ax.set_xlabel('5-fold seed-grouped balanced accuracy');ax.legend()
        self.save(fig,'D01_channel_separability','D1 · Separability using one measurement channel at a time','Predicts which variable was shifted, not why an individual attempt failed. All isolated shifts included; scale fitted on training folds only.')
        x=m['features'];flat=x.reshape(len(x),-1);sd=flat.std(axis=0);z=((flat-flat.mean(axis=0))/np.where(sd>1e-10,sd,1)).reshape(x.shape)
        centers=np.array([z[m['labels']==f].mean(axis=0) for f in FACTORS]);within=[];between=[]
        for j in range(len(CHANNELS)):
            within.append(np.sqrt(np.mean(np.concatenate([(z[m['labels']==f,:,j]-centers[k,:,j]).ravel()**2 for k,f in enumerate(FACTORS)]))))
            between.append(np.sqrt(np.mean([(centers[a,:,j]-centers[b,:,j])**2 for a in range(len(FACTORS)) for b in range(a)])))
        fig,ax=plt.subplots(figsize=(13,9));ax.scatter(within,between,color='#2471a3',s=55)
        for rank,j in enumerate(np.argsort(between)):
            ax.annotate(CHANNELS[j],(within[j],between[j]),fontsize=8,xytext=(1.03,.03+.94*rank/(len(CHANNELS)-1)),textcoords='axes fraction',va='center',arrowprops=dict(arrowstyle='-',color='.65',lw=.6))
        ax.set_xlabel('Within-variable RMS spread (standardized)');ax.set_ylabel('Between-variable centroid RMS distance (standardized)')
        self.save(fig,'D02_within_across_spread','D2 · Measurement consistency versus separation','Descriptive full-sample standardization for this plot only. High across-variable separation and low within-variable spread are desirable; scores use held-out seeds.')
        fig,ax=plt.subplots(figsize=(10,6));ts=m['time_scores'];ax.plot([v['time'] for v in ts],[v['result']['balanced_accuracy'] if v['result'] else np.nan for v in ts],'o-')
        for v in ts:ax.annotate(f"n={v['n']}",(v['time'],v['result']['balanced_accuracy']),xytext=(0,8),textcoords='offset points',fontsize=8)
        ax.axhline(1/len(FACTORS),c='gray',ls='--');ax.set_ylim(0,1);ax.set_xlabel('History available after nominal lift (s)');ax.set_ylabel('Seed-grouped balanced accuracy')
        self.save(fig,'D03_separability_over_time','D3 · How early is the intervention identifiable?','Only samples at/before each cutoff are used. Nominal-lift timing is privileged offline alignment; 9 seeds eligible. This is not a deployment latency estimate.')
        means=d['gap'][m['indices']].mean(axis=1);centered=means-means.mean(axis=0);den=np.sqrt((centered**2).sum(axis=0));den=den[:,None]*den[None,:];corr=np.divide(centered.T@centered,den,out=np.full_like(den,np.nan),where=den>1e-12)
        fig,ax=plt.subplots(figsize=(13,11));im=ax.imshow(np.ma.masked_invalid(corr),vmin=-1,vmax=1,cmap='coolwarm');ax.set_xticks(range(len(CHANNELS)),CHANNELS,rotation=65,ha='right');ax.set_yticks(range(len(CHANNELS)),CHANNELS);fig.colorbar(im,ax=ax,label='Pearson r')
        self.save(fig,'D04_channel_correlation','D4 · Correlation between episode-mean gap channels','One point per isolated-shift episode; timesteps are not treated as independent samples. Blank cells indicate constant channels. Shared seeds still induce dependence.')

    def atlas(self):
        d,m=self.d,self.m;xy=m['embedding'];pure=m['indices']
        def marker(r):
            if r['single']=='shape':return 'P'
            return 'v' if np.isfinite(r['magnitude']) and (r['magnitude']<0 if r['single']=='com' else r['magnitude']<1) else '^'
        fig,ax=plt.subplots(figsize=(11,8))
        for f in FACTORS:
            for mark in ['v','^','P']:
                ix=[i for i in pure if d['single'][i]==f and marker(d['records'][i])==mark]
                if ix:ax.scatter(xy[ix,0],xy[ix,1],s=40,color=COLORS[f],marker=mark,alpha=.75)
        ax.legend(handles=[Line2D([0],[0],marker='o',color='w',markerfacecolor=COLORS[f],label=f,markersize=7) for f in FACTORS],fontsize=8)
        ax.set_xlabel(f"PC1 ({m['pca_variance'][0]:.1%} variance)");ax.set_ylabel(f"PC2 ({m['pca_variance'][1]:.1%} variance)")
        self.save(fig,'E01_gap_atlas_intervention','E1 · PCA gap atlas: isolated interventions','Standardized reset-aligned gaps; exploratory fit on singles only. ▼ lower/negative level; ▲ higher/positive level; P sphere. Actual magnitude mapping is in conditions.csv.')
        fig,ax=plt.subplots(figsize=(11,8))
        for rule in np.unique(d['rule'][pure]):
            ix=pure[d['rule'][pure]==rule];ax.scatter(xy[ix,0],xy[ix,1],color=RCOLORS.get(rule,'gray'),alpha=.7,label=DISPLAY.get(rule,rule))
        ax.legend();ax.set_xlabel('PC1 (same embedding)');ax.set_ylabel('PC2 (same embedding)')
        self.save(fig,'E02_gap_atlas_rule','E2 · Exactly the same atlas colored by rule label','A rule label describes an outcome, while the experimental label describes a changed variable. PCA is descriptive and does not prove cluster validity.')
        fig,ax=plt.subplots(figsize=(11,8));ax.scatter(xy[pure,0],xy[pure,1],c='lightgray',s=20,label='single-variable training atlas')
        mix=np.flatnonzero(d['single']=='mixed');counts=np.array([len(d['records'][i]['active']) for i in mix]);sc=ax.scatter(xy[mix,0],xy[mix,1],c=counts,cmap='viridis',marker='x',alpha=.6);fig.colorbar(sc,ax=ax,label='Number of varied factors');ax.legend();ax.set_xlabel('PC1');ax.set_ylabel('PC2')
        self.save(fig,'E03_combinations_projected','E3 · Mixed conditions projected onto the single-variable atlas','Scaler and PCA fitted only on singles; combinations are transformed without refitting. Being between groups is a visual pattern, not evidence of additive causes.')

    def classification(self):
        d,m=self.d,self.m;cm=m['confusion'];fig,ax=plt.subplots(figsize=(11,9));im=ax.imshow(cm,cmap='Blues');ax.set_xticks(range(8),FACTOR_NAMES,rotation=35,ha='right');ax.set_yticks(range(8),FACTOR_NAMES);ax.set_xlabel('Predicted shifted variable');ax.set_ylabel('Actual shifted variable')
        for j in range(8):
            for k in range(8):ax.text(k,j,str(cm[j,k]),ha='center',va='center',color='white' if cm[j,k]>cm.max()/2 else 'black')
        self.save(fig,'F01_intervention_confusion',f"F1 · Selected-channel classification: {m['selected']['accuracy']:.1%} accuracy",'Five best channels ranked using only each training fold; 5-fold grouped by starting seed. Classes are interventions, not proven failure mechanisms.')
        fig,ax=plt.subplots(figsize=(12,7));rules=[r for r in RULES if r in d['rule'][m['indices']]];tab=np.array([[np.sum((d['single']==f)&(d['rule']==r)) for r in rules] for f in FACTORS]);ax.imshow(tab,cmap='Blues');ax.set_xticks(range(len(rules)),[DISPLAY.get(r,r) for r in rules],rotation=30,ha='right');ax.set_yticks(range(8),FACTOR_NAMES)
        for j in range(8):
            for k in range(len(rules)):ax.text(k,j,str(tab[j,k]),ha='center',va='center')
        self.save(fig,'F02_rules_vs_interventions','F2 · Rule label versus changed variable','Counts of isolated-shift episodes. A single outcome such as drop can follow several different interventions; success is included.')
        fig,ax=plt.subplots(figsize=(11,6));ax.plot(range(1,len(CHANNELS)+1),[r['balanced_accuracy'] for r in m['counts']],'o-');ax.axhline(.125,c='gray',ls='--');ax.set_xticks(range(1,len(CHANNELS)+1));ax.set_ylim(0,1);ax.set_xlabel('Number of channels retained');ax.set_ylabel('Seed-grouped balanced accuracy')
        self.save(fig,'F03_accuracy_channel_count','F3 · Accuracy versus measurement count','Channel ranking is recomputed inside each training fold. This curve is exploratory; choosing its best count would require an additional independent test set.')
        fig,axes=plt.subplots(2,4,figsize=(16,8));pred=m['selected']['pred'];ix=m['indices']
        for f,ax in zip(FACTORS,axes.flat):
            cis=sorted(set(d['condition'][d['single']==f]));ticks=[];rates=[];err=[]
            for ci in cis:
                mask=d['condition'][ix]==ci;p,lo,hi=wilson(pred[mask]==f);rates.append(p);err.append((lo,hi));ticks.append(d['descriptions'][ci])
            ax.errorbar(range(len(cis)),rates,yerr=np.array(err).T,fmt='o-',capsize=3,color=COLORS[f]);ax.set_xticks(range(len(cis)),ticks,rotation=20,ha='right',fontsize=7);ax.set_title(f);ax.set_ylim(-.05,1.05);ax.set_ylabel('Correct intervention classification')
        self.save(fig,'F04_accuracy_magnitude','F4 · Held-out classification by actual shift magnitude','Same out-of-fold predictions as F1; 10 starts per condition. Bars: 95% Wilson intervals. No missing magnitudes are invented.')
        c=m['combo'];fig,(ax,bx)=plt.subplots(1,2,figsize=(15,6));xx=np.arange(8);ax.bar(xx-.18,c['precision'],.36,label='precision');ax.bar(xx+.18,c['recall'],.36,label='recall');ax.set_xticks(xx,FACTOR_NAMES,rotation=35,ha='right');ax.set_ylim(0,1);ax.legend();ax.set_title('Detect each changed factor')
        truth=c['target'].sum(axis=1);predicted=c['pred'].sum(axis=1);mat=np.zeros((9,9),int)
        for a,b in zip(truth,predicted):mat[a,b]+=1
        bx.imshow(mat,cmap='Blues');bx.set_xlabel('Number of factors predicted');bx.set_ylabel('Number of factors actually changed');bx.set_xticks(range(9));bx.set_yticks(range(9))
        for a,b in zip(*np.nonzero(mat)):bx.text(b,a,str(mat[a,b]),ha='center',va='center')
        self.save(fig,'F05_single_to_combo',f"F5 · Singles → combinations: exact match {c['exact_match']:.1%}, micro-F1 {c['micro_f1']:.2f}",'8 binary detectors; training uses singles + nominal only. Test combinations have held-out seeds. Threshold 0.5 fixed in advance; combinations are multi-label.')

    def gripper(self):
        d=self.d;fig,(ax,bx)=plt.subplots(1,2,figsize=(17,7));cap=d['raw'][:,:,17].ravel();meas=d['raw'][:,:,15:17].mean(axis=2).ravel()
        hb=ax.hexbin(cap,meas,gridsize=50,bins='log',mincnt=1,cmap='viridis');fig.colorbar(hb,ax=ax,label='log10 sample count');ax.set_xlabel('Commanded per-finger motor cap (N)');ax.set_ylabel('Mean measured compression per finger (N)');ax.set_title('Not a force target-versus-tracking plot')
        fractions=[np.mean([r['motor_ceiling_fraction'] for r in d['records'] if r['condition']==ci]) for ci in range(len(d['conditions']))];bx.bar(range(len(fractions)),fractions);bx.set_xticks(range(0,len(fractions),3),[f'C{i+1:02d}' for i in range(0,len(fractions),3)],rotation=60);bx.set_ylim(0,1);bx.set_ylabel('Fraction of commands at ≥99% normalized strength');bx.set_xlabel('Condition')
        self.save(fig,'G01_cap_vs_force','G1 · Commanded motor limit versus contact force; command-ceiling use','Contact force can exceed a motor cap during impacts. Actual actuator effort/torque saturation is not logged, so true motor-limit hits cannot be established.')
        fig,(ax,bx)=plt.subplots(1,2,figsize=(15,7));finite=0;unknown=0
        for rule in np.unique(d['rule'][~d['success']]):
            ids=[i for i,r in enumerate(d['records']) if not r['success'] and r['rule']==rule and np.isfinite(r['failure_time'])];late=[i for i,r in enumerate(d['records']) if not r['success'] and r['rule']==rule and not np.isfinite(r['failure_time'])]
            for ix,axis,field in [(ids,ax,'failure_time'),(late,bx,'detection_time')]:
                x=[];y=[]
                for i in ix:
                    j=int(np.clip(np.searchsorted(d['time'],d['records'][i][field]),0,len(d['time'])-1));x.append(d['raw'][i,j,14]*1000);y.append(d['raw'][i,j,18])
                if x:axis.scatter(x,y,c=RCOLORS.get(rule,'gray'),s=25,alpha=.5,label=f'{DISPLAY.get(rule,rule)} n={len(x)}')
            finite+=len(ids);unknown+=len(late)
        for axis in (ax,bx):axis.set_xlabel('Finger opening (mm)');axis.set_ylabel('Object-relative Z velocity in moving TCP frame (m/s)');axis.axhline(0,c='gray',lw=.5);axis.legend(fontsize=7)
        ax.set_title(f'Detected event onset (n={finite})');bx.set_title(f'Unknown onset: horizon/detection only (n={unknown})')
        self.save(fig,'G02_failure_opening_velocity','G2 · Gripper opening and relative motion around failure','Two populations kept separate: detected slip/drop onset versus unknown physical onset. Relative velocity is in a moving frame; sag versus slip is not directly labeled.')

    def confounds(self):
        d,m=self.d,self.m;records=d['records'];height=np.array([r['values']['goal_height'] for r in records]);clear=np.array([r['max_clearance'] for r in records]);fig,axes=plt.subplots(1,3,figsize=(17,6))
        for ax,f in zip(axes[:2],['mass','object_friction']):
            v=np.array([r['values'][f] for r in records]);sc=ax.scatter(v,clear,c=height,cmap='viridis',alpha=.35,s=18,vmin=.1,vmax=.3);ax.set_xlabel(f);ax.set_ylabel('Maximum achieved bottom clearance (m)')
        for shape,mark in [('cube','s'),('sphere','o')]:
            mask=np.array([r['values']['shape']==shape for r in records]);axes[2].scatter(height[mask],clear[mask],marker=mark,alpha=.25,label=shape)
        axes[2].plot([.1,.3],[.1,.3],'k--',lw=1);axes[2].set_xlabel('Requested center lift from spawn (m)');axes[2].set_ylabel('Maximum achieved bottom clearance (m)');axes[2].legend();fig.colorbar(sc,ax=axes[1],label='Requested lift (m)',shrink=.7)
        self.save(fig,'H01_lift_demand_properties','H1 · Task demand and achieved lift versus physical properties','All episodes; mixed conditions are confounded. Center lift and bottom clearance differ when geometry rotates. These scatter plots are descriptive, not isolated causal effects.')
        from models import classifier
        from sklearn.model_selection import GroupKFold
        eligible=np.array([r['single']=='mixed' and len(set(r['active'])&{'mass','object_friction'})==1 and bool(set(r['active'])&{'size','shape','com'}) for r in records])
        labels=np.array(['mass' if 'mass' in r['active'] else 'object_friction' for r in records]);pred=np.full(len(records),'',dtype='<U32');xx=d['gap'][:,::5].reshape(len(records),-1)
        for train,test in GroupKFold(5).split(xx,groups=d['seed']):
            tr=train[np.isin(d['single'][train],['mass','object_friction'])];te=test[eligible[test]]
            if len(te):model=classifier();model.fit(xx[tr],d['single'][tr]);pred[te]=model.predict(xx[te])
        fig,(ax,bx)=plt.subplots(1,2,figsize=(15,6));groups=[np.isin(d['single'],['mass','object_friction'])]+[eligible&np.array([f in r['active'] for r in records]) for f in ['size','shape','com']];names=['isolated controls','size also changed','shape also changed','COM also changed']
        rates=[m['dynamic']['accuracy']]+[np.mean(pred[g]==labels[g]) if g.any() else np.nan for g in groups[1:]];ax.bar(range(4),rates,color=['#2471a3','#b7950b','#b7950b','#b7950b']);ax.set_xticks(range(4),names,rotation=25,ha='right');ax.set_ylim(0,1);ax.set_ylabel('Held-out mass-versus-friction accuracy')
        for i,g in enumerate(groups):ax.text(i,.03,f'n={g.sum()}',ha='center')
        for offset,f in [(-.18,'mass'),(.18,'object_friction')]:bx.bar(np.arange(3)+offset,[np.sum(g&(labels==f)) for g in groups[1:]],.36,label=f)
        bx.set_xticks(range(3),names[1:],rotation=25,ha='right');bx.set_ylabel('Test episode count');bx.legend()
        self.geometry_transfer=dict(eligible=int(eligible.sum()),accuracy=float(np.mean(pred[eligible]==labels[eligible])) if eligible.any() else None,
            strata=[dict(name=n,n=int(g.sum())) for n,g in zip(names,groups)])
        self.save(fig,'H02_geometry_dynamic_separability','H2 · Transfer of mass/friction signatures across geometric changes','Train only on isolated mass/friction controls; test held-out-seed mixed episodes with exactly one dynamic shift plus geometry/COM. Other mixed factors may still confound; strata overlap.')
