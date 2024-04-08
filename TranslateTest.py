import os
import json
from translate import Translator
import opencc

# 指定文件夹路径
folder_path = "C:/Users/admin/Desktop/I18N"
result = []
# 获取文件夹中所有 JSON 文件名
json_files = [file for file in os.listdir(folder_path) if file.endswith(".json")]
text = 'I will go home right now'
languages = ['de', 'en', 'es', 'fr', 'hi', 'it', 'ja', 'ko', 'pt', 'ru', 'zh-CHS', 'zh-CHT']

'''def convert_simplified_to_traditional(data):
    if isinstance(data, str):
        return json_data.convert(data)
    elif isinstance(data, list):
        return [convert_simplified_to_traditional(item) for item in data]
    elif isinstance(data, dict):
        return {k: convert_simplified_to_traditional(v) for k, v in data.items()}
    else:
        return data
'''

for lang in languages:
    translator = Translator(to_lang=lang)
    translation = translator.translate(text)
    result.append(translation)

cc = opencc.OpenCC('s2t')
result[-1] = cc.convert(result[-1])

for i in range(len(result)):
    file_name = json_files[i]
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'r', encoding='utf-8') as f:  # 使用 "r" 模式打开文件
        json_data = json.load(f)
        last_field_name = int(list(json_data.keys())[-2])
        newId = last_field_name + 1
        data_list = list(json_data.items())
        data_list.insert(len(data_list) - 1, (newId, result[i]))
        updated_data = dict(data_list)

    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(updated_data, file, ensure_ascii=False, indent=2, separators=(",", ": "))
