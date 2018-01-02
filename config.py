import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.curdir, '.env'))

JSON_AS_ASCII = False

SECRET_KEY = 'secret'

DATA_BACKEND = os.environ.get('DATA_BACKEND')

PROJECT_ID = os.environ.get('PROJECT_ID')

DATASTORE_DATASET_ID = PROJECT_ID
DATASTORE_KIND = os.environ.get('DATASTORE_KIND')

CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')
MAX_CONTENT_LENGTH = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['json', 'csv'])
