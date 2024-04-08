import pandas as pd
import os

# 指定文件夹路径
folder_path = r'C:\Users\Admin\Desktop\有修改关卡\2020数据分析\2020数据'

# 获取文件夹中所有的Excel文件
excel_files = [file for file in os.listdir(folder_path) if file.endswith('.xlsx')]

# 如果存在Excel文件
if excel_files:
    # 创建一个空DataFrame用于存储所有数据
    all_data = pd.DataFrame()

    # 逐个读取Excel文件并合并数据
    for file in excel_files:
        # 构建完整文件路径
        file_path = os.path.join(folder_path, file)

        # 读取Excel文件数据
        excel_data = pd.read_excel(file_path)

        # 将当前文件的数据合并到总数据中
        all_data = pd.concat([all_data, excel_data], ignore_index=True)

    # 将合并后的数据保存到新的Excel文件
    output_file = r'C:\Users\Admin\Desktop\有修改关卡\2020数据分析\2020数据\file.xlsx'
    all_data.to_excel(output_file, index=False)

    print(f'合并完成，结果已保存到 {output_file}')
else:
    print('指定文件夹中没有Excel文件')
