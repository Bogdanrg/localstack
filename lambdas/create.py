import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

dynamodb = boto3.resource('dynamodb', endpoint_url=os.environ.get("DYNAMODB_URL"))
client = boto3.client('lambda')


def create(event, context):
    table = dynamodb.Table(os.environ.get("FOOD_TABLE"))
    data = json.loads(event['body'])
    response = client.invoke(
        FunctionName='auth',
        InvocationType='RequestResponse',
        Payload=json.dumps(event['body'])
    )
    response_payload = json.load(response['Payload'])
    if not response_payload.get('isAuthorized'):
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'reason': 'Access denied'
            }),
            "isBase64Encoded": False
        }
    year_food_production = {
        "Entity": data["entity"],
        "Year": data["year"],
        "Maize": data["maize"],
        "Rice": data["rice"],
        "Yams": data["yams"],
        "Wheat": data["wheat"],
        "Tomatoes": data["tomatoes"],
        "Tea": data["tea"],
        "Potatoes": data["potatoes"]
    }
    try:
        table.put_item(Item=year_food_production)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
            }),
            "isBase64Encoded": False
        }
    except ClientError as err:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                "reason": err.response["Error"]["Message"]
            }),
            "isBase64Encoded": False
        }
