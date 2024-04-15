import os
import json
import pandas as pd

# 指定文件夹路径
folder_path = r'D:\source\ht009_new\Product\Setting\Cfg012'

# 创建一个空的字典列表
data_list = []

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r') as f:
            data = json.load(f)
            file_name = filename[:-5]  # 去除文件扩展名
            num_dict = {}
            for item in data.get('numList', []):
                width = item.get('width')
                num = item.get('num')
                if width is not None and num is not None:
                    num_dict[f'Width{width}'] = num
            # 将每个文件的数据添加到字典列表中
            data_list.append({'File Name': file_name, **num_dict})

# 创建 DataFrame
df = pd.DataFrame(data_list)

# 填充缺失值为0
df = df.fillna(0)

# 保存为Excel文件
excel_filename = 'output2.xlsx'
df.to_excel(excel_filename, index=False)
print(f'Excel file "{excel_filename}" has been generated.')
