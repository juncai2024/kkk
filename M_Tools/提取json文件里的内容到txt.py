import os
import json

# 目标目录
target_dir = r'E:\直播录屏\金瓶梅字幕'
os.chdir(target_dir)

# 遍历目录下所有 json 文件
for filename in os.listdir(target_dir):
    if filename.endswith('.json'):
        json_path = os.path.join(target_dir, filename)
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                text_data = []
                for item in data.get('body', []):
                    text = item.get('content', '')
                    if text:
                        text_data.append(text)

            # 生成对应的 txt 文件（比如 15.json -> 15_subtitle.txt）
            txt_filename = f"{os.path.splitext(filename)[0]}_subtitle.txt"
            with open(txt_filename, 'w', encoding='utf-8') as txt_file:
                txt_file.write('\n'.join(text_data))  # 更高效的写入方式
            print(f"成功处理：{filename} -> {txt_filename}")

        except Exception as e:
            print(f"处理 {filename} 失败：{str(e)}")