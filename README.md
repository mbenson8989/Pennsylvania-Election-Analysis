# Pennsylvania Election Analysis: 2022 vs 2026 Governor (ΔG method)

**\*2026 figures are UNOFFICIAL** (PA DOS election returns site status "U" as of Nov 19, 2026). 2022 figures are DOS official.

All 67 Pennsylvania counties, Pennsylvania Department of State (DOS) data only, same method as the Nebraska, Iowa, South Dakota, Texas, Michigan, Georgia, North Carolina and Kansas analyses. Method origin: [Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit).

**Wiki:** [Home](https://github.com/mbenson8989/Pennsylvania-Election-Analysis/wiki) · [Reverse Math](https://github.com/mbenson8989/Pennsylvania-Election-Analysis/wiki/Reverse-Math) · [Locked Pennsylvania Formula](https://github.com/mbenson8989/Pennsylvania-Election-Analysis/wiki/Locked-Pennsylvania-Formula) · [Floor and Ceiling](https://github.com/mbenson8989/Pennsylvania-Election-Analysis/wiki/Floor-and-Ceiling) · [Graphs](https://github.com/mbenson8989/Pennsylvania-Election-Analysis/wiki/Graphs)

## Files
- `pa_gov_2022_2026_by_population.csv`: the verified 67-county table (population order)
- `pa_analysis_full.csv`, `pa_results_summary.json`: analysis outputs (constants, regions, floor/ceiling, Texas-style check)
- `raw/`: DOS files exactly as downloaded; `raw/SOURCES.tsv` logs URL, time (CST), HTTP status, bytes, SHA-256
- `scripts/`: `fetch.sh`, `build_table.py`, `verify_pass1.py`, `verify_pass2.py`, `analysis.py`, `charts.py`, `build_wiki.py`
- `verification/pass1_report.json`, `verification/pass2_report.json`: two independent re-parses of the raw files; 2,077 of 2,077 figures matched in each, 0 discrepancies

## Denominator note
DOS publishes no county-level total ballots cast for the 2022 or 2026 general election. S uses the governor-race total (all governor candidates on DOS returns). Population (sort order only): U.S. Census Bureau Vintage 2025 county estimates.

These files measure a pattern; they make no claim about intent, fraud or cause.
