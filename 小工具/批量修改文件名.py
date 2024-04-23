import os
import pandas as pd

def add_prefix(folder_path):
    prefix = input("请输入要添加的前缀字符：")
    for filename in os.listdir(folder_path):
        old_filepath = os.path.join(folder_path, filename)
        if os.path.isfile(old_filepath):
            new_filename = prefix + filename
            new_filepath = os.path.join(folder_path, new_filename)
            os.rename(old_filepath, new_filepath)

def add_suffix(folder_path):
    suffix = input("请输入要添加的后缀字符：")
    for filename in os.listdir(folder_path):
        old_filepath = os.path.join(folder_path, filename)
        if os.path.isfile(old_filepath):
            filename_parts = os.path.splitext(filename)
            new_filename = filename_parts[0] + suffix + filename_parts[1]
            new_filepath = os.path.join(folder_path, new_filename)
            os.rename(old_filepath, new_filepath)

def rename_from_excel(folder_path, excel_path):
    df = pd.read_excel(excel_path)
    for index, row in df.iterrows():
        old_filename = row['原文件名']
        new_filename = row['修改后文件名']
        old_filepath = os.path.join(folder_path, old_filename)
        new_filepath = os.path.join(folder_path, new_filename)
        if os.path.exists(new_filepath):
            counter = 1
            while os.path.exists(new_filepath):
                name, extension = os.path.splitext(new_filename)
                new_filename = f"{name}_{counter}{extension}"
                new_filepath = os.path.join(folder_path, new_filename)
                counter += 1
        os.rename(old_filepath, new_filepath)

def remove_chars(folder_path):
    chars = input("请输入要删除的字符：")
    for filename in os.listdir(folder_path):
        old_filepath = os.path.join(folder_path, filename)
        if os.path.isfile(old_filepath):
            new_filename = filename.replace(chars, '')
            new_filepath = os.path.join(folder_path, new_filename)
            os.rename(old_filepath, new_filepath)

def main():
    folder_path = input("请输入要处理的文件夹路径：")
    print("功能列表：")
    print("1. 批量在文件名前加指定的前缀")
    print("2. 批量在文件名后加后缀")
    print("3. 读取excel列表，按excel列表里的文件名给文件夹里的文件重命名")
    print("4. 删除文件名里的指定字符")
    option = input("请选择功能(1/2/3/4)：")

    if option == '1':
        add_prefix(folder_path)
    elif option == '2':
        add_suffix(folder_path)
    elif option == '3':
        excel_path = input("请输入excel文件的路径：")
        rename_from_excel(folder_path, excel_path)
    elif option == '4':
        remove_chars(folder_path)
    else:
        print("无效的选项，请重新运行程序并输入正确的选项。")

if __name__ == "__main__":
    main()
