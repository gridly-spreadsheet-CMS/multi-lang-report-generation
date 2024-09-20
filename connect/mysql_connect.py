import mysql.connector
import logging
from datetime import datetime
import sys

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from constants.configs import *

class MySQLConnector:
    def __init__(self, config):
        self.config = config
        self.name = "MySQL"

    def connect_to_mysql(self):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()
            logging.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connect to MySQL successfully!")
            return conn, cursor
        except Exception as e:
            logging.error(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MySQL encountered an error: {str(e)}")
            return None, None

    def execute_query(self, query):
        conn, cursor = self.connect_to_mysql()
        if conn:
            try:
                cursor.execute(query)
                results = cursor.fetchall()
                conn.commit()
                return results
            except Exception as e:
                conn.rollback()
                logging.error(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error executing query: {e}")
                return None
        else:
            return None
