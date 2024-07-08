import os
import pandas as pd

# 指定文件夹路径
folder_path = r'D:\source2\ht007\goodsmaster20240104\TextAsset'

# 获取所有符合命名规则的 JSON 文件
json_files = [f for f in os.listdir(folder_path)if f.endswith((".png"))]

# 创建 DataFrame
df = pd.DataFrame({'FileName': json_files})

# 将 DataFrame 写入 Excel 文件的A列，output.xlsx 换成指定的excel文件路径
df.to_excel(r'D:\source2\ht007\goodsmaster20240104\TextAsset\output.xlsx', index=False, header=None)

print("数据处理完毕")
