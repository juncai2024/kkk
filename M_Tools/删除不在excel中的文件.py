import os
import pandas as pd

# 设置当前工作目录
os.chdir(r'D:\set_excel')

# 读取 named.xlsx 中的文件名
named_df = pd.read_excel('08level.xlsx', header=None, names=['FileName'])

# 获取 A 文件夹中的 PNG 文件列表
png_files = [f for f in os.listdir('B') if f.lower().endswith('.png')]
print(png_files)
# 遍历 A 文件夹中的文件，删除不在 named.xlsx 中的文件
for png_file in png_files:
    if png_file not in named_df['FileName'].values:
        file_path = os.path.join('B', png_file)
        os.remove(file_path)
        print(f"Deleted: {file_path}")

print("Deletion complete.")
