import numpy as np 
import pandas as pd

import warnings
import logging

warnings.filterwarnings('ignore')
import os, sys

sys.path.insert(1, '/'.join(os.path.realpath(__file__).split('/')[0:-2]))
from connect.redshift_connect import *

class Processor:
    def __init__(self):
        self.raw_datasets = {}
        self.processed_datasets = {}

    def load_data(self, data_source, dataset_type, dataset_name):
        if dataset_type == 'csv':
            self.raw_datasets[dataset_name] = pd.read_csv(data_source)

        elif dataset_type == 'excel':
            self.raw_datasets[dataset_name] = pd.read_excel(data_source)
        elif dataset_type == 'dataframe':
            if isinstance(data_source, pd.DataFrame):
                self.raw_datasets[dataset_name] = data_source
            else:
                raise ValueError('Data Source must be a Pandas Dataframe')
        else:
            logging.error(f'''[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Unsupported data type''')

    
    def get_raw_dataset_by_name(self, dataset_name):
        if dataset_name in self.raw_datasets:
            return self.raw_datasets[dataset_name]
        else:
            raise ValueError(f'''No dataset named {dataset_name} available.''')
    
    def get_processed_dataset_by_name(self, dataset_name):
        if dataset_name in self.processed_datasets:
            return self.processed_datasets[dataset_name]
        else:
            raise ValueError(f'''No dataset named {dataset_name} available.''')

    def get_all_processed_datasets(self):
        return self.processed_datasets

    def preprocess_data(self, dataset_name, schema, not_null_col=None):
        if dataset_name not in self.raw_datasets:
            raise ValueError(f'''No dataset named {dataset_name} available for preprocessing.''')
        
        data = self.raw_datasets[dataset_name]
        
        if schema:
            for col, dtype in schema.items():
                if dtype == 'datetime':
                    data[col] = pd.to_datetime(data[col], errors='coerce')
                elif dtype == 'float':
                    data[col] = pd.to_numeric(data[col], errors='coerce')
                elif dtype == 'int':
                    # Convert to float first to handle NaN properly
                    data[col] = pd.to_numeric(data[col], errors='coerce').astype('Int64')
                elif dtype == 'str':
                    data[col] = data[col].astype(str)
                    data[col] = data[col].replace('null', pd.NA)
        
        # Remove duplicates
        data = data.drop_duplicates()
        
        # Drop rows with missing values in specified columns
        if not_null_col:
            data = data.dropna(subset=not_null_col)

        self.processed_datasets[dataset_name] = data
            
    def basic_aggregation(self, dataset_name, timestamp_column_name, agg_column_name, agg_by=['avg'], agg_period='daily', rename_agg_column={}
                          , order_by='asc', rounded_numerical_result_by=None, start_date=None, end_date=None):
        """
        Performs basic aggregation on the data for given parameters.

        Args:
            agg_by (str): Specifies the aggregation function to apply. Options include:
                          'avg' for average, 'sum' for total sum, 'max' for maximum, 'min' for minimum.
                          Default is 'avg'.
            
            agg_period (str): Specifies the time period over which to aggregate the data.
                              Options are 'daily', 'weekly', 'monthly', 'yearly'.
                              Default is 'daily'.
            
            order_by (str): Specifies the order of the resulting data. Can be 'asc' for ascending or
                            'desc' for descending. Default is 'asc'.
            
            rounded_numerical_result_by (int): Specifies the number of decimal places to round numerical results to.
                                               Default is 2.
            
            start_date (str): Optional; Specifies the start date for filtering the data. 
                              Dates should be in 'YYYY-MM-DD' format. Default is None.
            
            end_date (str): Optional; Specifies the end date for filtering the data.
                            Dates should be in 'YYYY-MM-DD' format. Default is None.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the aggregated data.

        Raises:
            ValueError: If 'timestamp' column is missing or if invalid parameters are provided for
                        aggregation type or period.
        """

        if dataset_name not in self.raw_datasets:
            raise ValueError(f'''No dataset named {dataset_name} available for preprocessing.''')

        data = self.raw_datasets[dataset_name]

        if timestamp_column_name not in data.columns:
            raise ValueError(f'''No '{timestamp_column_name}' column available for aggregation.''')
        
        # Ensure the timestamp column is in datetime format
        data[timestamp_column_name] = pd.to_datetime(data[timestamp_column_name])
        
        # Filter data based on timeframe
        if start_date and end_date:
            data = data[(data[timestamp_column_name] >= pd.to_datetime(start_date)) & (data[timestamp_column_name] <= pd.to_datetime(end_date))]

        # Extract the date part for aggregation
        if agg_period == 'daily':
            data['period'] = data[timestamp_column_name].dt.strftime('%Y-%m-%d')
        elif agg_period == 'weekly':
            # Extract the starting day of the week
            data['period'] = data[timestamp_column_name].dt.to_period('W').apply(lambda x: x.start_time.strftime('%Y-%m-%d'))
        elif agg_period == 'monthly':
            data['period'] = data[timestamp_column_name].dt.to_period('M').apply(lambda x: x.start_time.strftime('%Y-%m-%d'))
        elif agg_period == 'yearly':
            data['period'] = data[timestamp_column_name].dt.to_period('Y').apply(lambda x: x.start_time.strftime('%Y-%m-%d'))
        else:
            raise ValueError('''Unsupported aggregation period. Choose 'daily', 'weekly', 'monthly', or 'yearly'.''')
        
        data['period'] = pd.to_datetime(data['period'])

        try:
            result = data.groupby('period').agg({agg_column_name: agg_by}).reset_index()
            result.columns = ['_'.join(col).strip() if col[1] else col[0] for col in result.columns.values]

        except Exception as e:
            raise ValueError(f'''Aggregation failed with error: {e}''')


        # Round numerical results
        numerical_cols = result.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns

        result[numerical_cols] = result[numerical_cols].apply(lambda x: round(x, rounded_numerical_result_by))

        result.rename(columns=rename_agg_column, inplace=True)

        # Order results
        if order_by == 'asc':
            result = result.sort_values(by='period', ascending=True)
        elif order_by == 'desc':
            result = result.sort_values(by='period', ascending=False)
        else:
            raise ValueError(f'''Order should be 'asc' or 'desc'.''')

        self.processed_datasets[dataset_name] = result

            