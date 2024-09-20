import redshift_connector
import os, sys
import logging
from datetime import datetime

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from constants.configs import *

class RedshiftConnector:
    def __init__(self, config):
        self.config = config
        self.name = REDSHIFT_NAME
    
    def get_name(self):
        return self.name
    
    def connect_to_redshift(self):
        try:
            conn = redshift_connector.connect(
                **self.config
            )
            cursor = conn.cursor()
            logging.info(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Connect to Redshift successfully!''')
            return conn, cursor
        
        except Exception as e:
            logging.error(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Redshift encountered an error: {str(e)}''')
            return None, None
    

    @staticmethod
    def generate_query_string(table_name, column_fields, date_from, date_to, date_column_name):
        formatted_columns = ', '.join(column_fields)
        query_str = f'''
            SELECT {formatted_columns}
            FROM {table_name}
            WHERE {date_column_name} BETWEEN '{date_from}' AND '{date_to}'
        '''
        return query_str.strip()
    
    def get_data_from_redshift(self, query_str):
        logging.info(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extracting data from Redshift''')
        
        conn, cursor = self.connect_to_redshift()

        if conn:
            try:
                cursor.execute(query_str)
                df = cursor.fetch_dataframe()
                logging.info(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Redshift extraction completed''')
                return df
            
            except Exception as e:
                logging.error(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {str(e)}''')
                cursor.execute('rollback') 
                return None

    def handle_multitple_queries(self, queries):
        try:
            conn, cursor = self.connect_to_redshift()                       
            cursor.execute('begin')

            logging.info(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Inserting data...''')

            for query in queries:
                try:
                    cursor.execute(query)
                except Exception as e:
                    logging.error(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Query failed: {query}. Error: {e}''')
                    conn.rollback()           
            cursor.execute('commit')
              
            logging.info(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Insertion completed!''')

        except Exception as e: 
            logging.error(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {str(e)}''')
            conn.rollback()    


    def load_data_from_s3_to_redshift(self, source, destination):

        '''
            Loads data from an S3 bucket into a Redshift table.

            Args:
                source: File path of the CSV file in the S3 bucket.
                destination: Name of the destination table in Redshift.

            Returns:
                None

            This method connects to Redshift, executes a COPY command to load data from the specified S3 file into the specified Redshift table.        
        '''

        conn, cursor = self.connect_to_redshift()
        
        q = f'''
            copy {destination}
            from '{source}'
            credentials 'aws_access_key_id={AWS_ACCESS_KEY_ID};aws_secret_access_key={AWS_SECRET_ACCESS_KEY}' 
            format as csv
            delimiter ','
            ignoreheader 1
            emptyasnull
            blanksasnull
            maxerror 0   
            timeformat 'auto';
        '''
        
        if conn:
            try:
                cursor.execute('begin')
                cursor.execute(q)
                cursor.execute('commit')
                logging.info(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Load completed!''')
                
            except Exception as e: 
                logging.error(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {str(e)}''')
                conn.rollback() 

    def create_table_if_not_exists(self, schema, table_name, is_staging):
        '''
            Creates a table in Redshift if it does not already exist.

            Args:
                table_name: Name of the table to create.
                schema: Dictionary representing the table schema where keys are field names and values are data types.
                is_staging: If True, create a staging table whose all data types are string

            Returns:
                None

            This method constructs a CREATE TABLE query based on the provided schema and executes it in Redshift.
        '''
        conn, cursor = self.connect_to_redshift()

        if is_staging:
            fields = ', '.join([f'''{field} CHARACTER VARYING''' for field in schema.keys()])
        else:        
            fields = ', '.join([f'''{field} {data_type}''' for field, data_type in schema.items()])

        query_str = f'''create table if not exists {table_name} ({fields});'''

        if conn:
            try:
                cursor.execute(query_str)
                logging.info(f'Executing: {query_str}')
                conn.commit()
                logging.info(f'Create table {table_name} successfully!')

            except Exception as e: 
                logging.error(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {str(e)}''')
                conn.rollback()   

    def truncate_table(self, table_name):
        conn, cursor = self.connect_to_redshift()

        q = f'''truncate table {table_name};'''

        if conn:
            try:
                cursor.execute(q)
                conn.commit()
                logging.info(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Truncate table {table_name} successfully!''')
            
            except Exception as e: 
                logging.error(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {str(e)}''')
                conn.rollback()    