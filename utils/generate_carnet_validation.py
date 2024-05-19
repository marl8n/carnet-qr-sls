from utils import get_data_from_carnet

def generate_carnet_validation(carnet):
    """
    Generate a carnet validation code
    YYYY = Year
    CC = Career code
    NNN = Student number
    A = Validation code
    Get YYYYCCNNNA using vectors
    """
    carnet_data = get_data_from_carnet(carnet)

    # Generate A using vectors
    a = carnet_data['year'] + carnet_data['career'] + carnet_data['number']
    a = int(a) % 10

    return f'{carnet}{a}'