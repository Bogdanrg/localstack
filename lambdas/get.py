import json
import logging
import os

import boto3

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

dynamodb = boto3.resource('dynamodb', endpoint_url=os.environ.get("DYNAMODB_URL"))
client = boto3.client('lambda')


class FoodService:
    @staticmethod
    def get_items_by_entity(entity, table, page=1, page_size=30):
        result = table.get_item(
            Key={
                'Entity': entity
            }
        )
        return result

    @staticmethod
    def get_items_by_year(year, table, page=1, page_size=30):
        result = table.get_item(
            Key={
                'Year': year
            }
        )
        return result

    @staticmethod
    def get_all(table, page=1, page_size=30):
        result = table.scan(LastEvaluatedKey=page * page_size - page_size, Limit=page_size)
        return result


class GetFoodHandler:
    filter_by_handlers = {
        "entity": FoodService.get_items_by_entity,
        "year": FoodService.get_items_by_year,
        "no_action": FoodService.get_all
    }

    @staticmethod
    def get(event, context):
        table = dynamodb.Table(os.environ.get("FOOD_TABLE"))
        data = json.loads(event['body'])
        auth_response = GetFoodHandler.authenticate(data)
        auth_response_payload = json.load(auth_response['Payload'])
        if not auth_response_payload.get('isAuthorized'):
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
        event_type = data.get("action", "no_action")
        event_handler = self.action_handlers.get(event_type)
        if callable(event_handler):
    @staticmethod
    def authenticate(credentials):
        response = client.invoke(
            FunctionName='auth',
            InvocationType='RequestResponse',
            Payload=json.dumps(credentials)
        )
        return response


def get(event, context):
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'reason': 'Not found'
        }),
        "isBase64Encoded": False
    }
