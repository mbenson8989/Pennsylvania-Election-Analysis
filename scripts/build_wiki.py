import pandas as pd, json, datetime
D='/workspace/pa/data/'; W='/workspace/pa/wiki/'
t=pd.read_csv(D+'pa_analysis_full.csv'); S=json.load(open(D+'pa_results_summary.json'))
p1=json.load(open('/workspace/pa/verification/pass1_report.json')); p2=json.load(open('/workspace/pa/verification/pass2_report.json'))
sw=S['statewide']; ds=S['dG_stats']; k=S['const_all']; kn=S['const_narrowed']; cs=S['common_slope_regional']
REPO='https://github.com/mbenson8989/Pennsylvania-Election-Analysis'; RAWU='https://raw.githubusercontent.com/mbenson8989/Pennsylvania-Election-Analysis/main/'
CEDAR='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
BUILT=datetime.datetime.now().strftime('%b %d %Y %I:%M %p CST')
fl=t.loc[t.dG.idxmin()]; ce=t.loc[t.dG.idxmax()]
n=lambda v:f'{int(round(v)):,}'; sg=lambda v,d=2:f'{v:+.{d}f}'; pc=lambda v:f'{v:.2f}%'
BANNER=("> **\\*2026 figures are UNOFFICIAL.** The Pennsylvania Department of State (DOS) election returns site (electionreturns.pa.gov) lists the November 3, 2026 General Election with status \"U\" (unofficial) as of Nov 19, 2026 11:52 AM CST; 2026 vote counts are not certified. 2022 figures are DOS official (certified) returns. Governor race. "
 "**Denominator:** DOS publishes no county-level \"total ballots cast\" for the 2022 or 2026 general election, so these pages divide by the **governor-race total** (all governor candidates on the DOS returns; DOS reports no governor write-ins). "
 "Registration is the DOS Voter Registration Statistics for the Nov 8, 2022 Election and the Nov 3, 2026 General Election (certified). Votes are votes for the Democratic candidate, not a count of registered Democrats who voted. These pages measure a pattern; they make no claim about intent, fraud or cause.")
CED=f"Method origin: the [Cedar County Audit (Nebraska)]({CEDAR})."
def related(*pages): return '\n---\n**Related:** '+' · '.join(f'[{a}]({REPO}/wiki/{b})' for a,b in pages)+f' · [Cedar County Audit]({CEDAR})\n'
def img(f,cap): return f'![{cap.replace("*","")}]({RAWU}{f})\n\n*{cap.replace("*",chr(92)+"*")}*\n'
fn_fc=f'PA_deltaG_by_county_population_order_-_floor_{fl.county}_ceiling_{ce.county}.png'
POP='U.S. Census Bureau Vintage 2025 county estimates, July 1, 2025 (co-est2025-alldata.csv); used for sort order only.'
# ---------------- HOME ----------------
home=f"""# Pennsylvania 2022 vs 2026 Governor Race: ΔG Method

**Version 1, built {BUILT}**

{BANNER}

Method developed by Morissa Benson. It began with the **Cedar County audit in Nebraska** ([Cedar County Audit]({CEDAR})): a small county where Democratic governor votes rose while Democratic registration fell. This wiki applies the same county-by-county arithmetic to all 67 Pennsylvania counties using Pennsylvania Department of State numbers only. The Pennsylvania constant is computed from Pennsylvania data only; no other state's constant is reused.

## Contents

1. [Cedar County Audit]({CEDAR}): where the method began (Nebraska wiki)
2. [Reverse Math]({REPO}/wiki/Reverse-Math): statewide, then all 67 counties (largest to smallest population), the Pennsylvania constant and regional constants
3. [Locked Pennsylvania Formula]({REPO}/wiki/Locked-Pennsylvania-Formula): the equation, with a blank fill-in template and a worked example
4. [Floor and Ceiling]({REPO}/wiki/Floor-and-Ceiling): floor and ceiling counties, the Texas-style over-ballot check, counties to narrow out
5. [Graphs]({REPO}/wiki/Graphs): slope chart, stacked bars, ΔG by population order, constant scatter, ceiling/floor bars, over-ballot check

## Statewide at a glance

| Measure | 2022 (official) | 2026\\* (unofficial) | Change |
|---|---|---|---|
| Democratic registration (DOS election-day statistics) | {n(sw['RegD22'])} | {n(sw['RegD26'])} | {sw['RegD26']-sw['RegD22']:+,} ({100*(sw['RegD26']/sw['RegD22']-1):+.1f}%) |
| Republican registration | {n(sw['RegR22'])} | {n(sw['RegR26'])} | {sw['RegR26']-sw['RegR22']:+,} ({100*(sw['RegR26']/sw['RegR22']-1):+.1f}%) |
| Total registration | {n(sw['RegTot22'])} | {n(sw['RegTot26'])} | {sw['RegTot26']-sw['RegTot22']:+,} |
| Democratic governor votes (Shapiro both years) | {n(sw['D22'])} | {n(sw['D26'])}\\* | {sw['D26']-sw['D22']:+,}\\* ({100*(sw['D26']/sw['D22']-1):+.1f}%) |
| Republican governor votes (Mastriano 2022, Garrity 2026) | {n(sw['R22'])} | {n(sw['R26'])}\\* | {sw['R26']-sw['R22']:+,}\\* |
| Governor-race total (all candidates) | {n(sw['T22'])} | {n(sw['T26'])}\\* | {sw['T26']-sw['T22']:+,}\\* |
| **S** = Dem votes ÷ governor-race total | {pc(sw['S22'])} | {pc(sw['S26'])}\\* | {sg(sw['S26']-sw['S22'])}\\* |
| **R** = Dem registration share | {pc(sw['Rsh22'])} | {pc(sw['Rsh26'])} | {sg(sw['Rsh26']-sw['Rsh22'])} |
| **G** = S − R | {sg(sw['G22'])} | {sg(sw['G26'])}\\* | **ΔG = {sg(sw['dG'])}\\*** |

## Key findings (2026 unofficial\\*)

- **ΔG is positive in all 67 counties**, from {sg(fl.dG)} ({fl.county}) to {sg(ce.dG)} ({ce.county}); mean {sg(ds['mean'])}, median {sg(ds['median'])}.
- Democratic registration **share** fell in all 67 counties; the Democratic registration **count** fell in {ds['reg_fell']} (the 4 non-loss counties are Montgomery, Chester, Union and Snyder).
- **Pennsylvania constant (PA data only):** ΔG = {sg(k['a'])} + {k['k']:.2f} × registration-share drop (n = 67, slope 95% CI {k['k_ci'][0]:.2f} to {k['k_ci'][1]:.2f}, R² {k['r2']:.2f}). With 8 influential counties narrowed out: ΔG = {sg(kn['a'])} + {kn['k']:.2f} × drop (n = {kn['n']}, R² {kn['r2']:.2f}).
- **Regional constants:** regions share one slope (p = {S['region_test']['p_slopes']:.2f} for different slopes) but not one intercept (p = {S['region_test']['p_intercepts']:.1e}). Northeast / Lehigh Valley sits highest (intercept {sg(cs['intercepts']['Northeast / Lehigh Valley'])}, mean ΔG {sg(S['regional']['Northeast / Lehigh Valley']['mean_dG'])}).
- **Ceiling (highest ΔG):** {', '.join(f"{r['county']} {sg(r['dG'])}\\*" for r in S['dG_ceiling'])}. **Floor (lowest ΔG):** {', '.join(f"{r['county']} {sg(r['dG'])}\\*" for r in S['dG_floor'])}.
- **Baseline floor (most Republican baseline):** {', '.join(S['floor_baseline'])} ({S['floor_rule']}). **Baseline ceiling:** Philadelphia (2022 Democratic share {pc(t.loc[t.county=='Philadelphia','S22'].iloc[0])}, registration share {pc(t.loc[t.county=='Philadelphia','Rsh22'].iloc[0])}).
- **Texas-style over-ballot check:** counties where Democratic + Republican governor votes exceed the count they are checked against: **2022: 0, 2026\\*: 0** (against the governor-race total and against registered voters). DOS has no county ballots-cast figure for either year; statewide 2026\\* D + R = {n(S['texas']['statewide_2026_vs_ENR_ballots_counted']['DR'])} vs DOS "ballots counted" {n(S['texas']['statewide_2026_vs_ENR_ballots_counted']['ballots_counted'])}.

## Verification

Every figure for all 67 counties was checked in **two independent passes** against the raw DOS files before anything was published: Pass 1 **{p1['matches']:,} of {p1['figures_checked']:,}** figures matched, Pass 2 **{p2['matches']:,} of {p2['figures_checked']:,}** matched, **0 discrepancies** in either pass. Data, scripts and both pass reports: [{REPO}]({REPO}).

## Sources

| Data | Source |
|---|---|
| 2022 governor results by county (official) | DOS election returns, electionreturns.pa.gov, 2022 General Election (status O) |
| 2026 governor results by county (UNOFFICIAL) | DOS election returns, electionreturns.pa.gov, 2026 General Election (status U) |
| 2022 registration by party | DOS "2022 Voter Registration Statistics, November 8, 2022 Election" (PDF) |
| 2026 registration by party | DOS "2026 Voter Registration Statistics, November 3, 2026 General Election" (certified, PDF) |
| Population (sort order only) | {POP} |
{related(('Reverse Math','Reverse-Math'),('Locked Pennsylvania Formula','Locked-Pennsylvania-Formula'),('Floor and Ceiling','Floor-and-Ceiling'),('Graphs','Graphs'))}"""
# ---------------- REVERSE MATH ----------------
rows=[]
for r in t.itertuples():
    res=f"{sg(r.residual)}" if r.dem_reg_fell else 'non-loss'; imp=f"{r.implied_offset_votes:+,.0f}" if r.dem_reg_fell else 'n/a'
    rows.append(f"| {r.county} | {r.population_2025:,} | {r.region} | {r.RegD22:,} → {r.RegD26:,} | {r.Rsh22:.2f} → {r.Rsh26:.2f} | {r.reg_share_drop:.2f} | {r.D22:,} → {r.D26:,} | {r.T22:,} → {r.T26:,} | {r.S22:.2f} → {r.S26:.2f} | {sg(r.G22)} | {sg(r.G26)} | **{sg(r.dG)}** | {res} | {imp} | {r.gap_votes:+,.0f} |")
regrows='\n'.join(f"| {rg} | {v['counties']} | {sg(v['mean_dG'])} | {sg(v['a'])} | {v['k']:.2f} (SE {v['k_se']:.2f}) | {v['r2']:.2f} | {sg(cs['intercepts'][rg])} |" for rg,v in S['regional'].items())
rmems={rg:', '.join(t[t.region==rg].county) for rg in S['regional']}
rm=f"""# Reverse Math

{BANNER}

{CED} The same arithmetic used in the Cedar County audit work, applied to Pennsylvania's 67 counties. Same equation, a different constant per state: Pennsylvania's numbers come only from Pennsylvania DOS files.

## Step 1: the locked gap

**G = (Democratic governor votes ÷ governor-race total) − (Democratic registered voters ÷ total registered voters)**, in percentage points. Positive G means the Democratic share of votes is above the Democratic share of registration.

**ΔG = G 2026\\* − G 2022.** Statewide: G {sg(sw['G22'])} → {sg(sw['G26'])}\\*, **ΔG {sg(sw['dG'])}\\***. Across the 67 counties: mean **{sg(ds['mean'])}**, median **{sg(ds['median'])}**, range {sg(fl.dG)} ({fl.county}) to {sg(ce.dG)} ({ce.county}). ΔG is positive in all 67.

## Step 2: the reverse-factoring step

A separate, labeled step on top of the locked gap. It subtracts the expected loss from the drop in Democratic registration share, then solves backward for votes:

- **Residual = ΔG − registration-share drop**, where registration-share drop = R 2022 − R 2026. Algebraically the residual equals S 2026 − S 2022 (the vote-share surplus).
- **Implied injected/offset votes = residual × 2026 governor-race total ÷ 100.**
- **Gap in votes = D 2026 − D 2022 × (Dem registered 2026 ÷ Dem registered 2022)**, the Nebraska gap: 2026 Democratic votes minus what 2022 votes would be if they had shrunk with Democratic registration.
- Only counties whose Democratic registration **count** fell run the residual step ({ds['reg_fell']} of 67). The 4 non-loss counties (Montgomery, Chester, Union, Snyder) get raw numbers only.

**Statewide worked example:** S {pc(sw['S22'])} → {pc(sw['S26'])}\\*; R {pc(sw['Rsh22'])} → {pc(sw['Rsh26'])} (drop {sw['drop']:.2f}); ΔG {sg(sw['dG'])}\\*; residual {sg(sw['dG'])} − {sw['drop']:.2f} = **{sg(sw['residual'])}\\***; implied votes {sg(sw['residual'])} × {n(sw['T26'])} ÷ 100 = **{sw['implied']:+,.0f}\\***; gap in votes {n(sw['D26'])} − {n(sw['D22'])} × ({n(sw['RegD26'])} ÷ {n(sw['RegD22'])}) = **{sw['gap_votes']:+,.0f}\\***.

Summed over the {ds['reg_fell']} loss counties: implied votes **{ds['implied_sum_loss']:+,.0f}\\***. Gap in votes summed over all 67: **{ds['gap_sum']:+,.0f}\\***.

> **Hypothesis label.** Reading the residual as injected or offset votes is Morissa Benson's hypothesis. The arithmetic cannot test it: the same number reflects turnout changes, crossover voting, candidate differences (Mastriano 2022 vs Garrity 2026) and any other cause. Candidate votes are not turnout.

## Step 3: Pennsylvania's constant

Fitting ΔG against the registration-share drop across all 67 counties (ordinary least squares, Pennsylvania data only):

**ΔG = {sg(k['a'])} + {k['k']:.2f} × registration-share drop** (intercept 95% CI {k['a_ci'][0]:+.2f} to {k['a_ci'][1]:+.2f}; slope SE {k['k_se']:.2f}, 95% CI {k['k_ci'][0]:.2f} to {k['k_ci'][1]:.2f}; R² {k['r2']:.2f}; residual SD {k['resid_sd']:.2f} points).

With the 8 narrowed-out counties removed (see [Floor and Ceiling]({REPO}/wiki/Floor-and-Ceiling#counties-to-narrow-out)): **ΔG = {sg(kn['a'])} + {kn['k']:.2f} × drop** (n = {kn['n']}, slope 95% CI {kn['k_ci'][0]:.2f} to {kn['k_ci'][1]:.2f}, R² {kn['r2']:.2f}). Narrowing barely moves the constant.

An intercept of about +4.6 means a Pennsylvania county with no registration-share drop would still be expected to show ΔG of about +4.6 points; each point of registration-share drop adds about 0.55 points. This is Pennsylvania's own constant; do not carry another state's number over.

Forward fit (G = m × D/100 + b, D = Dem registration share): 2022 m = {S['fwd_2022']['k']:+.2f}, b = {S['fwd_2022']['a']:+.2f} (R² {S['fwd_2022']['r2']:.2f}); 2026\\* m = {S['fwd_2026']['k']:+.2f}, b = {S['fwd_2026']['a']:+.2f} (R² {S['fwd_2026']['r2']:.2f}).

## Step 4: regional constants

Working regions for this test (a grouping chosen for this analysis, not an official DOS region list): {'; '.join(f'**{rg}** ({len(t[t.region==rg])}): {rmems[rg]}' for rg in S['regional'])}.

| Region | Counties | Mean ΔG\\* | Own intercept | Own slope | R² | Intercept with shared slope ({cs['k']:.2f}) |
|---|---|---|---|---|---|---|
{regrows}

**Test:** letting each region have its own slope does not improve the fit (F = {S['region_test']['F_slopes']:.2f}, p = {S['region_test']['p_slopes']:.2f}); letting each region have its own intercept does (F = {S['region_test']['F_intercepts']:.2f}, p = {S['region_test']['p_intercepts']:.1e}; R² rises from {S['region_test']['r2_single']:.2f} to {S['region_test']['r2_region_intercepts']:.2f}). So Pennsylvania has **one slope ({cs['k']:.2f}) with regional intercepts**: Northeast / Lehigh Valley runs about 2 points above the rest of the state. Southeast and South Central slopes rest on 5 and 9 counties; treat regional slopes as rough.

## All 67 counties (largest to smallest population)

Population: {POP} Res. = residual (points); Implied = implied injected/offset votes; Gap = gap in votes.

| County | Population | Region | Dem reg 2022 → 2026 | Dem reg share % | Reg-share drop | Dem gov votes 2022 → 2026\\* | Race total 2022 → 2026\\* | S % 2022 → 2026\\* | G 2022 | G 2026\\* | ΔG\\* | Res.\\* | Implied\\* | Gap\\* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}
{related(('Locked Pennsylvania Formula','Locked-Pennsylvania-Formula'),('Floor and Ceiling','Floor-and-Ceiling'),('Graphs','Graphs'),('Home','Home'))}"""
# ---------------- LOCKED FORMULA ----------------
pk=t[t.county==ce.county].iloc[0]
lf=f"""# Locked Pennsylvania Formula

{BANNER}

{CED}

## Pennsylvania equation (final fitted)

**Pennsylvania equation: ΔG = {sg(k['a'])} + {k['k']:.2f} × (Democratic registration-share drop, points)**

This is the **locked (primary) Pennsylvania equation**: ordinary least squares across **all 67 counties**, the same all-county fit of ΔG on the registration-share drop used to set each state's own constant. Pennsylvania data only.

| Term | Meaning | Units |
|---|---|---|
| ΔG | G 2026\\* − G 2022, where G = S − R (see [The equation](#the-equation)) | percentage points |
| Registration-share drop | R 2022 − R 2026 (Democratic registered ÷ total registered × 100; positive = share fell) | percentage points |
| {sg(k['a'])} (constant) | Expected ΔG in a county whose Democratic registration share did not change | percentage points |
| {k['k']:.2f} (multiplier) | Added ΔG for each 1 point of registration-share drop | points of ΔG per point of drop |

| Fit | Constant (95% CI) | Multiplier (95% CI) | n | R² |
|---|---|---|---|---|
| **Locked: all 67 counties** | **{sg(k['a'])}** ({k['a_ci'][0]:+.2f} to {k['a_ci'][1]:+.2f}) | **{k['k']:.2f}** ({k['k_ci'][0]:.2f} to {k['k_ci'][1]:.2f}) | 67 | {k['r2']:.2f} |
| Sensitivity: 8 narrowed-out counties removed | {sg(kn['a'])} ({kn['a_ci'][0]:+.2f} to {kn['a_ci'][1]:+.2f}) | {kn['k']:.2f} ({kn['k_ci'][0]:.2f} to {kn['k_ci'][1]:.2f}) | {kn['n']} | {kn['r2']:.2f} |

Narrowed-out counties: {', '.join(d['county'] for d in S['narrowed'])} (reasons on [Floor and Ceiling]({REPO}/wiki/Floor-and-Ceiling#counties-to-narrow-out)).

**Regional variant (supplementary, not the locked equation):** one shared multiplier **{cs['k']:.2f}** with regional constants: {'; '.join(f"{rg} {sg(v)}" for rg,v in sorted(cs['intercepts'].items(), key=lambda x:-x[1]))} (R² {S['region_test']['r2_region_intercepts']:.2f}). See [Reverse Math, Step 4]({REPO}/wiki/Reverse-Math#step-4-regional-constants).

**Worked example ({ce.county}):** registration-share drop {pk.reg_share_drop:.2f} → expected ΔG = {sg(k['a'])} + {k['k']:.2f} × {pk.reg_share_drop:.2f} = **{k['a']+k['k']*pk.reg_share_drop:+.2f}**; actual ΔG = **{sg(pk.dG)}\\*** (2026 unofficial), {pk.dG-(k['a']+k['k']*pk.reg_share_drop):+.2f} above the line. Computed from unrounded values.

## The equation

- **S** (Democratic vote share) = Democratic governor votes ÷ governor-race total (all candidates) × 100. *The brief calls for total ballots cast; DOS publishes no county ballots-cast figure for the 2022 or 2026 general election, so the governor-race total stands in. Nebraska found the two denominators give nearly identical ΔG (r = 0.999).*
- **R** (Democratic registration share) = Democratic registered voters ÷ total registered voters × 100 (DOS election-day registration statistics)
- **G** = S − R
- **ΔG** = G(2026) − G(2022) = (S2026 − S2022) − (R2026 − R2022)
- **Reverse step (registration-loss subtraction):** residual = ΔG − (R2022 − R2026) = vote-share surplus
- **Implied injected/offset votes** = residual × 2026 governor-race total ÷ 100
- **Gap in votes:** D2026 − D2022 × (RegDem2026 ÷ RegDem2022)
- **Pennsylvania constant (PA data only):** ΔG = {sg(k['a'])} + {k['k']:.2f} × (R2022 − R2026); narrowed: {sg(kn['a'])} + {kn['k']:.2f} × drop

## Blank template

| Line | Item | 2022 | 2026* |
|---|---|---|---|
| 1 | Democratic governor votes | ______ | ______ |
| 2 | Governor-race total (all candidates) | ______ | ______ |
| 3 | S = line 1 ÷ line 2 × 100 | ______ | ______ |
| 4 | Democratic registered voters (DOS election statistics) | ______ | ______ |
| 5 | Total registered voters | ______ | ______ |
| 6 | R = line 4 ÷ line 5 × 100 | ______ | ______ |
| 7 | G = line 3 − line 6 | ______ | ______ |
| 8 | ΔG = G 2026 − G 2022 | | ______ |
| 9 | Registration-share change = R 2026 − R 2022 | | ______ |
| 10 | Did Democratic registration fall? (line 4: 2026 < 2022) | | Yes / No |
| 11 | If yes: residual = line 8 − \\|line 9\\| | | ______ |
| 12 | If yes: implied votes = line 11 × line 2 (2026) ÷ 100 | | ______ |
| 13 | Gap in votes = D2026 − D2022 × (line 4 2026 ÷ line 4 2022) | | ______ |
| 14 | Expected ΔG from PA constant = {k['a']:.2f} + {k['k']:.2f} × (−line 9) | | ______ |

## Rules for using this formula

1. **If a county lost Democratic registration, run the residual step** (lines 11–12). {ds['reg_fell']} of 67 Pennsylvania counties did. **Non-loss counties** (Montgomery, Chester, Union, Snyder gained registered Democrats) skip lines 11–12 and get raw numbers only; their registration *share* still fell because total registration grew faster.
2. **The starting point is different in every state.** Pennsylvania's constant comes from Pennsylvania DOS files only. Compare Pennsylvania counties against Pennsylvania's own range ({sg(fl.dG)} to {sg(ce.dG)}), not against another state's figures.
3. **Always pull out the ceiling and floor counties.** In Pennsylvania the ceiling is {ce.county} ({sg(ce.dG)}\\*) and the floor is {fl.county} ({sg(fl.dG)}\\*). See [Floor and Ceiling]({REPO}/wiki/Floor-and-Ceiling).

## Worked example: {ce.county} (ceiling county)

| Line | Item | 2022 | 2026* |
|---|---|---|---|
| 1 | Democratic governor votes | {pk.D22:,} | {pk.D26:,}* |
| 2 | Governor-race total | {pk.T22:,} | {pk.T26:,}* |
| 3 | S | {pk.S22:.2f} | {pk.S26:.2f}* |
| 4 | Democratic registered | {pk.RegD22:,} | {pk.RegD26:,} |
| 5 | Total registered | {pk.RegTot22:,} | {pk.RegTot26:,} |
| 6 | R | {pk.Rsh22:.2f} | {pk.Rsh26:.2f} |
| 7 | G | {sg(pk.G22)} | {sg(pk.G26)}* |
| 8 | ΔG | | {sg(pk.dG)}* |
| 9 | Registration-share change | | {-pk.reg_share_drop:+.2f} |
| 10 | Registration fell? | | Yes |
| 11 | Residual | | {sg(pk.residual)}* |
| 12 | Implied votes | | {pk.implied_offset_votes:+,.0f}* |
| 13 | Gap in votes | | {pk.gap_votes:+,.0f}* |
| 14 | Expected ΔG from PA constant | | {k['a']+k['k']*pk.reg_share_drop:+.2f} (actual is {pk.dG-(k['a']+k['k']*pk.reg_share_drop):+.2f} above) |

Residual and implied votes are computed from unrounded shares.
{related(('Reverse Math','Reverse-Math'),('Floor and Ceiling','Floor-and-Ceiling'),('Graphs','Graphs'),('Home','Home'))}"""
# ---------------- FLOOR & CEILING ----------------
def det(sub):
    return '\n'.join(f"| {r.county} | {r.population_2025:,} | {r.Rsh22:.2f}% | {r.S22:.2f}% | {sg(r.G22)} | {sg(r.G26)}* | **{sg(r.dG)}*** | {r.RegD22:,} → {r.RegD26:,} | {r.D22:,} → {r.D26:,}* |" for r in sub.sort_values('population_2025',ascending=False).itertuples())
H='| County | Population | Dem reg share 2022 | Dem vote share 2022 | G 2022 | G 2026* | ΔG* | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026* |\n|---|---|---|---|---|---|---|---|---|'
bf=t[t.county.isin(S['floor_baseline'])]; bc=t.nlargest(5,'S22'); cl=t.nlargest(5,'dG'); fl5=t.nsmallest(5,'dG')
REASON={'Philadelphia':'Baseline ceiling: 75% Democratic registration, 86% Democratic vote share in 2022, little room to move. Highest-influence county in the 2026 forward fit (Cook\'s D 0.41).',
 'Montgomery':'Non-loss county (gained registered Democrats). High influence in the 2022 and 2026 forward fits (top-5 Democratic vote share).',
 'Delaware':'Philadelphia-collar ceiling-type county (top-5 2022 Democratic vote share). High influence in the 2022 forward fit.',
 'Chester':'Non-loss county; largest gap between vote share and registration share in 2022 (G +20.4). High influence in both forward fits.',
 'Lackawanna':'High influence in both forward fits (2022 G +5.6 on 55.7% Democratic registration, well below the forward-fit line).',
 'Fayette':'Largest Democratic registration-share drop in the state (7.35 points), so it sets the right end of the constant line; high influence in the 2022 forward fit.',
 'Fulton':'Baseline floor: lowest 2022 Democratic vote share in the state (17.9%). High influence in both forward fits.',
 'Cameron':'Smallest county (population 4,211; 1,611 governor votes in 2026*). The only county where the Democratic vote share fell (−0.48), and the one county above the influence cutoff in the constant fit (Cook\'s D 0.060).'}
nrows='\n'.join(f"| {d['county']} | {d['region']} | {d['cook_const']:.3f} / {d['cook22']:.3f} / {d['cook26']:.3f} | {REASON[d['county']]} |" for d in S['narrowed'])
fb=', '.join(f"{d['county']}" for d in S['fell_both'])
tx=S['texas']
fc=f"""# Floor and Ceiling

{BANNER}

{CED}

## How to read floor and ceiling counties

Look for the pattern at both ends. The **floor** is the most Republican baseline: counties whose Democratic base is too small for the pattern to show. The **ceiling** is the heavily Democratic end, plus the counties with the largest ΔG. In Pennsylvania:

- **The ΔG floor** (single lowest ΔG) is **{fl.county}, {sg(fl.dG)}\\***.
- **The ΔG ceiling** (single highest ΔG) is **{ce.county}, {sg(ce.dG)}\\***.

Every Pennsylvania county falls between those two. Unlike Nebraska, no Pennsylvania county has a negative ΔG.

## Terminology

- **Baseline floor counties (most Republican baseline):** {', '.join(S['floor_baseline'])}. Rule: {S['floor_rule']}. Fulton is the most Republican baseline in the state (2022 Democratic vote share {pc(t.loc[t.county=='Fulton','S22'].iloc[0])}).
- **Baseline ceiling counties (most Democratic baseline):** {', '.join(bc.county)} (the five highest 2022 Democratic vote shares). Philadelphia is the single baseline ceiling.
- **ΔG ceiling counties:** {', '.join(f"{r['county']} {sg(r['dG'])}\\*" for r in S['dG_ceiling'])}. Pike, Monroe and Carbon are in the Northeast / Lehigh Valley group, Greene in the Southwest, Mercer in the Central / T group; all five lost registered Democrats.
- **ΔG floor counties:** {', '.join(f"{r['county']} {sg(r['dG'])}\\*" for r in S['dG_floor'])}.
- **Non-loss counties** (gained registered Democrats; raw numbers only, no residual step): {', '.join(f"{d['county']} ({d['RegD22']:,} → {d['RegD26']:,} registered; votes {d['D22']:,} → {d['D26']:,}\\*)" for d in S['nonloss'])}.
- **Registration fell and Democratic votes fell too** ({len(S['fell_both'])} counties, raw numbers only): {fb}.

## Baseline floor detail

{H}
{det(bf)}

## Baseline ceiling detail

{H}
{det(bc)}

## ΔG ceiling detail (top 5)

{H}
{det(cl)}

## ΔG floor detail (bottom 5)

{H}
{det(fl5)}

## Texas-style over-ballot check

Question: is there any county where Democratic + Republican governor votes exceed ballots cast?

**DOS publishes no county-level ballots-cast figure for the 2022 or 2026 general election** (the DOS "vote history" summary files start with 2024; the 2022 and 2026 general bulk-data sections have none, and the results site's county ballot-count field is blank for 2026). So the check was run against the two DOS figures that do exist for every county:

| Check | 2022 (official) | 2026\\* (unofficial) |
|---|---|---|
| Counties where D + R > governor-race total | **0** | **0** |
| Counties where D + R > total registered voters | **0** | **0** |
| Highest (D + R) ÷ race total | {tx['22']['max_DR_over_T']:.2f}% ({tx['22']['max_county']}) | {tx['26']['max_DR_over_T']:.2f}% ({tx['26']['max_county']}) |
| Highest (D + R) ÷ registered | {tx['22']['max_turnout_DRoverReg']:.2f}% ({tx['22']['max_turnout_county']}) | {tx['26']['max_turnout_DRoverReg']:.2f}% ({tx['26']['max_turnout_county']}) |

Statewide 2026\\*: D + R = {n(tx['statewide_2026_vs_ENR_ballots_counted']['DR'])}, governor-race total {n(tx['statewide_2026_vs_ENR_ballots_counted']['race_total'])}, DOS results-site "ballots counted" {n(tx['statewide_2026_vs_ENR_ballots_counted']['ballots_counted'])} (statewide only). D + R is below ballots counted. **No over-ballot anomalies.** Against the race total the check cannot fail by construction (D and R are part of it), so the registered-voter check is the meaningful county test here. Also checked: every candidate's election-day + mail-in + provisional votes add exactly to the candidate total in every county, both years (0 mismatches).

## Pennsylvania constants

| Fit | Intercept | Slope | R² | n |
|---|---|---|---|---|
| ΔG on registration-share drop (PA constant) | {sg(k['a'])} | {k['k']:.2f} | {k['r2']:.2f} | 67 |
| Same, narrowed | {sg(kn['a'])} | {kn['k']:.2f} | {kn['r2']:.2f} | {kn['n']} |
| Forward fit 2022: G on D/100 | {sg(S['fwd_2022']['a'])} | {S['fwd_2022']['k']:+.2f} | {S['fwd_2022']['r2']:.2f} | 67 |
| Forward fit 2026\\*: G on D/100 | {sg(S['fwd_2026']['a'])} | {S['fwd_2026']['k']:+.2f} | {S['fwd_2026']['r2']:.2f} | 67 |
| Forward fit 2022, narrowed | {sg(S['fwd_2022_narrowed']['a'])} | {S['fwd_2022_narrowed']['k']:+.2f} | {S['fwd_2022_narrowed']['r2']:.2f} | {S['fwd_2022_narrowed']['n']} |
| Forward fit 2026\\*, narrowed | {sg(S['fwd_2026_narrowed']['a'])} | {S['fwd_2026_narrowed']['k']:+.2f} | {S['fwd_2026_narrowed']['r2']:.2f} | {S['fwd_2026_narrowed']['n']} |

Regional constants: see [Reverse Math, Step 4]({REPO}/wiki/Reverse-Math#step-4-regional-constants).

## Counties to narrow out

Rule: Cook's distance above 4/n (0.060) in the constant fit or either forward fit. Cook's D shown as constant / 2022 forward / 2026 forward.

| County | Region | Cook's D | Reason |
|---|---|---|---|
{nrows}

Data caveats (kept in all tables, flagged): **Lawrence** 2022, the DOS results site (official, used here) shows 105 more Democratic and 140 more Republican governor votes than the DOS 2022 bulk precinct file; **Warren** 2022 differs by 1 minor-party vote. Six counties' 2022 registration in the DOS bulk precinct file differs from the DOS election-day PDF used here (Bucks, Cumberland, Juniata, Montgomery, Snyder, Somerset), a different snapshot.

{img('PA_Ceiling_and_Floor_Counties_DeltaG_by_Population.png','Ceiling (top 5 ΔG, orange) and floor (bottom 5 ΔG, green) counties, population order.')}
{img(fn_fc,f'All 67 counties, ΔG in population order; floor {fl.county} and ceiling {ce.county} marked.')}
{related(('Reverse Math','Reverse-Math'),('Graphs','Graphs'),('Locked Pennsylvania Formula','Locked-Pennsylvania-Formula'),('Home','Home'))}"""
# ---------------- GRAPHS ----------------
gr=f"""# Graphs

{BANNER}

{CED} All charts use the verified 67-county table; counties are in population order (largest to smallest) unless a chart says otherwise.

## 1. County slope chart

{img('PA_Slope_G2022_to_G2026_County_Slope_Chart.png',f'Each line is one county, G 2022 to G 2026*. G rose in all 67 counties; ceiling {ce.county} and floor {fl.county} highlighted.')}
## 2. Stacked bars

{img('PA_governor_stacked_share_by_population.png','2022 Democratic share plus the 2022 → 2026* change, all 67 counties in population order.')}
{img('PA_governor_stacked_share_with_Dem_registration_loss_by_population.png','Vote-share change (above the line) and Democratic registration-share loss (below the line); black dots are ΔG*.')}
## 3. ΔG by population order

{img(fn_fc,f'All 67 counties in population order, colored by region. Floor: {fl.county} ({sg(fl.dG)}*). Ceiling: {ce.county} ({sg(ce.dG)}*).')}
## 4. Pennsylvania constant

{img('PA_DeltaG_vs_Registration_Share_Drop_PA_Constant.png',f"ΔG* against the registration-share drop, colored by region, marker size by population. Line: ΔG = {sg(k['a'])} + {k['k']:.2f} × drop (R² {k['r2']:.2f}, n = 67).")}
## 5. Vote-share bars sorted by 2022 Democratic share

{img('PA_governor_2022_Dem_share_vs_gain_bar_chart.png','All 67 counties sorted by 2022 Democratic vote share. Blue is 2022; orange is the 2026* gain (red = loss; Cameron only).')}
## 6. Ceiling and floor counties

{img('PA_Ceiling_and_Floor_Counties_DeltaG_by_Population.png','Top 5 and bottom 5 ΔG* counties, population order.')}
## 7. Texas-style over-ballot check

{img('PA_over_ballot_check_dem_plus_rep.png','(D + R) ÷ governor-race total (top) and ÷ registered voters (bottom), both years. No county crosses 100%.')}
{related(('Reverse Math','Reverse-Math'),('Floor and Ceiling','Floor-and-Ceiling'),('Locked Pennsylvania Formula','Locked-Pennsylvania-Formula'),('Home','Home'))}"""
import re
def fixtables(md):
    out=[]
    for line in md.split('\n'):
        if line.startswith('|'):
            line=re.sub(r'(?<!\\)\*\*\*',r'**\\*',line)
            line=re.sub(r'(?<![\\*])\*(?!\*)',r'\\*',line)
        out.append(line)
    return '\n'.join(out)
for name,body in (('Home',home),('Reverse-Math',rm),('Locked-Pennsylvania-Formula',lf),('Floor-and-Ceiling',fc),('Graphs',gr)):
    body=fixtables(body)
    open(W+name+'.md','w').write(body)
    assert CEDAR in body and 'UNOFFICIAL' in body
SIDEBAR=f"""**Pennsylvania ΔG wiki**

1. [Home]({REPO}/wiki/Home)
2. [Cedar Audit (Nebraska)]({CEDAR})
3. [Floor and Ceiling]({REPO}/wiki/Floor-and-Ceiling)
4. [Reverse Math]({REPO}/wiki/Reverse-Math)
5. [Locked Pennsylvania Formula]({REPO}/wiki/Locked-Pennsylvania-Formula)
6. [Graphs]({REPO}/wiki/Graphs)

\\*2026 figures unofficial.
"""
open(W+'_Sidebar.md','w').write(SIDEBAR)
print('wiki ok', BUILT)
