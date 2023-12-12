import json
import logging
from datetime import datetime, date

import boto3
import os

from botocore.exceptions import ClientError

AWS_REGION = 'us-east-1'
AWS_PROFILE = 'localstack'
ENDPOINT_URL = os.environ.get('LOCALSTACK_ENDPOINT_URL')

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

boto3.setup_default_session(profile_name=AWS_PROFILE)
dynamodb_client = boto3.client(
    "dynamodb", region_name=AWS_REGION,
    endpoint_url="http://127.0.0.1:4566",
    aws_access_key_id="asdf",
    aws_secret_access_key="asdf")


def json_datetime_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def create_dynamodb_table(table_name):
    try:
        response = dynamodb_client.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'Name',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'Email',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'Name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Email',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            },
            Tags=[
                {
                    'Key': 'Name',
                    'Value': 'hands-on-cloud-dynamodb-table'
                },
            ],
        )
    except ClientError:
        logger.exception('Could not create the table.')
        raise
    else:
        return response


def index_dynamo_db_table(table_name):
    try:
        response = dynamodb_client.update_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'Name',
                    'AttributeType': 'S'
                },
            ],
            TableName=table_name,
            GlobalSecondaryIndexUpdates=[
                {
                    'Create': {
                        'IndexName': 'UsersIndex',
                        'KeySchema': [
                            {
                                'AttributeName': 'Name',
                                'KeyType': 'HASH'
                            }
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        },
                        'ProvisionedThroughput': {
                            'ReadCapacityUnits': 1,
                            'WriteCapacityUnits': 1
                        }
                    }
                }
            ]
        )
    except ClientError:
        logger.exception('Could not index the table.')
        raise
    else:
        return response


def main():
    table_name = 'users'
    logger.info('Creating a DynamoDB table...')
    dynamodb_table = create_dynamodb_table(table_name)
    logger.info(
        f'DynamoDB table created: {json.dumps(dynamodb_table, indent=4, default=json_datetime_serializer)}')
    logger.info('Indexing table...')
    response = index_dynamo_db_table(table_name)
    logger.info(response)


if __name__ == '__main__':
    main()
