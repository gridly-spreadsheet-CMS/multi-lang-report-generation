import os
from dotenv import load_dotenv

# Load environment variables from a .env file for local testing
load_dotenv()

# Redshift configuration
REDSHIFT_HOST = os.getenv('REDSHIFT_HOST')
REDSHIFT_USER = os.getenv('REDSHIFT_USER')
REDSHIFT_PASSWORD = os.getenv('REDSHIFT_PASSWORD')
REDSHIFT_PORT = os.getenv('REDSHIFT_PORT')
REDSHIFT_DATABASE = os.getenv('REDSHIFT_DATABASE')
REDSHIFT_CLUSTER = os.getenv('REDSHIFT_CLUSTER')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
IAM = True  # Use IAM authentication
REDSHIFT_REGION = os.getenv('REDSHIFT_REGION')
BUCKET_NAME = os.getenv('BUCKET_NAME')
REDSHIFT_NAME = 'Your Redshift'

# Redshift config dictionary
REDSHIFT_CONFIG = {
    'host': REDSHIFT_HOST,
    'database': REDSHIFT_DATABASE,
    'port': int(REDSHIFT_PORT),
    'db_user': REDSHIFT_USER,
    'password': REDSHIFT_PASSWORD,
    'iam': IAM,
    'cluster_identifier': REDSHIFT_CLUSTER,
    'access_key_id': AWS_ACCESS_KEY_ID,
    'secret_access_key': AWS_SECRET_ACCESS_KEY,
    'region': REDSHIFT_REGION
}

# BigQuery configuration for local testing
BIGQUERY_PROJECT = os.getenv('BIGQUERY_PROJECT')
BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET')
BIGQUERY_TABLE = os.getenv('BIGQUERY_TABLE')
BIGQUERY_KEY_PATH = os.getenv('BIGQUERY_KEY_PATH')

# BigQuery config dictionary
BIGQUERY_CONFIG = {
    'project': BIGQUERY_PROJECT,
    'dataset': BIGQUERY_DATASET,
    'table': BIGQUERY_TABLE,
    'key_path': BIGQUERY_KEY_PATH  # Path to service account key for local testing
}

# MySQL configuration for local testing
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')

# MySQL config dictionary
MYSQL_CONFIG = {
    'host': MYSQL_HOST,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'port': int(MYSQL_PORT),
    'database': MYSQL_DATABASE
}

# Comment: The above configurations are used for local testing, pulling sensitive information from a .env file
