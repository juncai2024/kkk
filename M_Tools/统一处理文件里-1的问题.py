import os

# 让用户输入文件夹路径
folder_path = r'/Volumes/MiniDataHD/课程/回放/12月回放/先秦(12.29)'

# 检查输入的路径是否存在
if not os.path.isdir(folder_path):
    print(f'文件夹路径 "{folder_path}" 不存在！')
else:
    # 遍历文件夹中的文件
    for filename in os.listdir(folder_path):
        # 检查是否是.mp4文件，并且文件名中包含'-1'
        if filename.endswith('-1.mp4'):
            # 构造新的文件名，去掉'-1'
            new_filename = filename.replace('-1.mp4', '.mp4')
            # 获取完整的旧文件路径和新文件路径
            old_file = os.path.join(folder_path, filename)
            new_file = os.path.join(folder_path, new_filename)
            # 重命名文件
            os.rename(old_file, new_file)
            print(f'已将 {filename} 重命名为 {new_filename}')

    print("处理完成！")
