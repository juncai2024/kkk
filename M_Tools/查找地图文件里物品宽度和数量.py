import os
import json
import pandas as pd

def extract_values(folder_path):
    results = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                data = json.load(file)
                num_list = data.get('numList', [])
                widths = [item['width'] for item in num_list if 'width' in item]
                nums = [item['num'] for item in num_list if 'num' in item]
                results.append({
                    'Filename': filename,
                    'Width': ','.join(map(str, widths)),
                    'Num': ','.join(map(str, nums))
                })
    return results

folder_path = r'D:\set_excel\08level'
results = extract_values(folder_path)
df = pd.DataFrame(results)
df.to_excel(r'D:\set_excel\08level\file.xlsx', index=False)