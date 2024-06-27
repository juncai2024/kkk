import json

import pandas as pd

# 指定 JSON 文件路径
json_file_path = r'D:\study\test\A\Rewards.json'

# 读取 JSON 文件
with open(json_file_path, 'r') as f:
    data = json.load(f)

# 创建一个空的 DataFrame
dfs = []

# 遍历 JSON 数据并添加到 DataFrame 列表中
for tier, rewards in data.items():
    for reward in rewards:
        reward_type = reward[0]['type']
        reward_amount = reward[0]['amount']
        dfs.append(pd.DataFrame({'Tier': [tier], 'Type': [reward_type], 'Amount': [reward_amount]}))

# 合并 DataFrame
df = pd.concat(dfs, ignore_index=True)

# 将 DataFrame 保存为 Excel 文件
excel_filename = 'weekly_challenge_rewards.xlsx'
df.to_excel(excel_filename, index=False)
print(f'Excel file "{excel_filename}" has been generated.')
