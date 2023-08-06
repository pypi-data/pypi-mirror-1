from random import choice
import re

def _random_number(matchobj):
    return str(choice(range(1, 10)))

def numerify(number_string):
    return re.sub(r'\#', _random_number, number_string)

# TODO: letterify
