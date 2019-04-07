s3_bucket = 'askcrowd'

INFO = 'askcrowd-info'
USERS = 'askcrowd-users'
POLLS = 'askcrowd-polls'
COMMENTS = 'askcrowd-comments'

username_char = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
password_char = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz~!@#$%^&*_.?'
salt_char = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

from app.db import *

key = {'name': 'flask'}
secret_key = db_read(INFO, key)['secret_key']
