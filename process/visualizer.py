import plotly.io as pio
import plotly.express as px
import uuid
from datetime import datetime
import os
import pandas as pd

output_dir = os.path.join(os.path.dirname(__file__), 'data/images/')

class DataVisualizer:
    def __init__(self, datasets):
        self.datasets = datasets
        self.charts = {}
        self.summary_tables = {}     


    def generate_chart(self, dataset_name, chart_type='line', x=None, y=None, title=None, labels=None, bubble_chart_size=None, custom_styles=None
                       , output_dir=output_dir):
        """
        Generates an interactive chart using Plotly.

        Args:
            chart_type (str): Type of the chart ('line', 'bar', 'scatter', etc.).
            x (str): The name of the column to be used as x-axis.
            y (str): The name of the column to be used as y-axis.
            title (str): Title of the chart.
            labels (dict): Labels for axes, e.g., {'x':'Date', 'y':'Value'}
            width (int): Width of the chart.
            height (int): Height of the chart.
        Returns:
            The Plotly figure object for further customization or display.
        """

        if dataset_name not in self.datasets:
            raise ValueError(f'''Dataset '{dataset_name}' not found.''')
        
        dataframe = self.datasets[dataset_name]
        fig = None
        
        if chart_type == 'line':
            fig = px.line(dataframe, x=x, y=y, labels=labels)
        
        elif chart_type == 'bar':
            fig = px.bar(dataframe, x=x, y=y, labels=labels)
        
        elif chart_type == 'stacked_bar':
            fig = px.bar(dataframe, x=x, y=y, labels=labels, barmode='stack')
        
        elif chart_type == 'scatter':
            fig = px.scatter(dataframe, x=x, y=y, labels=labels)
        
        elif chart_type == 'pie':
            if not y:  # Ensure 'y' is provided for pie chart as category names
                raise ValueError("For pie charts, 'y' must specify the category names.")
            fig = px.pie(dataframe, values=x, names=y, labels=labels)
        
        elif chart_type == 'bubble':
            if not bubble_chart_size:
                raise ValueError("For bubble charts, 'size' must specify the column for marker size.")
            fig = px.scatter(dataframe, x=x, y=y, size=bubble_chart_size, labels=labels)
        
        else:
            raise ValueError("Unsupported chart type. Supported types: 'line', 'bar', 'scatter', 'pie', 'bubble'.")

        fig.update_layout(
            plot_bgcolor='rgba(0, 0, 0, 0)',  # Makes plot background transparent
            paper_bgcolor='rgba(0, 0, 0, 0)',  # Makes paper background transparent
            autosize=True,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(
                showline=False, 
                showgrid=False,  
                zeroline=False  
            ),
            yaxis=dict(
                showline=False, 
                showgrid=False, 
                zeroline=False  
            )
        )

        # Apply custom styles if provided
        if custom_styles:
            if 'color' in custom_styles:
                fig.update_traces(marker_color=custom_styles['color'])
            if 'font_family' in custom_styles:
                fig.update_layout(font_family=custom_styles['font_family'])
            if 'font_size' in custom_styles:
                fig.update_layout(font_size=custom_styles['font_size'])
            if 'axis_color' in custom_styles:
                fig.update_xaxes(color=custom_styles['axis_color'])
                fig.update_yaxes(color=custom_styles['axis_color'])

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            pio.write_image(fig, f'''{output_dir}{title}.png''')
            print(f"Image saved successfully")
        except Exception as e:
            print(f"Failed to save image: {e}")

        pio.write_image(fig, file=f'''{output_dir}{title}.png''', format='png', engine='kaleido')

        chart_html = pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config={'responsive': True})
        
        id = str(uuid.uuid4())

        self.charts[id] = {
            'html': chart_html,
            'title': title,
            'created_at': datetime.now(),
            'file_path': f'{output_dir}{title}.png'
        }
        return id


    def generate_summary_table(self, dataset_name, highlight_columns=None, highlight_column_color=None, highlight_text_color='#FFFFFF', title=None, rounded_by=0):         
        def apply_styles(value, text_color):
            return f'color: {text_color};'

        if dataset_name not in self.datasets:
            raise ValueError(f'''Dataset '{dataset_name}' not found.''')
        
        dataframe = self.datasets[dataset_name]

        # Format dictionary to specify formatting for each column
        format_dict = {}
        for col in dataframe.columns:
            if pd.api.types.is_numeric_dtype(dataframe[col]):
                format_dict[col] = f"{{:,.{rounded_by}f}}"  # Formatting for numeric columns
            elif pd.api.types.is_datetime64_any_dtype(dataframe[col]):
                dataframe[col] = dataframe[col].dt.strftime('%Y-%m-%d')  # Convert datetime columns to string format

        styled_stats = dataframe.style.format(format_dict) \
                                    .hide(axis='index') \
                                    .bar(subset=highlight_columns, color=highlight_column_color) \
                                    .set_table_styles([
                                        {'selector': 'th', 'props': [('padding', '10px'), ('text-align', 'center')]},
                                        {'selector': 'td', 'props': [('padding', '8px')]}
                                    ]) \
                                    .applymap(apply_styles, text_color=highlight_text_color, subset=highlight_columns)

        summary_table = styled_stats.to_html().replace('<table border="1" class="dataframe">', '<table class="table table-striped">')

        id = str(uuid.uuid4())

        self.summary_tables[id] = {
            'html': summary_table,
            'title': title,
            'created_at': datetime.now()
        }
        return id

    def get_chart_by_id(self, chart_id):
        return self.charts.get(chart_id, {}).get('html')
    
    def get_chart_by_title(self, title):
        for chart_id, chart_info in self.charts.items():
            if chart_info['title'] == title:
                return chart_info
        return None

    def get_chart_id_by_title(self, title):
        for chart_id, chart_info in self.charts.items():
            if chart_info.get("title") == title:
                return chart_id
        return None  
    
    def get_summary_table_by_id(self, summary_table_id):
        return self.summary_tables.get(summary_table_id, {}).get('html')
    
    def get_summary_table_by_title(self, title):
        for table_id, table_info in self.summary_tables.items():
            if table_info['title'] == title:
                return table_info
        return None

    def get_summary_table_id_by_title(self, title):
        for table_id, table_info in self.summary_tables.items():
            if table_info.get("title") == title:
                return table_id
        return None
    
    def list_charts(self):
        return [{'id': key, **value} for key, value in self.charts.items()]

    def list_summary_tables(self):
        return [{'id': key, **value} for key, value in self.summary_tables.items()]


