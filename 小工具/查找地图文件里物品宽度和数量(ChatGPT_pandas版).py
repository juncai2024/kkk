import os
import json
import pandas as pd

# 指定文件夹路径
folder_path = r'D:\source\ht_static\地图备份\地图0311IOS困难关修改'

# 创建一个空的DataFrame
df = pd.DataFrame(columns=['File Name', 'Width', 'Num'])

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as f:
            data = json.load(f)
            file_name = filename[:-5]  # 去除文件扩展名
            for item in data.get('numList', []):
                width = item.get('width')
                num = item.get('num')
                if width is not None or num is not None:
                    df = pd.concat([df, pd.DataFrame({'File Name': [file_name], 'Width': [width], 'Num': [num]})], ignore_index=True)

# 保存为Excel文件
excel_filename = 'output2.xlsx'
df.to_excel(excel_filename, index=False)
print(f'Excel file "{excel_filename}" has been generated.')
