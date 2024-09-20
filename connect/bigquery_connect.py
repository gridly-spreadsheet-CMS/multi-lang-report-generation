from google.cloud import bigquery
from google.oauth2 import service_account
import logging
from datetime import datetime

class BigQueryConnector:
    def __init__(self, credentials_path, project_id):
        self.credentials_path = credentials_path
        self.project_id = project_id
        self.client = self.connect_to_bigquery()

    def connect_to_bigquery(self):
        try:
            # Load credentials and create a BigQuery client
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path)
            client = bigquery.Client(credentials=credentials, project=self.project_id)
            logging.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connected to BigQuery successfully!")
            return client
        except Exception as e:
            logging.error(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Failed to connect to BigQuery: {e}")
            return None

    def execute_query(self, query):
        try:
            query_job = self.client.query(query)
            results = query_job.result()  # Wait for the job to complete.
            logging.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Query executed successfully!")
            return results
        except Exception as e:
            logging.error(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error executing query: {e}")
            return None