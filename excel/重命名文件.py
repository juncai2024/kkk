import os
os.chdir(r'D:\study\test')
with open('ccfg.txt', 'r', encoding='utf-8') as filess:
    filess1 = filess.readlines()
    for i in filess1:
        print(i)

    filess.close()