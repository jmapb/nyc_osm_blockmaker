# NYC OSM Blockmaker

Download New York City building footprints and convert to OpenStreetMap format

### Usage:

`nyc_osm_blockmaker.py block [nyc_geoservice_api_key]`

* `block` should be a 6-digit code that specifies a city block -- 1 digit for the borough (1=Manhattan, 2=Bronx, 3=Brooklyn, 4=Queens, 5=Staten Island) and 5 for the block number within that borough. Additional digits can be appended to request a partial block, up to a full 9-digit BBL (borough-block-lot) code.\
All building footprints that match the requested block will be converted to OpenStreetMap features and saved in a single `.osm` file. Building ways and multipolygons will be tagged with `building=yes`, `height`, and `nycdoitt:bin`, as in the original NYC building import. (See https://github.com/osmlab/nycbuildings.)

* `nyc_geoservice_api_key` is optional. If specified, will be used to add addresses from NYC's Geoservice API to the footprint features. (See https://geoservice.planning.nyc.gov/Register to request a Geoservice API key.) Buildings with only a single address will be tagged with `addr:housenumber`, `addr:street`, and `addr:postcode`. Buildings with multiple possible addresses will remain untagged -- address data for these is best determined by survey.\
If no API key is specified on the command line, the environment variable GEOSERVICE_API_KEY will be used, if found. Passing a single char as the API key on the command line (eg `nyc_osm_blockmaker.py 101020 -`) will prevent checking for this environment variable.

### Examples:

```
> python nyc_osm_blockmaker.py 101020
BIN 1024771
BIN 1076194
BIN 1024772
BIN 1087187
BIN 1024777
BIN 1024778
BIN 1024779
BIN 1076195
BIN 1024781
BIN 1024782
BIN 1024783
BIN 1024784
BIN 1024786

Processed 13 footprints
Wrote blockmaker_101020.osm with 116 nodes, 13 ways, 0 multipolygons
```

```
> python nyc_osm_blockmaker.py 506259 GEOSERVICE_API_KEY_HERE
BIN 5124085, 260 Detroit Avenue
BIN 5080631, 250 Detroit Avenue
BIN 5169167, 246 Detroit Avenue
BIN 5164510, 244 Detroit Avenue
BIN 5080632, 240 Detroit Avenue
BIN 5112467, 236 Detroit Avenue
BIN 5169738, not tagging garage address 234 GARAGE Detroit Avenue
BIN 5104432, multipolygon with 1 inner way, not tagging address (multiple addresses found)
BIN 5080634, 100 Jefferson Boulevard

Processed 9 footprints
Wrote blockmaker_506259.osm with 101 nodes, 10 ways, 1 multipolygon
```

```
> python nyc_osm_blockmaker.py 30458603 GEOSERVICE_API_KEY_HERE
BIN 3405401, not tagging address (none found)
BIN 3327531, multipolygon with 4 inner ways, 888 Fountain Avenue
BIN 3405182, not tagging address (none found)
BIN 3327532, 11655 Seaview Avenue

Processed 4 footprints
Wrote blockmaker_30458603.osm with 175 nodes, 8 ways, 1 multipolygon
```

### Dependencies:

 * Python Requests (https://github.com/psf/requests)
 * NYC building footprints dataset (https://data.cityofnewyork.us/City-Government/Building-Footprints/5zhs-2jue/)
 * NYC Geoservice API (https://geoservice.planning.nyc.gov/)
