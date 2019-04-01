import random
import boto3

from app.macro import *

def db_get():

    db = boto3.resource('dynamodb')
    return db

def db_write(table, item):

    db = db_get()
    db_table = db.Table(table)
    db_table.put_item(Item=item)

def db_read(table, key):

    db = db_get()
    db_table = db.Table(table)
    response = db_table.get_item(Key=key)
    try:
        item = response['Item']
    except:
        item = None
    return item

def db_scan(table, fe):

    db = db_get()
    db_table = db.Table(table)
    if fe:
        response = db_table.scan(FilterExpression=fe)
    else:
        response = db_table.scan()
    return response['Items']

def db_delete(table, key):

    db = db_get()
    db_table = db.Table(table)
    db_table.delete_item(Key=key)

# def s3_get():
#
#     s3 = boto3.client("s3")
#     return s3
#
# def s3_write(upload, filename):
#
#     s3 = s3_get()
#     s3.upload_file(upload, s3_bucket, filename)
#
# def s3_read(filename):
#
#     s3 = s3_get()
#     url = s3.generate_presigned_url('get_object',
#                               Params={
#                                   'Bucket': s3_bucket,
#                                   'Key': filename,
#                               },
#                               ExpiresIn=3600)
#     return url

def generate_salt():
    chars = []
    for i in range(16):
        chars.append(random.choice(salt_char))
    return "".join(chars)
