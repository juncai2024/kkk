import os
from PIL import Image


def convert_image_format(ip_dir, ip_format, op_format, save_opt, op_dir=None):
    # 获取文件夹中的所有文件
    files = os.listdir(ip_dir)

    # 过滤出指定格式的文件
    images = [f for f in files if f.endswith(f".{ip_format}")]

    if not images:
        print(f"在目录中没有找到{ip_format}格式的文件。")
        return

    # 处理每个图片文件
    for img_name in images:
        img_path = os.path.join(ip_dir, img_name)

        # 打开图片文件
        img = Image.open(img_path)

        # 获取不带扩展名的文件名
        base_name = os.path.splitext(img_name)[0]

        # 确定输出路径
        if save_opt == '1':
            output_path = os.path.join(ip_dir, f"{base_name}.{op_format}")
        elif save_opt == '2':
            if not op_dir:
                print("未提供输出目录。")
                return
            if not os.path.exists(op_dir):
                os.makedirs(op_dir)
            output_path = os.path.join(op_dir, f"{base_name}.{op_format}")
        else:
            print("无效的保存选项。")
            return

        # 确保输出格式为Pillow可识别的格式
        output_format_for_pillow = op_format.lower()
        if output_format_for_pillow == 'jpg':
            output_format_for_pillow = 'jpeg'

        # 保存图片为新的格式，并使用用户指定的扩展名
        img.save(output_path, format=output_format_for_pillow.upper())
        print(f"将 {img_name} 转换为 {base_name}.{op_format} 并保存到 {output_path}")


# 用户输入
input_dir = input("请输入包含图片的文件夹路径: ")
input_format = input("请输入输入图片格式 (如: jpg, png, bmp): ").lower()
output_format = input("请输入输出图片格式 (如: jpg, png, bmp, webp): ").lower()
save_option = input("输入 '1' 保存到相同目录，输入 '2' 保存到不同目录: ")

if save_option == '2':
    output_dir = input("请输入保存转换后图片的目录: ")
    convert_image_format(input_dir, input_format, output_format, save_option, output_dir)
else:
    convert_image_format(input_dir, input_format, output_format, save_option)
