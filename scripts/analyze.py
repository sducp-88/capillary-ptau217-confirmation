"""Frozen-plan secondary analysis. Run with Python 3.12 and the supplied requirements; never modifies source inputs."""
from pathlib import Path
import sys, json, hashlib, math, platform, shutil
ROOT=Path(__file__).resolve().parents[1]
import numpy as np
import pandas as pd
import scipy
from scipy.stats import binom, beta
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

SEED=20261008; REPEATS=200
for sub in ['results','data','evidence/source','figures','qa']:(ROOT/sub).mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,obj):
 (ROOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False,default=lambda x:x.item() if isinstance(x,np.generic) else str(x)),encoding='utf-8')
def finite(v): return float(v) if np.isfinite(v) else ('-inf' if v<0 else 'inf')
src=ROOT/'evidence/source/T030_41591_2025_4080_MOESM3_ESM.xlsx'
local=src
manifest=[{'name':src.name,'path':str(src),'sha256':'4b1f5983b8548d4f4f5edc08f4b541358ade1d624d0d1d8aaaf44535e89f092b'}]
assert sha(src)==manifest[0]['sha256'], 'Source workbook checksum differs'
save('evidence/source/source_manifest_verified.json',manifest)

d=pd.read_excel(local,sheet_name='Extended Data Figure 3')
assert list(d)==['cap_ptau217','plasma_ptau217','status_csf_ab42ptau']
assert len(d)==176 and d.notna().all().all() and not d.duplicated().any()
y=d.status_csf_ab42ptau.to_numpy(int); x=d.cap_ptau217.to_numpy(float); p=d.plasma_ptau217.to_numpy(float)
assert y.sum()==99 and set(y)=={0,1}
d.insert(0,'source_excel_row',np.arange(len(d))+2)
d.to_csv(ROOT/'data/public_paired_source_rows.csv',index=False)

def empirical(x,y,target=.90):
 u=np.unique(x); c=np.r_[np.nextafter(u[0],-np.inf),(u[1:]+u[:-1])/2,np.nextafter(u[-1],np.inf)]
 se=(x[y==1,None]>=c).mean(0); sp=(x[y==0,None]<c).mean(0)
 return float(c[se>=target-1e-12].max()),float(c[sp>=target-1e-12].min()),{}

def rank_n(n,error,delta):
 rr=np.arange(1,n+1); keep=rr[binom.cdf(rr-1,n,error)<=delta]
 return int(keep.max()) if len(keep) else 0

def assured(x,y,target=.90,delta=.025):
 err=1-target; pos=np.sort(x[y==1]); neg=np.sort(x[y==0]); rp=rank_n(len(pos),err,delta); rn=rank_n(len(neg),err,delta)
 lo=float(pos[rp-1]) if rp else -np.inf
 hi=float(np.nextafter(neg[len(neg)-rn],np.inf)) if rn else np.inf
 return lo,hi,{'positive_rank':rp,'negative_upper_tail_rank':rn,'positive_failure_bound':float(binom.cdf(rp-1,len(pos),err)) if rp else 0.,'negative_failure_bound':float(binom.cdf(rn-1,len(neg),err)) if rn else 0.,'error_tolerance':err,'tail_delta':delta}

def decisions(x,lo,hi):
 if lo>=hi:return np.where(x<(lo+hi)/2,0,2)
 return np.where(x<lo,0,np.where(x>=hi,2,1))

def metrics(y,z):
 n=len(y); n1=int(y.sum()); n0=n-n1; counts=np.array([[(z[y==c]==k).sum() for k in range(3)] for c in [0,1]])
 tn,g0,fp=map(int,counts[0]); fn,g1,tp=map(int,counts[1]); nn=tn+fn; ng=g0+g1; np_=fp+tp
 return dict(n=n,csf_positive=n1,csf_negative=n0,negative_n=nn,gray_n=ng,positive_n=np_,tn=tn,fn=fn,fp=fp,tp=tp,gray_csf_negative=g0,gray_csf_positive=g1,
  fn_rate=fn/n1,fp_rate=fp/n0,sensitivity_lower=1-fn/n1,specificity_lower=tn/n0,specificity_upper=1-fp/n0,sensitivity_upper=tp/n1,
  gray_fraction=ng/n,triage_confirmation_fraction=1-nn/n,residual_error_fraction=(fn+fp)/n,triage_residual_error_fraction=fn/n,
  npv=tn/nn if nn else None,ppv=tp/np_ if np_ else None,definitive_accuracy=(tn+tp)/(nn+np_) if nn+np_ else None)
def cp(k,n,confidence=.95):
 a=(1-confidence)/2
 return [float(beta.ppf(a,k,n-k+1)) if k else 0.,float(beta.ppf(1-a,k+1,n-k)) if k<n else 1.]

RULES={
 'empirical90':lambda a,b:empirical(a,b,.90),
 'assured90':lambda a,b:assured(a,b,.90,.025),
 'empirical95':lambda a,b:empirical(a,b,.95),
 'assured95':lambda a,b:assured(a,b,.95,.025),
 'marginal90':lambda a,b:assured(a,b,.90,.05),
}
full={}; row=d.copy(); pf=np.where(p>.42,2,0)
row['plasma_fixed042_decision']=pf
for name,func in {'published':lambda a,b:(.01,.02,{}),**RULES}.items():
 lo,hi,extra=func(x,y); z=decisions(x,lo,hi)
 m=metrics(y,z); m.update(lower=finite(lo),upper=finite(hi),overlap=bool(lo>=hi),**extra)
 if name=='published':m['descriptive_exact_intervals']={k:cp(v,den) for k,v,den in [('fn_rate',m['fn'],99),('fp_rate',m['fp'],77),('gray_fraction',m['gray_n'],176),('npv',m['tn'],m['negative_n']),('ppv',m['tp'],m['positive_n'])]}
 full[name]=m; row[name+'_decision']=z
row.to_csv(ROOT/'results/full_sample_row_decisions.csv',index=False)

paired={}
for name in ['published','empirical90','assured90']:
 z=row[name+'_decision'].to_numpy(); opposite=np.abs(z-pf)==2
 wrongc=((z==0)&(y==1))|((z==2)&(y==0)); wrongp=(pf==2)!=y
 paired[name]={'matrix_csf_negative':pd.crosstab(pd.Series(z[y==0]),pd.Series(pf[y==0])).reindex(index=[0,1,2],columns=[0,2],fill_value=0).values.tolist(),
 'matrix_csf_positive':pd.crosstab(pd.Series(z[y==1]),pd.Series(pf[y==1])).reindex(index=[0,1,2],columns=[0,2],fill_value=0).values.tolist(),
 'three_class_different':int((z!=pf).sum()),'gray_structure_only':int((z==1).sum()),'definite_opposite':int(opposite.sum()),
 'opposite_capillary_wrong_plasma_matches_csf':int((opposite&wrongc).sum()),'opposite_plasma_wrong_capillary_matches_csf':int((opposite&wrongp).sum()),
 'shared_definitive_errors':int((wrongc&wrongp).sum()),'plasma_fn':int(((pf==0)&(y==1)).sum()),'plasma_fp':int(((pf==2)&(y==0)).sum())}

allmetrics=[]; cuts=[]; assignments=[]; predsum={k:np.zeros((len(y),3),int) for k in RULES}
for rep in range(REPEATS):
 folds=list(StratifiedKFold(n_splits=5,shuffle=True,random_state=SEED+rep).split(x,y))
 zall={k:np.full(len(y),-1,int) for k in RULES}
 for fold,(tr,te) in enumerate(folds):
  for ix in te: assignments.append((rep,fold,int(ix+2)))
  assert not set(tr)&set(te)
  for name,func in RULES.items():
   lo,hi,extra=func(x[tr],y[tr]);z=decisions(x[te],lo,hi);zall[name][te]=z
   for c in range(3):predsum[name][te,c]+=(z==c)
   cuts.append(dict(repeat=rep,fold=fold,rule=name,train_n=len(tr),test_n=len(te),train_positive=int(y[tr].sum()),train_negative=int((y[tr]==0).sum()),lower=finite(lo),upper=finite(hi),overlap=bool(lo>=hi),**extra))
 for name,z in zall.items():
  assert (z>=0).all()
  m=metrics(y,z);m.update(repeat=rep,rule=name,paired_definite_opposite_fraction=float((np.abs(z-pf)==2).mean()));allmetrics.append(m)
cv=pd.DataFrame(allmetrics);cv.to_csv(ROOT/'results/crossfit_repeat_metrics.csv',index=False)
pd.DataFrame(cuts).to_csv(ROOT/'results/crossfit_cutoffs.csv',index=False)
pd.DataFrame(assignments,columns=['repeat','fold','source_excel_row']).to_csv(ROOT/'results/crossfit_fold_assignments.csv',index=False)
probs=pd.DataFrame({'source_excel_row':d.source_excel_row,'csf_reference':y})
for name,arr in predsum.items():
 assert np.all(arr.sum(axis=1)==REPEATS)
 for c,lab in enumerate(['negative','gray','positive']):probs[name+'_'+lab+'_probability']=arr[:,c]/REPEATS
 probs[name+'_modal_probability']=arr.max(1)/REPEATS
probs.to_csv(ROOT/'results/row_crossfit_decision_frequencies.csv',index=False)
report_metrics=['fn','fp','gray_n','fn_rate','fp_rate','sensitivity_lower','specificity_lower','gray_fraction','triage_confirmation_fraction','residual_error_fraction','triage_residual_error_fraction','npv','ppv','paired_definite_opposite_fraction']
def numeric_or_none(v):return float(v) if pd.notna(v) else None
cvs={name:{col:{'mean':numeric_or_none(g[col].mean()),'split_p2_5':numeric_or_none(g[col].quantile(.025)),'split_p97_5':numeric_or_none(g[col].quantile(.975))} for col in report_metrics} for name,g in cv.groupby('rule')}
prevalence=[]
for name,m in full.items():
 for pi in [.10,.30,.50,.5625]:
  fn=pi*m['fn_rate'];fp=(1-pi)*m['fp_rate'];gray=pi*m['gray_csf_positive']/99+(1-pi)*m['gray_csf_negative']/77
  negative=pi*m['fn_rate']+(1-pi)*m['tn']/77;positive=1-negative-gray
  prevalence.append(dict(rule=name,prevalence=pi,gray_confirmation=gray,triage_confirmation=1-negative,fn_population=fn,fp_population=fp,
    negative_residual_risk=fn/negative if negative else None,positive_residual_risk=fp/positive if positive else None))
pd.DataFrame(prevalence).to_csv(ROOT/'results/prevalence_sensitivity.csv',index=False)

checks=[]
for n in [61,62,77,79,80,99]:
 for err in [.10,.05]:
  r=rank_n(n,err,.025)
  if r:
   fail=float(binom.cdf(r-1,n,err)); independent=float(1-beta.cdf(err,r,n-r+1))
   assert abs(fail-independent)<1e-12
   assert fail<=.025 and (r==n or binom.cdf(r,n,err)>.025)
  else:fail=0.;independent=0.
  checks.append(dict(n=n,error=err,rank=r,failure_probability_binomial=fail,failure_probability_beta=independent))
boundary={}
for lop in ['lt','le']:
 for hop in ['ge','gt']:
  neg=x<.01 if lop=='lt' else x<=.01;pos=x>=.02 if hop=='ge' else x>.02
  z=np.where(neg,0,np.where(pos,2,1));boundary[lop+'_'+hop]=metrics(y,z)
save('results/boundary_sensitivity.json',boundary)
assert full['published']['gray_n']==53 and full['published']['fn']==9 and full['published']['fp']==8
assert full['empirical90']['gray_n']==54 and paired['empirical90']['definite_opposite']==11
assert paired['empirical90']['three_class_different']==65
assert all(sha(z['path'])==z['sha256'] for z in manifest)
summary={'analysis_date':'2026-10-08','seed':SEED,'repeats':REPEATS,'folds':5,'n':176,'csf_positive':99,'csf_negative':77,'source_sha256':sha(src),'plan_sha256':sha(ROOT/'protocol/ANALYSIS_PLAN_v1.md'),
 'auc_reproduction':{'capillary':roc_auc_score(y,x),'plasma':roc_auc_score(y,p)},'full_sample':full,'paired_descriptive':paired,'crossfit':cvs,
 'minimum_zero_error_n_per_class_97_5_confidence':{str(err):math.ceil(math.log(.025)/math.log(1-err)) for err in [.10,.05]},
 'interval_label':'Crossfit percentile ranges describe split variability, not population confidence intervals or external validation.'}
save('results/summary_v1.json',summary)
save('qa/numerical_checks.json',{'source_hashes_unchanged':True,'expected_reproduction_counts':True,'fold_leakage_checks':True,'every_row_once_per_repeat':True,'tolerance_beta_binomial_crosscheck':checks})
save('runtime_environment.json',{'python':sys.executable,'python_version':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'scipy':scipy.__version__,'scikit_learn':__import__('sklearn').__version__,'openpyxl':__import__('openpyxl').__version__,'seed':SEED})
print(json.dumps({'full_sample':full,'paired_descriptive':paired,'crossfit_means':{k:{m:round(v['mean'],5) if v['mean'] is not None else None for m,v in z.items()} for k,z in cvs.items()}},indent=2))
