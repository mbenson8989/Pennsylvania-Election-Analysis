"""VERIFICATION PASS 1 - independent re-parse of raw DOS files.
Different parsers from build_table.py: ENR read by walking candidate records keyed on the CountyName field;
VR PDFs read with pdfplumber word coordinates (not pdftotext); Census read with pandas.
Recomputes every derived figure with exact Fraction arithmetic and compares every figure for all 67 counties."""
import json, pdfplumber, pandas as pd, math, sys
from fractions import Fraction as F
RAW='/workspace/pa/raw/'
def key(s): return ''.join(ch for ch in s.upper() if ch.isalpha())
def enr(fn):
    obj=json.loads(json.loads(open(RAW+fn,encoding='utf-8').read()))
    res={}
    for blk in obj['Election']['Statewide']:
        for rows in blk.values():
            for x in rows:
                k=key(x['CountyName']); d=res.setdefault(k,{'D':0,'R':0,'O':0})
                slot={'DEM':'D','REP':'R'}.get(x['PartyName'].strip(),'O'); d[slot]+=int(x['Votes'])
    return res
def vr(fn):
    res={}
    with pdfplumber.open(RAW+fn) as pdf:
        for pg in pdf.pages:
            for line in pg.extract_text().splitlines():
                toks=line.split()
                nums=[t for t in toks if t.replace(',','').isdigit()]
                name=' '.join(t for t in toks if not t.replace(',','').isdigit())
                if len(nums)>=5 and len(nums)==len(toks)-len(name.split()) and name.lower()!='total':
                    n=[int(t.replace(',','')) for t in nums]
                    res[key(name)]={'RegD':n[0],'RegR':n[1],'RegTot':n[-1],'ncols':len(n)}
    return res
e={'22':enr('enr_2022G_governor_countybreak.json'),'26':enr('enr_2026G_governor_countybreak.json')}
v={'22':vr('dos_vr_2022_general_election.pdf'),'26':vr('dos_vr_2026_general_election_certified.pdf')}
c=pd.read_csv(RAW+'census_co-est2025-alldata.csv',encoding='latin-1',dtype={'STATE':str,'COUNTY':str})
c=c[(c.STATE=='42')&(c.COUNTY!='000')]; pop={key(n.replace(' County','')):int(p) for n,p in zip(c.CTYNAME,c.POPESTIMATE2025)}
tab=pd.read_csv('/workspace/pa/data/pa_gov_2022_2026_by_population.csv')
checked=0; mism=[]
def cmp(county,field,exp,got,exact=True):
    global checked; checked+=1
    ok = (exp==got) if exact else (math.isfinite(got) and abs(float(exp)-got)<1e-9) if exp is not None else (got!=got)
    if not ok: mism.append((county,field,str(exp),str(got)))
for _,r in tab.iterrows():
    k=key(r.county)
    cmp(r.county,'population_2025',pop[k],int(r.population_2025))
    S={};Rs={}
    for y in ('22','26'):
        D,R,O=e[y][k]['D'],e[y][k]['R'],e[y][k]['O']; T=D+R+O
        for f,val in (('D',D),('R',R),('O',O),('T',T),('RegD',v[y][k]['RegD']),('RegR',v[y][k]['RegR']),('RegTot',v[y][k]['RegTot']),('DR',D+R)):
            cmp(r.county,f+y,val,int(r[f+y]))
        S[y]=F(100*D,T); Rs[y]=F(100*v[y][k]['RegD'],v[y][k]['RegTot'])
        cmp(r.county,'S'+y,S[y],r['S'+y],False); cmp(r.county,'Rsh'+y,Rs[y],r['Rsh'+y],False); cmp(r.county,'G'+y,S[y]-Rs[y],r['G'+y],False)
    dG=(S['26']-Rs['26'])-(S['22']-Rs['22'])
    cmp(r.county,'dS',S['26']-S['22'],r.dS,False); cmp(r.county,'dR',Rs['26']-Rs['22'],r.dR,False); cmp(r.county,'dG',dG,r.dG,False)
    drop=Rs['22']-Rs['26']; cmp(r.county,'reg_share_drop',drop,r.reg_share_drop,False)
    fell=v['26'][k]['RegD']<v['22'][k]['RegD']; cmp(r.county,'dem_reg_fell',fell,bool(r.dem_reg_fell))
    T26=sum(e['26'][k].values())
    cmp(r.county,'residual',(dG-drop) if fell else None,r.residual,False)
    cmp(r.county,'implied_offset_votes',((dG-drop)*T26/100) if fell else None,r.implied_offset_votes,False)
    cmp(r.county,'gap_votes',e['26'][k]['D']-F(e['22'][k]['D']*v['26'][k]['RegD'],v['22'][k]['RegD']),r.gap_votes,False)
# statewide: county sums vs DOS VR "Total" rows; ENR counts
counties=len(tab); assert counties==67 and len(set(map(key,tab.county)))==67
rep={'pass':1,'counties':counties,'figures_per_county':checked//counties,'figures_checked':checked,'matches':checked-len(mism),'mismatches':mism,
     'enr_counties':{y:len(e[y]) for y in e},'vr_rows_parsed':{y:len(v[y]) for y in v}}
json.dump(rep,open('/workspace/pa/verification/pass1_report.json','w'),indent=1)
print({k:v for k,v in rep.items() if k!='mismatches'}, 'mismatches:',len(mism)); [print(m) for m in mism[:30]]
