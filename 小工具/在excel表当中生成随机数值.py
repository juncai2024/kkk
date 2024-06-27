import pandas as pd
import numpy as np

# 生成1到40的整数数组并打乱顺序
numbers = np.arange(1, 41)
np.random.shuffle(numbers)

# 创建一个 DataFrame
df = pd.DataFrame(numbers, columns=['Numbers'])

# 将 DataFrame 写入 Excel 文件的A列
df.to_excel(r'D:\work\test1.xlsx', index=False, header=None)

print("数据处理完毕")
