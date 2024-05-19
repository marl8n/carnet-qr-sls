import json
import logging
import os
import time
from io import BytesIO
import qrcode

from botocore.exceptions import ClientError
import boto3
dynamodb = boto3.resource('dynamodb')

from utils import generate_carnet_validation

def delete(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Delete carnet from the database
    try:
        result = table.delete_item(
            Key={
                'id': event['pathParameters']['id']
            }
        )
    except ClientError as e:
        logging.error(e.response['Error']['Message'])
        return {
            "statusCode": 400,
            "body": json.dumps({"error_message": "Could not delete the carnet"})
        }
    else:
        # Create a response
        response = {
            "statusCode": 200,
            "body": json.dumps({"message": "Carnet deleted successfully"})
        }

    return response
