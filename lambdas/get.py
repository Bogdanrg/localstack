import json
import logging
import boto3

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

DYNAMODB_ENDPOINT = "http://localstack:4566"
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT)
client = boto3.client('lambda')


def get(event, context):
    table = dynamodb.Table("posts")
    data = json.loads(event['body'])
    response = client.invoke(
        FunctionName='auth',
        InvocationType='RequestResponse',
        Payload=json.dumps(event['body'])
    )
    response_payload = json.load(response['Payload'])
    print(response_payload)
    if not response_payload.get('isAuthorized'):
        return {
            "statusCode": 500,
            "reason": "Access denied"
        }
    result = table.get_item(
        Key={
            'Username': data['name'],
            'Title': data['title']
        }
    )
    return {
        "statusCode": 200,
        "context":
            {
                "item": result["Item"]
            }
    }
