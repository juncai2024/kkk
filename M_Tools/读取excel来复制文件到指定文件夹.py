import pandas as pd
import os
import shutil

# 文件路径
excel_path = r'D:\study\test\sound\sound.xlsx'  # 替换为你的Excel文件路径
source_folder = r'D:\神泣\神泣5区\神泣5区测试服\Client\data\Sound'      # 替换为你的源文件夹路径
destination_folder = r'D:\study\test\sound'  # 替换为你的目标文件夹路径

# 读取Excel文件中的文件名
df = pd.read_excel(excel_path)
file_names_from_excel = df.iloc[:, 0].tolist()  # 假设Excel中的文件名都在A列

# 获取源文件夹中的所有文件名
files_in_source = os.listdir(source_folder)

# 遍历文件夹中的文件，并与Excel中的文件名进行匹配
for file_name in files_in_source:
    # 检查文件是否在Excel文件名列表中
    if file_name in file_names_from_excel:
        source_file_path = os.path.join(source_folder, file_name)
        destination_file_path = os.path.join(destination_folder, file_name)

        # 复制文件到目标文件夹
        shutil.copy(source_file_path, destination_file_path)
        print(f"文件已复制: {file_name}")

print("所有匹配的文件已复制完成。")
