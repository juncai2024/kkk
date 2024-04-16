import os
import re

# 指定文件夹路径
folder_path = r'D:\source\ht_static\ht012'

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 检查文件名是否匹配指定格式
    match = re.match(r'(.+)\(\d+\)\.xlsx', filename)
    if match:
        # 提取文件名和扩展名
        base_name = match.group(1)
        extension = '.xlsx'
        # 构建新文件名
        new_filename = base_name + extension

        # 构建旧文件路径和新文件路径
        old_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)

        # 重命名文件
        os.rename(old_file_path, new_file_path)

        print(f'Renamed {filename} to {new_filename}')
    else:
        print(f'Skipped {filename} (does not match the pattern)')

print('All files renamed successfully')
