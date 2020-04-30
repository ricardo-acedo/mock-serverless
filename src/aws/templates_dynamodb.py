import logging
import os

import boto3
from boto3.dynamodb.conditions import Key

from src.aws.decimal_encoder import parse_json

TEMPLATES_TABLE = os.environ.get('TEMPLATES_TABLE')
IS_OFFLINE = os.environ.get('IS_OFFLINE')
PATH_INDEX = os.environ.get('TEMPLATES_PATH_INDEX')

if IS_OFFLINE:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8000',
        aws_session_token='1234',
        aws_secret_access_key='1234',
        aws_access_key_id='1234'
    )
else:
    dynamodb = boto3.resource('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table = dynamodb.Table(TEMPLATES_TABLE)


def query_path(path, http_status):
    return table.query(
        IndexName=PATH_INDEX,
        KeyConditionExpression=Key('path').eq(path) & Key('httpStatus').eq(http_status)
    )['Items']


def add_template(template):
    logger.info(f'Adding template to DB {template}')
    if query_path(template.path, template.httpStatus):
        return None

    resp = table.put_item(
        Item=template.to_dict()
    )
    return resp


def update_template(template):
    logger.info(f'Updating template to DB {template}')
    table.put_item(
        Item=template.to_dict()
    )


def get_template(template_id):
    logger.info(f'Getting template from DB id {template_id}')
    response = table.get_item(
        Key={
            'id': template_id
        }
    )
    item = response.get('Item')
    return parse_json(item) if item is not None else item


def get_all_templates():
    response = table.scan()
    return list(map(parse_json, response['Items']))


def get_all_templates_path_index():
    return table.scan(IndexName=PATH_INDEX)['Items']


def delete_template(template_id):
    logger.info(f'Deleting template from DB id {template_id}')
    response = table.delete_item(
        Key={
            'id': template_id
        },
        ReturnValues='ALL_OLD'
    )
    return response.get('Attributes')
