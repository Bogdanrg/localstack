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
    response = client.invoke(
        FunctionName='auth',
        InvocationType='RequestResponse',
        Payload=event
    )
    print(response)
    if not response['isAuthorized']:
        return {
            "statusCode": 500
        }
    response = {
        "statusCode": 200,
        "body": "Ok"
    }

    return response
