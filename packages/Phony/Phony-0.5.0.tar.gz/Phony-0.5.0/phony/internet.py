from random import choice

common_tlds = """com org net""".split()

# http://en.wikipedia.org/wiki/List_of_Internet_top-level_domains
other_tlds = """
aero asia biz cat coop edu gov info int jobs mil mobi museum name
pro tel travel arpa
""".split()

all_domains = common_tlds + other_tlds

# If you get bored, add the country TLDs here

def domain_name(country='us', common_tlds_only=True):
    """Create a random domain name."""

    from phony.company import company_name

    name = company_name(country=country).lower().replace(' ', '').replace('.', '')
    if common_tlds_only:
        return "%s.%s" % (name, choice(common_tlds))
    else:
        return "%s.%s" % (name, choice(all_domains))


def user_name_dot_separated(country='us', source_name=None):
    """
    Generate a random 'username'

    Used for the email_address() system, but could be useful for other services

    source is the string to use. Otherwise, generate the random one.

    """
    from phony.people import name

    if not source_name:
        source_name = name(country=country)

    return source_name.lower().replace(' ', '.')


def email_address(country='us', free_service=False, common_tlds_only=None, source_name=None):
    """
    Generate a fake email address.
    """
    user_name_function = choice([user_name_dot_separated]) # Planning ahead. Want to add other types
    user = user_name_function(country=country, source_name=source_name)
    if free_service:
        domain = choice(['gmail.com', 'yahoo.com', 'hotmail.com'])
    else:
        domain = domain_name(country=country, common_tlds_only=common_tlds_only)
    return "%s@%s" % (user, domain)


def ip4_address_class_a():
    """Generate a Class A IP4 address"""
    return "%s.%s.%s.%s" % (
        choice(range(11, 127)), # 10.x.x.x is reserved, so just start at 11
        choice(range(1, 255)),
        choice(range(1, 255)),
        choice(range(1, 255)),
    )


def ip4_address_class_b():
    """Generate a Class B IP4 address"""
    return "%s.%s.%s.%s" % (
        choice(range(128, 191)),
        choice(range(1, 255)),
        choice(range(1, 255)),
        choice(range(1, 255)),
    )


def ip4_address_class_c():
    """Generate a Class C IP4 address"""
    return "%s.%s.%s.%s" % (
        choice(range(193, 223)),
        choice(range(1, 255)),
        choice(range(1, 255)),
        choice(range(1, 255)),
    )

def ip4_address():
    """Generate a random IP4 address."""
    ip_class = choice([ip4_address_class_a, ip4_address_class_b, ip4_address_class_c])
    return ip_class()
ip_address = ip4_address # Default to a random IP4 address

def _random_hex_address():
    a = ""
    for i in range(4):
        a += choice(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"])
    return a

def ip6_address():
    """Generate a random IP6 address."""
    parts = []
    for i in range(8):
        parts.append(_random_hex_address())
    return ":".join(parts)
