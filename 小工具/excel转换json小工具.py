import pandas as pd
import json
import os


def excel_to_json(excel_path):
    # 读取Excel文件的所有工作表
    xls = pd.ExcelFile(excel_path)

    json_result = {}

    # 遍历所有工作表
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)

        # 获取第一行作为字段名
        columns = df.iloc[0]
        # 获取字段名和数据类型
        fields = {}
        for col in columns:
            if isinstance(col, str) and '(' in col:
                field_name, type_info = col.split('(')
                type_key, type_value = type_info.strip(')').split(':')
                fields[field_name] = type_value

        # 从第三行开始读取数据
        data = df.iloc[2:].reset_index(drop=True)

        # 根据字段类型转换数据
        def convert_type(value, dtype):
            if pd.isnull(value):
                return None
            if dtype == 's':
                return str(value)
            elif dtype == 'n':
                return int(value)
            elif dtype == 'a':
                if isinstance(value, str):
                    return [item.strip() for item in value.split(',')]
                else:
                    return value
            elif dtype == 'b':
                return bool(value)
            elif dtype == 'd':
                return json.loads(value) if isinstance(value, str) else value
            else:
                return value

        result = {}
        for idx, row in data.iterrows():
            row_dict = {}
            for col_name, dtype in fields.items():
                col_label = f'{col_name}(t:{dtype})'
                if col_label in columns.values:
                    row_dict[col_name] = convert_type(row[columns == col_label].values[0], dtype)
            result[idx + 1] = row_dict  # 用idx + 1作为键，符合示例中的格式

        json_result[sheet_name] = result

    # 输出JSON文件
    json_path = os.path.splitext(excel_path)[0] + '.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_result, f, ensure_ascii=False, indent=4)

    print(f"JSON文件已保存至: {json_path}")


if __name__ == "__main__":
    excel_path = input("请输入Excel文件路径: ")
    excel_to_json(excel_path)
