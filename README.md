# resto-voronoi

```mermaid
graph TD
    overlap([compute_overlaps])
    swept_data[\swept data/]
    border_shape[\border shapes/]
    census_shape[\census shapes/]
    population[\population/]
    vor([Vor])
    swept_data --> Location
    border_shape --> Location
    Location --> vor
    vor -->VorRegion
    census_shape --> CensusArea
    population --> CensusArea
    VorRegion --> overlap
    CensusArea --> overlap
    overlap --> PopRegion
```


## Census data

Population data is sourced from Statistics Canada and the US Census Bureau, links below. Population data is pre-processed -- see `population/extract_pop_{canada, us}.py` -- into a simpler format: a list of (id, population) pairs. For Canada, each id corresponds to a "dissemination area"; for the US, each id corresponds to a "Census block".

### Canada
- [Statistics Canada, 2021 Census of Population](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/prof/index.cfm?Lang=E)
- Province-level population:
    - "Census Profile, 2021 - Canada, Provinces and Territories"
    - Catalogue number: 98-401-X2021001	
    - Extract CSV into `data/input/census/canada/98-401-X2021001_eng_CSV/`
- Dissemination area population
    - "Census Profile, 2021 - Canada, Provinces, Territories, Census Divisions, Census Subdivisions and Dissemination Areas"
    - Catalogue number: 98-401-X2021006
    - Extract CSV into `data/input/census/canada/98-401-X2021006_eng_CSV/`

### United States
[2020 Census: Redistricting File (Public Law 94-171) Dataset](https://www.census.gov/data/datasets/2020/dec/2020-census-redistricting-summary-file-dataset.html)
- [Data files direct link](https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/)
- [Technical documentation](https://www2.census.gov/programs-surveys/decennial/2020/technical-documentation/complete-tech-docs/summary-file/2020Census_PL94_171Redistricting_StatesTechDoc_English.pdf) for data files
- Extract each state data file `{state}2020.pl.zip` into `data/input/census/us/{state}2020.pl/`.

## Geographic shapes
Boundary files for states/provinces/territories and census dissemination areas/census blocks.
### Canada
Statistics Canada [2021 Census - Boundary files](https://www12.statcan.gc.ca/census-recensement/2021/geo/sip-pis/boundary-limites/index2021-eng.cfm?year=21)
- Type: Digital Boundary File
- Format: Shapefile

For province boundaries:
- Administrative boundaries: Provinces/Territories
- Extract `lpr_000a21a_e.zip` to `data/input/shapes/canada`
For census dissemination area boundaries:
    - Statistical boundaries: Dissemination areas
    - Extract `lda_000a21a_e.zip` to `data/input/shapes/canada_census`

### United States
Census Bureau [Cartographic boundary files]: https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.2022.html

For states:
- "States 1:20,000,000 (national)": `cb_2022_us_state_20m.zip`
- extract to `data/input/shapes/us/cb_2022_us_state_20m.*`
For census blocks:
- "Census Block Groups 1:500,000 (state)": `cb_2021_{code}_bg_500k.zip`
- extract to `data/input/shapes/us_census/cb_2021_{code}_bg_500k/`
