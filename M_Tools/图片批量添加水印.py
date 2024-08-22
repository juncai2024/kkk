from PIL import Image, ImageDraw, ImageFont
import os


def add_watermark(image_path, watermark_text="larry", font_size=36, position="bottom_right"):
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)

        # 加载指定大小的字体
        font = ImageFont.truetype("arial.ttf", font_size)

        # 获取文本的边界框，返回值为 (left, top, right, bottom)
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # 计算文本的坐标
        width, height = img.size

        if position == "bottom_right":
            x = width - text_width - 10
            y = height - text_height - 10
        elif position == "bottom_left":
            x = 10
            y = height - text_height - 10
        elif position == "top_right":
            x = width - text_width - 10
            y = 10
        elif position == "top_left":
            x = 10
            y = 10
        elif position == "center":
            x = (width - text_width) // 2
            y = (height - text_height) // 2

        # 在图像上添加红色文本水印
        draw.text((x, y), watermark_text, font=font, fill=(255, 0, 0))  # 颜色为红色 (RGB: 255, 0, 0)

        # 保存图片
        img.save(image_path)


# 处理文件夹中的图片
folder_path = r"D:\study\test\cs"  # 替换为你的图片文件夹路径
for filename in os.listdir(folder_path):
    if filename.lower().endswith(('png', 'jpg', 'jpeg')):
        add_watermark(os.path.join(folder_path, filename), font_size=36, position="top_right")
