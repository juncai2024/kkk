import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class AutoScrollImage:
    def __init__(self, root, image_path, scroll_speed):
        self.root = root
        self.scroll_speed = scroll_speed

        # 创建画布并设置窗口大小
        self.canvas = tk.Canvas(root, width=900, height=1100)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建滚动条
        self.scrollbar = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定画布和滚动条
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        # 加载图片
        self.image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(self.image)

        # 创建一个窗口小部件来容纳图像
        self.image_frame = tk.Frame(self.canvas, width=self.photo.width(), height=self.photo.height())
        self.image_frame.pack()

        # 将图像添加到窗口小部件
        self.label = tk.Label(self.image_frame, image=self.photo)
        self.label.image = self.photo
        self.label.pack()

        # 配置画布的滚动区域
        self.canvas.create_window((0, 0), window=self.image_frame, anchor="nw")
        self.canvas.config(scrollregion=(0, 0, self.photo.width(), self.photo.height()))

        # 移动到图像的最右边
        self.canvas.xview_moveto(1)

        # 开始自动滚动
        self.start_auto_scroll()

    def start_auto_scroll(self):
        # 如果滚动到了最左边，则回到最右边
        if self.canvas.canvasx(0) <= 0:
            self.canvas.xview_moveto(1)
        else:
            self.canvas.xview_scroll(-1, "units")
        self.root.after(self.scroll_speed, self.start_auto_scroll)

# 创建主窗口
root = tk.Tk()
root.title("自动滚动查看图片")

# 设置滚动速度（以毫秒为单位，可以根据需要调整）
scroll_speed = 500  # 数值越小，滚动速度越快

# 图片路径
image_path = r"D:\照片\簪花仕女图\簪花仕女图卷1080.jpg"

# 创建自动滚动图像对象
auto_scroll_image = AutoScrollImage(root, image_path, scroll_speed)

# 运行主循环
root.mainloop()
