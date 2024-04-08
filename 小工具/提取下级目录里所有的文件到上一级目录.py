import os
import shutil

# 源文件夹路径
source_folder = r"D:\source2\ht012\new12_13"

# 目标文件夹路径
destination_folder = r"D:\source2\ht012\new12_13"

# 遍历源文件夹中的所有子文件夹
for root, dirs, files in os.walk(source_folder):
    for file in files:
        # 检查文件类型为.fbx
        if file.endswith(".jpg"):
            # 构造源文件的完整路径
            source_file_path = os.path.join(root, file)

            # 构造目标文件夹的完整路径
            destination_file_path = os.path.join(destination_folder, file)

            # 复制文件
            shutil.move(source_file_path, destination_file_path)

print("文件复制完成！")