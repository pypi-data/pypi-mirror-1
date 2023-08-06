from random import choice

def name(country='us', prefix=False, suffix=False):
    """
    Create a phony name
    """
    from phony.us.people import first_names, last_names
    # TODO: Check the prefix
    # TODO: Check the suffix
    name = choice(first_names) + " " + choice(last_names)
    return name

# TODO: male_name, female_name

def identification_number(country='us'):
    """
    Generate a phony identification number.
    """
    from phony.us.people import identification_number

    return identification_number()

