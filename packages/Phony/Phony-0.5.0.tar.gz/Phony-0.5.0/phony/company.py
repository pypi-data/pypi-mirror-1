from random import choice

def company_name(country='us', suffix=False):
    """
    Create a phony name
    """
    from phony.us.company import company_prefixes, company_names, company_suffix
    return "%s %s %s" % (choice(company_prefixes), choice(company_names), choice(company_suffix))
