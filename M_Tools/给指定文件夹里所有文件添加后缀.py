import os

# 指定文件夹路径
folder_path = 'your_folder_path'

# 遍历文件夹中的所有文件
for filename in os.listdir(folder_path):
    # 构建原始文件路径和新文件路径
    old_file_path = os.path.join(folder_path, filename)
    new_file_path = old_file_path + '.json'

    # 对文件名进行修改
    os.rename(old_file_path, new_file_path)
    print(f'Renamed "{old_file_path}" to "{new_file_path}"')

print('File renaming completed.')
