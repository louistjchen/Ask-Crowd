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

def s3_get():

    s3 = boto3.client("s3")
    return s3

def upload_file_to_s3(file, bucket_name=s3_bucket, acl="public-read"):

    """
    Docs: http://boto3.readthedocs.io/en/latest/guide/s3.html
    """

    s3 = s3_get()
    s3.upload_fileobj(
        file,
        bucket_name,
        file.filename,
        ExtraArgs={
            "ACL": acl,
            "ContentType": file.content_type
        }
    )

    return "https://s3.amazonaws.com/"+s3_bucket+"/"+file.filename

def s3_write(upload, filename):

    s3 = s3_get()
    s3.upload_file(upload, s3_bucket, filename)

def s3_read(filename):

    s3 = s3_get()
    url = s3.generate_presigned_url('get_object',
                              Params={
                                  'Bucket': s3_bucket,
                                  'Key': filename,
                              },
                              ExpiresIn=3600)
    return url

def generate_salt():
    chars = []
    for i in range(16):
        chars.append(random.choice(salt_char))
    return "".join(chars)
