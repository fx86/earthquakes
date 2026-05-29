# Earthquakes Data Schema

This document describes the structure and columns of the CSV files in the `earthquakes.data/` folder.

---

## 1. all_earthquakes.csv

**Description**: Main dataset containing earthquake event records from 2015-2018  
**Total Records**: ~1,241,789 rows

### Columns

| Column | Type | Description | Sample Data |
|--------|------|-------------|-------------|
| `depth` | Float | Depth of the earthquake hypocenter in kilometers | `28.9`, `16.36`, `12.3` |
| `depthError` | Float | Uncertainty/error margin for depth measurement in kilometers | `0.3`, `0.88`, `0.4` |
| `dmin` | Float | Horizontal distance from the epicenter to the nearest station (degrees) | `0.05199`, `0.07658` |
| `gap` | Float | Largest azimuthal gap between azimuthally adjacent stations (degrees) | `46.0`, `38.0` |
| `horizontalError` | Float | Uncertainty in horizontal position (kilometers) | `0.2`, `0.36`, `0.3` |
| `id` | String | Unique identifier for the earthquake event | `ak11715681`, `ci37245567` |
| `latitude` | Float | Geographic latitude of the epicenter (decimal degrees) | `61.3325`, `34.3926667` |
| `locationSource` | String | Network code that provided the location | `ak`, `ci`, `nc` |
| `longitude` | Float | Geographic longitude of the epicenter (decimal degrees) | `-147.9983`, `-118.9808333` |
| `mag` | Float | Magnitude of the earthquake | `1.2`, `1.36`, `0.8` |
| `magError` | Float | Uncertainty in magnitude calculation | `0.052`, `0.145` |
| `magNst` | Float | Number of stations used to calculate magnitude | `15.0`, `27.0` |
| `magSource` | String | Network code for the magnitude source | `ak`, `ci`, `nc` |
| `magType` | String | Method/type used to calculate magnitude (ml=local, md=duration, etc.) | `ml`, `md` |
| `source_network` | String | Primary seismic network that reported the event | `ak`, `ci`, `nc` |
| `num_of_nw_stations` | Integer | Number of network stations that detected the event | `38`, `29` |
| `place` | String | Human-readable description of the earthquake location | `"59km ESE of Butte, Alaska"`, `"6km W of Fillmore, CA"` |
| `rms` | Float | Root mean square travel time residual (seconds) - measure of fit quality | `0.45`, `0.29`, `0.51` |
| `status` | String | Review status of the event | `reviewed`, `automatic` |
| `time` | Timestamp | Date and time when the earthquake occurred (UTC) | `2015-09-19 23:59:29.000` |
| `type` | String | Type of seismic event | `earthquake` |
| `updated` | Timestamp | Last time the event information was updated (UTC) | `2015-09-24T23:57:41.501Z` |
| `country` | String | Country where the earthquake occurred | `United States of America` |
| `year` | Integer | Year of the earthquake event | `2015`, `2016`, `2017` |
| `continent` | String | Continent where the earthquake occurred | `North America`, `Asia`, `Africa` |

---

## 2. seismic_networks.csv

**Description**: Reference data for seismic monitoring networks worldwide  
**Total Records**: ~1,625 networks

### Columns

| Column | Type | Description | Sample Data |
|--------|------|-------------|-------------|
| `Description` | String | Full name and description of the seismic network | `"Generic Asian Strong Motion Network"`, `"Anchorage Strong Motion Network"` |
| `End Year` | Integer | Year when the network ceased operations (2500 indicates still active) | `2500`, `2015` |
| `Network` | String | Short code/identifier for the network (2-3 characters) | `A`, `AA`, `AB`, `AK` |
| `Reports` | String | Whether the network submits reports (Y/N) | `N`, `Y` |
| `Start Year` | Integer | Year when the network began operations | `1970`, `1995`, `2003` |
| `Stations` | Integer | Number of seismic stations in the network | `0`, `150`, `4758` |
| `type` | String | Type of network (permanent, virtual, temporary) | `perm_nw`, `virt_nw`, `temp_nw` |

---

## 3. countries-continents.csv

**Description**: Mapping of countries to their respective continents  
**Total Records**: ~465 entries

### Columns

| Column | Type | Description | Sample Data |
|--------|------|-------------|-------------|
| `country` | String | Name of the country or territory | `Algeria`, `United States of America`, `Kuril Islands` |
| `continent` | String | Continent where the country is located | `Africa`, `North America`, `Asia`, `Europe` |

**Note**: Some entries may represent regions or island groups rather than sovereign countries (e.g., "Kuril Islands", "Central")

---

## Data Relationships

- `all_earthquakes.country` can be joined with `countries-continents.country`
- `all_earthquakes.source_network` can be joined with `seismic_networks.Network`
- `all_earthquakes.continent` is derived from the country-continent mapping

## Data Quality Notes

- Empty/null values appear in several columns (especially `dmin`, `gap`, `magError`, `magNst`)
- Year 2500 in `seismic_networks.End Year` indicates currently active networks
- Some earthquakes may not have country information if they occurred in international waters
- The `place` field provides human-readable location context
