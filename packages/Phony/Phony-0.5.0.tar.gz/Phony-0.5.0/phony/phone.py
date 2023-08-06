
def phone_number(country='us', area_code=True):
    """
    Create a phony phone number.
    """
    from phony.us.phone import generate_number
    return generate_number(area_code=area_code)
