import json
import logging
import boto3

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

DYNAMODB_ENDPOINT = "http://localstack:4566"
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT)


def get(event, context):
    table = dynamodb.Table("users")

    result = table.get_item(
        Key={
            'Name': event['pathParameters']['Name'],
            'Email': "user@gmail.com"
        }
    )

    response = {
        "statusCode": 200,
        "body": json.dumps(result['Item'])
    }

    return response
