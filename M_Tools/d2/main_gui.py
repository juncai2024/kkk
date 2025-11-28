# main_gui.py
"""
D2R 装备识别 GUI（中文）
依赖: paddleocr, pillow, pandas, openpyxl, tqdm
使用方法: python main_gui.py
需要文件: item_parser.py, rules_engine.py, rules_full.json 与本文件放在同一目录
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import pandas as pd
import json

from item_parser import parse_item   # parse_item(img_path) -> dict
import rules_engine as engine        # engine.load_rules(), engine.evaluate(item)

# 默认规则文件路径
RULES_PATH = "rules_full.json"
SUPPORTED_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".webp")

# GUI 应用
class D2RApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("D2R 装备识别器（国服 A - 中文）")
        self.geometry("1100x700")
        self.minsize(1000,650)

        self.images = []   # list of file paths
        self.results = []  # recognition results

        # load rules
        try:
            self.rules = engine.load_rules(RULES_PATH)
        except Exception as e:
            messagebox.showerror("规则加载错误", f"加载规则失败: {e}")
            self.rules = []

        self._build_ui()

    def _build_ui(self):
        # 左侧控制面板
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        ttk.Button(left, text="添加文件", command=self.add_files).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="添加文件夹", command=self.add_folder).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="清空列表", command=self.clear_list).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="处理所选", command=self.process_selected_thread).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="处理全部", command=self.process_all_thread).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="导出 CSV/Excel", command=self.export_results).pack(fill=tk.X, pady=4)
        ttk.Button(left, text="热重载规则", command=self.reload_rules).pack(fill=tk.X, pady=4)

        self.lb = tk.Listbox(left, width=40, height=30)
        self.lb.pack(fill=tk.BOTH, expand=True, pady=6)
        self.lb.bind("<<ListboxSelect>>", self.on_select)

        # 右侧展示区
        right = ttk.Frame(self)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        # 顶部：图片预览与 OCR 文本
        top = ttk.Frame(right)
        top.pack(fill=tk.BOTH, expand=True)

        # 画布显示图片
        self.canvas = tk.Canvas(top, bg="#111", width=480, height=360)
        self.canvas.pack(side=tk.LEFT, padx=6, pady=6)
        self.tkimg = None

        info = ttk.Frame(top)
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(info, text="OCR 文本：").pack(anchor=tk.W)
        self.txt_ocr = tk.Text(info, height=12, wrap=tk.WORD)
        self.txt_ocr.pack(fill=tk.BOTH, expand=True, pady=4)

        ttk.Label(info, text="价值判断：").pack(anchor=tk.W)
        self.txt_res = tk.Text(info, height=8, wrap=tk.WORD)
        self.txt_res.pack(fill=tk.BOTH, expand=True, pady=4)

        # 底部：状态 & 进度
        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, padx=8, pady=6)
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(bottom, textvariable=self.status_var).pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(bottom, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.RIGHT)

    # 文件操作
    def add_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.webp")])
        for p in paths:
            if p and p.lower().endswith(SUPPORTED_EXTS) and p not in self.images:
                self.images.append(p)
                self.lb.insert(tk.END, os.path.basename(p))

    def add_folder(self):
        d = filedialog.askdirectory()
        if not d:
            return
        added = 0
        for f in os.listdir(d):
            fp = os.path.join(d, f)
            if os.path.isfile(fp) and fp.lower().endswith(SUPPORTED_EXTS):
                if fp not in self.images:
                    self.images.append(fp)
                    self.lb.insert(tk.END, os.path.basename(fp))
                    added += 1
        messagebox.showinfo("提示", f"已添加 {added} 张图片")

    def clear_list(self):
        self.images = []
        self.results = []
        self.lb.delete(0, tk.END)
        self.canvas.delete("all")
        self.txt_ocr.delete("1.0", tk.END)
        self.txt_res.delete("1.0", tk.END)
        self.status_var.set("已清空")

    def on_select(self, evt):
        sel = self.lb.curselection()
        if not sel:
            return
        idx = sel[0]
        path = self.images[idx]
        self.show_image(path)
        existing = next((r for r in self.results if r["path"]==path), None)
        if existing:
            self.txt_ocr.delete("1.0", tk.END)
            self.txt_ocr.insert(tk.END, existing.get("ocr_text",""))
            self.txt_res.delete("1.0", tk.END)
            self.txt_res.insert(tk.END, f"结果：{existing.get('value')}\n规则ID: {existing.get('rule_id')}\n原因: {existing.get('reason')}")
        else:
            # perform quick parse for preview (parse_item internally runs OCR)
            self.status_var.set("OCR 预览...")
            self.update_idletasks()
            try:
                it = parse_item(path)
                self.txt_ocr.delete("1.0", tk.END)
                self.txt_ocr.insert(tk.END, "\n".join(it.get("raw_lines",[])))
                self.txt_res.delete("1.0", tk.END)
                self.txt_res.insert(tk.END, "解析预览:\n" + json.dumps(it, ensure_ascii=False, indent=2))
            except Exception as e:
                self.txt_ocr.delete("1.0", tk.END)
                self.txt_res.delete("1.0", tk.END)
                self.txt_res.insert(tk.END, f"OCR/解析错误: {e}")
            finally:
                self.status_var.set("就绪")

    def show_image(self, path):
        try:
            img = Image.open(path)
            max_w, max_h = 480, 360
            w,h = img.size
            scale = min(max_w/w, max_h/h, 1.0)
            new_w,new_h = int(w*scale), int(h*scale)
            img = img.resize((new_w,new_h), Image.LANCZOS)
            self.tkimg = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(max_w//2, max_h//2, image=self.tkimg, anchor=tk.CENTER)
        except Exception as e:
            self.canvas.delete("all")
            self.canvas.create_text(240,180, text="无法显示图片", fill="white")

    # 处理线程
    def process_all_thread(self):
        if not self.images:
            messagebox.showwarning("提示", "请先添加图片")
            return
        t = threading.Thread(target=self.process_paths, args=(self.images,))
        t.daemon = True
        t.start()

    def process_selected_thread(self):
        sel = self.lb.curselection()
        if not sel:
            messagebox.showwarning("提示", "请先选择图片")
            return
        paths = [self.images[i] for i in sel]
        t = threading.Thread(target=self.process_paths, args=(paths,))
        t.daemon = True
        t.start()

    def process_paths(self, paths):
        self.status_var.set(f"开始识别 {len(paths)} 张图片")
        self.progress["maximum"] = len(paths)
        count = 0
        for p in paths:
            count += 1
            self.progress["value"] = count
            self.status_var.set(f"识别中 ({count}/{len(paths)})：{os.path.basename(p)}")
            self.update_idletasks()
            try:
                item = parse_item(p)
                res = engine.evaluate(item, self.rules)
                rec = {
                    "path": p,
                    "ocr_text": "\n".join(item.get("raw_lines", [])),
                    "item": item,
                    "rule_id": res.get("rule_id"),
                    "value": res.get("value"),
                    "reason": res.get("reason")
                }
            except Exception as e:
                rec = {
                    "path": p,
                    "ocr_text": "",
                    "item": {},
                    "rule_id": None,
                    "value": "识别失败",
                    "reason": str(e)
                }
            # 保存结果（覆盖旧记录）
            self.results = [r for r in self.results if r.get("path") != p]
            self.results.append(rec)

            # 如果当前选中该图片，刷新显示
            sel = self.lb.curselection()
            if sel and self.images[sel[0]] == p:
                self.txt_ocr.delete("1.0", tk.END)
                self.txt_ocr.insert(tk.END, rec.get("ocr_text",""))
                self.txt_res.delete("1.0", tk.END)
                self.txt_res.insert(tk.END, f"结果：{rec.get('value')}\n规则ID: {rec.get('rule_id')}\n原因: {rec.get('reason')}")

        self.status_var.set("处理完成")
        messagebox.showinfo("完成", f"已处理 {len(paths)} 张图片")

    def export_results(self):
        if not self.results:
            messagebox.showwarning("提示", "无结果可导出")
            return
        f = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv")])
        if not f: return
        rows = []
        for r in self.results:
            rows.append({
                "file": os.path.basename(r["path"]),
                "path": r["path"],
                "value": r.get("value"),
                "rule_id": r.get("rule_id"),
                "reason": r.get("reason"),
                "ocr_text": r.get("ocr_text")
            })
        df = pd.DataFrame(rows)
        try:
            if f.lower().endswith(".csv"):
                df.to_csv(f, index=False, encoding="utf-8-sig")
            else:
                df.to_excel(f, index=False)
            messagebox.showinfo("导出完成", f"已导出到：{f}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))

    def reload_rules(self):
        try:
            self.rules = engine.load_rules(RULES_PATH)
            messagebox.showinfo("规则重载", "规则文件已重新加载")
        except Exception as e:
            messagebox.showerror("重载失败", str(e))

def main():
    app = D2RApp()
    app.mainloop()

if __name__ == "__main__":
    main()
