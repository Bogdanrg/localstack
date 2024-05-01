import decimal
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


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


def get_update_params(body):
    update_expression = []
    attribute_values = dict()
    attribute_names = dict()

    for key, val in body.items():
        update_expression.append(f" #{key.lower()} = :{key.lower()}")
        attribute_values[f":{key.lower()}"] = val
        attribute_names[f"#{key.lower()}"] = key

    return "set " + ", ".join(update_expression), attribute_values, attribute_names


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
    new_post.pop('password')
    new_post.pop('year')
    new_post.pop('entity')

    update_expression, attribute_values, attribute_names = get_update_params(new_post)
    response = table.update_item(
        Key={
            'Entity': data['entity'],
            'Year': data['year']
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=attribute_values,
        ExpressionAttributeNames=attribute_names,
        ReturnValues="UPDATED_NEW"
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
            }, cls=DecimalEncoder),
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
