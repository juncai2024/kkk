import tkinter as tk
from tkinter import colorchooser, simpledialog, filedialog, messagebox
import json

class PuzzleMapEditor:
    def __init__(self, master):
        self.master = master
        master.title("拼图地图编辑器")

        # 默认参数
        self.map_w = 10
        self.map_h = 10
        self.cell_size = 40  # 像素
        self.current_region_id = None
        self.regions = {}  # region_id -> {'name': str, 'color': hex}
        self.grid = [[None for _ in range(self.map_w)] for _ in range(self.map_h)]

        # UI 布局
        ctrl = tk.Frame(master)
        ctrl.pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=6)

        tk.Label(ctrl, text="地图宽 (列)").pack()
        self.entry_w = tk.Entry(ctrl)
        self.entry_w.insert(0, str(self.map_w))
        self.entry_w.pack()

        tk.Label(ctrl, text="地图高 (行)").pack()
        self.entry_h = tk.Entry(ctrl)
        self.entry_h.insert(0, str(self.map_h))
        self.entry_h.pack()

        tk.Button(ctrl, text="新建地图", command=self.new_map).pack(fill=tk.X, pady=4)
        tk.Button(ctrl, text="重置标记（清空所有）", command=self.clear_all).pack(fill=tk.X, pady=4)

        tk.Label(ctrl, text="当前部件（Region）").pack(pady=(10,0))
        self.region_listbox = tk.Listbox(ctrl, height=8)
        self.region_listbox.pack(fill=tk.X)
        self.region_listbox.bind("<<ListboxSelect>>", self.on_region_select)

        btn_frame = tk.Frame(ctrl)
        btn_frame.pack(fill=tk.X, pady=4)
        tk.Button(btn_frame, text="新建部件", command=self.create_region).pack(side=tk.LEFT, expand=True, fill=tk.X)
        tk.Button(btn_frame, text="删除部件", command=self.delete_region).pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Button(ctrl, text="选择颜色", command=self.change_region_color).pack(fill=tk.X, pady=4)
        tk.Button(ctrl, text="导出为 JSON", command=self.export_json).pack(fill=tk.X, pady=4)
        tk.Button(ctrl, text="导入 JSON", command=self.import_json).pack(fill=tk.X, pady=4)

        # 说明
        tk.Label(ctrl, text="用法：点击或按住左键拖动涂色；右键清除格子归属").pack(pady=(10,0))

        # 画布
        canvas_frame = tk.Frame(master)
        canvas_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.on_left_down)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_up)
        self.canvas.bind("<Button-3>", self.on_right_click)

        self._dragging = False

        # 初始化显示
        self.draw_grid()

    # ---------- 地图 / 绘制 ----------
    def new_map(self):
        try:
            w = int(self.entry_w.get())
            h = int(self.entry_h.get())
            if w <= 0 or h <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("错误", "宽和高必须为正整数")
            return

        self.map_w = w
        self.map_h = h
        self.grid = [[None for _ in range(self.map_w)] for _ in range(self.map_h)]
        self.regions = {}
        self.current_region_id = None
        self.region_listbox.delete(0, tk.END)
        self.draw_grid()

    def clear_all(self):
        for y in range(self.map_h):
            for x in range(self.map_w):
                self.grid[y][x] = None
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")
        # 调整画布大小
        width = self.map_w * self.cell_size
        height = self.map_h * self.cell_size
        self.canvas.config(scrollregion=(0,0,width,height), width=min(width, 800), height=min(height, 800))

        for y in range(self.map_h):
            for x in range(self.map_w):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                cell_tag = f"cell_{x}_{y}"
                rid = self.grid[y][x]
                fill = self.regions[rid]['color'] if (rid is not None and rid in self.regions) else ""
                # 先画矩形（fill color），再画网格线（outline）
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="gray", tags=(cell_tag,))
                if rid is not None:
                    # 显示简短 id
                    self.canvas.create_text(x1+4, y1+4, anchor="nw", text=str(rid), font=("TkDefaultFont", 8),
                                            tags=(cell_tag,))

    # ---------- 区域管理 ----------
    def create_region(self):
        name = simpledialog.askstring("新建部件", "输入部件名称（可空）:")
        color = colorchooser.askcolor(title="选择部件颜色")[1]
        if color is None:
            return
        # 新 id（自增）
        new_id = 1
        while new_id in self.regions:
            new_id += 1
        self.regions[new_id] = {"name": name or f"region_{new_id}", "color": color}
        self.region_listbox.insert(tk.END, f"{new_id}: {self.regions[new_id]['name']} ({color})")
        # 选中它
        self.region_listbox.selection_clear(0, tk.END)
        self.region_listbox.selection_set(tk.END)
        self.current_region_id = new_id

    def delete_region(self):
        sel = self.region_listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "先选择要删除的部件")
            return
        idx = sel[0]
        text = self.region_listbox.get(idx)
        rid = int(text.split(":")[0])
        if messagebox.askyesno("确认", f"删除部件 {rid}？格子会被清空归属。"):
            # 清理格子引用
            for y in range(self.map_h):
                for x in range(self.map_w):
                    if self.grid[y][x] == rid:
                        self.grid[y][x] = None
            del self.regions[rid]
            self.region_listbox.delete(idx)
            self.current_region_id = None
            self.draw_grid()

    def on_region_select(self, _ev=None):
        sel = self.region_listbox.curselection()
        if not sel:
            self.current_region_id = None
            return
        idx = sel[0]
        text = self.region_listbox.get(idx)
        rid = int(text.split(":")[0])
        self.current_region_id = rid

    def change_region_color(self):
        sel = self.region_listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "先选择要改色的部件")
            return
        idx = sel[0]
        text = self.region_listbox.get(idx)
        rid = int(text.split(":")[0])
        new_color = colorchooser.askcolor(title="选择新颜色")[1]
        if new_color is None:
            return
        self.regions[rid]['color'] = new_color
        # 更新 listbox 显示
        self.region_listbox.delete(idx)
        self.region_listbox.insert(idx, f"{rid}: {self.regions[rid]['name']} ({new_color})")
        self.draw_grid()

    # ---------- 鼠标事件（涂色 / 清除） ----------
    def cell_from_event(self, event):
        # 计算 canvas 上的格子（考虑 scrollregion origin 是 0,0）
        x = int(event.x // self.cell_size)
        y = int(event.y // self.cell_size)
        if 0 <= x < self.map_w and 0 <= y < self.map_h:
            return x, y
        return None

    def on_left_down(self, event):
        if self.current_region_id is None:
            messagebox.showinfo("提示", "先创建并选中一个部件（Region）再涂色")
            return
        cell = self.cell_from_event(event)
        if cell:
            self._dragging = True
            self.paint_cell(cell[0], cell[1], self.current_region_id)

    def on_left_drag(self, event):
        if not self._dragging or self.current_region_id is None:
            return
        cell = self.cell_from_event(event)
        if cell:
            self.paint_cell(cell[0], cell[1], self.current_region_id)

    def on_left_up(self, event):
        self._dragging = False

    def on_right_click(self, event):
        cell = self.cell_from_event(event)
        if cell:
            x, y = cell
            self.grid[y][x] = None
            self.draw_grid()

    def paint_cell(self, x, y, region_id):
        # 仅当格子需要更新时才重绘
        if self.grid[y][x] != region_id:
            self.grid[y][x] = region_id
            x1 = x * self.cell_size
            y1 = y * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            # 覆盖 redraw（更简单直接：重绘整个网格；若格子很多，可优化为只更新该格）
            self.draw_grid()

    # ---------- 导入/导出 ----------
    def export_json(self):
        if not self.regions:
            if not messagebox.askyesno("确认", "当前没有部件，仍然导出空地图吗？"):
                return
        out = {
            "width": self.map_w,
            "height": self.map_h,
            "cell_size": self.cell_size,
            # regions: list of {id, name, color}
            "regions": [{"id": rid, "name": info["name"], "color": info["color"]} for rid, info in self.regions.items()],
            # grid: list of rows; each cell is null or region_id
            "grid": self.grid
        }
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON 文件", "*.json")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("导出完成", f"已保存到：\n{path}")

    def import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON 文件", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"打开或解析 JSON 失败：{e}")
            return

        try:
            w = int(data["width"])
            h = int(data["height"])
            grid = data["grid"]
            regions_in = data.get("regions", [])
        except Exception as e:
            messagebox.showerror("格式错误", f"JSON 缺少必要字段或格式不对：{e}")
            return

        # 载入 regions（保持 id）
        self.regions = {}
        for r in regions_in:
            rid = int(r["id"])
            name = r.get("name", f"region_{rid}")
            color = r.get("color", "#cccccc")
            self.regions[rid] = {"name": name, "color": color}

        # 载入 grid
        # 保证 grid 的尺寸正确
        self.map_w = w
        self.map_h = h
        self.grid = [[None for _ in range(self.map_w)] for _ in range(self.map_h)]
        # grid 可能是 list of lists
        for y in range(min(len(grid), self.map_h)):
            row = grid[y]
            for x in range(min(len(row), self.map_w)):
                val = row[x]
                # 允许 null 或者数字（region id）
                self.grid[y][x] = val if val in self.regions else (val if val is None else None)

        # 更新 UI
        self.entry_w.delete(0, tk.END); self.entry_w.insert(0, str(self.map_w))
        self.entry_h.delete(0, tk.END); self.entry_h.insert(0, str(self.map_h))
        # 填充 listbox
        self.region_listbox.delete(0, tk.END)
        for rid, info in self.regions.items():
            self.region_listbox.insert(tk.END, f"{rid}: {info['name']} ({info['color']})")
        self.current_region_id = None
        self.draw_grid()
        messagebox.showinfo("导入完成", f"已从 {path} 载入")

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleMapEditor(root)
    root.mainloop()