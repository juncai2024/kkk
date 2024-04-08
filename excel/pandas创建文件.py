import pandas as pd
import os

os.chdir(r'D:\study\test')
datt = pd.DataFrame({'序号': [1, 2, 3], '姓名': ['孙悟空', '孙行者', '行者孙']})
datt = datt.set_index('序号')
datt.to_excel('zjc666.xlsx')
