import json
import logging
import boto3

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

DYNAMODB_ENDPOINT = "http://localstack:4566"
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT)


def create(event, context):
    table = dynamodb.Table("users")

    response = {
        "statusCode": 200,
        "body": json.dumps(user)
    }

    return response
