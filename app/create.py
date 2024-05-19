import json
import logging
import os
import time
from io import BytesIO
import qrcode

from botocore.exceptions import ClientError
import boto3
dynamodb = boto3.resource('dynamodb')


import re

def get_data_from_carnet(carnet):
    # YYYY = Year
    # CC = Career code
    # NNN = Student number
    # YYYY CC NNN
    regex = r'(\d{4}) (\d{2}) (\d{3})'
    match = re.match(regex, carnet)
    if match is not None:
        year, career, number = match.groups()
        return {
            'year': year,
            'career': career,
            'number': number
        }
    else:
        pass
        # handle the case where the carnet does not match the regex
        # for example, you could raise an exception or return a default value

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

# 2017 hasta 2024 máximo 150

def create(event, context):
    data = event
    if 'carnet' not in data:
        logging.error("Validation Failed")
        raise ClientError("Couldn't create without carnet.")
    
    if 'name' not in data:
        logging.error("Validation Failed")
        raise ClientError("Couldn't create without name.")

    # Get carnet data
    carnet = data['carnet']
    carnet_data = get_data_from_carnet(carnet)

    timestamp = str(time.time())
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Create QR code image
    carnet_qr = qrcode.make(carnet)

    # Save QR code image to BytesIO object
    qr_code_io = BytesIO()
    carnet_qr.save(qr_code_io, format='SVG')
    qr_code_io.seek(0)

    # Create an s3 Client
    s3 = boto3.client('s3')

    # Upload the QR code image to S3
    s3.upload_fileobj(qr_code_io, os.environ['S3_BUCKET'], f'{carnet}.svg')
    qr_url = s3.generate_presigned_url('get_object', Params={'Bucket': os.environ['S3_BUCKET'], 'Key': f'{carnet}.svg'}, ExpiresIn=3600)

    # Create id
    carnet_id = generate_carnet_validation(carnet)

    item = {
        'id': carnet_id,
        'carnet': data['carnet'],
        'name': data['name'],
        'year': carnet_data['year'],
        'career': carnet_data['career'],
        'number': carnet_data['number'],
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    # write the todo to the database
    table.put_item(Item=item)

    # create a response
    response = {
        "statusCode": 201,
        "body": json.dumps({
            "message": "Carnet created successfully",
            "user": item,
            "qr_url": qr_url
        })
    }

    return response
