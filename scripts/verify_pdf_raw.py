"""t5u: verify EVERY cell of the PA 67-county PDF against the RAW DOS files in /workspace/pa/raw (no CSV / summary tables used).
Raw parsing written fresh: ENR JSON walked recursively; DOS VR PDFs read with `pdftotext -raw`.
Recomputation uses exact rational arithmetic; printed values are rounded half-to-even at the printed decimal (Python's format rule);
any value lying exactly on a rounding half is flagged. Cells are extracted from the generated PDF with pdfplumber."""
import json, re, subprocess, pdfplumber
from fractions import Fraction as Fr
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
getcontext().prec=50
RAW='/workspace/pa/raw/'; PDF='/workspace/pa/pdf/Pennsylvania_67_County_Democratic_Registration_and_Vote_Change.pdf'
nk=lambda s: re.sub(r'[^A-Z]','',s.upper())
# ---- votes: walk every candidate record in the ENR county-break files ----
def walk(o,acc):
    if isinstance(o,dict):
        if 'CountyName' in o and 'Votes' in o and 'PartyName' in o:
            d=acc.setdefault(nk(o['CountyName']),{'D':0,'T':0})
            v=int(o['Votes']); d['T']+=v
            if o['PartyName'].strip()=='DEM': d['D']+=v
        else:
            for x in o.values(): walk(x,acc)
    elif isinstance(o,list):
        for x in o: walk(x,acc)
def enr(fn):
    acc={}; walk(json.loads(json.loads(open(RAW+fn).read())),acc); return acc
V={'22':enr('enr_2022G_governor_countybreak.json'),'26':enr('enr_2026G_governor_countybreak.json')}
# ---- registration: DOS VR statistics PDFs ----
def vr(fn):
    out={}
    for line in subprocess.check_output(['pdftotext','-raw',RAW+fn,'-']).decode().splitlines():
        m=re.fullmatch(r'\s*([A-Za-z]+(?: [A-Za-z]+)?)((?:\s+[\d,]+){5,6})\s*',line)
        if m:
            n=[int(x.replace(',','')) for x in m.group(2).split()]
            out[nk(m.group(1))]={'D':n[0],'T':n[-1]}
    return out
R={'22':vr('dos_vr_2022_general_election.pdf'),'26':vr('dos_vr_2026_general_election_certified.pdf')}
DOS_TOTAL={y:R[y].pop('TOTAL') for y in R}
counties=sorted(V['22']); assert len(counties)==67 and sorted(V['26'])==counties==sorted(R['22'])==sorted(R['26'])
# ---- statewide: county sums, checked against DOS statewide figures ----
SW={'RD22':sum(R['22'][c]['D'] for c in counties),'RT22':sum(R['22'][c]['T'] for c in counties),'RD26':sum(R['26'][c]['D'] for c in counties),'RT26':sum(R['26'][c]['T'] for c in counties),
    'D22':sum(V['22'][c]['D'] for c in counties),'T22':sum(V['22'][c]['T'] for c in counties),'D26':sum(V['26'][c]['D'] for c in counties),'T26':sum(V['26'][c]['T'] for c in counties)}
st22=json.loads(json.loads(open(RAW+'enr_2022G_governor_statewide.json').read()))
acc={}; 
def walk2(o):
    if isinstance(o,dict):
        if 'PartyName' in o and 'Votes' in o: acc.setdefault('T',0); acc['T']=acc['T']+int(o['Votes']); acc['D']=acc.get('D',0)+(int(o['Votes']) if o['PartyName'].strip()=='DEM' else 0)
        else: [walk2(x) for x in o.values()]
    elif isinstance(o,list): [walk2(x) for x in o]
walk2(st22)
SW_CHECKS={'RegD22 county sum = DOS 2022 VR Total row':SW['RD22']==DOS_TOTAL['22']['D'],'RegTot22 county sum = DOS 2022 VR Total row':SW['RT22']==DOS_TOTAL['22']['T'],
 'RegD26 county sum = DOS 2026 VR Total row':SW['RD26']==DOS_TOTAL['26']['D'],'RegTot26 county sum = DOS 2026 VR Total row':SW['RT26']==DOS_TOTAL['26']['T'],
 'D22 county sum = DOS 2022 statewide official (GetOfficeData)':SW['D22']==acc['D'],'T22 county sum = DOS 2022 statewide official (GetOfficeData)':SW['T22']==acc['T']}
# ---- expected printed strings ----
half=[]
def rnd(x,dp,tag):
    q=Decimal(x.numerator)/Decimal(x.denominator); e=Decimal(1).scaleb(-dp)
    if (q/e*2)%2==1: half.append(tag)   # exactly on a half -> flag
    return q.quantize(e,rounding=ROUND_HALF_EVEN)
def pct(v,dp,tag,sign=False):
    d=rnd(v,dp,tag); s=f'{d:+.{dp}f}' if sign else f'{d:.{dp}f}'
    return s
num=lambda n:f'{n:,}'; chg=lambda n:f'{n:+,}' if n!=0 else '+0'
def rows(name,rd22,rt22,rd26,rt26,d22,t22,d26,t26):
    sh26=Fr(100*rd26,rt26); sh22=Fr(100*rd22,rt22); s22=Fr(100*d22,t22); s26=Fr(100*d26,t26)
    r1=[pct(sh26,1,name+':share26')+'%',num(rd22),num(rd26),chg(rd26-rd22),pct(Fr(100*(rd26-rd22),rd22),1,name+':regpct',True)+'%',
        num(d22),num(d26),chg(d26-d22),pct(Fr(100*(d26-d22),d22),1,name+':votepct',True)+'%',num(t22),num(t26),chg(t26-t22),pct(Fr(100*(t26-t22),t22),1,name+':ballotpct',True)+'%']
    r2=[pct(s22,1,name+':s22')+'%',pct(s26,1,name+':s26')+'%',pct(s26-s22,2,name+':ds',True),pct(sh22,1,name+':sh22')+'%',num(rt22),pct(sh26,1,name+':sh26')+'%',num(rt26)]
    return r1,r2,sh26
EXP={}
for c in counties:
    EXP[c]=rows(c,R['22'][c]['D'],R['22'][c]['T'],R['26'][c]['D'],R['26'][c]['T'],V['22'][c]['D'],V['22'][c]['T'],V['26'][c]['D'],V['26'][c]['T'])
EXP['STATEWIDETOTAL']=rows('Statewide',SW['RD22'],SW['RT22'],SW['RD26'],SW['RT26'],SW['D22'],SW['T22'],SW['D26'],SW['T26'])
exp_order=sorted(counties,key=lambda c:(-EXP[c][2],c))
# ---- extract cells from the generated PDF with pdfplumber ----
got1={};got2={};order=[];heads=[]
with pdfplumber.open(PDF) as pdf:
    npages=len(pdf.pages)
    for pg in pdf.pages:
        for line in pg.extract_text().splitlines():
            toks=line.split()
            i=0
            while i<len(toks) and re.fullmatch(r'[A-Za-z]+',toks[i]): i+=1
            name=nk(''.join(toks[:i])); cells=toks[i:]
            if not name or not cells or not re.fullmatch(r'[+-]?[\d,.]+%?',cells[0]): continue
            if len(cells)==13: got1[name]=cells; order.append(name)
            elif len(cells)==7: got2[name]=cells
total=0; mism=[]
for k,(r1,r2,_) in EXP.items():
    for sec,exp,got in (('table1',r1,got1.get(k)),('table2',r2,got2.get(k))):
        if got is None: mism.append({'row':k,'table':sec,'problem':'row missing from PDF'}); total+=len(exp); continue
        if len(got)!=len(exp): mism.append({'row':k,'table':sec,'problem':f'{len(got)} cells, expected {len(exp)}'})
        for j,(e,g) in enumerate(zip(exp,got)):
            total+=1
            if e!=g: mism.append({'row':k,'table':sec,'col':j+2,'expected_from_raw':e,'pdf':g})
rep={'check':'PDF cell-by-cell vs RAW DOS files (t5u)','pdf':PDF.split('/')[-1],'pdf_pages':npages,'rows_per_table':{'table1':len(got1),'table2':len(got2)},
 'cells_checked':total,'matches':total-len(mism),'mismatches':mism,'exact_half_rounding_cases':half,
 'county_sort_order_matches_raw':[o for o in order if o!='STATEWIDETOTAL']==exp_order,'statewide_checks':SW_CHECKS,'statewide_sums_from_raw':SW,
 'note_2026_statewide':'DOS statewide 2026 governor endpoint returned no data (2026 UNOFFICIAL, status U); 2026 statewide = sum of 67 DOS county results.',
 'raw_files':['enr_2022G_governor_countybreak.json','enr_2026G_governor_countybreak.json','dos_vr_2022_general_election.pdf','dos_vr_2026_general_election_certified.pdf','enr_2022G_governor_statewide.json'],
 'CLEAN':not mism and all(SW_CHECKS.values()) and not half}
json.dump(rep,open('/workspace/pa/verification/pdf_cell_check_raw.json','w'),indent=1)
print({k:v for k,v in rep.items() if k not in ('mismatches','statewide_sums_from_raw','raw_files')}); print('mismatches:',len(mism)); [print(m) for m in mism[:40]]
