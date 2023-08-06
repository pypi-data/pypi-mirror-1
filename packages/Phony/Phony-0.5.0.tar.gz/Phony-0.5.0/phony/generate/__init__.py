
def csv_formatter(pattern, **kwargs):
    return "1, 2, 3"

def generate(pattern=None, quantity=10, format='csv', formatter=None, file_name=None, **kwargs):
    output = ""
    if not formatter:
        if format == 'csv':
            formatter = csv_formatter


    for i in range(quantity):
        output += formatter(pattern, **kwargs)

    if not file_name:
        return output
    # else save to file

