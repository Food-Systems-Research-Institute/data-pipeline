# Agricultural data collection
A reusable data pipeline for collecting, processing, and organizing agricultural data from diverse sources, including APIs, web scraping, and bulk data downloads. The project aims to provide a central collection of agricultural datasets and establish a scalable foundation for data access, analysis, and research at the Vermont Data Collaborative.

# Collection Scripts
- `collect_nass.py`
- `collect_farm_income.py`
- `collect_food_access_atlas.py`
- `collect_feeding_america.py`

---

# 1. `collect_nass.py` - USDA National Agricultural Statistics Service

### Description

Collects agricultural census and survey data from the USDA National Agricultural Statistics Service (NASS) using the publicly available Quick Stats API.

NASS provides a broad range of agricultural statistics, including:
- **Farm characteristics:** Number of farms, farm size, land use, ownership, and operator demographics.
- **Crop production:** Acres planted and harvested, production quantities, yields, and commodity sales.
- **Livestock:** Inventory, production, sales, and animal product statistics.
- **Farm economics:** Income, expenses, production costs, government payments, and market values.
- **Agricultural demographics:** Characteristics of farm operators and agricultural workers.

Data are available at multiple geographic levels, including national, state, and county, depending on the dataset and reporting year.

### Potential Uses

- Analyze changes in agricultural production over time.
- Compare farm economics across states and counties.
- Examine trends in farm size, land ownership, and agricultural demographics.
- Identify regional differences in crop and livestock production.
- Study relationships between agricultural production, expenses, and farm income.
- Track changes in Vermont and Northeast agricultural industries.

### Data Collection

This script uses the NASS Quick Stats API. Since the API does not provide built-in pagination and limits responses to 50,000 records, the script divides large queries into smaller, filtered requests.

Each request is initially stored in its own DuckDB table. There is also an option to combine the resulting tables into a single table and optionally remove the original request tables.

Use `collect_nass()` to run the collection.

### Prerequisites

Before running the NASS data collection script, ensure you have:

- Python installed.
- [uv](https://docs.astral.sh/uv/) installed for Python environment and dependency management.
- A USDA NASS Quick Stats API key. Register at the [NASS Quick Stats website](https://quickstats.nass.usda.gov/).
- Internet access to make API requests.

### Setup

1. Clone the repository and navigate to the project directory.

2. Install project dependencies:

   `uv sync`

3. Create a `.env` file in the directory expected by the API script and add your NASS API key:

   `NASS_API_KEY=your_api_key_here`

4. Ensure `.env` is excluded from version control. Never commit or share your API key.

5. Ensure the configured DuckDB database path is accessible.

### Running the Script

From the project root, run:

    uv run python -c 'from api.collect_nass import collect_nass; collect_nass(years=[2017, 2022])'

**Arguments(years is the only required paramater):**

| Argument | Description | Default |
|---|---|---|
| `years` | List of years to collect | (REQUIRED) |
| `source` | NASS data source (e.g., `CENSUS`, `SURVEY`) | `CENSUS` |
| `sector` | NASS data group (e.g., `ECONOMICS`, `CROPS`) | ALL SECTORS |
| `states` | List of states to collect | ALL STATES IN THE NORTHEAST |
| `dry_run` | for testing, only requests data count without creating tables | True |
| `combine_tables` | combine all requests into one table(True/False) | False |
| `drop_sources` | Drop original request tables(True/False) | False |
| `**filters` | Any further filtering. See `nass_api_parameters.csv` for more query options| `agg_level_desc = "STATE"` |


### Important Notes

- NASS API requests are subject to a 50,000-record response limit.
- Large queries may need to be subdivided using additional filters.
- Collection times depend on dataset size and API response times.

---

# 2. `collect_farm_income.py` - USDA ERS Farm Income and Wealth Statistics

### Description

Scrapes the USDA Economic Research Service (ERS) Farm Income and Wealth Statistics data download page to retrieve the latest available release and load the data into `agData.duckdb`.

The dataset provides historical estimates of U.S. and state-level agricultural income and financial conditions. It includes information on:

- **Farm income:** Net farm income, net cash farm income, and farm-sector returns.
- **Cash receipts:** Revenue generated from agricultural commodities and agricultural product sales.
- **Production expenses:** Costs associated with operating agricultural businesses, including inputs, labor, and other production expenses.
- **Government payments:** Federal government payments and agricultural assistance programs.
- **Farm assets:** Land, buildings, machinery, livestock, financial assets, and other agricultural resources.
- **Farm debt:** Outstanding agricultural debt and liabilities.
- **Financial ratios:** Measures of farm profitability, liquidity, and solvency.

The dataset includes historical estimates and forecasts, which are periodically revised as new information becomes available.

**Geographic coverage:** United States and individual states. ERS Farm Income and Wealth Statistics do not provide county-level farm-sector income estimates.

### Potential Uses

- Analyze changes in farm income and profitability over time.
- Compare agricultural income and expenses between states.
- Examine the financial health and economic stability of agricultural industries.
- Study the effects of production expenses and government payments on farm income.
- Evaluate trends in agricultural debt, assets, and financial risk.
- Identify economic pressures affecting farmers and agricultural businesses.
- Compare Vermont's agricultural economy with other states and national trends.

### Data Collection

The script scrapes the ERS download page to identify and retrieve the latest available data files. The downloaded data are processed and loaded into DuckDB.

This approach allows the database to be updated as ERS publishes new releases without manually locating and downloading each file.

### Running the Script

From the project root, run:

`uv run python -c 'from ers.collect_farm_income import run_collect; run_collect()'`

### Important Notes

- The script retrieves the latest available release rather than a user-specified year.
- ERS periodically revises historical estimates.
- Geographic coverage is limited to national and state-level estimates.
- Refer to the [USDA ERS Farm Income and Wealth Statistics](https://www.ers.usda.gov/data-products/farm-income-and-wealth-statistics) documentation for variable definitions and methodology.

---

# 3. `collect_food_access_atlas.py`

To run from terminal use:
`uv run python -c 'from ers.collect_food_access_atlas import collect_food_access_atlas; run_collect()'`

Tables created include:
- `ers_food_access_2019_food_access_research_atlas`
- `ers_food_access_2019_readme`
- `ers_food_access_2019_variablelookup`
- `ers_food_access_2025_sram_driving_distance_data`
- `ers_food_access_2025_sram_general_tract_characteristics_data`
- `ers_food_access_2025_sram_straight_line_distance_data`
- `ers_food_access_2025_sram_variable_lookup_driving_distance`
- `ers_food_access_2025_sram_variable_lookup_general_tract_characteristics`
- `ers_food_access_2025_sram_variable_lookup_straight_line_distance` 

# 4. `collect_feeding_america.py`

To run from terminal use:
`uv run python -c 'from ers.collect_feeding_america import collect_feeding_america; run_collect()'`

request data from `https://feedingamerica.az1.qualtrics.com/jfe/form/SV_5tJt5m9K62hRC6N` and move the unzipped folder into data/raw/

