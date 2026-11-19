"""Pennsylvania 67-county PDF modeled on Nebraska_93_County_Democratic_Registration_and_Vote_Change.pdf.
Uses ONLY the verified table pa_gov_2022_2026_by_population.csv."""
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
OUT='/workspace/pa/pdf/Pennsylvania_67_County_Democratic_Registration_and_Vote_Change.pdf'
t=pd.read_csv('/workspace/pa/data/pa_gov_2022_2026_by_population.csv')
t['share26']=100*t.RegD26/t.RegTot26
t=t.sort_values(['share26','county'],ascending=[False,True]).reset_index(drop=True)
num=lambda v:f'{int(v):,}'; chg=lambda v:f'{int(v):+,}'; pct=lambda a,b:f'{100*(b-a)/a:+.1f}%'; sh=lambda v:f'{v:.1f}%'
def row1(name,r):
    return [name,sh(100*r['RegD26']/r['RegTot26']),num(r['RegD22']),num(r['RegD26']),chg(r['RegD26']-r['RegD22']),pct(r['RegD22'],r['RegD26']),
            num(r['D22']),num(r['D26']),chg(r['D26']-r['D22']),pct(r['D22'],r['D26']),num(r['T22']),num(r['T26']),chg(r['T26']-r['T22']),pct(r['T22'],r['T26'])]
def row2(name,r):
    s22=100*r['D22']/r['T22']; s26=100*r['D26']/r['T26']
    return [name,sh(s22),sh(s26),f'{s26-s22:+.2f}',sh(100*r['RegD22']/r['RegTot22']),num(r['RegTot22']),sh(100*r['RegD26']/r['RegTot26']),num(r['RegTot26'])]
tot={k:int(t[k].sum()) for k in ('RegD22','RegD26','RegTot22','RegTot26','D22','D26','T22','T26')}
rose=t.RegD26>t.RegD22; fell=t.D26<t.D22
TITLE1='Pennsylvania 67 Counties — Democratic Registration, Democratic Governor Votes and Total Ballots, 2022 vs 2026*'
TITLE2='Democratic Governor Votes as a Share of Total Ballots, and Democratic Share of Registration, 2022 vs 2026*'
SORT=('Sorted by 2026 Democratic share of registration (Democratic registered voters ÷ all registered voters, DOS statistics for the Nov 3, 2026 General Election), highest first. '
      f'{t.county[0]} leads by share and by raw Democratic registration.')
NOTE=('*2026 figures are UNOFFICIAL: the Pennsylvania Department of State (DOS) results site (electionreturns.pa.gov) lists the Nov 3, 2026 General Election with status "U" (unofficial), checked 19 Nov 2026 5:01 PM CST; not certified. '
      '2022 votes and ballots: DOS official (certified) 2022 General Election returns. Registration: DOS Voter Registration Statistics for the Nov 8, 2022 Election and the Nov 3, 2026 General Election (certified). '
      '<b>Total ballots = governor-race total</b> (all governor candidates on the DOS returns; DOS reports no governor write-ins), because DOS publishes no county-level total ballots cast for either election. '
      'Votes are votes for the Democratic governor candidate (Shapiro both years), not a count of registered Democrats who voted.')
NOTE2='Share of ballots = Democratic governor votes ÷ total ballots (governor-race total). Share of registration = Democratic registered voters ÷ all registered voters. Change (pts) = 2026 share minus 2022 share, in percentage points.'
st=ParagraphStyle('t',fontName='Helvetica-Bold',fontSize=12.5,leading=15); it=ParagraphStyle('i',fontName='Helvetica-Oblique',fontSize=7.2,leading=8.8)
sm=ParagraphStyle('s',fontName='Helvetica-Oblique',fontSize=6.6,leading=8)
hs=ParagraphStyle('h',fontName='Helvetica-Bold',fontSize=6.6,leading=7.8,alignment=1,textColor=colors.white)
HEAD=colors.HexColor('#1F4E79'); BLUE=colors.HexColor('#DDEBF7'); ORANGE=colors.HexColor('#FCE4D6'); BOTH=colors.HexColor('#E2D9F3'); GREY=colors.HexColor('#F2F2F2')
H1=['County','Dem Reg Share 2026 %','Dem Reg 2022<br/>(Nov 8)','Dem Reg 2026<br/>(Nov 3)','Reg Change #','Reg Change %','Dem Gov Votes 2022','Dem Gov Votes 2026*','Vote Change #','Vote Change % (on 2022 base)','Total Ballots 2022','Total Ballots 2026*','Ballot Change #','Ballot Change %']
H2=['County','Dem Share of Ballots 2022 %','Dem Share of Ballots 2026* %','Change (pts)','Dem Share of Registration 2022 %','Total Registered 2022<br/>(Nov 8)','Dem Share of Registration 2026 %','Total Registered 2026<br/>(Nov 3)']
def table(head,rows,widths,shade):
    data=[[Paragraph(h,hs) for h in head]]+rows
    tb=Table(data,colWidths=widths,repeatRows=1)
    sty=[('BACKGROUND',(0,0),(-1,0),HEAD),('FONT',(0,1),(-1,-1),'Helvetica',7),('ALIGN',(1,1),(-1,-1),'RIGHT'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
         ('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#BFBFBF')),('TOPPADDING',(0,1),(-1,-1),1.2),('BOTTOMPADDING',(0,1),(-1,-1),1.2),
         ('FONT',(0,-1),(-1,-1),'Helvetica-Bold',7),('BACKGROUND',(0,-1),(-1,-1),GREY),('LINEABOVE',(0,-1),(-1,-1),1,colors.black)]
    for i,c in enumerate(shade,1):
        if c is not None: sty.append(('BACKGROUND',(0,i),(-1,i),c))
    tb.setStyle(TableStyle(sty)); return tb
shade=[BOTH if a and b else BLUE if a else ORANGE if b else None for a,b in zip(rose,fell)]
leg_rows=[['Legend:', 'Democratic registration rose ('+', '.join(t.county[rose&~fell])+')','Democratic governor votes fell ('+str(int((fell&~rose).sum()))+' counties)','Both ('+', '.join(t.county[rose&fell])+')']]
leg=Table(leg_rows,colWidths=[0.6*inch,3.2*inch,2.5*inch,1.6*inch]); leg.setStyle(TableStyle([('FONT',(0,0),(-1,-1),'Helvetica',6.8),('FONT',(0,0),(0,0),'Helvetica-Bold',6.8),
    ('BACKGROUND',(1,0),(1,0),BLUE),('BACKGROUND',(2,0),(2,0),ORANGE),('BACKGROUND',(3,0),(3,0),BOTH),('BOX',(1,0),(-1,0),0.25,colors.grey),('INNERGRID',(1,0),(-1,0),0.25,colors.grey)]))
R1=[row1(r.county,r) for _,r in t.iterrows()]+[row1('Statewide total',tot)]
R2=[row2(r.county,r) for _,r in t.iterrows()]+[row2('Statewide total',tot)]
W1=[1.05*inch]+[0.635*inch]*13; W2=[1.3*inch]+[1.05*inch]*7
def foot(c,d):
    c.saveState(); c.setFont('Helvetica-Oblique',7); c.drawString(0.45*inch,0.3*inch,'*2026 figures UNOFFICIAL (PA DOS status "U"), not certified. Total ballots = governor-race total. Source: PA Department of State.')
    c.drawRightString(10.55*inch,0.3*inch,f'Page {d.page} of {{NP}}'); c.restoreState()
class Doc(SimpleDocTemplate): pass
story=[Paragraph(TITLE1,st),Paragraph(SORT,it),Spacer(1,3),Paragraph(NOTE,sm),Spacer(1,4),leg,Spacer(1,4),table(H1,R1,W1,shade+[None]),PageBreak(),
       Paragraph(TITLE2,st),Paragraph(SORT,it),Spacer(1,3),Paragraph(NOTE,sm),Paragraph(NOTE2,sm),Spacer(1,4),table(H2,R2,W2,[None]*68)]
def build(np):
    def f(c,d):
        c.saveState(); c.setFont('Helvetica-Oblique',7); c.drawString(0.45*inch,0.3*inch,'*2026 figures UNOFFICIAL (PA DOS status "U"), not certified. Total ballots = governor-race total. Source: PA Department of State.')
        c.drawRightString(10.55*inch,0.3*inch,f'Page {d.page} of {np}'); c.restoreState()
    doc=SimpleDocTemplate(OUT,pagesize=landscape(letter),leftMargin=0.45*inch,rightMargin=0.45*inch,topMargin=0.4*inch,bottomMargin=0.5*inch,
        title='Pennsylvania 67 County Democratic Registration and Vote Change, 2022 vs 2026 (2026 unofficial)',author='mbenson8989 / Pennsylvania-Election-Analysis')
    import copy; doc.build(copy.deepcopy(story),onFirstPage=f,onLaterPages=f); return doc.page
n=build(0); n=build(n); print('pages',n)
import json; json.dump({'R1':R1,'R2':R2,'pages':n},open('/workspace/pa/pdf/pdf_cells.json','w'))
