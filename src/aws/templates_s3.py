import json
import logging
import os

import boto3

BUCKET_NAME = os.environ.get('S3_BUCKET')
IS_OFFLINE = os.environ.get('IS_OFFLINE')
log = logging.getLogger()

if IS_OFFLINE:
    s3 = boto3.resource(
        's3',
        region_name='localhost',
        endpoint_url='http://localhost:8001',
        aws_session_token='S3RVER',
        aws_secret_access_key='S3RVER',
        aws_access_key_id='S3RVER'
    )
else:
    s3 = boto3.resource('s3')


def save_file(template, file):
    path = s3.Object(BUCKET_NAME, template.get_s3_location())
    if template.responseType == 'json':
        path.put(Body=bytes(json.dumps(file).encode('UTF-8')))


def get_file(template):
    path = s3.Object(BUCKET_NAME, template.get_s3_location())
    if template.responseType == 'json':
        try:
            content = path.get()['Body'].read()
            return json.loads(content)
        except Exception as e:
            log.error('Template not found in bucket', e)
            return None


def delete_file(template):
    path = s3.Object(BUCKET_NAME, template.get_s3_location())
    path.delete()
