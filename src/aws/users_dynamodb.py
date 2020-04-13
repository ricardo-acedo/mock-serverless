import os
import boto3

from src.aws.decimal_encoder import parse_json

USERS_TABLE = os.environ.get('USERS_TABLE')
IS_OFFLINE = os.environ.get('IS_OFFLINE')

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

table = dynamodb.Table(USERS_TABLE)


def add_user(user):
    return table.put_item(
        Item=user.to_dict()
    )


def get_user(user_id):
    response = table.get_item(
        Key={
            'id': user_id
        }
    )
    item = response.get('Item')
    return parse_json(item) if item is not None else item


def get_all_users():
    response = table.scan()
    return list(map(parse_json, response['Items']))


def delete_user(user_id):
    response = table.delete_item(
        Key={
            'id': user_id
        },
        ReturnValues='ALL_OLD'
    )
    return response.get('Attributes')
