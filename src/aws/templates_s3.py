import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

BUCKET_NAME = os.environ.get('S3_BUCKET')
IS_OFFLINE = os.environ.get('IS_OFFLINE')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
    logger.info(f'Trying to save template file for template {template}')
    path = s3.Object(BUCKET_NAME, template.get_s3_location())
    if template.responseType == 'json':
        logger.info(f'Trying to save template file to path {path}')
        path.put(Body=bytes(json.dumps(file).encode('UTF-8')))


def get_file(template):
    logger.info(f'Trying to get template file for {template}')
    path = s3.Object(BUCKET_NAME, template.get_s3_location())
    if template.responseType == 'json':
        logger.info(f'Trying to get template file from {path}')
        try:
            content = path.get()['Body'].read()
            return json.loads(content)
        except ClientError:
            logger.warning(f'Template not found in bucket for {path}')
            return None


def delete_file(template):
    logger.info(f'Trying to delete template file for {template}')
    path = s3.Object(BUCKET_NAME, template.get_s3_location())
    path.delete()
