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

def ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def nyc_street_to_osm(nyc_street):
    SUBS = {'AV': 'Avenue', 'AVE': 'Avenue', 'BL': 'Boulevard', 'BLVD': 'Boulevard',
        'EXPWY': 'Expressway', 'FT': 'Fort', 'MAJ': 'Major', 'MEM': 'Memorial',
        'OF': 'of', 'PK-NEAR': 'Park-Near', 'PLZ': 'Plaza', 'RD': 'Road', 'WM':
        'William', 'DEKAY': 'DeKay', 'DEKALB': 'DeKalb', 'DEPEYSTER': 'DePeyster',
        'MACDONOUGH': 'MacDonough', 'MACFARLAND': 'MacFarland', 'MCBRIDE': 'McBride',
        'MCCLANCY': 'McClancy', 'MCCLELLAN': 'McClellan', 'MCDONALD': 'McDonald',
        'MCGRAW': 'McGraw', 'MCGUINNESS': 'McGuinness', 'MCINTOSH': 'McIntosh',
        'MCKOY': 'McKoy', 'LAFONTAINE': 'La Fontaine', 'LAFORGE': 'La Forge'}
    DIRECTIONS = {'E': 'East', 'N': 'North', 'S': 'South', 'W': 'West'}
    SAINT_STARTS = {'AD', 'AL', 'AN', 'AU', 'CH', 'CL', 'ED', 'FE', 'FR', 'GE', 'JA',
        'JO', 'JU', 'LA', 'LU', 'MA', 'NI', 'OU', 'PA', 'PE', 'RA', 'ST'}
    tokens = nyc_street.split()
    for i, token in enumerate(tokens):
        if token in SUBS:
            tokens[i] = SUBS[token]
        elif i > 2 and token in DIRECTIONS:
            tokens[i] = DIRECTIONS[token]
        elif i > 0 and token == 'THE':
            tokens[i] = 'the'
        elif token == 'SR' and (set(tokens[:i]) & {'Expressway', 'Park', 'Parkway'}):
            tokens[i] = 'Service Road'
        elif token == 'ST':
            if i < len(tokens) - 1 and tokens[i+1][:2] in SAINT_STARTS:
                tokens[i] = 'Saint'
            else:
                tokens[i] = 'Street'
        elif token.isdigit() and i < len(tokens) - 1 and tokens[0] != 'Dock':
            tokens[i] = ordinal(int(token))
        else:
            tokens[i] = token.title()
    return ' '.join(tokens).replace('M L King', 'Martin Luther King')

def pluralize(n, unit):
    return '{} {}{}'.format(n, unit, '' if n == 1 else 's')

if len(sys.argv) > 1:
    block = sys.argv[1]
    if len(sys.argv) > 2:
        geoservice_api_key = sys.argv[2]

if len(block) < 6:
    print("Usage:")
    print("  {} block [nyc_geoservice_api_key]".format(sys.argv[0]))
    print("  Block code must be 6 digits long (1 for borough + 5 for block)")
    sys.exit(1)

fp_response = requests.get("{}?$where=starts_with(base_bbl,'{}')".format(FOOTPRINTS_API, block))
fp_response.raise_for_status()
for fp in fp_response.json():
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
                        housenumber = gs_addresses[0]['low_address_number'].strip()
                        street = nyc_street_to_osm(gs_addresses[-1]['street_name'])
                        if 'GAR' in housenumber:
                            addr_desc = ', not tagging garage address {} {}'.format(housenumber, street)
                        else:
                            addr_desc = ', {} {}'.format(housenumber, street)
                            tags['addr:housenumber'] = housenumber
                            tags['addr:street'] = street
                            gs_response = requests.get("{}Function_1B?Borough={}&AddressNo={}&StreetName={}&TPAD=Y&Key={}".format(GEOSERVICE_API, block[0], housenumber, street, geoservice_api_key))
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
            print("BIN {}, multipolygon with {}{}".format(fp['bin'], pluralize(len(fp_ways)-1, 'inner way'), addr_desc))
            tags['type'] = 'multipolygon'
            multipolygons.append([tags, len(ways)+1, len(fp_ways)])
            ways = ways + [[{}, w] for w in fp_ways]
    else:
        print("BIN {} skipped, no valid geometry found".format(fp['bin']))

if footprint_count:
    print("\nProcessed {}".format(pluralize(footprint_count, 'footprint')))
    filename = 'blockmaker_{}.osm'.format(block)
    with open(filename, "w") as f:
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
    print("Wrote {} with {} nodes, {}, {}".format(filename, len(nodes), pluralize(len(ways), 'way'), pluralize(len(multipolygons), 'multipolygon')))
else:
    print("No footprints found")
