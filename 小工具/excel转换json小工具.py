import pandas as pd
import json
import os


def excel_to_json(excel_path):
    # 读取Excel文件
    df = pd.read_excel(excel_path)

    # 提取数据，跳过前两行
    data = df.iloc[2:].to_dict(orient='records')

    # 构建JSON对象
    json_data = {
        'data': data
    }

    # 保存JSON文件
    json_path = os.path.splitext(excel_path)[0] + '.json'
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    return json_path


# 获取用户输入的Excel文件路径
excel_file_path = input(r"请输入需要转换的Excel文件路径：")
json_file_path = excel_to_json(excel_file_path)
print(f'JSON文件已保存至：{json_file_path}')