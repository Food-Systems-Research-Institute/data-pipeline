# Agricultural data collection
Automate data collection for ag data through APIs, web-scraping and bulk downloading. The goal of this work is to create a resuable data-pipeline to be used by Vermont Data Collaborative.

# Collection Scripts
- `collect_nass.py`
- `collect_farm_income.py`
- `collect_food_access_atlas.py`

---

# 1. `collect_nass.py` 
This script uses the publically available NASS API to collect NASS census and survey data. Use `collect_nass()` to run this script. This API does not have built in pagination, so currently to prevent rate limiting, use further querying. Adding parameters to collect nass will create an individuala request for each item in the category. For example, you can specify the sector, which is one of five options(see example where sector is economics). I have provided the ability to do so in the `collect_nass` function.

---

### Example below ⬇️. Collect census economics data for each of the years and each state in the northeast. This will create an individual table for each year state pair, and when complete will union all tables into one. State is the default, but can change to county. 

#### See `nass_api_parameters.csv` for more query options. 

```collect_nass("CENSUS", "ECONOMICS", years=[1997, 2002, 2007, 2012, 2017, 2022])```

---

# 2. `collect_farm_income.py`

Scrapes ers farm income download page for the latest release and loads it into `agData.db`. Run using `run_collect()`

---

# 3. `collect_food_access_atlas`
same as `collect_farm_income.py` except more tables are collected.
They include:
- `ers_food_access_2019_food_access_research_atlas`
- `ers_food_access_2019_readme`
- `ers_food_access_2019_variablelookup`
- `ers_food_access_2025_sram_driving_distance_data`
- `ers_food_access_2025_sram_general_tract_characteristics_data`
- `ers_food_access_2025_sram_straight_line_distance_data`
- `ers_food_access_2025_sram_variable_lookup_driving_distance`
- `ers_food_access_2025_sram_variable_lookup_general_tract_characteristics`
- `ers_food_access_2025_sram_variable_lookup_straight_line_distance` 



