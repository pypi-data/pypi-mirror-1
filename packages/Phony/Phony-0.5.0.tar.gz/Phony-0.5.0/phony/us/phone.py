from random import choice

def generate_number(area_code=True):
    """Generate a phone number formatted for the U.S.A."""

    number = ""
    if area_code:
        for i in range(0, 3):
            number += str(choice(range(1, 10)))
        number += "-"

    for i in range(0, 3):
        number += str(choice(range(1, 10)))
    number += "-"
    for i in range(0, 4):
        number += str(choice(range(10)))
    return number

