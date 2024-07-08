import os
import json
import pandas as pd


# 确保安装了pandas和openpyxl库
# pip install pandas openpyxl

def find_badge_files(folder_path):
    # 初始化存储结果的列表
    files_with_badge = []

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)

            # 尝试打开并加载JSON文件
            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)

                    # 检查'badge'键是否存在且其值为"hard"或"extreme"
                    if data.get('badge') in ['hard', 'extreme']:
                        files_with_badge.append({
                            'Filename': filename,
                            'Badge': data['badge']
                        })
            except Exception as e:
                # 打印错误信息，但继续处理下一个文件
                print(f"Error processing {filename}: {e}")

    return files_with_badge


# 设置文件夹路径
folder_path = r'D:\set_excel\08level'

# 调用函数查找符合条件的文件
result = find_badge_files(folder_path)

# 使用pandas创建DataFrame
df = pd.DataFrame(result)

# 将DataFrame写入Excel文件
excel_path = r'D:\set_excel\08level\file.xlsx'
df.to_excel(excel_path, index=False)

print(f"The Excel file has been created at {excel_path}")