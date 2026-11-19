"""Check every PDF table cell against values recomputed independently from the verified CSV (text extracted from the PDF itself)."""
import subprocess, re, json, pandas as pd
P='/workspace/pa/pdf/Pennsylvania_67_County_Democratic_Registration_and_Vote_Change.pdf'
t=pd.read_csv('/workspace/pa/data/pa_gov_2022_2026_by_population.csv')
pages=subprocess.check_output(['pdftotext','-layout',P,'-']).decode().split('\f')
rows1={};rows2={};order=[]
for i,pg in enumerate(pages):
    for line in pg.splitlines():
        m=re.match(r'^\s*([A-Z][a-zA-Z]+(?: total)?)\s+(-?[\d.]+%.*)$',line)
        if not m: continue
        toks=m.group(2).split()
        if len(toks)==13: rows1[m.group(1)]=toks; order.append(m.group(1))
        elif len(toks)==7: rows2[m.group(1)]=toks
def f(v): return f'{v:,}'
def s(v): return ('+' if v>0 else '') + f'{v:,}' if v!=0 else '0'
def p(a,b): x=round(100*(b-a)/a,1); return f'{x:+.1f}%'
exp1={};exp2={}
tot=t[['RegD22','RegD26','RegTot22','RegTot26','D22','D26','T22','T26']].sum()
recs=[(r.county,r) for r in t.itertuples()]+[('Statewide total',tot)]
for name,r in recs:
    g=lambda k: int(getattr(r,k)) if hasattr(r,k) else int(r[k])
    rd22,rd26,rt22,rt26,d22,d26,t22,t26=(g(k) for k in ('RegD22','RegD26','RegTot22','RegTot26','D22','D26','T22','T26'))
    exp1[name]=[f'{100*rd26/rt26:.1f}%',f(rd22),f(rd26),s(rd26-rd22),p(rd22,rd26),f(d22),f(d26),s(d26-d22),p(d22,d26),f(t22),f(t26),s(t26-t22),p(t22,t26)]
    exp2[name]=[f'{100*d22/t22:.1f}%',f'{100*d26/t26:.1f}%',f'{100*d26/t26-100*d22/t22:+.2f}',f'{100*rd22/rt22:.1f}%',f(rt22),f'{100*rd26/rt26:.1f}%',f(rt26)]
cells=0;mm=[]
for E,R in ((exp1,rows1),(exp2,rows2)):
    for k,v in E.items():
        got=R.get(k)
        if got is None: mm.append((k,'missing row')); continue
        for a,b in zip(v,got):
            cells+=1
            if a!=b: mm.append((k,a,b))
co=[c for c in order if c!='Statewide total']
exp_order=list(t.assign(sh=t.RegD26/t.RegTot26).sort_values(['sh','county'],ascending=[False,True]).county)
dos={'RegD22':4046694,'RegTot22':8873144,'RegD26':3887465,'RegTot26':9052695,'D22':3031137,'T22':5366179}  # DOS VR PDF Total rows; DOS 2022 official statewide (GetOfficeData)
import re as _r
sw=json.load(open('/workspace/pa/data/statewide_sums.json'))
res=dict(cells_checked=cells,mismatches=mm,rows_section1=len(rows1),rows_section2=len(rows2),sort_order_ok=co==exp_order,
  statewide_vs_column_sums=all(int(tot[k])==v for k,v in dos.items()),
  statewide_2026_votes_vs_enr_county_sum=dict(D26=int(tot.D26),T26=int(tot.T26),enr=sw['enr_2026']),
  pdf_pages=len([x for x in pages if x.strip()]))
json.dump(res,open('/workspace/pa/verification/pdf_cell_check.json','w'),indent=1,default=str); print(res)
