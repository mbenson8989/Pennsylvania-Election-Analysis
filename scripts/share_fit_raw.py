"""t6u: SHARE version S = m*(D/100) + b, independent computation straight from the RAW DOS files.
S = surplus (points) = Dem governor votes / governor-race total *100 - D;  D = Dem registration share (%, 0-100).
Closed-form OLS with exact rationals; compared against analysis.py (statsmodels on the verified CSV)."""
import json, re, subprocess
from fractions import Fraction as Fr
RAW='/workspace/pa/raw/'; nk=lambda s: re.sub('[^A-Z]','',s.upper())
def enr(fn):
    acc={}
    def w(o):
        if isinstance(o,dict):
            if {'CountyName','Votes','PartyName'}<=o.keys():
                d=acc.setdefault(nk(o['CountyName']),[0,0]); v=int(o['Votes']); d[1]+=v; d[0]+=v if o['PartyName'].strip()=='DEM' else 0
            else: [w(x) for x in o.values()]
        elif isinstance(o,list): [w(x) for x in o]
    w(json.loads(json.loads(open(RAW+fn).read()))); return acc
def vr(fn):
    out={}
    for l in subprocess.check_output(['pdftotext','-raw',RAW+fn,'-']).decode().splitlines():
        m=re.fullmatch(r'\s*([A-Za-z]+(?: [A-Za-z]+)?)((?:\s+[\d,]+){5,6})\s*',l)
        if m and m.group(1)!='Total': n=[int(x.replace(',','')) for x in m.group(2).split()]; out[nk(m.group(1))]=(n[0],n[-1])
    return out
OUT={}
S_=json.load(open('/workspace/pa/data/pa_results_summary.json'))
for y,ef,vf,key in (('2022','enr_2022G_governor_countybreak.json','dos_vr_2022_general_election.pdf','fwd_2022'),('2026','enr_2026G_governor_countybreak.json','dos_vr_2026_general_election_certified.pdf','fwd_2026')):
    E=enr(ef); V=vr(vf); cs=sorted(E); assert len(cs)==67 and sorted(V)==cs
    D={c:Fr(100*V[c][0],V[c][1]) for c in cs}; S={c:Fr(100*E[c][0],E[c][1])-D[c] for c in cs}
    x={c:D[c]/100 for c in cs}; n=67; mx=sum(x.values())/n; my=sum(S.values())/n
    m=sum((x[c]-mx)*(S[c]-my) for c in cs)/sum((x[c]-mx)**2 for c in cs); b=my-m*mx
    res={c:S[c]-(m*x[c]+b) for c in cs}
    sst=sum((S[c]-my)**2 for c in cs); r2=1-sum(r*r for r in res.values())/sst
    mae=sum(abs(r) for r in res.values())/n; cmax=max(cs,key=lambda c:abs(res[c]))
    ref=S_[key]
    OUT[y]=dict(m=float(m),b=float(b),r2=float(r2),mean_abs_resid=float(mae),max_resid_county=cmax.title().replace('Mckean','McKean'),max_resid=float(res[cmax]),
        within_2pts=sum(abs(r)<=2 for r in res.values()),within_5pts=sum(abs(r)<=5 for r in res.values()),
        mean_S=float(my),statsmodels_m=ref['k'],statsmodels_b=ref['a'],statsmodels_r2=ref['r2'],
        agree=abs(float(m)-ref['k'])<1e-9 and abs(float(b)-ref['a'])<1e-9 and abs(float(r2)-ref['r2'])<1e-9,
        resid={c.title().replace('Mckean','McKean'):float(r) for c,r in res.items()})
json.dump(OUT,open('/workspace/pa/verification/share_fit_check.json','w'),indent=1)
for y,o in OUT.items(): print(y,{k:v for k,v in o.items() if k!='resid'})
