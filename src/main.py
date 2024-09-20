import os, sys
sys.path.insert(1, '/'.join(os.path.realpath(__file__).split('/')[0:-2]))

import time
from datetime import datetime, timedelta

from constants.configs import *

from connect.redshift_connect import *
from process.processor import *
from process.visualizer import *
from process.generator import *  
from process.translation_flow import *
from process.gridly_features import *
from process.slack_client import *

base_dir = os.path.join(os.path.dirname(__file__), 'data/sample/')

if __name__ == '__main__':
    start_time = time.time()
    print('Start time: {}'.format(datetime.now().strftime('%B %d, %Y %H:%M:%S')))

    # Create a connection to the data. In this example, I use AWS Redshift
    redshift = RedshiftConnector(REDSHIFT_CONFIG)

    query_str = redshift.generate_query_string(
        table_name = 'YOUR TABLE NAME',     
        column_fields = ['col_1', 'col_2'],
        date_from = '2024-01-01', date_to = '2024-06-30', 
        date_column_name ='date'
    )

    # Data extracted from a DB will return as a dataframe
    extracted_data = redshift.get_data_from_redshift(query_str)

    # Define column name and desire data type
    active_users_schema = {
        'user_id': 'str',
        'date': 'timestamp'
    }
    scatter_plot_schema = {
        'X': 'float',
        'Y': 'float'
    }

    bubble_chart_schema = {
        'X': 'float',
        'Y': 'float',
        'Size': 'int'
    }

    user_activity_schema = {
        'month': 'datetime',
        '#_new_users': 'int',
        'accumulated_new_users': 'int',
        '#_active_users': 'int',
        '#_events_occurred': 'int'
    }

    data_processor = Processor()
    
    # Load data from sources or files
    data_processor.load_data(extracted_data, 'dataframe', 'active_users')
    
    f1_path = os.path.join(base_dir, 'scatterPlotData.csv')
    f2_path = os.path.join(base_dir, 'BubbleChartData.csv')
    f3_path = os.path.join(base_dir, 'UserActivityData.csv')

    data_processor.load_data(data_source=f1_path, dataset_type='csv', dataset_name='scatter_plot')
    data_processor.load_data(data_source=f2_path, dataset_type='csv', dataset_name='bubble_chart')
    data_processor.load_data(data_source=f3_path, dataset_type='csv', dataset_name='user_activity')

    # Data type conversion, remove dup and remove records with null values in specific columns
    data_processor.preprocess_data('active_users', active_users_schema, not_null_col=['user_id'])
    data_processor.preprocess_data('scatter_plot', scatter_plot_schema)
    data_processor.preprocess_data('bubble_chart', bubble_chart_schema)
    data_processor.preprocess_data('user_activity', user_activity_schema)
   
    # Create simple metrics
    data_processor.basic_aggregation(
        dataset_name='active_users',
        timestamp_column_name='date', 
        agg_column_name='user_id', 
        agg_by=['nunique'], 
        agg_period='weekly', 
        rename_agg_column={
            'user_id_nunique': 'active_users'
        },
        order_by='asc', 
        rounded_numerical_result_by=0
    )
    
    # Process and update datasets if necessary
    active_users_df = data_processor.get_processed_dataset_by_name('active_users')
    scatter_plot_df = data_processor.get_raw_dataset_by_name('scatter_plot')
    bubble_chart_df = data_processor.get_raw_dataset_by_name('bubble_chart')
    user_activity_df = data_processor.get_raw_dataset_by_name('user_activity')

    combined_datasets = {
        'active_users': active_users_df,
        'scatter_plot': scatter_plot_df,
        'bubble_chart': bubble_chart_df,
        'user_activity': user_activity_df
    }

    # Create visualization
    visualizer = DataVisualizer(combined_datasets)

    bar_chart_id = visualizer.generate_chart(
        dataset_name='active_users', 
        chart_type='bar', 
        x='period', 
        y='active_users', 
        title='Weekly Active Users', 
        labels={'x': 'week', 'y': 'active_users'},
        custom_styles={'color': '#6CABDD'}
    )

    summary_table_id = visualizer.generate_summary_table(
        dataset_name='user_activity',
        highlight_columns=['#_active_users', '#_events_occurred'], 
        highlight_column_color='#6CABDD', 
        highlight_text_color='#FFFFFF',
        title='Weekly Active Users Summary Statistics'
    )

    # Generate a scatter plot for sales data
    scatter_chart_id = visualizer.generate_chart(
        dataset_name='scatter_plot',
        chart_type='scatter',
        x='X',
        y='Y',
        title='Sample Scatter Plot',
        labels={'x': 'Date', 'y': 'Sales'},
        custom_styles={'color': '#6CABDD'}
    )

    # Generate a bubble chart for sales data with 'Customer_Count' affecting the bubble size
    bubble_chart_id = visualizer.generate_chart(
        dataset_name='bubble_chart',
        chart_type='bubble',
        x='X',
        y='Y',
        bubble_chart_size='Size',
        title='Sample Bubble Chart',
        labels={'x': 'Date', 'y': 'Sales'},
        custom_styles={'color': '#6CABDD'}
    )

    # Define description for each chart and table
    chart_descriptions = {
        bar_chart_id: {
            'text':'This bar chart illustrates the trend of active users on a weekly basis throughout the year. Each bar represents the number of users who were active during a given week, providing insights into user engagement and activity peaks. The chart helps identify weeks with unusually high or low activity, which could be correlated with marketing campaigns, product updates, or external events affecting user engagement. Understanding these patterns is crucial for optimizing user retention strategies and planning future engagement initiatives.',
            'format': 'list'
        }
    }

    table_descriptions = {
        summary_table_id: {
            'text': 'The table below provides a comprehensive summary of key user engagement metrics, including the mean, median, and standard deviation of weekly active users, as well as other relevant statistics. The summary aims to provide a quick snapshot of the overall health and stability of user engagement on the platform. By examining these statistics, stakeholders can gauge the effectiveness of recent initiatives, identify potential areas for improvement, and make data-driven decisions to enhance user experience and platform performance.',
            'format': 'paragraph'
        }
    }

    prev_week = (datetime.now() - timedelta(weeks=1)).strftime('%U')
    
    # Generate the report
    report = ReportGenerator(
        report_title= f'Sample Report for Week {prev_week}', 
        author_name='Han Nguyen - nhn@gridly.com', 
        created_date=datetime.now().strftime('%Y-%m-%d'), visualizer=visualizer
    ) 

    single_chart_titles = ['Weekly Active Users']
    dual_charts_titles = [('Sample Scatter Plot', 'Sample Bubble Chart')]
    table_titles = ['Weekly Active Users Summary Statistics']

    html_report = report.generate_html_report(single_chart_titles, dual_charts_titles, chart_descriptions, table_titles, table_descriptions)

    output_dir = os.path.join(os.path.dirname(__file__), 'data/output')
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Extract text and modify the HTML       
    selectors = {
        'tags': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'th', 'li'],
        'classes': ['metadata'],
        'ids': ['main-title', 'section-header']
    }    

    data, modified_html = extract(html_report, selectors=selectors, is_file=False)
    save_to_csv(data, os.path.join(output_dir, 'extracted_text.csv'))

    with open(os.path.join(output_dir, 'source_report.html'), 'w', encoding='utf-8') as file:
        file.write(modified_html)
        print('Source report saved to {}'.format(os.path.join(output_dir, 'source_report.html')))
    
    # Import source text to a Gridly localization grid 
    API_key = 'YOUR GRIDLY API KEY'
    view_id = 'YOUR GRIDLY VIEW ID'

    import_request = {
        'withHeader': True,
        'backup': False,
        'columnMappings':[{
                'columnId': 'column1',
                'fileColumnIndex':0
            }, 
            {
                'columnId': 'column2',
                'fileColumnIndex':1
            }
        ]
    }

    gridly_feature = GridlyFeature(view_id, API_key)

    try:
        gridly_feature.import_file(os.path.join(output_dir, 'extracted_text.csv'), import_request)
    except Exception as e:
        print(e)
    
    print("Waiting for translations to complete...")
    time.sleep(30)  
    
    try:
        gridly_feature.export_file(os.path.join(output_dir, 'exported_text.csv'))
    except Exception as e:
        print(e)

    source_html_path = os.path.join(output_dir, 'source_report.html')
    translations_csv_path = os.path.join(output_dir, 'exported_text.csv')
    target_languages = ['French', 'Swedish']
    
    paths = create_translated_html_files(source_html_path, translations_csv_path, output_dir, target_languages)

    client = SlackClient()

    files = {
        'YOUR SLACK CHANNEL ID': paths        
    }

    message = 'Hi guys, here are the localized reports for you!'

    for channel_id, file_paths in files.items():
        client.post_message(channel_id, message)
        for path in file_paths:
            file_id = client.upload_file(channel_id, path)

    print('End time: {}'.format(datetime.now().strftime('%B %d, %Y %H:%M:%S')))
    print('Total time: {}'.format(time.time() - start_time))