import re

def get_data_from_carnet(carnet):
    # YYYY = Year
    # CC = Career code
    # NNN = Student number
    # YYYY CC NNN
    regex = r'(\d{4}) (\d{2}) (\d{3})'
    year, career, number = re.match(regex, carnet).groups()

    return {
        'year': year,
        'career': career,
        'number': number
    }