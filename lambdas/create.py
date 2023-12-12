import json
import logging
import boto3


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

DYNAMODB_ENDPOINT = "http://localstack:4566"
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT)


def create(event, context):
    data = json.loads(event['body'])

    table = dynamodb.Table("users")

    user = {
        "Name": data["name"],
        "Email": data["email"]
    }
    table.put_item(Item=user)

    response = {
        "statusCode": 200,
        "body": json.dumps(user)
    }

    return response
