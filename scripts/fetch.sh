#!/bin/bash
# Fetch raw DOS files untouched; log URL, time, HTTP status, bytes, sha256
cd /workspace/pa/raw
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36'
log(){ f=$1; u=$2; code=$(curl -sL -A "$UA" -o "$f" -w "%{http_code}" "$u"); echo -e "$(date '+%Y-%m-%d %H:%M:%S %Z')\t$f\t$code\t$(stat -c%s "$f")\t$(sha256sum "$f"|cut -c1-64)\t$u" >> SOURCES.tsv; }
P=https://www.pa.gov/content/dam/copapwp-pagov/en/dos/resources/voting-and-elections
E=https://www.electionreturns.pa.gov/api
log dos_vr_2022_general_election.pdf "$P/voting-and-election-statistics/voter-registration-statistics/2022%20Election%20VR%20Statistics.pdf"
log dos_vr_2026_general_election_certified.pdf "$P/voting-and-election-statistics/voter-registration-statistics/certified%20voter%20registration%20stats%20general%20election%202026%20-%20final.pdf"
log dos_er_2022_general_precinct.txt "$P/bulk-data/ElectionReturns_2022_General_PrecinctReturns.txt"
log dos_er_2022_general_readme.txt "$P/bulk-data/ElectionReturns_2022_General_Readme.txt"
log dos_vr_2022_general_precinct.txt "$P/bulk-data/VoterRegistration_2022_General_Precinct.txt"
log dos_vr_2022_general_readme.txt "$P/bulk-data/VoterRegistration_2022_General_Readme.txt"
log enr_elections_list.json "$E/Reports/GetElectionList"
log enr_2026G_governor_countybreak.json "$E/ElectionReturn/GetCountyBreak?officeId=3&districtId=1&methodName=GetCountyBreak&electionid=117&electiontype=G&isactive=1"
log enr_2022G_governor_countybreak.json "$E/ElectionReturn/GetCountyBreak?officeId=3&districtId=1&methodName=GetCountyBreak&electionid=94&electiontype=G&isactive=0"
# Population (sort order only; NOT a DOS file)
log census_co-est2025-alldata.csv "https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv"
