import pandas as pd
import os


def convert_csv_to_excel(da_path):
    for root, dirs, files in os.walk(da_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    df.to_excel(file_path.replace('.csv', '.xlsx'), index=False)
                    print(f"成功将 {file} 转换为Excel文件")
                except Exception as e:
                    print(f"处理文件 {file} 时出错: {e}")


def convert_excel_to_csv(da_path):
    for root, dirs, files in os.walk(da_path):
        for file in files:
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_excel(file_path)
                    df.to_csv(file_path.replace('.xlsx', '.csv'), index=False)
                    print(f"成功将 {file} 转换为CSV文件")
                except Exception as e:
                    print(f"处理文件 {file} 时出错: {e}")


if __name__ == "__main__":
    fp_path = r'D:\study\test\cs'
    print('请输你要处理的文件方式：')
    print('1: Excel 转换成 CSV')
    print('2: CSV 转换成 Excel')
    choice = input('请输入你的选择：')

    if choice == '1':
        convert_excel_to_csv(fp_path)
    elif choice == '2':
        convert_csv_to_excel(fp_path)
    else:
        print("无效的选择，请输入 1 或 2")
