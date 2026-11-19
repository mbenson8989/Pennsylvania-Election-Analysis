"""VERIFICATION PASS 2 - second independent re-parse of the raw DOS files, written separately from pass 1 and build_table.py.
ENR: regex over the raw (double-encoded) response text, no json module. VR PDFs: `pdftotext -raw` + regex.
Census: csv module. Derived figures recomputed with decimal arithmetic at 40 digits.
Also: statewide county-sum vs DOS 'Total' rows, ENR vote-method component check, and cross-source comparison of
2022 ENR vs DOS bulk precinct returns file and 2022 VR PDF vs DOS bulk precinct VR file (informational)."""
import re, csv, subprocess, json, decimal
from decimal import Decimal as Dm
decimal.getcontext().prec=40
RAW='/workspace/pa/raw/'
K=lambda s: re.sub('[^A-Z]','',s.upper())
def enr_text(fn):
    t=open(RAW+fn,encoding='utf-8').read().replace('\\"','"')
    out={}; comp_bad=[]
    for m in re.finditer(r'\{"ID":"[^"]*","ElectionYear":"\d+","CountyName":"([^"]+)","PartyName":"([^"]*)","CandidateName":"([^"]*)","Votes":"(\d+)".*?"ElectionDayVotes":"(\d+)".*?"MailInVotes":"(\d+)".*?"ProvisionalVotes":"(\d+)"',t):
        c,p,n,vv,ed,mi,pr=m.groups(); c=K(c); vv,ed,mi,pr=map(int,(vv,ed,mi,pr))
        d=out.setdefault(c,{'D':0,'R':0,'O':0,'n':0}); d['D' if p=='DEM' else 'R' if p=='REP' else 'O']+=vv; d['n']+=1
        if ed+mi+pr!=vv: comp_bad.append((c,p,vv,ed,mi,pr))
    return out,comp_bad
def vr_raw(fn):
    t=subprocess.check_output(['pdftotext','-raw',RAW+fn,'-']).decode()
    out={}; total=None
    for line in t.splitlines():
        m=re.fullmatch(r'([A-Za-z][A-Za-z ]+?) ((?:\d{1,3}(?:,\d{3})*\s*){5,6})',line.strip())
        if m:
            n=[int(x.replace(',','')) for x in m.group(2).split()]
            if m.group(1)=='Total': total=n
            else: out[K(m.group(1))]=n
    return out,total
E={},{}
e22,cb22=enr_text('enr_2022G_governor_countybreak.json'); e26,cb26=enr_text('enr_2026G_governor_countybreak.json')
v22,t22=vr_raw('dos_vr_2022_general_election.pdf'); v26,t26=vr_raw('dos_vr_2026_general_election_certified.pdf')
pop={K(r['CTYNAME'][:-7]):int(r['POPESTIMATE2025']) for r in csv.DictReader(open(RAW+'census_co-est2025-alldata.csv',encoding='latin-1')) if r['STATE']=='42' and r['COUNTY']!='000'}
tab=list(csv.DictReader(open('/workspace/pa/data/pa_gov_2022_2026_by_population.csv')))
mism=[]; n=0
def chk(c,f,exp,got):
    global n; n+=1
    if exp is None:
        if got!='': mism.append((c,f,'blank',got)); return
    elif isinstance(exp,bool):
        if str(exp)!=got: mism.append((c,f,exp,got))
    elif isinstance(exp,int):
        if str(exp)!=got: mism.append((c,f,exp,got))
    else:
        if abs(exp-Dm(got))>Dm('1e-9'): mism.append((c,f,str(exp),got))
for r in tab:
    c=K(r['county']); chk(c,'population_2025',pop[c],r['population_2025'])
    S={};R={};T={}
    for y,e,v in (('22',e22,v22),('26',e26,v26)):
        D,Rv,O=e[c]['D'],e[c]['R'],e[c]['O']; T[y]=D+Rv+O; reg=v[c]
        for f,x in (('D',D),('R',Rv),('O',O),('T',T[y]),('RegD',reg[0]),('RegR',reg[1]),('RegTot',reg[-1]),('DR',D+Rv)): chk(c,f+y,x,r[f+y])
        S[y]=Dm(100)*D/T[y]; R[y]=Dm(100)*reg[0]/reg[-1]
        chk(c,'S'+y,S[y],r['S'+y]); chk(c,'Rsh'+y,R[y],r['Rsh'+y]); chk(c,'G'+y,S[y]-R[y],r['G'+y])
    dG=(S['26']-R['26'])-(S['22']-R['22']); drop=R['22']-R['26']; fell=v26[c][0]<v22[c][0]
    for f,x in (('dS',S['26']-S['22']),('dR',R['26']-R['22']),('dG',dG),('reg_share_drop',drop),('dem_reg_fell',fell),
                ('residual',dG-drop if fell else None),('implied_offset_votes',(dG-drop)*T['26']/100 if fell else None),
                ('gap_votes',e26[c]['D']-Dm(e22[c]['D'])*v26[c][0]/v22[c][0])): chk(c,f,x,r[f])
# ---- statewide / structural checks ----
SW=[]
def sw(item,a,b): SW.append({'item':item,'expected':a,'got':b,'ok':a==b})
sw('VR 2022 county sum (D,R,Total) vs DOS Total row',[t22[0],t22[1],t22[-1]],[sum(v[0] for v in v22.values()),sum(v[1] for v in v22.values()),sum(v[-1] for v in v22.values())])
sw('VR 2026 county sum (D,R,Total) vs DOS Total row',[t26[0],t26[1],t26[-1]],[sum(v[0] for v in v26.values()),sum(v[1] for v in v26.values()),sum(v[-1] for v in v26.values())])
el=open(RAW+'enr_elections_list.json').read().replace('\\"','"')
m=re.search(r'"Electionid":117,"ElectionType":"G".*?"ElectionStatus":"(\w)".*?"RegisteredVotes":(\d+),"BallotsCounted":(\d+)',el)
st26,reg26_enr,ball26=m.group(1),int(m.group(2)),int(m.group(3))
m=re.search(r'"Electionid":94,"ElectionType":"G".*?"ElectionStatus":"(\w)".*?"RegisteredVotes":(\d+),"BallotsCounted":(\d+)',el)
st22,reg22_enr,ball22=m.group(1),int(m.group(2)),int(m.group(3))
sw('ENR 2026 GetElectionList RegisteredVotes vs DOS 2026 VR PDF Total',reg26_enr,t26[-1])
INFO={'enr_status_2022':st22,'enr_status_2026':st26,'enr_ballots_counted_2026_statewide':ball26,'enr_ballots_counted_2022_statewide':ball22,
 'enr_registered_2022_statewide':reg22_enr,'vr_pdf_2022_total':t22[-1],
 'statewide_2026_DplusR':sum(e26[c]['D']+e26[c]['R'] for c in e26),'statewide_2026_race_total':sum(sum(list(e26[c].values())[:3]) for c in e26),
 'vote_method_component_mismatches_2022':cb22,'vote_method_component_mismatches_2026':cb26,
 'candidate_rows':{'2022':sum(e22[c]['n'] for c in e22),'2026':sum(e26[c]['n'] for c in e26)}}
# ---- cross-source (informational): DOS bulk precinct files for 2022 ----
codes={}
bulk={}
for row in csv.reader(open(RAW+'dos_er_2022_general_precinct.txt',encoding='latin-1')):
    if row[8]=='GOV':
        b=bulk.setdefault(int(row[2]),{'D':0,'R':0,'O':0}); b['D' if row[9]=='DEM' else 'R' if row[9]=='REP' else 'O']+=int(row[15])
# county codes are alphabetical 1..67 per DOS readme
alpha=sorted(e22)
xs=[]
for i,c in enumerate(alpha,1):
    for k in 'DRO':
        if bulk[i][k]!=e22[c][k]: xs.append({'county':c,'field':k,'ENR_official':e22[c][k],'bulk_precinct_file':bulk[i][k],'diff':e22[c][k]-bulk[i][k]})
vrb={}
for row in csv.reader(open(RAW+'dos_vr_2022_general_precinct.txt',encoding='latin-1')):
    cc=int(row[2])
    if cc==0: continue
    b=vrb.setdefault(cc,[0,0,0]); vals=[int(row[i]) for i in (6,9,12,15,18,21)]; b[0]+=vals[0]; b[1]+=vals[1]; b[2]+=sum(vals)
xv=[]
for i,c in enumerate(alpha,1):
    a=v22[c]; b=vrb[i]
    if [a[0],a[1],a[-1]]!=b: xv.append({'county':c,'VR_pdf':[a[0],a[1],a[-1]],'bulk_precinct_VR':b})
rep={'pass':2,'counties':len(tab),'figures_checked':n,'matches':n-len(mism),'mismatches':mism,'statewide_checks':SW,'info':INFO,
     'cross_source_2022_ENR_vs_bulk_precinct_returns':xs,'cross_source_2022_VRpdf_vs_bulk_precinct_VR':xv}
json.dump(rep,open('/workspace/pa/verification/pass2_report.json','w'),indent=1,default=str)
print('pass2',len(tab),'counties; figures',n,'matches',n-len(mism),'mismatches',len(mism))
for s in SW: print(s)
print({k:v for k,v in INFO.items() if 'component' not in k}, 'component mismatches', len(cb22), len(cb26))
print('xsrc returns diffs',len(xs),'counties',len({x["county"] for x in xs})); [print(x) for x in xs[:40]]
print('xsrc VR diffs',len(xv)); [print(x) for x in xv[:10]]
