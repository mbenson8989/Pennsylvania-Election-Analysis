"""PA analysis on the verified table (both passes must be clean)."""
import pandas as pd, numpy as np, json, statsmodels.api as sm, statsmodels.formula.api as smf
V='/workspace/pa/verification/'; D='/workspace/pa/data/'
p1=json.load(open(V+'pass1_report.json')); p2=json.load(open(V+'pass2_report.json'))
assert not p1['mismatches'] and not p2['mismatches'] and p1['figures_checked']==p2['figures_checked']==2077
t=pd.read_csv(D+'pa_gov_2022_2026_by_population.csv')
REG={'Southeast (Philadelphia + collar)':['Philadelphia','Bucks','Chester','Delaware','Montgomery'],
 'Southwest':['Allegheny','Armstrong','Beaver','Butler','Fayette','Greene','Indiana','Lawrence','Washington','Westmoreland'],
 'Northeast / Lehigh Valley':['Lehigh','Northampton','Carbon','Monroe','Pike','Wayne','Lackawanna','Luzerne','Wyoming','Susquehanna','Schuylkill'],
 'South Central':['Adams','Berks','Cumberland','Dauphin','Franklin','Lancaster','Lebanon','Perry','York']}
m={c:r for r,cs in REG.items() for c in cs}; t['region']=t.county.map(m).fillna('Central / T (rest of state)')
assert t.region.value_counts().sum()==67
def fit(df,y,x):
    X=sm.add_constant(df[x].values); r=sm.OLS(df[y].values,X).fit(); ci=r.conf_int()
    infl=r.get_influence().cooks_distance[0]
    return dict(n=len(df),a=float(r.params[0]),a_ci=ci[0].tolist(),k=float(r.params[1]),k_se=float(r.bse[1]),k_ci=ci[1].tolist(),r2=float(r.rsquared),
                resid_sd=float(np.sqrt(r.scale)),p_k=float(r.pvalues[1])),r,infl
OUT={}
# PA constant: dG = a + k * registration-share drop (SD form)
OUT['const_all'],r_all,cook=fit(t,'dG','reg_share_drop'); t['cook']=cook; t['fit_dG']=r_all.fittedvalues; t['res_dG']=t.dG-t.fit_dG
# forward fit G = m*(Rsh/100)+b each year
t['Rsh22f']=t.Rsh22/100; t['Rsh26f']=t.Rsh26/100
OUT['fwd_2022'],_,c22=fit(t,'G22','Rsh22f'); OUT['fwd_2026'],_,c26=fit(t,'G26','Rsh26f'); t['cook22']=c22; t['cook26']=c26
# Mean ratio constant: dS relative to registration-share drop (statewide pooled)
sw=dict(D22=int(t.D22.sum()),T22=int(t.T22.sum()),D26=int(t.D26.sum()),T26=int(t.T26.sum()),RegD22=int(t.RegD22.sum()),RegTot22=int(t.RegTot22.sum()),RegD26=int(t.RegD26.sum()),RegTot26=int(t.RegTot26.sum()),
        R22=int(t.R22.sum()),R26=int(t.R26.sum()),O22=int(t.O22.sum()),O26=int(t.O26.sum()),RegR22=int(t.RegR22.sum()),RegR26=int(t.RegR26.sum()))
for y in ('22','26'): sw['S'+y]=100*sw['D'+y]/sw['T'+y]; sw['R'+'sh'+y]=100*sw['RegD'+y]/sw['RegTot'+y]; sw['G'+y]=sw['S'+y]-sw['Rsh'+y]
sw['dG']=sw['G26']-sw['G22']; sw['drop']=sw['Rsh22']-sw['Rsh26']; sw['residual']=sw['dG']-sw['drop']; sw['implied']=sw['residual']*sw['T26']/100
sw['gap_votes']=sw['D26']-sw['D22']*sw['RegD26']/sw['RegD22']; OUT['statewide']=sw
# regional constants + interaction test
OUT['regional']={}
for rg,df in t.groupby('region'):
    OUT['regional'][rg]=fit(df,'dG','reg_share_drop')[0] if len(df)>=5 else None
    OUT['regional'][rg].update(mean_dG=float(df.dG.mean()),median_dG=float(df.dG.median()),counties=len(df))
full=smf.ols('dG ~ reg_share_drop*C(region)',t).fit(); red=smf.ols('dG ~ reg_share_drop',t).fit(); inter=smf.ols('dG ~ reg_share_drop + C(region)',t).fit()
an=sm.stats.anova_lm(red,inter,full); OUT['region_test']=dict(F_intercepts=float(an.F[1]),p_intercepts=float(an['Pr(>F)'][1]),F_slopes=float(an.F[2]),p_slopes=float(an['Pr(>F)'][2]),
    r2_single=float(red.rsquared),r2_region_intercepts=float(inter.rsquared),r2_full=float(full.rsquared))
# narrowing: Cook's D > 4/n in the constant fit or either forward fit
thr=4/67; t['narrow']=(t.cook>thr)|(t.cook22>thr)|(t.cook26>thr)
nar=t[t.narrow]
OUT['narrowed']=[dict(county=r.county,region=r.region,cook_const=round(r.cook,3),cook22=round(r.cook22,3),cook26=round(r.cook26,3),dG=r.dG,drop=r.reg_share_drop,Rsh22=r.Rsh22) for r in nar.itertuples()]
OUT['const_narrowed'],_,_=fit(t[~t.narrow],'dG','reg_share_drop')
OUT['fwd_2022_narrowed'],_,_=fit(t[~t.narrow],'G22','Rsh22f'); OUT['fwd_2026_narrowed'],_,_=fit(t[~t.narrow],'G26','Rsh26f')
# floor & ceiling
q10=t.S22.quantile(.10); q25=t.G22.quantile(.25)
OUT['floor_rule']=f'2022 Dem vote share <= 10th percentile ({q10:.2f}%) AND G2022 <= 25th percentile ({q25:+.2f})'
OUT['floor_baseline']=t[(t.S22<=q10)&(t.G22<=q25)].sort_values('S22').county.tolist()
OUT['lowest_S22']=t.nsmallest(7,'S22')[['county','S22','Rsh22']].to_dict('records')
OUT['lowest_Rsh22']=t.nsmallest(7,'Rsh22')[['county','Rsh22','S22']].to_dict('records')
OUT['highest_S22']=t.nlargest(5,'S22')[['county','S22','Rsh22']].to_dict('records')
OUT['dG_floor']=t.nsmallest(5,'dG')[['county','dG','population_2025']].to_dict('records')
OUT['dG_ceiling']=t.nlargest(5,'dG')[['county','dG','population_2025']].to_dict('records')
OUT['dG_stats']=dict(mean=float(t.dG.mean()),median=float(t.dG.median()),min=float(t.dG.min()),max=float(t.dG.max()),positive=int((t.dG>0).sum()),
    dS_positive=int((t.dS>0).sum()),reg_fell=int(t.dem_reg_fell.sum()),reg_share_fell=int((t.reg_share_drop>0).sum()),
    implied_sum_loss=float(t.implied_offset_votes.sum()),gap_sum=float(t.gap_votes.sum()))
OUT['nonloss']=t[~t.dem_reg_fell][['county','RegD22','RegD26','D22','D26','dG','dS']].to_dict('records')
OUT['fell_both']=t[(t.dem_reg_fell)&(t.D26<t.D22)][['county','RegD22','RegD26','D22','D26','dG']].to_dict('records')
# Texas-style check
for y in ('22','26'):
    t['DRminusT'+y]=t['DR'+y]-t['T'+y]; t['DRminusReg'+y]=t['DR'+y]-t['RegTot'+y]; t['DRoverT'+y]=100*t['DR'+y]/t['T'+y]
OUT['texas']={y:dict(over_race_total=t[t['DRminusT'+y]>0].county.tolist(),over_registered=t[t['DRminusReg'+y]>0].county.tolist(),
    max_DR_over_T=float(t['DRoverT'+y].max()),max_county=t.loc[t['DRoverT'+y].idxmax(),'county'],
    max_turnout_DRoverReg=float((100*t['DR'+y]/t['RegTot'+y]).max()),max_turnout_county=t.loc[(t['DR'+y]/t['RegTot'+y]).idxmax(),'county']) for y in ('22','26')}
OUT['texas']['statewide_2026_vs_ENR_ballots_counted']=dict(DR=sw['D26']+sw['R26'],race_total=sw['T26'],ballots_counted=p2['info']['enr_ballots_counted_2026_statewide'])
t.to_csv(D+'pa_analysis_full.csv',index=False)
json.dump(OUT,open(D+'pa_results_summary.json','w'),indent=1,default=float)
print(json.dumps({k:OUT[k] for k in ('const_all','const_narrowed','fwd_2022','fwd_2026','region_test','floor_rule','floor_baseline','dG_floor','dG_ceiling','dG_stats','texas','highest_S22')},indent=0,default=float))
for rg,v in OUT['regional'].items(): print(rg, {k:(round(x,3) if isinstance(x,float) else x) for k,x in v.items() if k in ('n','a','k','k_se','r2','mean_dG')})
print('narrowed',[(n['county'],n['cook_const'],n['cook22'],n['cook26']) for n in OUT['narrowed']])
print('nonloss',OUT['nonloss']); print('fell_both',OUT['fell_both']); print(json.dumps(sw,indent=0))
# common-slope model with regional intercepts (slopes not significantly different by region)
cs=smf.ols('dG ~ reg_share_drop + C(region) - 1',t).fit()
OUT['common_slope_regional']=dict(k=float(cs.params['reg_share_drop']),k_se=float(cs.bse['reg_share_drop']),r2=float(inter.rsquared),
   intercepts={k.replace('C(region)[','').rstrip(']'):float(v) for k,v in cs.params.items() if k.startswith('C(region)')},
   intercept_se={k.replace('C(region)[','').rstrip(']'):float(v) for k,v in cs.bse.items() if k.startswith('C(region)')})
OUT['dS_negative']=t[t.dS<=0][['county','S22','S26','dS']].to_dict('records')
json.dump(OUT,open(D+'pa_results_summary.json','w'),indent=1,default=float)
print(OUT['common_slope_regional']); print(OUT['dS_negative'])
