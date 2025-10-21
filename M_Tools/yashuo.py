import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageOps
import io
import base64
import os
from pathlib import Path


class PhotoCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PC端照片压缩工具")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

        # 主题颜色
        self.primary_color = "#1e40af"  # 深蓝色
        self.secondary_color = "#e0e0e0"
        self.accent_color = "#2563eb"  # 亮蓝色
        self.text_color = "#333333"

        # 初始化变量
        self.original_image = None
        self.compressed_image = None
        self.original_base64 = None
        self.compressed_base64 = None
        self.original_size = 0
        self.compressed_size = 0
        self.original_path = None
        self.output_format = tk.StringVar(value="JPEG")
        self.quality = tk.IntVar(value=80)
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']

        # 设置UI
        self.setup_ui()

        # 绑定拖拽事件
        self.setup_drag_drop()

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="照片压缩工具", font=("Helvetica", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 上传区域
        upload_frame = ttk.LabelFrame(main_frame, text="上传图片", padding="10")
        upload_frame.grid(row=1, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E))
        main_frame.columnconfigure(0, weight=1)

        self.drag_drop_label = ttk.Label(
            upload_frame,
            text="拖拽图片到此处或点击上传",
            font=("Helvetica", 12),
            wraplength=500,
            justify=tk.CENTER
        )
        self.drag_drop_label.grid(row=0, column=0, padx=20, pady=20)

        upload_button = ttk.Button(upload_frame, text="选择图片", command=self.upload_image)
        upload_button.grid(row=0, column=1, padx=10)

        # 压缩设置
        settings_frame = ttk.LabelFrame(main_frame, text="压缩设置", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E))

        # 输出格式选择
        format_label = ttk.Label(settings_frame, text="输出格式:")
        format_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)

        format_options = ["JPEG", "PNG", "WEBP"]
        format_combobox = ttk.Combobox(
            settings_frame,
            textvariable=self.output_format,
            values=format_options,
            state="readonly"
        )
        format_combobox.grid(row=0, column=1, padx=(0, 20), pady=5, sticky=tk.W)

        # 质量滑块
        quality_label = ttk.Label(settings_frame, text="压缩质量:")
        quality_label.grid(row=0, column=2, padx=(0, 10), pady=5, sticky=tk.W)

        quality_slider = ttk.Scale(
            settings_frame,
            from_=1,
            to=100,
            variable=self.quality,
            orient=tk.HORIZONTAL,
            command=self.update_quality_label
        )
        quality_slider.grid(row=0, column=3, padx=(0, 10), pady=5, sticky=(tk.W, tk.E))
        settings_frame.columnconfigure(3, weight=1)

        self.quality_value_label = ttk.Label(settings_frame, text=f"{self.quality.get()}%")
        self.quality_value_label.grid(row=0, column=4, padx=(0, 20), pady=5, sticky=tk.W)

        # 压缩按钮 - 使用普通按钮替代ttk按钮，确保颜色显示正确
        compress_button = tk.Button(
            settings_frame,
            text="开始压缩",
            command=self.compress_image,
            bg="#2563eb",  # 亮蓝色背景
            fg="white",  # 白色文字
            font=("Helvetica", 10, "bold"),
            padx=12,
            pady=6,
            relief="solid",
            bd=1,
            activebackground="#1e40af",  # 点击时深蓝色
            activeforeground="white"  # 点击时白色文字
        )
        compress_button.grid(row=0, column=5, padx=(0, 10), pady=5)

        # 下载按钮 - 使用普通按钮替代ttk按钮，确保颜色显示正确
        download_button = tk.Button(
            settings_frame,
            text="下载图片",
            command=self.download_image,
            bg="#2563eb",  # 亮蓝色背景
            fg="white",  # 白色文字
            font=("Helvetica", 10, "bold"),
            padx=12,
            pady=6,
            relief="solid",
            bd=1,
            activebackground="#1e40af",  # 点击时深蓝色
            activeforeground="white"  # 点击时白色文字
        )
        download_button.grid(row=0, column=6, pady=5)

        # 预览区域
        preview_frame = ttk.Frame(main_frame)
        preview_frame.grid(row=3, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.rowconfigure(3, weight=1)

        # 原始图片预览
        original_frame = ttk.LabelFrame(preview_frame, text="原始图片", padding="10")
        original_frame.grid(row=0, column=0, padx=(0, 15), sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)

        self.original_image_label = ttk.Label(original_frame, text="暂无图片", anchor=tk.CENTER)
        self.original_image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        original_frame.columnconfigure(0, weight=1)
        original_frame.rowconfigure(0, weight=1)

        self.original_info_text = scrolledtext.ScrolledText(original_frame, height=4, wrap=tk.WORD)
        self.original_info_text.grid(row=1, column=0, pady=(10, 0), sticky=(tk.W, tk.E))

        # 压缩后图片预览
        compressed_frame = ttk.LabelFrame(preview_frame, text="压缩后图片", padding="10")
        compressed_frame.grid(row=0, column=1, padx=(15, 0), sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_frame.columnconfigure(1, weight=1)

        self.compressed_image_label = ttk.Label(compressed_frame, text="暂无图片", anchor=tk.CENTER)
        self.compressed_image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        compressed_frame.columnconfigure(0, weight=1)
        compressed_frame.rowconfigure(0, weight=1)

        self.compressed_info_text = scrolledtext.ScrolledText(compressed_frame, height=4, wrap=tk.WORD)
        self.compressed_info_text.grid(row=1, column=0, pady=(10, 0), sticky=(tk.W, tk.E))

        # 压缩信息
        info_frame = ttk.LabelFrame(main_frame, text="压缩信息", padding="10")
        info_frame.grid(row=4, column=0, columnspan=3, pady=(0, 15), sticky=(tk.W, tk.E))

        self.info_text = scrolledtext.ScrolledText(info_frame, height=5, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        info_frame.columnconfigure(0, weight=1)

        # 设置样式
        self.setup_styles()

    def setup_styles(self):
        style = ttk.Style()

        # 主样式
        style.configure(".", font=("Helvetica", 10), foreground=self.text_color)

        # 标签框架样式
        style.configure("TLabelFrame", font=("Helvetica", 11, "bold"))
        style.configure("TLabelFrame.Label", foreground=self.primary_color)

        # 按钮样式
        style.configure("TButton", padding=6, relief="flat", background=self.secondary_color)

        # 强调按钮样式 - 使用具体的颜色值确保显示正确
        # 为了确保正常状态下的样式生效，我们需要更具体的样式定义
        style.configure("Accent.TButton",
                        padding=8,
                        relief="solid",
                        borderwidth=1,
                        bordercolor="#2563eb",
                        background="#2563eb",  # 亮蓝色
                        foreground="white",  # 白色文字
                        font=("Helvetica", 10, "bold"))

        # 确保正常状态的样式被正确应用
        style.map("Accent.TButton",
                  background=[("disabled", "#cccccc"),  # 禁用状态
                              ("active", "#1e40af"),  # 点击时深蓝色
                              ("pressed", "#1e40af"),  # 按下时深蓝色
                              ("hover", "#3b82f6")],  # 悬停时中蓝色
                  foreground=[("disabled", "#666666"),
                              ("active", "white"),
                              ("pressed", "white"),
                              ("hover", "white")],
                  bordercolor=[("disabled", "#999999"),
                               ("active", "#1e40af"),
                               ("pressed", "#1e40af"),
                               ("hover", "#3b82f6")])

        # 滑块样式
        style.configure("TScale", background=self.secondary_color)

    def setup_drag_drop(self):
        # 实现完整的文件拖放功能
        try:
            # 对于Windows系统，使用OLE拖放接口
            if os.name == 'nt':
                self.setup_windows_drag_drop()
            else:
                # 对于其他系统，提供基本的拖拽提示
                self.setup_basic_drag_feedback()

        except ImportError:
            # 如果没有安装pywin32，提供基本的拖拽提示
            self.setup_basic_drag_feedback()
            self.update_info("提示: 需要安装pywin32才能使用完整的拖拽功能")

        except Exception as e:
            self.update_info(f"拖拽功能初始化失败: {str(e)}")
            self.setup_basic_drag_feedback()

    def setup_windows_drag_drop(self):
        # Windows系统的OLE拖放实现
        import pythoncom
        import win32clipboard
        from win32com.shell import shell, shellcon

        # 创建拖放目标类
        class DropTarget:
            def __init__(self, widget, callback):
                self.widget = widget
                self.callback = callback
                self.hwnd = widget.winfo_id()

            def QueryInterface(self, iid):
                if iid == pythoncom.IID_IDropTarget or iid == pythoncom.IID_IUnknown:
                    return self
                raise pythoncom.COMError(0, "No interface", None)

            def DragEnter(self, dataobj, grfKeyState, pt, pdwEffect):
                # 检查是否是否包含文件
                formats = dataobj.GetFormats()
                if shellcon.CF_HDROP in formats:
                    self.widget.config(background="#e8f0fe")
                    return pdwEffect & shellcon.DROPEFFECT_COPY
                return shellcon.DROPEFFECT_NONE

            def DragOver(self, grfKeyState, pt, pdwEffect):
                return pdwEffect & shellcon.DROPEFFECT_COPY

            def DragLeave(self):
                self.widget.config(background="")

            def Drop(self, dataobj, grfKeyState, pt, pdwEffect):
                self.widget.config(background="")
                try:
                    # 获取拖放的文件
                    files = dataobj.GetData(shellcon.CF_HDROP)
                    for file in files:
                        if self.callback.is_image_file(file):
                            self.callback.process_image(file)
                            break
                except Exception as e:
                    self.callback.update_info(f"处理拖放文件失败: {str(e)}")
                return pdwEffect & shellcon.DROPEFFECT_COPY

        # 注册拖放目标
        self.drop_target = DropTarget(self.drag_drop_label, self)
        pythoncom.RegisterDragDrop(self.drag_drop_label.winfo_id(), self.drop_target)
        self.drag_drop_label.config(text="拖拽图片到此处或点击上传")

    def setup_basic_drag_feedback(self):
        # 基本的拖拽视觉反馈（不处理实际的文件拖放）
        self.drag_active = False

        # 绑定鼠标事件
        self.drag_drop_label.bind('<ButtonPress-1>', self.on_mouse_press)
        self.drag_drop_label.bind('<ButtonRelease-1>', self.on_mouse_release)
        self.drag_drop_label.bind('<B1-Motion>', self.on_mouse_drag)

        # 添加视觉反馈
        self.drag_drop_label.bind('<Enter>', self.on_mouse_enter)
        self.drag_drop_label.bind('<Leave>', self.on_mouse_leave)

        # 根据系统显示不同的提示
        if os.name == 'nt':
            self.drag_drop_label.config(text="拖拽功能需要pywin32\n请点击上传按钮选择图片")
        else:
            self.drag_drop_label.config(text="拖拽功能仅在Windows上支持\n请点击上传按钮选择图片")

    def on_mouse_enter(self, event):
        # 鼠标进入时改变背景色
        event.widget.config(background="#f0f0f0")

    def on_mouse_leave(self, event):
        # 鼠标离开时恢复背景色
        event.widget.config(background="")

    def on_mouse_press(self, event):
        # 鼠标按下时记录状态
        self.drag_active = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_mouse_drag(self, event):
        # 鼠标拖拽时的处理
        if self.drag_active:
            # 计算拖拽距离
            drag_distance = ((event.x - self.drag_start_x) ** 2 +
                             (event.y - self.drag_start_y) ** 2) ** 0.5

            # 如果拖拽距离超过阈值，显示提示
            if drag_distance > 10:
                self.drag_drop_label.config(text="释放鼠标上传图片...")

    def on_mouse_release(self, event):
        # 鼠标释放时的处理
        if self.drag_active:
            # 恢复提示文本
            self.drag_drop_label.config(text="拖拽图片到此处或点击上传")
            self.drag_active = False

    def is_image_file(self, file_path):
        # 检查文件是否为图片
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.image_extensions

    def upload_image(self):
        # 上传图片
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("Image Files", " ".join([f"*{ext}" for ext in self.image_extensions]))]
        )

        if file_path and self.is_image_file(file_path):
            self.process_image(file_path)

    def process_image(self, file_path):
        # 处理上传的图片
        try:
            # 检查是否重复上传
            if file_path == self.original_path:
                messagebox.showinfo("提示", "请勿重复上传同一张图片")
                return

            # 打开图片
            self.original_image = Image.open(file_path)
            self.original_path = file_path

            # 转换为RGB模式（如果是RGBA）
            if self.original_image.mode in ('RGBA', 'LA'):
                background = Image.new(self.original_image.mode[:-1], self.original_image.size, (255, 255, 255))
                background.paste(self.original_image, self.original_image.split()[-1])
                self.original_image = background

            # 计算原始图片大小
            self.original_size = os.path.getsize(file_path)

            # 转换为base64
            self.original_base64 = self.image_to_base64(self.original_image)

            # 更新UI
            self.update_original_preview()
            self.update_compressed_preview()
            self.update_info("图片上传成功")

        except Exception as e:
            messagebox.showerror("错误", f"处理图片时发生错误: {str(e)}")
            self.update_info(f"处理图片时发生错误: {str(e)}")

    def image_to_base64(self, image):
        # 将图片转换为base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

    def base64_to_image(self, base64_str):
        # 将base64转换为图片
        image_data = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(image_data))

    def update_original_preview(self):
        # 更新原始图片预览
        if self.original_image:
            # 调整图片大小以适应预览区域
            preview_image = self.resize_image(self.original_image, 400, 300)
            photo = ImageTk.PhotoImage(preview_image)

            self.original_image_label.config(image=photo)
            self.original_image_label.image = photo

            # 更新信息
            info = f"文件名: {os.path.basename(self.original_path)}\n"
            info += f"尺寸: {self.original_image.width} x {self.original_image.height}\n"
            info += f"大小: {self.format_file_size(self.original_size)}\n"
            info += f"格式: {self.original_image.format}"

            self.original_info_text.delete(1.0, tk.END)
            self.original_info_text.insert(tk.END, info)
        else:
            self.original_image_label.config(text="暂无图片", image="")
            self.original_info_text.delete(1.0, tk.END)
            self.original_info_text.insert(tk.END, "暂无图片信息")

    def update_compressed_preview(self):
        # 更新压缩后图片预览
        if self.compressed_image:
            # 调整图片以适应预览区域
            preview_image = self.resize_image(self.compressed_image, 400, 300)
            photo = ImageTk.PhotoImage(preview_image)

            self.compressed_image_label.config(image=photo)
            self.compressed_image_label.image = photo

            # 更新信息
            info = f"尺寸: {self.compressed_image.width} x {self.compressed_image.height}\n"
            info += f"大小: {self.format_file_size(self.compressed_size)}\n"
            info += f"格式: {self.output_format.get()}\n"

            if self.original_size > 0:
                compression_ratio = (1 - self.compressed_size / self.original_size) * 100
                info += f"压缩率: {compression_ratio:.2f}%"

            self.compressed_info_text.delete(1.0, tk.END)
            self.compressed_info_text.insert(tk.END, info)
        else:
            self.compressed_image_label.config(text="暂无图片", image="")
            self.compressed_info_text.delete(1.0, tk.END)
            self.compressed_info_text.insert(tk.END, "暂无压缩图片信息")

    def get_resample_filter(self):
        # 获取合适的重采样滤镜，兼容不同版本的Pillow
        try:
            # Pillow 9.1.0+
            return Image.Resampling.LANCZOS
        except AttributeError:
            # Pillow < 9.1.0
            return Image.LANCZOS

    def resize_image(self, image, max_width, max_height):
        # 按比例调整图片大小
        width, height = image.size
        ratio = min(max_width / width, max_height / height)

        if ratio < 1:
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            resample_filter = self.get_resample_filter()
            return image.resize((new_width, new_height), resample_filter)
        return image

    def format_file_size(self, size_bytes):
        # 格式化文件大小
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"

    def update_quality_label(self, event):
        # 更新质量标签
        self.quality_value_label.config(text=f"{self.quality.get()}%")

    def compress_image(self):
        # 压缩图片
        if not self.original_image:
            messagebox.showwarning("警告", "请先上传图片")
            return

        try:
            self.update_info("正在压缩图片...")
            self.root.update()  # 更新UI

            # 获取压缩设置
            format = self.output_format.get().lower()
            quality = self.quality.get()

            # 压缩图片
            self.compressed_image, self.compressed_size = self.compress_image_with_guarantee(
                self.original_image,
                format,
                quality,
                self.original_size
            )

            # 转换为base64
            self.compressed_base64 = self.image_to_base64(self.compressed_image)

            # 更新预览
            self.update_compressed_preview()

            # 更新信息
            compression_ratio = (1 - self.compressed_size / self.original_size) * 100
            info = f"压缩成功!\n"
            info += f"原始大小: {self.format_file_size(self.original_size)}\n"
            info += f"压缩后大小: {self.format_file_size(self.compressed_size)}\n"
            info += f"压缩率: {compression_ratio:.2f}%\n"
            info += f"输出格式: {format.upper()}\n"
            info += f"使用质量: {quality}%"

            self.update_info(info)
            messagebox.showinfo("成功", "图片压缩成功")

        except Exception as e:
            messagebox.showerror("错误", f"压缩图片时发生错误: {str(e)}")
            self.update_info(f"压缩图片时发生错误: {str(e)}")

    def compress_image_with_guarantee(self, image, format, quality, original_size):
        # 保证压缩后的图片一定比原图小
        compressed_size = original_size
        compressed_image = None
        current_quality = quality

        # 确保图片模式与输出格式兼容
        image = self.ensure_compatible_image_mode(image, format)

        # 如果是PNG格式，使用不同的压缩策略
        if format == 'png':
            # 尝试不同的压缩级别
            for level in range(9, 0, -1):
                buffered = io.BytesIO()
                image.save(buffered, format=format.upper(), compress_level=level)
                compressed_size = buffered.tell()

                if compressed_size < original_size:
                    buffered.seek(0)
                    compressed_image = Image.open(buffered)
                    break

            # 如果仍然无法压缩，尝试调整尺寸
            if compressed_size >= original_size:
                self.update_info("PNG压缩效果不佳，尝试调整尺寸...")
                self.root.update()

                # 逐步减小尺寸，直到压缩后大小小于原始大小
                scale_factor = 0.9
                while compressed_size >= original_size and scale_factor > 0.1:
                    new_width = int(image.width * scale_factor)
                    new_height = int(image.height * scale_factor)

                    resample_filter = self.get_resample_filter()
                    resized_image = image.resize((new_width, new_height), resample_filter)
                    buffered = io.BytesIO()
                    resized_image.save(buffered, format=format.upper(), compress_level=9)
                    compressed_size = buffered.tell()

                    if compressed_size < original_size:
                        buffered.seek(0)
                        compressed_image = Image.open(buffered)
                        break

                    scale_factor -= 0.1

        else:  # JPEG或WEBP格式
            # 尝试不同的质量设置
            while compressed_size >= original_size and current_quality > 0:
                buffered = io.BytesIO()
                image.save(buffered, format=format.upper(), quality=current_quality)
                compressed_size = buffered.tell()

                if compressed_size < original_size:
                    buffered.seek(0)
                    compressed_image = Image.open(buffered)
                    break

                current_quality -= 5

            # 如果仍然无法压缩，尝试调整尺寸
            if compressed_size >= original_size:
                self.update_info(f"{format.upper()}压缩效果不佳，尝试调整尺寸...")
                self.root.update()

                # 逐步减小尺寸，直到压缩后大小小于原始大小
                scale_factor = 0.9
                while compressed_size >= original_size and scale_factor > 0.1:
                    new_width = int(image.width * scale_factor)
                    new_height = int(image.height * scale_factor)

                    resample_filter = self.get_resample_filter()
                    resized_image = image.resize((new_width, new_height), resample_filter)
                    buffered = io.BytesIO()
                    resized_image.save(buffered, format=format.upper(), quality=current_quality)
                    compressed_size = buffered.tell()

                    if compressed_size < original_size:
                        buffered.seek(0)
                        compressed_image = Image.open(buffered)
                        break

                    scale_factor -= 0.1

        # 确保压缩成功
        if not compressed_image or compressed_size >= original_size:
            raise Exception("无法将图片压缩到更小的尺寸，请尝试更低的质量或更小的尺寸")

        return compressed_image, compressed_size

    def ensure_compatible_image_mode(self, image, format):
        # 确保图片模式与输出格式兼容
        if format.lower() == 'jpeg':
            # JPEG不支持透明度，转换为RGB模式
            if image.mode in ('RGBA', 'LA', 'P'):
                # 如果是RGBA或LA模式，先创建白色背景
                if image.mode in ('RGBA', 'LA'):
                    background = Image.new(image.mode[:-1], image.size, (255, 255, 255))
                    background.paste(image, image.split()[-1])
                    image = background
                # 如果是P模式（调色板），直接转换为RGB
                elif image.mode == 'P':
                    image = image.convert('RGB')
        elif format.lower() == 'png':
            # PNG支持透明度，如果是P模式且有透明度信息，转换为RGBA
            if image.mode == 'P':
                # 检查是否有透明度信息
                if 'transparency' in image.info:
                    image = image.convert('RGBA')
                else:
                    image = image.convert('RGB')
        elif format.lower() == 'webp':
            # WebP支持透明度，保持原有模式或转换为RGBA
            if image.mode == 'P':
                if 'transparency' in image.info:
                    image = image.convert('RGBA')
                else:
                    image = image.convert('RGB')

        return image

    def download_image(self):
        # 下载压缩后的图片
        if not self.compressed_image:
            messagebox.showwarning("警告", "请先压缩图片")
            return

        try:
            # 获取输出格式
            format = self.output_format.get().lower()

            # 获取原始文件名和路径
            original_filename = os.path.basename(self.original_path)
            original_dir = os.path.dirname(self.original_path)
            original_name, original_ext = os.path.splitext(original_filename)

            # 生成新文件名
            new_filename = f"{original_name}_compressed.{format}"
            default_path = os.path.join(original_dir, new_filename)

            # 选择保存路径
            save_path = filedialog.asksaveasfilename(
                initialfile=new_filename,
                defaultextension=f".{format}",
                filetypes=[(f"{format.upper()} Files", f"*.{format}")],
                initialdir=original_dir
            )

            if save_path:
                # 保存图片
                self.compressed_image.save(save_path, format=format.upper())

                # 更新信息
                info = f"图片已保存到:\n{save_path}\n"
                info += f"文件大小: {self.format_file_size(os.path.getsize(save_path))}"

                self.update_info(info)
                messagebox.showinfo("成功", "图片下载成功")

        except Exception as e:
            messagebox.showerror("错误", f"保存图片时发生错误: {str(e)}")
            self.update_info(f"保存图片时发生错误: {str(e)}")

    def update_info(self, text):
        # 更新信息文本
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, text)


def main():
    root = tk.Tk()
    app = PhotoCompressorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
