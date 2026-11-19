import pandas as pd, numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
D='/workspace/pa/data/'; O='/workspace/pa/repo/'
t=pd.read_csv(D+'pa_analysis_full.csv'); S=json.load(open(D+'pa_results_summary.json'))
UN='2026 figures UNOFFICIAL (PA DOS, not certified). Source: PA Department of State; Census V2025 population (sort order).'
fl,ce=t.loc[t.dG.idxmin(),'county'],t.loc[t.dG.idxmax(),'county']
cols={'Southeast (Philadelphia + collar)':'#1f77b4','Southwest':'#d62728','Northeast / Lehigh Valley':'#2ca02c','South Central':'#9467bd','Central / T (rest of state)':'#8c8c8c'}
def foot(fig): fig.text(0.01,0.005,UN,fontsize=7,color='#555')
# 1 slope chart
fig,ax=plt.subplots(figsize=(9,11))
for r in t.itertuples():
    c='#d95f02' if r.county==ce else '#1b9e77' if r.county==fl else cols[r.region]
    ax.plot([0,1],[r.G22,r.G26],color=c,alpha=.8 if r.county in (fl,ce) else .45,lw=2.2 if r.county in (fl,ce) else 1)
    if r.population_2025>400000 or r.county in (fl,ce): ax.text(1.02,r.G26,f'{r.county} ({r.dG:+.2f}*)',fontsize=7,va='center')
ax.set_xticks([0,1]); ax.set_xticklabels(['G 2022 (official)','G 2026* (unofficial)']); ax.set_xlim(-.1,1.45); ax.axhline(0,color='k',lw=.5)
ax.set_ylabel('G = Dem vote share − Dem registration share (points)'); ax.set_title(f'Pennsylvania: G 2022 → G 2026*, all 67 counties\nG rose in {S["dG_stats"]["positive"]} of 67 counties; floor {fl} {t.dG.min():+.2f}*, ceiling {ce} {t.dG.max():+.2f}*')
for k,c in cols.items(): ax.plot([],[],color=c,label=k)
ax.legend(fontsize=7,loc='lower left'); foot(fig); fig.tight_layout(rect=(0,.02,1,1)); fig.savefig(O+'PA_Slope_G2022_to_G2026_County_Slope_Chart.png',dpi=130); plt.close()
# 2 stacked share by population
fig,ax=plt.subplots(figsize=(16,6)); x=np.arange(67)
ax.bar(x,t.S22,color='#4c78a8',label='2022 Democratic vote share (official)')
ax.bar(x,t.dS.clip(lower=0),bottom=t.S22,color='#f58518',label='2022 → 2026* gain'); ax.bar(x,t.dS.clip(upper=0),bottom=t.S22,color='#e45756',label='2022 → 2026* loss')
ax.set_xticks(x); ax.set_xticklabels(t.county,rotation=90,fontsize=7); ax.set_ylabel('% of governor-race votes'); ax.set_title('Pennsylvania governor: 2022 Democratic share + 2026* change, counties largest → smallest population'); ax.legend(fontsize=8)
foot(fig); fig.tight_layout(rect=(0,.02,1,1)); fig.savefig(O+'PA_governor_stacked_share_by_population.png',dpi=120); plt.close()
# 3 vote-share gain above line, registration share loss below
fig,ax=plt.subplots(figsize=(16,6))
ax.bar(x,t.dS,color='#f58518',label='Vote-share change 2022 → 2026* (pts)'); ax.bar(x,-t.reg_share_drop,color='#4c78a8',label='Registration-share change (pts, negative = loss)')
ax.plot(x,t.dG,'k.',label='ΔG* (= vote-share change + registration-share loss)'); ax.axhline(0,color='k',lw=.6)
ax.set_xticks(x); ax.set_xticklabels(t.county,rotation=90,fontsize=7); ax.set_ylabel('points'); ax.set_title('Pennsylvania: vote-share change above the line, Democratic registration-share loss below, population order'); ax.legend(fontsize=8)
foot(fig); fig.tight_layout(rect=(0,.02,1,1)); fig.savefig(O+'PA_governor_stacked_share_with_Dem_registration_loss_by_population.png',dpi=120); plt.close()
# 4 dG population order with floor/ceiling
fig,ax=plt.subplots(figsize=(16,6))
c=['#1b9e77' if v==fl else '#d95f02' if v==ce else cols[r] for v,r in zip(t.county,t.region)]
ax.bar(x,t.dG,color=c); ax.axhline(t.dG.median(),color='k',ls='--',lw=.8,label=f'median {t.dG.median():+.2f}*')
ax.set_xticks(x); ax.set_xticklabels(t.county,rotation=90,fontsize=7); ax.set_ylabel('ΔG* (points)')
ax.set_title(f'Pennsylvania ΔG*, all 67 counties largest → smallest population. Floor: {fl} {t.dG.min():+.2f}*; Ceiling: {ce} {t.dG.max():+.2f}*')
from matplotlib.patches import Patch
h=[Patch(color=cc,label=k) for k,cc in cols.items()]+[Patch(color='#1b9e77',label=f'Floor {fl}'),Patch(color='#d95f02',label=f'Ceiling {ce}')]
ax.legend(handles=h+[ax.get_legend_handles_labels()[0][0]],fontsize=7); foot(fig); fig.tight_layout(rect=(0,.02,1,1)); fig.savefig(O+f'PA_deltaG_by_county_population_order_-_floor_{fl}_ceiling_{ce}.png',dpi=120); plt.close()
# 5 constant scatter
k=S['const_all']; fig,ax=plt.subplots(figsize=(10,7))
for rg,df in t.groupby('region'): ax.scatter(df.reg_share_drop,df.dG,color=cols[rg],label=rg,s=np.clip(np.sqrt(df.population_2025)/8,10,200),alpha=.75,edgecolor='k',lw=.3)
xx=np.linspace(t.reg_share_drop.min()-.2,t.reg_share_drop.max()+.2,10); ax.plot(xx,k['a']+k['k']*xx,'k-',label=f'PA constant: ΔG = {k["a"]:+.2f} + {k["k"]:.2f} × drop (R² {k["r2"]:.2f}, n=67)')
for r in t.itertuples():
    if r.narrow or r.county in (fl,ce) or r.population_2025>500000: ax.annotate(r.county,(r.reg_share_drop,r.dG),fontsize=7,xytext=(3,3),textcoords='offset points')
ax.set_xlabel('Democratic registration-share drop 2022 → 2026 (points)'); ax.set_ylabel('ΔG* (points)'); ax.set_title('Pennsylvania reverse-factoring constant (PA data only)\nmarker size ~ population')
ax.legend(fontsize=7); foot(fig); fig.tight_layout(rect=(0,.02,1,1)); fig.savefig(O+'PA_DeltaG_vs_Registration_Share_Drop_PA_Constant.png',dpi=130); plt.close()
# 6 ceiling & floor bars
sel=pd.concat([t.nlargest(5,'dG'),t.nsmallest(5,'dG')]).sort_values('population_2025',ascending=False)
fig,ax=plt.subplots(figsize=(11,5)); ax.bar(sel.county,sel.dG,color=['#d95f02' if v>=t.dG.nlargest(5).min() else '#1b9e77' for v in sel.dG])
for i,v in enumerate(sel.dG): ax.text(i,v+.1,f'{v:+.2f}*',ha='center',fontsize=8)
ax.set_ylabel('ΔG* (points)'); ax.set_title('Pennsylvania ceiling (top 5 ΔG, orange) and floor (bottom 5 ΔG, green) counties, population order'); plt.xticks(rotation=30)
foot(fig); fig.tight_layout(rect=(0,.02,1,1)); fig.savefig(O+'PA_Ceiling_and_Floor_Counties_DeltaG_by_Population.png',dpi=130); plt.close()
# 7 Texas-style check
fig,axs=plt.subplots(2,1,figsize=(16,8),sharex=True)
axs[0].plot(x,t.DRoverT22,'o-',ms=3,label='2022 (official)'); axs[0].plot(x,t.DRoverT26,'s-',ms=3,label='2026* (unofficial)'); axs[0].axhline(100,color='r',lw=1,label='100% line (D+R = race total)')
axs[0].set_ylabel('(D + R) ÷ governor-race total, %'); axs[0].legend(fontsize=8); axs[0].set_title('Texas-style check: Democratic + Republican governor votes vs governor-race total and vs registered voters. No county over either line.')
axs[1].plot(x,100*t.DR22/t.RegTot22,'o-',ms=3,label='2022'); axs[1].plot(x,100*t.DR26/t.RegTot26,'s-',ms=3,label='2026*'); axs[1].axhline(100,color='r',lw=1)
axs[1].set_ylabel('(D + R) ÷ registered voters, %'); axs[1].set_xticks(x); axs[1].set_xticklabels(t.county,rotation=90,fontsize=7); axs[1].legend(fontsize=8)
foot(fig); fig.tight_layout(rect=(0,.02,1,1)); fig.savefig(O+'PA_over_ballot_check_dem_plus_rep.png',dpi=120); plt.close()
# 8 2022 share vs change sorted by 2022 share
s=t.sort_values('S22'); fig,ax=plt.subplots(figsize=(16,6)); xs=np.arange(67)
ax.bar(xs,s.S22,color='#4c78a8',label='2022 Democratic share'); ax.bar(xs,s.dS,bottom=s.S22,color=np.where(s.dS>=0,'#f58518','#e45756'),label='2022 → 2026* change')
ax.set_xticks(xs); ax.set_xticklabels(s.county,rotation=90,fontsize=7); ax.set_title('All 67 counties sorted by 2022 Democratic vote share; orange = 2026* gain'); ax.legend(fontsize=8)
foot(fig); fig.tight_layout(rect=(0,.02,1,1)); fig.savefig(O+'PA_governor_2022_Dem_share_vs_gain_bar_chart.png',dpi=120); plt.close()
print(sorted(f for f in __import__('os').listdir(O) if f.endswith('.png')))
