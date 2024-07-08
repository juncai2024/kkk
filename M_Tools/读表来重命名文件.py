import pandas as pd
import os

# 读取Excel文件
excel_file = 'data.xlsx'
df = pd.read_excel(excel_file)

# 遍历Excel文件中的每一行
for index, row in df.iterrows():
    # 获取Excel中A列和B列的值，A列存放现在的文件名，B列是新新文件名
    json_filename = row['A']
    new_filename = row['B']

    # 构建JSON文件的完整路径
    json_filepath = os.path.join('B', json_filename)

    # 检查JSON文件是否存在
    if os.path.exists(json_filepath):
        # 构建新的文件路径
        new_filepath = os.path.join('B', new_filename)

        # 重命名JSON文件
        os.rename(json_filepath, new_filepath)
        print(f'Renamed {json_filename} to {new_filename}')
    else:
        print(f'JSON file {json_filename} not found')

print('All files renamed successfully')
