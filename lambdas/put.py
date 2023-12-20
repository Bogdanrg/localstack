import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

DYNAMODB_ENDPOINT = "http://localstack:4566"
dynamodb = boto3.resource('dynamodb', endpoint_url=DYNAMODB_ENDPOINT)
client = boto3.client('lambda')


def put(event, context):
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
    new_post = data
    new_post.pop('name')
    new_post.pop('password')
    try:
        table.update_item(
            Key={
                'Title': new_post['title'],
                'Username': new_post['name']
            },
            AttributeUpdates=new_post
        )
        return {
            "updated": True,
        }
    except ClientError as err:
        return {
            "updated": False,
            "reason": err.response["Error"]["Message"]
        }
