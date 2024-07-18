import os
import json
import pandas as pd

# 指定文件夹路径
folder_path = r'D:\study\test'

# 验证文件夹路径是否存在
if not os.path.exists(folder_path):
    raise FileNotFoundError(f"The folder path '{folder_path}' does not exist.")

# 创建一个空的列表来存储数据
data_list = []

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                file_name = filename[:-5]  # 去除文件扩展名
                for item in data.get('numList', []):
                    width = item.get('width')
                    num = item.get('num')
                    if width is not None or num is not None:
                        data_list.append({'File Name': file_name, 'Width': width, 'Num': num})
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {file_path}")
        except Exception as e:
            print(f"An error occurred while processing file: {file_path}. Error: {e}")

# 将数据列表转换为DataFrame
df = pd.DataFrame(data_list, columns=['File Name', 'Width', 'Num'])

# 保存为Excel文件
excel_filename = r'D:\study\test\output2.xlsx'
df.to_excel(excel_filename, index=False)
print(f'Excel file "{excel_filename}" has been generated.')
