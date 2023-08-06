
# http://www.bitboost.com/ref/international-address-formats.html
# Street / PO Box
# Appt.
# Postal code - How to do zip+4 genericlly?

# City
# State

def postal_code(country='us', extended=False):
    """docstring for postal_code"""
    from phony.us.location import postal_code
    return postal_code(extended=extended)

def street_name(country='us'):
    from phony.us.location import street_name
    return street_name()

def street_address(country='us'):
    from phony.us.location import street_address
    return street_address()

def secondary_address(country='us'):
    from phony.us.location import secondary_address
    return secondary_address()

def city_name(country='us'):
    from phony.us.location import city_name
    return city_name()

def address(country='us'):
    from phony.us.location import address
    return address()
