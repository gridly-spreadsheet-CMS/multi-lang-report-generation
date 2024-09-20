# Automated Data Processing and Reporting Using Gridly

## Introduction
In today's fast-paced business environment, efficiency in data processing and reporting is crucial. However, companies often grapple with the manual-intensive processes required to generate multilingual reports. These activities not only consume significant time and resources but also pose substantial risks of errors, leading to potential financial repercussions and delays in decision-making.

## Challenges in Traditional Data Reporting
**Inefficiency and Time Consumption:** Manual data processing is notoriously slow and resource-intensive. Teams spend hours compiling data into reports instead of focusing on strategic analysis or further data exploration.

**Cost Implications:** Manual reporting is fraught with the potential for errors due to human involvement. Mistakes in data entry or translation can lead to costly missteps, affecting overall business operations.

**Complexity in Multilingual Reporting:** Creating reports in multiple languages adds an additional layer of complexity. Relying solely on tools like Google Translate can lead to inaccuracies, particularly with industry-specific terminologies that require precise translation.

## Problem Overview
Traditionally, generating multilingual reports has been a cumbersome task, heavily reliant on manual effort. This is especially problematic in sectors where accuracy in terminology is paramount. While some automated tools are available, they often fail to seamlessly integrate with existing workflows or lack the sophistication needed for precise translations.

## Existing Solutions and Their Limitations
Most current solutions pivot on manual translations or basic automated tools, which may not consistently capture the nuances of specialized content. Furthermore, the process of extracting text to generate PO files for translation often isn't user-friendly, posing a barrier for non-technical staff.

This project automates the generation of multilingual data reports using Gridly for data management and Python for data processing and report generation. The system extracts data from various sources, processes it, and produces interactive, HTML-based reports in multiple languages, ensuring accuracy especially in domain-specific terminologies.

### Version
1.0.0

### Technologies and Frameworks
- **Python 3.x**: Ensure you have the latest version of Python installed.
- **Gridly API**: Used for managing translations and integrating multilingual capabilities seamlessly.

## Setup

### Installation

Clone the repository and navigate to the project directory. Install the necessary Python libraries using:

```bash
pip3 install -r requirements.txt
```

### Configuration
No additional configuration is required to run the application.

### How to Run
Extract data 
It depends on the data source. For example, if you want to extract data from a database, you need to provide credentials configured as environmental variables if you execute your script locally. 

Note: In the source directory, we have included a sample data generation function for testing purposes. This function generates mock data, allowing users to test the data processing pipeline without connecting to live data sources. It can be helpful for validating the workflow and ensuring the system behaves as expected.

Sample config object for MySQL:

```python
mysql_config = {
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "host": os.getenv('DB_HOST'),
    "database": os.getenv('DB_NAME'),
    "raise_on_warnings": True,
    "use_pure": False
}
```

Sample config object for AWS Redshift:
```python
# Configuration for Redshift connection using environment variables
REDSHIFT_CONFIG = {
    'host': os.getenv('REDSHIFT_HOST'),
    'database': os.getenv('REDSHIFT_DATABASE'),
    'port': int(os.getenv('REDSHIFT_PORT')),
    'db_user': os.getenv('REDSHIFT_USER'),
    'password': os.getenv('REDSHIFT_PASSWORD'),
    'iam': True,
    'cluster_identifier': os.getenv('REDSHIFT_CLUSTER'),
    'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
    'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'region': os.getenv('REDSHIFT_REGION')
}
```

Create a connection to the database using the appropriate configuration object:

```python
redshift = RedshiftConnector(REDSHIFT_CONFIG)
```

After setting up the database configuration, proceed to extract data using the defined configuration. This involves crafting SQL queries dynamically and executing them to fetch data:

```python
    query_str = redshift.generate_query_string(
        table_name = 'YOUR TABLE NAME',     
        column_fields = ['col_1', 'col_2'],
        date_from = '2024-01-01', date_to = '2024-06-30', 
        date_column_name ='date'
    )
    
    # Data extracted from a database will be returned as a Pandas dataframe
    extracted_data = redshift.get_data_from_redshift(query_str)
```

Define schemas for data preprocessing to ensure that the data types are correct and consistent, and to handle missing or duplicate data efficiently:

```python
    active_users_schema = {
        'user_id': 'str',
        'date': 'timestamp'
    }

```

Use the Processor class to load, clean, and prepare data for visualization:

```python
    data_processor = Processor()

    # Load data from sources or files
    data_processor.load_data(extracted_data, 'dataframe', 'active_users')

    # Data type conversion, remove dup and remove records with null values in specific columns
    data_processor.preprocess_data('active_users', active_users_schema, not_null_col=['user_id'])
    
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
```

With clean data, generate visualizations using the Visualizer class, which supports various chart types. For instance, generate a bar chart for active users:


```python
    # Combine processed datasets into a single object
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
        title='Gridly Weekly Active Users', 
        labels={'x': 'week', 'y': 'active_users'},
        custom_styles={'color': '#6CABDD'}
    )

```
The `visualizer` component of this project plays a crucial role in transforming the processed data into insightful, interactive visual representations. It supports a versatile range of chart types, each suited for different kinds of data analysis and reporting needs:

- **Line Charts**: Ideal for showcasing trends over time. Useful for visualizing data points connected by line segments, often used in time series data.
- **Bar Charts**: Effective for comparing quantities corresponding to different groups or categories.
- **Stacked Bar Charts**: Similar to bar charts but with the ability to stack values on top of each other within the bars, providing a cumulative representation of different categories.
- **Scatter Plots**: Best for displaying the relationships between two variables and identifying correlations with markers positioned at the intersecting points of data values on the plot.
- **Pie Charts**: Useful for illustrating the proportional distributions or percentage contributions of categories within a whole.
- **Bubble Charts**: A variation of scatter plots where an additional dimension can be represented by the size of the bubble markers, making it useful for visualizing three variables simultaneously.

These charts are powered by the `plotly` library, a powerful platform that enables the creation of highly customizable and interactive charts. `Plotly` excels in rendering complex graphical representations with features like zooming, panning, and hovering to display detailed data points, enhancing the user experience significantly.

By leveraging `plotly`, the `visualizer` provides you with the tools to tailor your charts according to specific needs or preferences, making your data reports more engaging and informative. Whether you need simple line charts or complex interactive bubble charts, `visualizer` equipped with `plotly` capabilities ensures that your data visualization needs are met with high precision and customizability.

Generate report in `source_language` using the ReportGenerator class
- Parameters:
    - title: Specifies the title of the report.
    - author_name: Identifies the author of the report.
    - created_date: Indicates when the report was created.
    - visualizer: A reference to the visualizer object, which is used to embed interactive charts within the report.


## Features
- Data Extraction: The system pulls data from configured sources, including databases and external files such as CSV, XLSX, or JSON.
- Data Preprocessing: Cleansing data, converting types, removing duplicates, and aggregating data as necessary.
- Report Generation: Supports generating dynamic and interactive HTML reports.
- Multilingual Support: Integrates with Gridly to manage translations, enhancing the accessibility of reports across different regions.
- Translation Management: Utilizes Gridly's translation management capabilities to ensure high accuracy in translations and updates.







