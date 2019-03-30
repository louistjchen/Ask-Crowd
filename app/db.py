import random
import boto3
import time
import calendar
import urllib.request

from flask import g
from app import webapp
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from app.macro import *

def db_write(table, item):

    db = boto3.resource('dynamodb')
    db_table = db.Table(table)
    db_table.put_item(Item=item)

def db_read(table, key):

    db = boto3.resource('dynamodb')
    db_table = db.Table(table)
    response = db_table.get_item(Key=key)
    try:
        item = response['Item']
    except:
        item = None
    return item

def generate_salt():
    chars = []
    for i in range(16):
        chars.append(random.choice(salt_char))
    return "".join(chars)

# def get_s3():
#
#     s3 = boto3.client("s3")
#     return s3
#
# def upload_file_to_s3(upload, filename):
#
#     s3 = get_s3()
#     s3.upload_file(upload, s3_bucket, filename)
#
# def download_file_from_s3(filename):
#
#     s3 = get_s3()
#     url = s3.generate_presigned_url('get_object',
#                               Params={
#                                   'Bucket': s3_bucket,
#                                   'Key': filename,
#                               },
#                               ExpiresIn=3600)
#     return url
