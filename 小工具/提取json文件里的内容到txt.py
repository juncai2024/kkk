import os
import json

# 切换到指定目录
os.chdir('/Users/larry/Documents/study/test')

# JSON 文件路径
patch1 = r'/Users/larry/Documents/study/test/字幕.json'

# 打开 JSON 文件并读取内容
with open(patch1, 'r') as f:
    data = json.load(f)
    text_data = []

    # 遍历每个字幕内容，提取并整理成列表
    for item in data.get('body', []):
        text = item.get('content')
        text_data.append(text)

# 将提取的内容写入到 txt 文件中
with open("subtitle.txt", "w") as txt_file:
    for line in text_data:
        txt_file.write(line + "\n")  # 每个内容占据一行，加上换行符

# 关闭文件
txt_file.close()