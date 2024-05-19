import logging
import os
import json
import boto3
from botocore.exceptions import ClientError
from utils import generate_carnet_validation

dynamodb = boto3.resource('dynamodb')

def get(event, context):
    data = event['body']

    if 'carnet' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't create without carnet.")

    id = generate_carnet_validation(data['carnet'])

    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Fetch carnet from the database
    try:
        result = table.get_item(
            Key={
                'id': id
            }
        )
        # Create an s3 Client
        s3 = boto3.client('s3')
        qr_url = s3.generate_presigned_url('get_object', Params={'Bucket': os.environ['S3_BUCKET'], 'Key': f'{data["carnet"]}.svg'}, ExpiresIn=3600)

    except ClientError as e:
        print(e.response['Error']['Message'])
        return {
            "statusCode": 400,
            "body": json.dumps({"error_message": "Could not fetch the carnet"})
        }
    else:
        # Create a response
        response = {
            "statusCode": 200,
            "body": {
                "message": "Carnet fetched successfully",
                "user": result['Item'],
                "qr_url": qr_url
            }
        }

    return response
