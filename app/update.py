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

def update(event, context):
    data = json.loads(event['body'])
    if 'carnet' not in data:
        logging.error("Validation Failed")
        raise ClientError("Couldn't update without carnet.")
    
    if 'name' not in data:
        logging.error("Validation Failed")
        raise ClientError("Couldn't update without name.")

    id = data['id'] if data['id'] is not None else generate_carnet_validation(data['carnet'])

    timestamp = str(time.time())
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # Update carnet in the database
    try:
        result = table.update_item(
            Key={
                'id': id
            },
            ExpressionAttributeNames={
              '#carnet_name': 'name',
            },
            ExpressionAttributeValues={
              ':name': data['name'],
              ':updatedAt': timestamp,
            },
            UpdateExpression='SET #carnet_name = :name, updatedAt = :updatedAt',
            ReturnValues='ALL_NEW',
        )
    except ClientError as e:
        logging.error(e.response['Error']['Message'])
        return {
            "statusCode": 400,
            "body": json.dumps({"error_message": "Could not update the carnet"})
        }
    else:
        # Create a response
        response = {
            "statusCode": 200,
            "body": json.dumps(result['Attributes'])
        }

    return response

