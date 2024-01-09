import json
import logging
import os
from copy import deepcopy

import boto3

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

dynamodb = boto3.resource('dynamodb', endpoint_url=os.environ.get("DYNAMODB_URL"))
client = boto3.client('lambda')


def put(event, context):
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
    new_post = deepcopy(data)
    new_post.pop('name')
    new_post.pop('code')
    new_post.pop('password')
    response = table.update_item(
        Key={
            'Code': data['code'],
            'Username': data['name']
        },
        AttributeUpdates=new_post,
        ReturnValues='ALL_NEW'
    )
    if response.get("Attributes"):
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'context': {
                    "item": response["Attributes"]
                }
            }),
            "isBase64Encoded": False
        }
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'reason': 'Not Found'
        }),
        "isBase64Encoded": False
    }
