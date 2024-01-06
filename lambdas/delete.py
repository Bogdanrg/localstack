import json
import logging
import os

import boto3

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

dynamodb = boto3.resource('dynamodb', endpoint_url=os.environ.get("DYNAMODB_URL"))
client = boto3.client('lambda')


def delete(event, context):
    table = dynamodb.Table(os.environ.get("POST_TABLE"))
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
    response = table.delete_item(
        Key={
            "Code": data["code"],
            "Username": data["name"]
        },
        ReturnValues='ALL_OLD'
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
            'reason': "Not found"
        }),
        "isBase64Encoded": False
    }
