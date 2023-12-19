import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

DYNAMODB_ENDPOINT = "http://localstack:4566"
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT)


def handler(event, context=None):
    print(event)
    data = json.loads(event['body'])
    table = dynamodb.Table("users")
    if event['requestContext']['http']['method'] == 'GET':
        response = process_get(data, table)
        return response
    elif event['requestContext']['http']['method'] == 'POST':
        response = process_post(data, table)
        return response


def process_post(data, table):
    if not data or not data.get('name') or not data.get('password'):
        return {
            "created": False,
            "reason": "no data"
        }
    user = {
        "Name": data["name"],
        "Password": data["password"]
    }
    try:
        table.put_item(Item=user)
        return {
            "created": True,
        }
    except ClientError as err:
        return {
            "created": False,
            "reason": err.response["Error"]["Message"]
        }


def process_get(data, table):
    if not data or not data.get('name') or not data.get('password'):
        return {
            "isAuthorized": False,
            "context": {
                "reason": "no data"
            }
        }
    result = table.get_item(
        Key={
            'Name': data['name'],
            'Password': data['password']
        }
    )
    if not result['Item']:
        return {
            "isAuthorized": False,
            "context": {
                "reason": "invalid data"
            }
        }
    return {
        "isAuthorized": True,
        "context": {
            "item": result['Item']
        }
    }

