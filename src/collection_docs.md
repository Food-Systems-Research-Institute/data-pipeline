# Collection Scripts
- `collect_nass.py`
- `collect_farm_income.py`

---

# 1. `collect_nass.py`
<summary>This script uses the publically available NASS API to collect NASS census data. This API does not have built in pagination, so currently to prevent rate limiting looping is used to make more specified requests. </summary>

---
ex. loop through all of the Northeast States and available years(census data is collected every 5 years) and create a table in the db for each state/year pair. NASS has a selection of sectors, which can be specified when 
ex. of usage here:

```
 for year in [2002, 2007, 2012, 2017, 2022]:
        for state in northeast_states:
            params = build_request(
                                sector="ECONOMICS", 
                                year=year, 
                                agg_level_desc="STATE", 
                                state_name=state
                            )
            count = get_record_count(count_url, params)
            table_name = get_table_name(params)
            
            print(get_NASS_data(get_url, count, params, table_name))
            build_NASS_table(get_url, params, table_name, count)
            time.sleep(.5)

```