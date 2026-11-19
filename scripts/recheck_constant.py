"""Recompute the PA constant directly from the verified table (independent of analysis.py) and compare to pa_results_summary.json."""
import pandas as pd, numpy as np, json
from scipy import stats
t=pd.read_csv('/workspace/pa/data/pa_gov_2022_2026_by_population.csv'); S=json.load(open('/workspace/pa/data/pa_results_summary.json'))
G22=100*t.D22/t.T22-100*t.RegD22/t.RegTot22; G26=100*t.D26/t.T26-100*t.RegD26/t.RegTot26
dG=G26-G22; drop=100*t.RegD22/t.RegTot22-100*t.RegD26/t.RegTot26
def ols(x,y):
    n=len(x); X=np.c_[np.ones(n),x]; b,res,_,_=np.linalg.lstsq(X,y,rcond=None); e=y-X@b; s2=e@e/(n-2)
    cov=s2*np.linalg.inv(X.T@X); se=np.sqrt(np.diag(cov)); tq=stats.t.ppf(.975,n-2)
    return dict(n=n,a=b[0],k=b[1],k_se=se[1],k_ci=[b[1]-tq*se[1],b[1]+tq*se[1]],a_ci=[b[0]-tq*se[0],b[0]+tq*se[0]],r2=1-e@e/((y-y.mean())@(y-y.mean())))
A=ols(drop.values,dG.values)
nar=[d['county'] for d in S['narrowed']]; m=~t.county.isin(nar)
N=ols(drop[m].values,dG[m].values)
REG=pd.read_csv('/workspace/pa/data/pa_analysis_full.csv').set_index('county').region.reindex(t.county).values
regs=sorted(set(REG)); X=np.c_[drop.values,np.array([[r==g for g in regs] for r in REG],float)]
b=np.linalg.lstsq(X,dG.values,rcond=None)[0]
out=dict(all67=A,narrowed=N,common_slope=b[0],intercepts=dict(zip(regs,b[1:])),
  statewide_dG=None)
for k1,k2 in (('all67','const_all'),('narrowed','const_narrowed')):
    for f in ('a','k','r2','k_se'): assert abs(out[k1][f]-S[k2][f])<1e-9,(k1,f)
assert abs(b[0]-S['common_slope_regional']['k'])<1e-9 and all(abs(out['intercepts'][r]-S['common_slope_regional']['intercepts'][r])<1e-9 for r in regs)
pike=t.county.eq('Pike'); out['pike']=dict(drop=float(drop[pike].iloc[0]),dG=float(dG[pike].iloc[0]),expected=float(A['a']+A['k']*drop[pike].iloc[0]))
json.dump(out,open('/workspace/pa/verification/constant_recheck.json','w'),indent=1,default=float)
print(json.dumps(out,indent=1,default=float)); print('MATCHES analysis.py summary: OK')
