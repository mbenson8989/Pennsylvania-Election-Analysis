"""Build the PA analysis table from raw DOS files (Pass 0 = the table that gets published).
Sources (all under /workspace/pa/raw, see SOURCES.tsv):
  ENR county break JSON (electionreturns.pa.gov) for 2022 (official, electionid 94) and 2026 (UNOFFICIAL, electionid 117) Governor
  DOS Voter Registration Statistics PDFs: Nov 8 2022 Election; Nov 3 2026 General Election (certified)
  Census Vintage 2025 county estimates (sort order only)
"""
import json, re, subprocess, csv
import pandas as pd, numpy as np
RAW='/workspace/pa/raw/'; OUT='/workspace/pa/data/'
def norm(c): return re.sub(r'\s+',' ',c.strip().upper()).replace('MC KEAN','MCKEAN')

def enr(fn):
    d=json.loads(json.load(open(RAW+fn)))
    out={}
    for blk in d['Election']['Statewide']:
        for c,rows in blk.items():
            r={'D':0,'R':0,'O':0}
            for x in rows:
                p=x['PartyName']; v=int(x['Votes'])
                r['D' if p=='DEM' else 'R' if p=='REP' else 'O']+=v
            r['T']=r['D']+r['R']+r['O']; out[norm(c)]=r
    return out

def vr(fn, ncols):
    txt=subprocess.run(['pdftotext','-layout',RAW+fn,'-'],capture_output=True,text=True).stdout
    out={}
    for line in txt.splitlines():
        m=re.match(r'^\s*([A-Za-z][A-Za-z ]*?)\s{2,}([\d,]+(?:\s+[\d,]+)+)\s*$',line)
        if not m: continue
        nums=[int(x.replace(',','')) for x in m.group(2).split()]
        if len(nums)!=ncols: continue
        name=norm(m.group(1))
        out[name]={'RegD':nums[0],'RegR':nums[1],'RegTot':nums[-1]}
    return out

e22=enr('enr_2022G_governor_countybreak.json'); e26=enr('enr_2026G_governor_countybreak.json')
v22=vr('dos_vr_2022_general_election.pdf',6); v26=vr('dos_vr_2026_general_election_certified.pdf',5)
tot22=v22.pop('TOTAL'); tot26=v26.pop('TOTAL')
pop={}
for r in csv.DictReader(open(RAW+'census_co-est2025-alldata.csv',encoding='latin-1')):
    if r['STATE']=='42' and r['COUNTY']!='000': pop[norm(r['CTYNAME'].replace(' County',''))]=int(r['POPESTIMATE2025'])
names=sorted(e22); assert len(names)==67 and sorted(e26)==names==sorted(v22)==sorted(v26)==sorted(pop), (len(names),set(names)^set(v26))
rows=[]
for c in names:
    r={'county':c.title().replace('Mckean','McKean'),'population_2025':pop[c]}
    for y,e,v in (('22',e22,v22),('26',e26,v26)):
        for k in 'DROT': r[f'{k}{y}']=e[c][k]
        for k in ('RegD','RegR','RegTot'): r[f'{k}{y}']=v[c][k]
    rows.append(r)
t=pd.DataFrame(rows).sort_values('population_2025',ascending=False).reset_index(drop=True)
# ---- Locked equation ----
for y in ('22','26'):
    t['S'+y]=100*t['D'+y]/t['T'+y]            # Dem votes / governor-race total (stand-in for ballots cast)
    t['Rsh'+y]=100*t['RegD'+y]/t['RegTot'+y]  # Dem registration share
    t['G'+y]=t['S'+y]-t['Rsh'+y]
t['dS']=t.S26-t.S22; t['dR']=t.Rsh26-t.Rsh22; t['dG']=t.G26-t.G22
t['reg_share_drop']=t.Rsh22-t.Rsh26
t['dem_reg_fell']=t.RegD26<t.RegD22
t['residual']=np.where(t.dem_reg_fell, t.dG-t.reg_share_drop, np.nan)           # = dS for loss counties
t['implied_offset_votes']=np.where(t.dem_reg_fell, t.residual*t.T26/100, np.nan)
t['gap_votes']=t.D26-t.D22*(t.RegD26/t.RegD22)                                   # NE "gap in votes"
t['DR22']=t.D22+t.R22; t['DR26']=t.D26+t.R26
t.to_csv(OUT+'pa_gov_2022_2026_by_population.csv',index=False)
st={'enr_2022':{k:int(t[k+'22'].sum()) for k in 'DROT'},'enr_2026':{k:int(t[k+'26'].sum()) for k in 'DROT'},
    'vr_2022_total_row':tot22,'vr_2022_county_sum':{k:int(t[k+'22'].sum()) for k in ('RegD','RegR','RegTot')},
    'vr_2026_total_row':tot26,'vr_2026_county_sum':{k:int(t[k+'26'].sum()) for k in ('RegD','RegR','RegTot')}}
json.dump(st,open(OUT+'statewide_sums.json','w'),indent=1); print(json.dumps(st,indent=1))
print(t[['county','population_2025','D22','T22','D26','T26','RegD22','RegTot22','RegD26','RegTot26','dG']].head(8).to_string())
