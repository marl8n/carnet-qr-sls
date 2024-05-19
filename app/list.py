import json
import os

from app import decimalencoder
import boto3
dynamodb = boto3.resource('dynamodb')


def list(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch all users from the database
    result = table.scan()

    # create a response
    response = {
        "statusCode": 200,
        "body": {
            "message": "Students fetched successfully",
            "students": result['Items'],
        }
    }

    return response
