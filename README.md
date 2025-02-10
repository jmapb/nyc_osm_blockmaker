# NYC OSM Blockmaker

Script for downloading New York City building footprints and converting them to OpenStreetMap format.

##### Usage:

`nyc_osm_blockmaker.py block [nyc_geoservice_api_key]`

`block` should be a 6-digit code that specifies a city block -- 1 digit for the borough (1=Manhattan, 2=Bronx, 3=Brooklyn, 4=Queens, 5=Staten Island) and 5 for the block number within that borough. Additional digits can be added to request a partial block, up to a full 9-digit BBL (borough-block-lot) code.

All building footprints that match the requested block will be converted to OpenStreetMap features and saved as a single `.osm` file. Building ways and multipolygons will be tagged with `building=yes`, `height`, and `nycdoitt:bin`, as in the original NYC building import (see https://github.com/osmlab/nycbuildings).

Specify a `nyc_geoservice_api_key` to add addresses from NYC's Geoservice API to the footprint features. See https://geoservice.planning.nyc.gov/Register to request a Geoservice API key. Buildings with only a single address will be tagged with `addr:housenumber`, `addr:street`, and `addr:postcode`. (Buildings with multiple possible addresses will remain untagged -- address data for these should be determined by survey.) 

##### Dependencies:

 * Python Requests (https://github.com/psf/requests)
 * NYC building footprints dataset (https://data.cityofnewyork.us/City-Government/Building-Footprints/5zhs-2jue/)
 * NYC Geoservice API (https://geoservice.planning.nyc.gov/)
