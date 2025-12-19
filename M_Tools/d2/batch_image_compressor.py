import os
import threading
from tkinter import Tk, Label, Button, Entry, StringVar, filedialog, ttk, messagebox, Frame, Scrollbar, Listbox
from io import BytesIO
import cv2
import numpy as np

def pic_compress(pic_path, out_path, target_size=199, quality=90, step=5, pic_type='.jpg'):
    try:
        # 读取图片bytes
        with open(pic_path, 'rb') as f:
            original_bytes = f.read()

        img_np = np.frombuffer(original_bytes, np.uint8)
        img_cv = cv2.imdecode(img_np, cv2.IMREAD_ANYCOLOR)

        original_size = len(original_bytes) / 1024
        current_size = original_size
        best_bytes = original_bytes
        final_path = out_path
        
        # 根据图片类型选择不同的压缩策略
        if pic_type.lower() in ['.jpg', '.jpeg']:
            # JPEG压缩策略：从高质量开始降低质量
            current_quality = quality
            while current_size > target_size and current_quality > 0:
                params = [int(cv2.IMWRITE_JPEG_QUALITY), current_quality]
                compressed_bytes = cv2.imencode(pic_type, img_cv, params)[1]
                compressed_size = len(compressed_bytes) / 1024
                
                if compressed_size < current_size:
                    current_size = compressed_size
                    best_bytes = compressed_bytes
                
                if current_size <= target_size or current_quality - step < 0:
                    break
                current_quality -= step
        elif pic_type.lower() == '.png':
            # PNG压缩策略：只使用压缩级别参数，不改变分辨率
            # 1. 尝试不同PNG压缩级别
            best_size = current_size
            best_png_bytes = original_bytes
            
            # 从最大压缩级别开始尝试
            for png_level in range(9, -1, -1):
                params = [int(cv2.IMWRITE_PNG_COMPRESSION), png_level]
                compressed_bytes = cv2.imencode(pic_type, img_cv, params)[1]
                compressed_size = len(compressed_bytes) / 1024
                
                if compressed_size < best_size:
                    best_size = compressed_size
                    best_png_bytes = compressed_bytes
            
            current_size = best_size
            best_bytes = best_png_bytes
            
            # 2. 如果仍然超过目标大小，考虑转换为JPEG格式
            if current_size > target_size:
                jpeg_quality = quality
                while current_size > target_size and jpeg_quality > 0:
                    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
                    jpeg_bytes = cv2.imencode('.jpg', img_cv, jpeg_params)[1]
                    compressed_size = len(jpeg_bytes) / 1024
                    
                    if compressed_size < current_size:
                        current_size = compressed_size
                        best_bytes = jpeg_bytes
                        # 更新输出文件类型为JPEG
                        final_path = out_path.rsplit('.', 1)[0] + '.jpg'
                    
                    if current_size <= target_size or jpeg_quality - step < 0:
                        break
                    jpeg_quality -= step
        else:
            # 其他格式使用默认压缩
            best_bytes = cv2.imencode(pic_type, img_cv)[1]
            current_size = len(best_bytes) / 1024

        # 保存图片
        with open(final_path, 'wb') as f:
            f.write(BytesIO(best_bytes).getvalue())

        return True, current_size, original_size
    except Exception as e:
        return False, str(e), 0

class ImageCompressorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量图片压缩工具")
        self.root.geometry("700x600")
        
        # 变量初始化
        self.input_files = []
        self.output_dir = StringVar(value="./")
        self.target_size = StringVar(value="100")
        self.quality = StringVar(value="90")
        self.step = StringVar(value="5")
        self.pic_type = StringVar(value=".jpg")
        
        # 创建UI组件
        self.create_widgets()
    
    def create_widgets(self):
        # 输入文件选择
        input_frame = Frame(self.root)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        Label(input_frame, text="选择图片文件:").pack(anchor="w")
        
        file_frame = Frame(input_frame)
        file_frame.pack(fill="x", pady=5)
        
        self.file_listbox = Listbox(file_frame, height=8, selectmode="extended")
        scrollbar = Scrollbar(file_frame, orient="vertical", command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        btn_frame = Frame(input_frame)
        btn_frame.pack(fill="x", pady=5)
        
        Button(btn_frame, text="添加图片", command=self.add_files).pack(side="left", padx=5)
        Button(btn_frame, text="移除选中", command=self.remove_selected).pack(side="left", padx=5)
        Button(btn_frame, text="清空列表", command=self.clear_files).pack(side="left", padx=5)
        
        # 输出目录选择
        output_frame = Frame(self.root)
        output_frame.pack(pady=10, padx=10, fill="x")
        
        Label(output_frame, text="输出目录:").pack(anchor="w")
        
        dir_frame = Frame(output_frame)
        dir_frame.pack(fill="x", pady=5)
        
        Entry(dir_frame, textvariable=self.output_dir, state="readonly").pack(side="left", fill="x", expand=True, padx=5)
        Button(dir_frame, text="浏览", command=self.select_output_dir).pack(side="right", padx=5)
        
        # 压缩参数设置
        params_frame = Frame(self.root)
        params_frame.pack(pady=10, padx=10, fill="x")
        
        Label(params_frame, text="压缩参数:").pack(anchor="w")
        
        # 参数网格布局
        param_grid = Frame(params_frame)
        param_grid.pack(fill="x", pady=5)
        
        # 目标大小
        Label(param_grid, text="目标大小(KB):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        Entry(param_grid, textvariable=self.target_size, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        # 初始质量
        Label(param_grid, text="初始质量(0-100):").grid(row=0, column=2, sticky="e", padx=5, pady=5)
        Entry(param_grid, textvariable=self.quality, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        # 质量步长
        Label(param_grid, text="质量步长:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        Entry(param_grid, textvariable=self.step, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # 图片类型
        Label(param_grid, text="图片类型:").grid(row=1, column=2, sticky="e", padx=5, pady=5)
        ttk.Combobox(param_grid, textvariable=self.pic_type, values=[".jpg", ".png"], width=8).grid(row=1, column=3, padx=5, pady=5)
        
        # 进度和状态
        progress_frame = Frame(self.root)
        progress_frame.pack(pady=10, padx=10, fill="x")
        
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill="x", pady=5)
        
        self.status_label = Label(progress_frame, text="就绪")
        self.status_label.pack(anchor="w")
        
        # 结果显示
        result_frame = Frame(self.root)
        result_frame.pack(pady=10, padx=10, fill="x")
        
        Label(result_frame, text="压缩结果:").pack(anchor="w")
        
        self.result_listbox = Listbox(result_frame, height=8)
        scrollbar = Scrollbar(result_frame, orient="vertical", command=self.result_listbox.yview)
        self.result_listbox.config(yscrollcommand=scrollbar.set)
        
        self.result_listbox.pack(side="left", fill="both", expand=True, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # 开始按钮
        Button(self.root, text="开始压缩", command=self.start_compression, font=("Arial", 12), bg="#4CAF50", fg="white", padx=20, pady=5).pack(pady=15)
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"), ("所有文件", "*.*")]
        )
        
        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                self.file_listbox.insert("end", os.path.basename(file))
    
    def remove_selected(self):
        selected_indices = self.file_listbox.curselection()
        for index in reversed(selected_indices):
            self.file_listbox.delete(index)
            del self.input_files[index]
    
    def clear_files(self):
        self.file_listbox.delete(0, "end")
        self.input_files.clear()
    
    def select_output_dir(self):
        dir = filedialog.askdirectory(title="选择输出目录")
        if dir:
            self.output_dir.set(dir)
    
    def start_compression(self):
        if not self.input_files:
            messagebox.showerror("错误", "请先添加图片文件")
            return
        
        # 验证参数
        try:
            target_size = float(self.target_size.get())
            quality = int(self.quality.get())
            step = int(self.step.get())
            pic_type = self.pic_type.get()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的参数值")
            return
        
        # 禁用开始按钮，防止重复点击
        self.root.update()
        
        # 清空结果
        self.result_listbox.delete(0, "end")
        
        # 开始压缩线程
        thread = threading.Thread(
            target=self.compress_batch,
            args=(target_size, quality, step, pic_type)
        )
        thread.daemon = True
        thread.start()
    
    def compress_batch(self, target_size, quality, step, pic_type):
        total_files = len(self.input_files)
        success_count = 0
        
        for i, file_path in enumerate(self.input_files):
            # 更新进度
            progress = (i + 1) / total_files * 100
            self.progress["value"] = progress
            
            # 更新状态
            filename = os.path.basename(file_path)
            self.status_label.config(text=f"正在压缩: {filename} ({i+1}/{total_files})")
            self.root.update_idletasks()
            
            # 生成输出路径
            output_dir = self.output_dir.get()
            base_name = os.path.splitext(filename)[0]
            
            # 如果输出目录为默认值("./"或""),则使用源文件所在文件夹
            if output_dir in ["./", "", "."]:
                # 获取源文件所在目录
                source_dir = os.path.dirname(file_path)
                output_path = os.path.join(source_dir, f"{base_name}_compressed{pic_type}")
            else:
                output_path = os.path.join(output_dir, f"{base_name}_compressed{pic_type}")
            
            # 确保输出文件名不与源文件重复
            # 检查文件是否存在，如果存在则添加数字后缀
            counter = 1
            base_output_path = output_path
            while os.path.exists(output_path):
                output_path = f"{os.path.splitext(base_output_path)[0]}_{counter}{os.path.splitext(base_output_path)[1]}"
                counter += 1
            
            # 调用压缩函数
            success, result, original_size = pic_compress(
                file_path, output_path, target_size, quality, step, pic_type
            )
            
            # 记录结果
            if success:
                success_count += 1
                result_msg = f"✓ {filename} - 压缩成功 ({original_size:.2f}KB → {result:.2f}KB)"
            else:
                result_msg = f"✗ {filename} - 压缩失败: {result}"
            
            self.result_listbox.insert("end", result_msg)
            self.result_listbox.see("end")
            self.root.update_idletasks()
        
        # 完成后更新状态
        self.status_label.config(text=f"压缩完成! 成功: {success_count}/{total_files}")
        self.progress["value"] = 100
        messagebox.showinfo("完成", f"批量压缩完成!\n成功: {success_count}/{total_files}")

if __name__ == '__main__':
    root = Tk()
    app = ImageCompressorApp(root)
    root.mainloop()