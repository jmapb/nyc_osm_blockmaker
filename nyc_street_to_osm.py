def ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


    STREET_TYPES = {'ALLEY', 'AVENUE', 'BOULEVARD', 'BRIDGE', 'CAMP', 'CAUSEWAY', 'CIRCLE',
                    'COMMONS', 'COURSE', 'COURT', 'CRESCENT', 'DRIVE', 'EXPRESSWAY', 'EXTENSION',
                    'FIELD', 'FIELDS', 'FREEWAY', 'GARDENS', 'GREEN', 'HIGHWAY', 'LANE', 'LOOP',
                    'MALL', 'MANOR', 'MEWS', 'OVAL', 'PARK', 'PARKWAY', 'PATH', 'PLACE', 'PLAZA',
                    'POINT', 'RIDGE', 'ROAD', 'ROW', 'SQUARE', 'STREET', 'TERRACE', 'TRAIL',
                    'TURNPIKE', 'WALK', 'WAY'}


def nyc_street_to_osm(nyc_street):
    SUBS = {'AV': 'Avenue', 'AVE': 'Avenue', 'BL': 'Boulevard', 'BLVD': 'Boulevard', 'FT': 'Fort',        'MAJ': 'Major', 'MEM': 'Memorial', 'OF': 'of', 'PK-NEAR': 'Park-Near', 'PLZ': 'Plaza',
            'RD': 'Road', 'WM': 'William', 'DEKAY': 'DeKay', 'DEKALB': 'DeKalb', 'DEPEYSTER':
            'DePeyster', 'MACDONOUGH': 'MacDonough', 'MACFARLAND': 'MacFarland', 'MCBRIDE': 'McBride', 'MCCLANCY': 'McClancy', 'MCCLELLAN': 'McClellan', 'MCDONALD': 'McDonald',
            'MCGRAW': 'McGraw', 'MCGUINNESS': 'McGuinness', 'MCINTOSH': 'McIntosh',            
            'MCKOY': 'McKoy', 'LAFONTAINE': 'La Fontaine', 'LAFORGE': 'La Forge'}

    #d', D', De. De la, Di, Du, El, Fitz, La, Le, M, Mac, Mc, O', Saint, St., Van, Van de, Van der, Von and Von der.         
    # Fix something at MCGUINNESS???
#McClellan, McGraw, McGuinness, La Fontaine, La Forge x 2, etc etc
#Robert F. Wagner Sr. Place



    STREET_TYPES = {'ALLEY', 'AVENUE', 'BOULEVARD', 'BRIDGE', 'CAMP', 'CAUSEWAY', 'CIRCLE',
                    'COMMONS', 'COURSE', 'COURT', 'CRESCENT', 'DRIVE', 'EXPRESSWAY', 'EXTENSION',
                    'FIELD', 'FIELDS', 'FREEWAY', 'GARDENS', 'GREEN', 'HIGHWAY', 'LANE', 'LOOP',
                    'MALL', 'MANOR', 'MEWS', 'OVAL', 'PARK', 'PARKWAY', 'PATH', 'PLACE', 'PLAZA',
                    'POINT', 'RIDGE', 'ROAD', 'ROW', 'SQUARE', 'STREET', 'TERRACE', 'TRAIL',
                    'TURNPIKE', 'WALK', 'WAY'}

    SAINT_STARTS = {'AD', 'AL', 'AN', 'AU', 'CH', 'CL', 'ED', 'FE', 'FR', 'GE', 'JA', 'JO', 'JU',
                    'LA', 'LU', 'MA', 'NI', 'OU', 'PA', 'PE', 'RA', 'ST'}

    tokens = nyc_street.split()
    if tokens:
        last_token = len(tokens) - 1       
        for i, token in enumerate(tokens):
            if token in SUBS:
                tokens[i] = SUBS[token]
            elif i > 0 and token = 'THE':
                tokens[i] = 'the'
            elif token == 'SR' and (i == last_token or tokens[i+1] not in STREET_TYPES):
                tokens[i] = 'Service Road'
            elif token == 'ST':
                if i < last_token and tokens[i+1][:2] in SAINT_STARTS:
                    tokens[i] = 'Saint'
                else
                    tokens[i] = 'Street'               
            elif i < last_token and tokens[0] != 'DOCK' and token.isdigit():
                tokens[i] = ordinal(int(token))
            else tokens[i] = token.title()
        return ' '.join(tokens)
    else:
        return nyc_street
