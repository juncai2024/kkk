import os
import re
import csv
import shutil
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText

class BatchRenamer:
    def __init__(self, root):
        self.root = root
        self.root.title("批量文件重命名工具")
        self.root.geometry("1000x800")  # 增加高度，确保所有控件都能显示
        self.root.minsize(800, 600)  # 设置最小窗口大小
        
        # 变量初始化
        self.folder_path = ""
        self.files = []
        self.selected_files = []
        self.rename_preview = []
        self.operation_history = []
        self.undo_stack = []
        
        # 冲突处理策略
        self.conflict_strategies = ["自动添加序号", "覆盖", "跳过", "停止"]
        self.current_conflict_strategy = tk.StringVar(value="自动添加序号")
        
        # 界面布局
        self.create_widgets()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部文件夹选择和过滤区域
        top_frame = ttk.LabelFrame(main_frame, text="文件夹选择和过滤", padding="10")
        top_frame.pack(fill=tk.X, pady=5)
        
        # 文件夹选择
        folder_frame = ttk.Frame(top_frame)
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(folder_frame, text="目标文件夹: ").pack(side=tk.LEFT, padx=5)
        self.folder_entry = ttk.Entry(folder_frame, width=50)
        self.folder_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="浏览", command=self.select_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="刷新文件列表", command=self.refresh_file_list).pack(side=tk.LEFT, padx=5)
        
        # 过滤条件
        filter_frame = ttk.LabelFrame(top_frame, text="文件过滤", padding="5")
        filter_frame.pack(fill=tk.X, pady=5)
        
        # 扩展名过滤
        ext_frame = ttk.Frame(filter_frame)
        ext_frame.pack(fill=tk.X, pady=2)
        ttk.Label(ext_frame, text="扩展名: ").pack(side=tk.LEFT, padx=5)
        self.ext_entry = ttk.Entry(ext_frame, width=20)
        self.ext_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(ext_frame, text="(如: jpg,png 多个用逗号分隔)").pack(side=tk.LEFT, padx=5)
        
        # 文件大小过滤
        size_frame = ttk.Frame(filter_frame)
        size_frame.pack(fill=tk.X, pady=2)
        ttk.Label(size_frame, text="文件大小: ").pack(side=tk.LEFT, padx=5)
        self.min_size_entry = ttk.Entry(size_frame, width=10)
        self.min_size_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="KB 到 ").pack(side=tk.LEFT, padx=5)
        self.max_size_entry = ttk.Entry(size_frame, width=10)
        self.max_size_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(size_frame, text="KB").pack(side=tk.LEFT, padx=5)
        
        # 修改时间过滤
        time_frame = ttk.Frame(filter_frame)
        time_frame.pack(fill=tk.X, pady=2)
        ttk.Label(time_frame, text="修改时间: ").pack(side=tk.LEFT, padx=5)
        self.min_time_entry = ttk.Entry(time_frame, width=15)
        self.min_time_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(time_frame, text="(YYYY-MM-DD) 到 ").pack(side=tk.LEFT, padx=5)
        self.max_time_entry = ttk.Entry(time_frame, width=15)
        self.max_time_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(time_frame, text="(YYYY-MM-DD)").pack(side=tk.LEFT, padx=5)
        
        # 关键字过滤
        keyword_frame = ttk.Frame(filter_frame)
        keyword_frame.pack(fill=tk.X, pady=2)
        ttk.Label(keyword_frame, text="关键字: ").pack(side=tk.LEFT, padx=5)
        self.keyword_entry = ttk.Entry(keyword_frame, width=30)
        self.keyword_entry.pack(side=tk.LEFT, padx=5)
        self.include_check = tk.BooleanVar(value=True)
        ttk.Checkbutton(keyword_frame, text="包含", variable=self.include_check).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="应用过滤", command=self.apply_filter).pack(side=tk.RIGHT, padx=5, pady=5)
        
        # 重命名规则区域
        rename_frame = ttk.LabelFrame(main_frame, text="重命名规则", padding="10")
        rename_frame.pack(fill=tk.X, pady=5)
        
        # 规则选择
        rule_frame = ttk.Frame(rename_frame)
        rule_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rule_frame, text="选择规则: ").pack(side=tk.LEFT, padx=5)
        self.rule_var = tk.StringVar()
        self.rule_combobox = ttk.Combobox(rule_frame, textvariable=self.rule_var, width=30)
        self.rule_combobox['values'] = [
            "删除指定字符", "在开头/结尾添加字符", "批量替换字符", "Excel映射表重命名",
            "自动编号", "批量更改大小写", "正则表达式替换", "文本裁剪", "文字插入"
        ]
        self.rule_combobox.pack(side=tk.LEFT, padx=5)
        self.rule_combobox.bind("<<ComboboxSelected>>", self.on_rule_change)
        
        # 规则参数框架
        self.rule_params_frame = ttk.LabelFrame(rename_frame, text="规则参数", padding="5")
        self.rule_params_frame.pack(fill=tk.X, pady=5)
        
        # 初始显示删除指定字符的参数
        self.show_delete_params()
        
        # 操作按钮区域（放在预览框上方）
        action_frame = ttk.LabelFrame(main_frame, text="操作控制", padding="10")
        action_frame.pack(fill=tk.X, pady=5)
        
        # 增大按钮字体和大小，使其更显眼
        style = ttk.Style()
        style.configure("Big.TButton", font=('Arial', 10, 'bold'))
        
        # 主要操作按钮
        main_button_frame = ttk.Frame(action_frame)
        main_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(main_button_frame, text="生成预览", command=self.generate_preview, style="Big.TButton").pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(main_button_frame, text="执行重命名", command=self.execute_rename, style="Big.TButton").pack(side=tk.LEFT, padx=10, pady=5)
        
        # 辅助操作按钮
        secondary_button_frame = ttk.Frame(action_frame)
        secondary_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(secondary_button_frame, text="冲突处理策略: ").pack(side=tk.LEFT, padx=5)
        self.conflict_combobox = ttk.Combobox(secondary_button_frame, textvariable=self.current_conflict_strategy, values=self.conflict_strategies, width=20)
        self.conflict_combobox.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(secondary_button_frame, text="撤销上一步", command=self.undo_rename).pack(side=tk.RIGHT, padx=10, pady=5)
        ttk.Button(secondary_button_frame, text="导出日志", command=self.export_log).pack(side=tk.RIGHT, padx=10, pady=5)
        ttk.Button(secondary_button_frame, text="导出重命名报告", command=self.export_rename_report).pack(side=tk.RIGHT, padx=10, pady=5)
        
        # 中间文件列表和预览区域
        mid_frame = ttk.Frame(main_frame)
        mid_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 文件列表
        left_frame = ttk.LabelFrame(mid_frame, text="文件列表", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 全选/取消全选
        select_frame = ttk.Frame(left_frame)
        select_frame.pack(fill=tk.X, pady=5)
        ttk.Button(select_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="取消全选", command=self.deselect_all).pack(side=tk.LEFT, padx=5)
        
        # 文件列表树 - 添加复选框列
        self.file_tree = ttk.Treeview(left_frame, columns=("select", "name", "size", "mtime"), show="headings")
        self.file_tree.heading("select", text="选择")
        self.file_tree.heading("name", text="文件名")
        self.file_tree.heading("size", text="大小(KB)")
        self.file_tree.heading("mtime", text="修改时间")
        self.file_tree.column("select", width=50, anchor=tk.CENTER)
        self.file_tree.column("name", width=200)
        self.file_tree.column("size", width=100, anchor=tk.CENTER)
        self.file_tree.column("mtime", width=150, anchor=tk.CENTER)
        
        # 添加滚动条
        file_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscroll=file_scroll.set)
        file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.pack(fill=tk.BOTH, expand=True)
        
        # 预览区域
        right_frame = ttk.LabelFrame(mid_frame, text="重命名预览", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # 预览树
        self.preview_tree = ttk.Treeview(right_frame, columns=("old", "new", "status"), show="headings")
        self.preview_tree.heading("old", text="原文件名")
        self.preview_tree.heading("new", text="新文件名")
        self.preview_tree.heading("status", text="状态")
        self.preview_tree.column("old", width=200)
        self.preview_tree.column("new", width=200)
        self.preview_tree.column("status", width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        preview_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscroll=preview_scroll.set)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.pack(fill=tk.BOTH, expand=True)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="10")
        log_frame.pack(fill=tk.X, pady=5)
        
        self.log_text = ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.X)
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="选择目标文件夹")
        if folder:
            self.folder_path = folder
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.refresh_file_list()
    
    def refresh_file_list(self):
        folder = self.folder_entry.get()
        if not os.path.exists(folder):
            messagebox.showerror("错误", "文件夹不存在！")
            return
        
        self.files = []
        try:
            for file in os.listdir(folder):
                file_path = os.path.join(folder, file)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path) // 1024  # KB
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                    self.files.append((file, size, mtime, file_path))
            
            self.display_file_list()
            self.log(f"已加载 {len(self.files)} 个文件")
        except Exception as e:
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")
    
    def display_file_list(self):
        # 清空现有列表
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 添加文件
        for file in self.files:
            self.file_tree.insert("", tk.END, values=("□",) + file[:3], tags=(file[0], "unselected"))
        
        # 绑定点击事件
        self.file_tree.bind("<Button-1>", self.on_file_click)
    
    def on_file_click(self, event):
        # 获取点击的行和列
        item = self.file_tree.identify_row(event.y)
        column = self.file_tree.identify_column(event.x)
        
        # 点击选择列时切换选择状态
        if column == "#1":
            if item:
                tags = self.file_tree.item(item, "tags")
                filename = tags[0]
                values = list(self.file_tree.item(item, "values"))
                
                if len(tags) > 1 and tags[1] == "selected":
                    # 取消选择
                    self.file_tree.item(item, tags=(filename, "unselected"))
                    values[0] = "□"
                else:
                    # 选择
                    self.file_tree.item(item, tags=(filename, "selected"))
                    values[0] = "☑"
                
                # 更新显示
                self.file_tree.item(item, values=tuple(values))
    
    def apply_filter(self):
        # 获取过滤条件
        exts = self.ext_entry.get().strip().lower().split(",") if self.ext_entry.get().strip() else []
        min_size = int(self.min_size_entry.get()) if self.min_size_entry.get().isdigit() else 0
        max_size = int(self.max_size_entry.get()) if self.max_size_entry.get().isdigit() else float("inf")
        min_time = self.min_time_entry.get().strip()
        max_time = self.max_time_entry.get().strip()
        keyword = self.keyword_entry.get().strip()
        include = self.include_check.get()
        
        filtered_files = []
        for file in self.files:
            filename = file[0]
            size = file[1]
            mtime = file[2]
            file_path = file[3]
            
            # 扩展名过滤
            if exts:
                ext = os.path.splitext(filename)[1].lower()[1:]  # 去除点
                if ext not in exts:
                    continue
            
            # 文件大小过滤
            if size < min_size or size > max_size:
                continue
            
            # 修改时间过滤
            if min_time:
                file_mtime = datetime.strptime(mtime.split()[0], "%Y-%m-%d")
                min_mtime = datetime.strptime(min_time, "%Y-%m-%d")
                if file_mtime < min_mtime:
                    continue
            if max_time:
                file_mtime = datetime.strptime(mtime.split()[0], "%Y-%m-%d")
                max_mtime = datetime.strptime(max_time, "%Y-%m-%d")
                if file_mtime > max_mtime:
                    continue
            
            # 关键字过滤
            if keyword:
                if include:
                    if keyword not in filename:
                        continue
                else:
                    if keyword in filename:
                        continue
            
            filtered_files.append(file)
        
        # 更新文件列表
        self.files = filtered_files
        self.display_file_list()
        self.log(f"应用过滤后剩余 {len(self.files)} 个文件")
    
    def select_all(self):
        for item in self.file_tree.get_children():
            values = list(self.file_tree.item(item, "values"))
            values[0] = "☑"
            filename = self.file_tree.item(item, "values")[1]  # 文件名在第二列
            self.file_tree.item(item, tags=(filename, "selected"), values=tuple(values))
    
    def deselect_all(self):
        for item in self.file_tree.get_children():
            values = list(self.file_tree.item(item, "values"))
            values[0] = "□"
            filename = self.file_tree.item(item, "values")[1]  # 文件名在第二列
            self.file_tree.item(item, tags=(filename, "unselected"), values=tuple(values))
    
    def on_rule_change(self, event):
        # 清空现有参数框架
        for widget in self.rule_params_frame.winfo_children():
            widget.destroy()
        
        # 根据选择的规则显示相应的参数
        rule = self.rule_var.get()
        if rule == "删除指定字符":
            self.show_delete_params()
        elif rule == "在开头/结尾添加字符":
            self.show_add_params()
        elif rule == "批量替换字符":
            self.show_replace_params()
        elif rule == "Excel映射表重命名":
            self.show_excel_params()
        elif rule == "自动编号":
            self.show_numbering_params()
        elif rule == "批量更改大小写":
            self.show_case_params()
        elif rule == "正则表达式替换":
            self.show_regex_params()
        elif rule == "文本裁剪":
            self.show_crop_params()
        elif rule == "文字插入":
            self.show_insert_params()
    
    def show_delete_params(self):
        ttk.Label(self.rule_params_frame, text="要删除的字符: ").pack(side=tk.LEFT, padx=5, pady=5)
        self.delete_char_entry = ttk.Entry(self.rule_params_frame, width=30)
        self.delete_char_entry.pack(side=tk.LEFT, padx=5, pady=5)
    
    def show_add_params(self):
        # 位置选择
        pos_frame = ttk.Frame(self.rule_params_frame)
        pos_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pos_frame, text="位置: ").pack(side=tk.LEFT, padx=5)
        self.add_pos_var = tk.StringVar(value="开头")
        ttk.Radiobutton(pos_frame, text="开头", variable=self.add_pos_var, value="开头").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(pos_frame, text="结尾(扩展名前)", variable=self.add_pos_var, value="结尾").pack(side=tk.LEFT, padx=5)
        
        # 要添加的字符
        char_frame = ttk.Frame(self.rule_params_frame)
        char_frame.pack(fill=tk.X, pady=2)
        ttk.Label(char_frame, text="要添加的字符: ").pack(side=tk.LEFT, padx=5)
        self.add_char_entry = ttk.Entry(char_frame, width=30)
        self.add_char_entry.pack(side=tk.LEFT, padx=5)
    
    def show_replace_params(self):
        # 查找字符
        find_frame = ttk.Frame(self.rule_params_frame)
        find_frame.pack(fill=tk.X, pady=2)
        ttk.Label(find_frame, text="查找: ").pack(side=tk.LEFT, padx=5)
        self.replace_find_entry = ttk.Entry(find_frame, width=30)
        self.replace_find_entry.pack(side=tk.LEFT, padx=5)
        
        # 替换字符
        replace_frame = ttk.Frame(self.rule_params_frame)
        replace_frame.pack(fill=tk.X, pady=2)
        ttk.Label(replace_frame, text="替换为: ").pack(side=tk.LEFT, padx=5)
        self.replace_with_entry = ttk.Entry(replace_frame, width=30)
        self.replace_with_entry.pack(side=tk.LEFT, padx=5)
        
        # 是否修改扩展名
        ext_frame = ttk.Frame(self.rule_params_frame)
        ext_frame.pack(fill=tk.X, pady=2)
        self.replace_ext_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(ext_frame, text="同时修改扩展名", variable=self.replace_ext_var).pack(side=tk.LEFT, padx=5)
    
    def show_excel_params(self):
        ttk.Label(self.rule_params_frame, text="Excel文件路径: ").pack(side=tk.LEFT, padx=5, pady=5)
        self.excel_path_entry = ttk.Entry(self.rule_params_frame, width=30)
        self.excel_path_entry.pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(self.rule_params_frame, text="浏览", command=self.select_excel).pack(side=tk.LEFT, padx=5, pady=5)
    
    def show_numbering_params(self):
        # 前缀
        prefix_frame = ttk.Frame(self.rule_params_frame)
        prefix_frame.pack(fill=tk.X, pady=2)
        ttk.Label(prefix_frame, text="前缀: ").pack(side=tk.LEFT, padx=5)
        self.number_prefix_entry = ttk.Entry(prefix_frame, width=15)
        self.number_prefix_entry.pack(side=tk.LEFT, padx=5)
        
        # 后缀
        suffix_frame = ttk.Frame(self.rule_params_frame)
        suffix_frame.pack(fill=tk.X, pady=2)
        ttk.Label(suffix_frame, text="后缀: ").pack(side=tk.LEFT, padx=5)
        self.number_suffix_entry = ttk.Entry(suffix_frame, width=15)
        self.number_suffix_entry.pack(side=tk.LEFT, padx=5)
        
        # 编号格式
        format_frame = ttk.Frame(self.rule_params_frame)
        format_frame.pack(fill=tk.X, pady=2)
        ttk.Label(format_frame, text="编号宽度: ").pack(side=tk.LEFT, padx=5)
        self.number_width_entry = ttk.Entry(format_frame, width=10)
        self.number_width_entry.insert(0, "3")
        self.number_width_entry.pack(side=tk.LEFT, padx=5)
        
        # 起始编号和步长
        start_step_frame = ttk.Frame(self.rule_params_frame)
        start_step_frame.pack(fill=tk.X, pady=2)
        ttk.Label(start_step_frame, text="起始编号: ").pack(side=tk.LEFT, padx=5)
        self.number_start_entry = ttk.Entry(start_step_frame, width=10)
        self.number_start_entry.insert(0, "1")
        self.number_start_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(start_step_frame, text="步长: ").pack(side=tk.LEFT, padx=5)
        self.number_step_entry = ttk.Entry(start_step_frame, width=10)
        self.number_step_entry.insert(0, "1")
        self.number_step_entry.pack(side=tk.LEFT, padx=5)
    
    def show_case_params(self):
        case_frame = ttk.Frame(self.rule_params_frame)
        case_frame.pack(fill=tk.X, pady=2)
        self.case_var = tk.StringVar(value="全部大写")
        ttk.Radiobutton(case_frame, text="全部大写", variable=self.case_var, value="全部大写").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(case_frame, text="全部小写", variable=self.case_var, value="全部小写").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(case_frame, text="首字母大写", variable=self.case_var, value="首字母大写").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(case_frame, text="仅扩展名大写", variable=self.case_var, value="仅扩展名大写").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(case_frame, text="仅扩展名小写", variable=self.case_var, value="仅扩展名小写").pack(side=tk.LEFT, padx=5)
    
    def show_regex_params(self):
        # 正则查找
        find_frame = ttk.Frame(self.rule_params_frame)
        find_frame.pack(fill=tk.X, pady=2)
        ttk.Label(find_frame, text="正则表达式: ").pack(side=tk.LEFT, padx=5)
        self.regex_find_entry = ttk.Entry(find_frame, width=30)
        self.regex_find_entry.pack(side=tk.LEFT, padx=5)
        
        # 正则替换
        replace_frame = ttk.Frame(self.rule_params_frame)
        replace_frame.pack(fill=tk.X, pady=2)
        ttk.Label(replace_frame, text="替换为: ").pack(side=tk.LEFT, padx=5)
        self.regex_replace_entry = ttk.Entry(replace_frame, width=30)
        self.regex_replace_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(replace_frame, text="(使用 \1, \2 引用捕获组)").pack(side=tk.LEFT, padx=5)
    
    def show_crop_params(self):
        crop_frame = ttk.Frame(self.rule_params_frame)
        crop_frame.pack(fill=tk.X, pady=2)
        ttk.Label(crop_frame, text="裁剪方式: ").pack(side=tk.LEFT, padx=5)
        self.crop_type_var = tk.StringVar(value="删除前N个字符")
        ttk.Radiobutton(crop_frame, text="删除前N个字符", variable=self.crop_type_var, value="删除前N个字符").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(crop_frame, text="删除后N个字符", variable=self.crop_type_var, value="删除后N个字符").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(crop_frame, text="删除第N到第M个字符", variable=self.crop_type_var, value="删除第N到第M个字符").pack(side=tk.LEFT, padx=5)
        
        # 参数
        param_frame = ttk.Frame(self.rule_params_frame)
        param_frame.pack(fill=tk.X, pady=2)
        ttk.Label(param_frame, text="参数1: ").pack(side=tk.LEFT, padx=5)
        self.crop_param1_entry = ttk.Entry(param_frame, width=10)
        self.crop_param1_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(param_frame, text="参数2: ").pack(side=tk.LEFT, padx=5)
        self.crop_param2_entry = ttk.Entry(param_frame, width=10)
        self.crop_param2_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(param_frame, text="(如: 删除前3个字符填3,0)").pack(side=tk.LEFT, padx=5)
    
    def show_insert_params(self):
        # 位置选择
        pos_frame = ttk.Frame(self.rule_params_frame)
        pos_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pos_frame, text="位置: ").pack(side=tk.LEFT, padx=5)
        self.insert_pos_var = tk.StringVar(value="指定位置")
        ttk.Radiobutton(pos_frame, text="指定位置", variable=self.insert_pos_var, value="指定位置").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(pos_frame, text="扩展名前", variable=self.insert_pos_var, value="扩展名前").pack(side=tk.LEFT, padx=5)
        
        # 指定位置
        index_frame = ttk.Frame(self.rule_params_frame)
        index_frame.pack(fill=tk.X, pady=2)
        ttk.Label(index_frame, text="在第N个字符后插入: ").pack(side=tk.LEFT, padx=5)
        self.insert_index_entry = ttk.Entry(index_frame, width=10)
        self.insert_index_entry.insert(0, "0")
        self.insert_index_entry.pack(side=tk.LEFT, padx=5)
        
        # 要插入的文本
        text_frame = ttk.Frame(self.rule_params_frame)
        text_frame.pack(fill=tk.X, pady=2)
        ttk.Label(text_frame, text="要插入的文本: ").pack(side=tk.LEFT, padx=5)
        self.insert_text_entry = ttk.Entry(text_frame, width=30)
        self.insert_text_entry.pack(side=tk.LEFT, padx=5)
    
    def select_excel(self):
        file = filedialog.askopenfilename(title="选择Excel映射表", filetypes=[("Excel文件", "*.xlsx;*.xls")])
        if file:
            self.excel_path_entry.delete(0, tk.END)
            self.excel_path_entry.insert(0, file)
    
    def generate_preview(self):
        # 获取选中的文件
        self.selected_files = []
        for item in self.file_tree.get_children():
            tags = self.file_tree.item(item, "tags")
            if len(tags) > 1 and tags[1] == "selected":
                filename = tags[0]
                for file in self.files:
                    if file[0] == filename:
                        self.selected_files.append(file)
                        break
        
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要重命名的文件！")
            return
        
        # 生成预览
        self.rename_preview = []
        rule = self.rule_var.get()
        
        try:
            for file in self.selected_files:
                old_name = file[0]
                new_name = old_name
                
                if rule == "删除指定字符":
                    new_name = self.apply_delete_rule(old_name)
                elif rule == "在开头/结尾添加字符":
                    new_name = self.apply_add_rule(old_name)
                elif rule == "批量替换字符":
                    new_name = self.apply_replace_rule(old_name)
                elif rule == "Excel映射表重命名":
                    new_name = self.apply_excel_rule(old_name)
                elif rule == "自动编号":
                    # 自动编号需要特殊处理，因为需要计数
                    pass
                elif rule == "批量更改大小写":
                    new_name = self.apply_case_rule(old_name)
                elif rule == "正则表达式替换":
                    new_name = self.apply_regex_rule(old_name)
                elif rule == "文本裁剪":
                    new_name = self.apply_crop_rule(old_name)
                elif rule == "文字插入":
                    new_name = self.apply_insert_rule(old_name)
                
                self.rename_preview.append((old_name, new_name, ""))
            
            # 处理自动编号
            if rule == "自动编号":
                self.apply_numbering_rule()
            
            # 检查冲突
            self.check_conflicts()
            
            # 显示预览
            self.display_preview()
            
            self.log(f"已生成 {len(self.rename_preview)} 个文件的重命名预览")
        except Exception as e:
            messagebox.showerror("错误", f"生成预览失败: {str(e)}")
    
    def apply_delete_rule(self, filename):
        delete_char = self.delete_char_entry.get()
        return filename.replace(delete_char, "")
    
    def apply_add_rule(self, filename):
        add_char = self.add_char_entry.get()
        pos = self.add_pos_var.get()
        
        if pos == "开头":
            return add_char + filename
        else:
            # 扩展名前添加
            name, ext = os.path.splitext(filename)
            return name + add_char + ext
    
    def apply_replace_rule(self, filename):
        find = self.replace_find_entry.get()
        replace_with = self.replace_with_entry.get()
        modify_ext = self.replace_ext_var.get()
        
        if modify_ext:
            # 修改整个文件名，包括扩展名
            return filename.replace(find, replace_with)
        else:
            # 只修改文件名，不修改扩展名
            name, ext = os.path.splitext(filename)
            return name.replace(find, replace_with) + ext
    
    def apply_excel_rule(self, filename):
        # 这里简化处理，实际应该读取Excel文件
        # 暂时返回原文件名
        return filename
    
    def apply_numbering_rule(self):
        prefix = self.number_prefix_entry.get()
        suffix = self.number_suffix_entry.get()
        width = int(self.number_width_entry.get())
        start = int(self.number_start_entry.get())
        step = int(self.number_step_entry.get())
        
        # 重新生成预览
        self.rename_preview = []
        count = start
        
        for file in self.selected_files:
            old_name = file[0]
            name, ext = os.path.splitext(old_name)
            new_name = f"{prefix}{count:0{width}d}{suffix}{ext}"
            self.rename_preview.append((old_name, new_name, ""))
            count += step
    
    def apply_case_rule(self, filename):
        case_type = self.case_var.get()
        name, ext = os.path.splitext(filename)
        
        if case_type == "全部大写":
            return filename.upper()
        elif case_type == "全部小写":
            return filename.lower()
        elif case_type == "首字母大写":
            return name.title() + ext
        elif case_type == "仅扩展名大写":
            return name + ext.upper()
        elif case_type == "仅扩展名小写":
            return name + ext.lower()
    
    def apply_regex_rule(self, filename):
        pattern = self.regex_find_entry.get()
        replace_with = self.regex_replace_entry.get()
        
        try:
            return re.sub(pattern, replace_with, filename)
        except re.error as e:
            messagebox.showerror("错误", f"正则表达式错误: {str(e)}")
            return filename
    
    def apply_crop_rule(self, filename):
        crop_type = self.crop_type_var.get()
        param1 = int(self.crop_param1_entry.get()) if self.crop_param1_entry.get().isdigit() else 0
        param2 = int(self.crop_param2_entry.get()) if self.crop_param2_entry.get().isdigit() else 0
        
        if crop_type == "删除前N个字符":
            return filename[param1:]
        elif crop_type == "删除后N个字符":
            return filename[:-param1] if param1 > 0 else filename
        elif crop_type == "删除第N到第M个字符":
            # 注意：Python字符串索引从0开始
            if param2 <= param1:
                return filename
            return filename[:param1-1] + filename[param2:]
        
        return filename
    
    def apply_insert_rule(self, filename):
        insert_text = self.insert_text_entry.get()
        pos_type = self.insert_pos_var.get()
        
        if pos_type == "指定位置":
            index = int(self.insert_index_entry.get()) if self.insert_index_entry.get().isdigit() else 0
            return filename[:index] + insert_text + filename[index:]
        else:
            # 扩展名前插入
            name, ext = os.path.splitext(filename)
            return name + insert_text + ext
    
    def check_conflicts(self):
        # 收集所有新文件名
        new_names = [item[1] for item in self.rename_preview]
        
        # 检查重复
        for i, item in enumerate(self.rename_preview):
            old_name, new_name, status = item
            if new_names.count(new_name) > 1:
                self.rename_preview[i] = (old_name, new_name, "冲突")
            # 检查是否与现有文件冲突
            elif new_name != old_name and os.path.exists(os.path.join(self.folder_path, new_name)):
                self.rename_preview[i] = (old_name, new_name, "与现有文件冲突")
    
    def display_preview(self):
        # 清空现有预览
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # 添加预览项
        for item in self.rename_preview:
            self.preview_tree.insert("", tk.END, values=item)
    
    def execute_rename(self):
        if not self.rename_preview:
            messagebox.showwarning("警告", "请先生成预览！")
            return
        
        # 确认操作
        if not messagebox.askyesno("确认", f"确定要重命名 {len(self.rename_preview)} 个文件吗？"):
            return
        
        # 执行重命名
        success_count = 0
        fail_count = 0
        conflict_strategy = self.current_conflict_strategy.get()
        
        # 记录操作，用于撤销
        undo_info = []
        
        try:
            for old_name, new_name, status in self.rename_preview:
                old_path = os.path.join(self.folder_path, old_name)
                new_path = os.path.join(self.folder_path, new_name)
                
                # 处理冲突
                if status == "冲突" or status == "与现有文件冲突":
                    if conflict_strategy == "自动添加序号":
                        # 自动添加序号
                        base_name, ext = os.path.splitext(new_name)
                        counter = 1
                        while os.path.exists(new_path):
                            new_path = os.path.join(self.folder_path, f"{base_name}_{counter}{ext}")
                            counter += 1
                        new_name = os.path.basename(new_path)
                    elif conflict_strategy == "覆盖":
                        # 覆盖
                        if os.path.exists(new_path):
                            os.remove(new_path)
                    elif conflict_strategy == "跳过":
                        # 跳过
                        self.log(f"跳过冲突文件: {old_name} -> {new_name}")
                        fail_count += 1
                        continue
                    elif conflict_strategy == "停止":
                        # 停止
                        self.log(f"遇到冲突，已停止: {old_name} -> {new_name}")
                        messagebox.showinfo("信息", "遇到冲突，已停止重命名操作")
                        return
                
                # 执行重命名
                os.rename(old_path, new_path)
                undo_info.append((old_name, new_name))
                success_count += 1
                self.log(f"成功重命名: {old_name} -> {new_name}")
            
            # 保存到撤销栈
            self.undo_stack.append(undo_info)
            
            # 更新文件列表
            self.refresh_file_list()
            
            messagebox.showinfo("成功", f"重命名完成！成功: {success_count} 个, 失败: {fail_count} 个")
        except Exception as e:
            messagebox.showerror("错误", f"重命名失败: {str(e)}")
    
    def undo_rename(self):
        if not self.undo_stack:
            messagebox.showwarning("警告", "没有可撤销的操作！")
            return
        
        # 获取最后一次操作
        undo_info = self.undo_stack.pop()
        
        # 执行撤销
        success_count = 0
        fail_count = 0
        
        try:
            for old_name, new_name in undo_info:
                # 注意：撤销时，原文件名是new_name，新文件名是old_name
                old_path = os.path.join(self.folder_path, new_name)
                new_path = os.path.join(self.folder_path, old_name)
                
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    success_count += 1
                    self.log(f"撤销重命名: {new_name} -> {old_name}")
                else:
                    fail_count += 1
                    self.log(f"撤销失败，文件不存在: {new_name}")
            
            # 更新文件列表
            self.refresh_file_list()
            
            messagebox.showinfo("成功", f"撤销完成！成功: {success_count} 个, 失败: {fail_count} 个")
        except Exception as e:
            messagebox.showerror("错误", f"撤销失败: {str(e)}")
    
    def export_log(self):
        # 导出日志到文件
        try:
            # 打开文件对话框，让用户选择保存位置
            file_path = filedialog.asksaveasfilename(
                title="导出日志",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            
            if not file_path:
                # 用户取消了操作
                return
            
            # 获取日志内容
            log_content = self.log_text.get("1.0", tk.END)
            
            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(log_content)
            
            messagebox.showinfo("成功", f"日志已成功导出到: {file_path}")
            self.log(f"日志已导出到: {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出日志失败: {str(e)}")
            self.log(f"导出日志失败: {str(e)}")
    
    def export_rename_report(self):
        # 导出重命名结果报告（CSV格式）
        try:
            if not self.rename_preview:
                messagebox.showwarning("警告", "请先生成重命名预览！")
                return
            
            # 打开文件对话框，让用户选择保存位置
            file_path = filedialog.asksaveasfilename(
                title="导出重命名报告",
                defaultextension=".csv",
                filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
            )
            
            if not file_path:
                # 用户取消了操作
                return
            
            # 写入CSV文件
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                # 写入表头
                writer.writerow(["原文件名", "新文件名", "状态"])
                # 写入数据
                for old_name, new_name, status in self.rename_preview:
                    writer.writerow([old_name, new_name, status])
            
            messagebox.showinfo("成功", f"重命名报告已成功导出到: {file_path}")
            self.log(f"重命名报告已导出到: {file_path}")
        except Exception as e:
            messagebox.showerror("错误", f"导出重命名报告失败: {str(e)}")
            self.log(f"导出重命名报告失败: {str(e)}")
    
    def log(self, message):
        # 记录日志
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchRenamer(root)
    root.mainloop()