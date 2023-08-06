# Generate phony names and identification numbers for people.
from phony.people import name, identification_number
print name()
print identification_number()

# Generate phony company names
from phony.company import company_name
print company_name()

# Generate phony phone numbers, with or without an area code
from phony.phone import phone_number
print phone_number(area_code=True)
print phone_number(area_code=False)

# Generate phony street addresses
from phony.location import postal_code, street_address, city_name, secondary_address, address
print address()
print street_address()
print secondary_address()
print city_name()
print postal_code()
print postal_code(extended=True)

# Generate fake domain names, email addresses, and ip addresses
from phony.internet import domain_name, email_address, ip4_address_class_a
from phony.internet import ip4_address_class_b, ip4_address_class_c, ip4_address, ip6_address
print domain_name()
print email_address()
print email_address(free_service=True)
print ip4_address_class_a()
print ip4_address_class_b()
print ip4_address_class_c()
print ip6_address()

# Generate phony words, ala lorem aka dummy text
from phony.lorem import words, sentence, paragraph, paragraphs
print words()
print sentence()
print paragraph()
print paragraphs(count=5)
