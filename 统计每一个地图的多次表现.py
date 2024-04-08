import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def read_json_file(json_file_path):
    # Read the JSON file
    json_data = pd.read_json(json_file_path)

    # Extract level IDs and corresponding map names
    level_map_dict = {}
    for level_id, level_info in json_data.items():
        map_name = level_info['MapName']
        level_map_dict[level_id] = map_name

    return level_map_dict

def process_excel_file(excel_file_path, level_map_dict):
    # Read the Excel file
    excel_data = pd.read_excel(excel_file_path)

    # Filter out the rows where id is 0
    excel_data = excel_data[excel_data['id'] != 0]

    # Create a dictionary to store the final output and data for charts
    output_dict = {}
    chart_data = {}

    # Iterate over each row in the Excel data
    for index, row in excel_data.iterrows():
        level_id = str(row['id'])
        t0_percent = row['t0%']
        t6plus_percent = row['t6plus%']

        # Get the corresponding map name using level_id
        map_name = level_map_dict.get('L' + level_id.zfill(3))

        # If map name exists, append the data
        if map_name:
            if map_name not in output_dict:
                output_dict[map_name] = []
                chart_data[map_name] = {'id': [], 't0%': [], 't6plus%': []}

            output_dict[map_name].append(f"ID: {level_id} [0] {t0_percent} [6] {t6plus_percent}")
            chart_data[map_name]['id'].append(level_id)
            chart_data[map_name]['t0%'].append(t0_percent)
            chart_data[map_name]['t6plus%'].append(t6plus_percent)

    return output_dict, chart_data

def create_charts(chart_data, map_name):
    # Create charts for t0% and t6plus%
    plt.figure(figsize=(10, 4))

    # Chart for t0%
    plt.subplot(1, 2, 1)
    plt.plot(chart_data[map_name]['id'], chart_data[map_name]['t0%'], marker='o')
    plt.title(f'{map_name} - t0%')
    plt.xlabel('Level ID')
    plt.ylabel('Win Rate (%)')

    # Chart for t6plus%
    plt.subplot(1, 2, 2)
    plt.plot(chart_data[map_name]['id'], chart_data[map_name]['t6plus%'], marker='o', color='r')
    plt.title(f'{map_name} - t6plus%')
    plt.xlabel('Level ID')
    plt.ylabel('Win Rate (%)')

    plt.tight_layout()
    plt.savefig(f'{map_name}_chart.png')
    plt.close()

def create_excel_file(output_dict, chart_data, output_file_path):
    # Prepare data for DataFrame
    data_for_df = []
    for map_name, level_data in output_dict.items():
        row = [map_name] + level_data
        data_for_df.append(row)
        create_charts(chart_data, map_name)

    # Create DataFrame
    df = pd.DataFrame(data_for_df)

    # Write to Excel
    with pd.ExcelWriter(output_file_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, header=False, sheet_name='Data')

        # Add charts to the Excel file
        for map_name in chart_data.keys():
            workbook = writer.book
            worksheet = workbook.add_worksheet(f'{map_name} Chart')
            worksheet.insert_image('A1', f'{map_name}_chart.png')

# File paths
json_file_path = 'level_summary-1.0.27 整体改简单之前.json'
excel_file_path = 'HT007_TripleMatchShelf-android-2023-12-6-2023-12-21-0day-global-all-1.0.27-活跃日Stage情况(不支持分组).xlsx'
output_file_path = '地图表现统计.xlsx'

# Read and process files
level_map_dict = read_json_file(json_file_path)
output_dict, chart_data = process_excel_file(excel_file_path, level_map_dict)

# Create output Excel file with charts
create_excel_file(output_dict, chart_data, output_file_path)

# Note: Replace 'path_to_your_json_file.json' and 'path_to_your_excel_file.xlsx' with the actual paths to your files.
# The output will be saved in 'output_file_with_charts.xlsx'. You can change this to your preferred file name and path.
