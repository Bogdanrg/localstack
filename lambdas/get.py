import decimal
import json
import logging
import os

import boto3
from boto3.dynamodb.conditions import Attr

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


class FoodProductionService:

    @staticmethod
    def paginate_scan(table, result, filter_by=None, value=None, page=1, page_size=30):
        page_count = 1
        while 'LastEvaluatedKey' in result:
            if page_count == page:
                return result
            else:
                if not filter_by:
                    result = table.scan(ExclusiveStartKey=result['LastEvaluatedKey'], Limit=page_size)
                if filter_by:
                    result = table.scan(ExclusiveStartKey=result['LastEvaluatedKey'],
                                        Limit=page_size,
                                        FilterExpression=Attr(filter_by).eq(value))
                page_count += 1
        return result

    @staticmethod
    def get_items_by_entity(entity, table, page=1, page_size=30, **kwargs):
        result = table.scan(Limit=page_size,
                            FilterExpression=Attr('Entity').eq(entity))
        paginated_result = FoodProductionService.paginate_scan(table=table,
                                                               result=result,
                                                               page=page,
                                                               page_size=page_size,
                                                               filter_by='Entity',
                                                               value=entity)
        return paginated_result

    @staticmethod
    def get_items_by_year(year, table, page=1, page_size=30, **kwargs):
        result = table.scan(Limit=page_size,
                            FilterExpression=Attr('Year').eq(year))
        paginated_result = FoodProductionService.paginate_scan(table=table,
                                                               result=result,
                                                               page=page,
                                                               page_size=page_size,
                                                               filter_by='Year',
                                                               value=year)
        return paginated_result

    @staticmethod
    def get_all(table, page=1, page_size=30, **kwargs):
        result = table.scan(Limit=page_size)
        paginated_result = FoodProductionService.paginate_scan(table=table,
                                                               result=result,
                                                               page=page,
                                                               page_size=page_size)
        return paginated_result


def get(event, context):
    search_filters = {
        "entity": FoodProductionService.get_items_by_entity,
        "year": FoodProductionService.get_items_by_year,
        "no_filter": FoodProductionService.get_all
    }
    table = dynamodb.Table(os.environ.get("FOOD_TABLE"))
    data = json.loads(event['body'])
    auth_response = client.invoke(
        FunctionName='auth',
        InvocationType='RequestResponse',
        Payload=json.dumps(event['body'])
    )
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
    event_type = data.get("filter_by", "no_filter")
    event_handler = search_filters.get(event_type)
    result = event_handler(table=table, **data)
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'content': result["Items"]
        }, cls=DecimalEncoder),
        "isBase64Encoded": False
    }
