import os

ip0 = input(r'请输入文件夹路径(例如 C:\abc)：')
ip1 = input('请输入要添加或删除的名字：')
ip2 = int(input('添加请按1，删除请按2：'))


# 返回指定文件夹下的文件和文件夹的名字，返回是一个列表
list1 = os.listdir(ip0)


#遍历目录列表中的每一个数据
for 遍历文件名 in 目录列表:

    if ip2 == 1:
        新名字 = ip1 + 遍历文件名
        print(新名字)
    elif ip2 == 2:
        前缀长度 = len(ip1)
        新名字 = 遍历文件名[前缀长度:]
        print(新名字)
    else:
        print('输入错误')
        break

    os.chdir(ip0)   # 改变当前工作目录到指定路径
    os.rename(遍历文件名,新名字) # 重命名




