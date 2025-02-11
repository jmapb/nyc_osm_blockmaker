import sys
import requests

GEOSERVICE_API = 'https://geoservice.planning.nyc.gov/geoservice/geoservice.svc/'
FOOTPRINTS_API = 'https://data.cityofnewyork.us/resource/5zhs-2jue.json'

nodes = {}
ways = []
multipolygons = []
footprint_count = 0
block = ''
geoservice_api_key = ''

if len(sys.argv) > 1:
    block = sys.argv[1]
    if len(sys.argv) > 2:
        geoservice_api_key = sys.argv[2]

if len(block) < 6:
    print("Usage:")
    print("  {} block [nyc_geoservice_api_key]".format(sys.argv[0]))
    print("  Block code must be 6 digits long (1 for borough + 5 for block)")
    sys.exit(1)

footprints_response = requests.get("{}?$where=starts_with(base_bbl,'{}')".format(FOOTPRINTS_API, block))
footprints_response.raise_for_status()
for fp in footprints_response.json():
    fp_ways = []
    addr_desc = ''
    for ring in fp['the_geom']['coordinates'][0]:
        ring_node_ids = []
        for lonlat in ring:
            nodes_key = tuple(lonlat)
            if nodes_key in nodes:
                node_id = nodes[nodes_key]
            else:
                node_id = len(nodes) + 1
                nodes[nodes_key] = node_id
            ring_node_ids.append(node_id)
        if ring_node_ids:
            fp_ways.append(ring_node_ids)
    if fp_ways:
        footprint_count += 1
        tags = {'building': 'yes'}
        tags['height'] = round(float(fp['heightroof']) * 0.3048, 1)
        tags['nycdoitt:bin'] = fp['bin']
        if len(geoservice_api_key) > 1:
            gs_response = requests.get("{}Function_BIN?BIN={}&TPAD=Y&Key={}".format(GEOSERVICE_API, fp['bin'], geoservice_api_key))
            if gs_response.status_code == requests.codes.ok:
                gs_addresses = gs_response.json()['display']['AddressRangeList']
                gs_addresses = [a for a in gs_addresses if a['low_address_number'].strip() != '']
                if gs_addresses:
                    if (len(gs_addresses) == 1) and (gs_addresses[0]['low_address_number'] == gs_addresses[0]['high_address_number']):
                        tags['addr:housenumber'] = gs_addresses[0]['low_address_number'].strip()
                        tags['addr:street'] = gs_addresses[0]['street_name'].strip().title()
                        addr_desc = ', {} {}'.format(tags['addr:housenumber'], tags['addr:street'])
                        gs_response = requests.get("{}Function_1B?Borough={}&AddressNo={}&StreetName={}&TPAD=Y&Key={}".format(GEOSERVICE_API, block[0], tags['addr:housenumber'], tags['addr:street'], geoservice_api_key))
                        gs_addr_info = gs_response.json()['display']
                        tags['addr:postcode'] = gs_addr_info['out_zip_code']
                        # Uncomment to include addr:city from NYC Geoservice data
                        #tags['addr:city'] = gs_addr_info['out_usps_city_name'].strip().title()
                    else:
                        addr_desc = ', not tagging address (multiple addresses found)'
                else:
                    addr_desc = ', not tagging address (none found)'
            else:
                if gs_response.status_code == requests.codes.unauthorized:
                    print("Geoservice address query returned status '401 Unauthorized', probably an invalid API key, skipping address lookups")
                else:
                    print("Geoservice address query returned status '{}', skipping address lookups".format(gs_response.status_code))
                geoservice_api_key = ''

        if len(fp_ways) == 1:
            print("BIN {}{}".format(fp['bin'], addr_desc))
            ways.append([tags, fp_ways[0]])
        else:
            print("BIN {}, multipolygon with {} inner ways{}".format(fp['bin'], len(fp_ways)-1, addr_desc))
            tags['type'] = 'multipolygon'
            multipolygons.append([tags, len(ways)+1, len(fp_ways)])
            ways = ways + [[{}, w] for w in fp_ways]
    else:
        print("BIN {} skipped, no valid geometry found".format(fp['bin']))

if footprint_count:
    print("Processed {} footprints, writing block{}.osm with {} nodes, {} ways, {} multipolygons".format(footprint_count, block, len(nodes), len(ways), len(multipolygons)))
    f = open("block{}.osm".format(block), "w")
    f.write("<?xml version='1.0' encoding='UTF-8'?>\r")
    f.write("<osm version='0.6' generator='nyc_osm_blockmaker' upload='false'>\r")
    for lonlat, id in nodes.items():
        f.write("  <node id='-{}' action='modify' visible='true' lat='{}' lon='{}' />\r".format(id, lonlat[1], lonlat[0]))
    for way_id, way in enumerate(ways):
        f.write("  <way id='-{}' action='modify' visible='true'>\r".format(way_id + 1))
        for n in way[1]:
            f.write("    <nd ref='-{}' />\r".format(n))
        for k, v in way[0].items():
            f.write("    <tag k='{}' v='{}' />\r".format(k, v))
        f.write("  </way>\r")
    for rel_id, rel in enumerate(multipolygons):
        f.write("  <relation id='-{}' action='modify' visible='true'>\r".format(rel_id + 1))
        f.write("    <member type='way' ref='-{}' role='outer' />\r".format(rel[1]))
        for i in range(rel[1] + 1, rel[1] + rel[2]):
            f.write("    <member type='way' ref='-{}' role='inner' />\r".format(i))
        for k, v in rel[0].items():
            f.write("    <tag k='{}' v='{}' />\r".format(k, v))
        f.write("  </relation>\r")
    f.write("</osm>")
    f.close()
else:
    print("No footprints found")
    