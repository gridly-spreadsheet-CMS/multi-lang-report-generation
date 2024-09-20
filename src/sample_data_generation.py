import pandas as pd
import numpy as np
import os

dir = os.path.join(os.path.dirname(__file__), 'data/sample/')

def generate_sample_data():
    np.random.seed(0)  # For reproducibility

    # Data for line and bar charts
    dates = pd.date_range(start='2021-01-01', periods=100, freq='D')
    values = np.random.randint(1, 100, size=100)
    line_bar_data = pd.DataFrame({'Date': dates, 'Value': values})
    line_bar_data.to_csv(f'{dir}LineBarChartData.csv', index=False)

    # Data for scatter plots
    x_values = np.random.normal(50, 15, 100)
    y_values = np.random.normal(50, 15, 100)
    scatter_data = pd.DataFrame({'X': x_values, 'Y': y_values})
    scatter_data.to_csv(f'{dir}ScatterPlotData.csv', index=False)

    # Data for pie charts
    categories = ['A', 'B', 'C', 'D']
    counts = np.random.randint(100, 500, size=4)
    pie_data = pd.DataFrame({'Category': categories, 'Count': counts})
    pie_data.to_csv(f'{dir}PieChartData.csv', index=False)

    # Data for heatmaps
    matrix_data = np.random.randint(0, 10, size=(10, 10))
    heatmap_data = pd.DataFrame(matrix_data)
    heatmap_data.to_csv(f'{dir}HeatmapData.csv', index=False)

    # Data for bubble charts
    bubble_x = np.random.normal(100, 20, 100)
    bubble_y = np.random.normal(200, 50, 100)
    bubble_sizes = np.random.randint(10, 100, size=100)
    bubble_data = pd.DataFrame({
        'X': bubble_x,
        'Y': bubble_y,
        'Size': bubble_sizes
    })
    bubble_data.to_csv(f'{dir}BubbleChartData.csv', index=False)


def generate_user_activity_data():
    # Define the months for which the data is to be generated
    months = pd.date_range(start='2024-01-01', periods=6, freq='MS')  # MS is month start frequency

    # Data - Since you provided a constant pattern, I'll replicate it here dynamically
    data = {
        'month': months,
        '#_new_users': [12, 2, 5, 7, 7, 8],  # No new users every month
        'accumulated_new_users': [12, 14, 19, 26, 33, 41],  # Constant accumulated users
        '#_active_users': [52, 63, 47, 49, 54, 21],  # Random active users data
        '#_edit_cells': [367647, 335432, 475321, 240353, 237733, 519867]  # Random edits per month
    }

    # Create DataFrame
    df = pd.DataFrame(data)
    df['month'] = df['month'].dt.strftime('%Y-%m-%d')  # Format date as YYYY-MM-DD

    # Save to CSV file
    df.to_csv(f'{dir}UserActivityData.csv', index=False)

if __name__ == '__main__':
    generate_sample_data()
    generate_user_activity_data()
