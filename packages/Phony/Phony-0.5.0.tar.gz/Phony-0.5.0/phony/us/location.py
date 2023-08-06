from random import choice
from phony import numerify
from phony.us.people import last_names

city_prefix = """
North East West South New Lake Port
""".split()

city_suffix = """
town ton land ville berg burgh borough bury view port mouth
stad furt chester mouth fort haven side shir
""".split()

street_suffix = """
Alley Avenue Branch Bridge Brook Brooks Burg Burgs Bypass Camp Canyon Cape Causeway
Center Centers Circle Circles Cliff Cliffs Club Common Corner Corners Course Court
Courts Cove Coves Creek Crescent Crest Crossing Crossroad Curve Dale Dam Divide
Drive Drive Drives Estate Estates Expressway Extension Extensions Fall Falls
Ferry Field Fields Flat Flats Ford Fords Forest Forge Forges Fork Forks Fort
Freeway Garden Gardens Gateway Glen Glens Green Greens Grove Groves Harbor
Harbors Haven Heights Highway Hill Hills Hollow Inlet Inlet Island Island
Islands Islands Isle Isle Junction Junctions Key Keys Knoll Knolls Lake Lakes
Land Landing Lane Light Lights Loaf Lock Locks Locks Lodge Lodge Loop Mall Manor
Manors Meadow Meadows Mews Mill Mills Mission Mission Motorway Mount Mountain
Mountain Mountains Mountains Neck Orchard Oval Overpass Park Parks Parkway
Parkways Pass Passage Path Pike Pine Pines Place Plain Plains Plains Plaza
Plaza Point Points Port Port Ports Ports Prairie Prairie Radial Ramp Ranch
Rapid Rapids Rest Ridge Ridges River Road Road Roads Roads Route Row Rue Run
Shoal Shoals Shore Shores Skyway Spring Springs Springs Spur Spurs Square Square
Squares Squares Station Station Stravenue Stravenue Stream Stream Street Street
Streets Summit Summit Terrace Throughway Trace Track Trafficway Trail Trail Tunnel
Tunnel Turnpike Turnpike Underpass Union Unions Valley Valleys Via Viaduct View Views
Village Village  Villages Ville Vista Vista Walk Walks Wall Way Ways Well Wells
""".split()

city_prefix = """
North East West South New Lake Port
""".split()

state_abbr = """
AL AK AS AZ AR CA CO CT DE DC FM FL GA GU HI ID IL IN IA KS KY LA ME MH MD MA MI
MN MS MO MT NE NV NH NJ NM NY NC ND MP OH OK OR PW PA PR RI SC SD TN TX UT VT VI
VA WA WV WI WY AE AA AP
""".split()

def postal_code(extended=False):
    """
    Generate a zipcode.
    """
    if not extended:
        return numerify('#####')
    else:
        return numerify('#####-####')

def city_name():
    """
    Generate a phony city name.
    """
    return choice([
        "%s%s" % (choice(last_names), choice(city_suffix)),
        "%s %s" % (choice(city_prefix), choice(last_names)),
        "%s %s%s" % (choice(city_prefix), choice(last_names), choice(city_suffix)),
    ])

def street_name():
    """
    Generate a random street name.
    """
    return "%s %s" % (choice(last_names), choice(street_suffix))

def street_address():
    """
    Generate a random street address.
    """
    # TODO: What about 123 83th Street or 234 2nd Ave.?
    return "%s %s" % (numerify(choice(["###", "####", '#####'])), street_name())

def secondary_address():
    """
    Generate a random secondary address
    """
    return choice([
        'Apt. %s' % numerify('###'),
        'Suite %s' % numerify('###')
    ])

def address():
    """
    Generate a phony address.
    """
    return choice([
        "%s\n%s %s, %s" % (street_address(), city_name(), choice(state_abbr), postal_code()),
        "%s\n%s\n%s %s, %s" % (secondary_address(), street_address(), city_name(), choice(state_abbr), postal_code()),
    ])
