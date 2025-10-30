"""
sudoku_game.py

更完善的数独桌面应用（Tkinter + Canvas）——增强版
功能清单：
- 更精致的 UI（Canvas 渐变背景、圆角按钮风格化/emoji 图标、简单动画）
- 高亮当前行/列/宫
- 回溯求解器 + 求解计数（用于唯一解检测）
- 生成器：在移除格子时检查是否保持唯一解（可配置）
- 铅笔记号（候选数）显示，多次点击切换候选/清除
- 撤销 / 重做（按动作存栈）
- 存档（保存/加载为 JSON）
- 计时器、难度选择、提示、重置、求解

使用方法：
1. 保存为 sudoku_game.py
2. 安装 Python 3.8+（含 tkinter）
3. 运行： python sudoku_game.py

备注：需要打包成 Mac 可执行文件的步骤在代码下方有说明（pyinstaller / py2app）。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import time
import json
import copy
import threading

# ----------------- 常量 -----------------
CELL_SIZE = 64
GRID_PADDING = 18
BOARD_SIZE = CELL_SIZE * 9
FONT_MAIN = ('Helvetica', 18)
FONT_FIXED = ('Helvetica', 18, 'bold')
FONT_PENCIL = ('Helvetica', 8)
HIGHLIGHT_COLOR = '#f0fbff'
SELECT_COLOR = '#cfeefe'
LINE_COLOR = '#2b2b2b'
FIXED_COLOR = '#0b2545'
USER_COLOR = '#0b7a3f'
ERROR_COLOR = '#ff7b7b'
BG_START = '#f6fbff'
BG_END = '#e6f2ff'

# ----------------- 算法（回溯 + 解计数） -----------------

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def valid(board, row, col, val):
    # 检查行/列/宫
    for c in range(9):
        if board[row][c] == val:
            return False
    for r in range(9):
        if board[r][col] == val:
            return False
    br = (row // 3) * 3
    bc = (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == val:
                return False
    return True


def solve_backtrack(board):
    pos = find_empty(board)
    if not pos:
        return True
    r, c = pos
    for val in range(1, 10):
        if valid(board, r, c, val):
            board[r][c] = val
            if solve_backtrack(board):
                return True
            board[r][c] = 0
    return False


def count_solutions(board, limit=2):
    """回溯计数解的数量。limit 表示找到 limit 个解时可以提前返回。"""
    pos = find_empty(board)
    if not pos:
        return 1
    r, c = pos
    count = 0
    for val in range(1, 10):
        if valid(board, r, c, val):
            board[r][c] = val
            cnt = count_solutions(board, limit)
            count += cnt
            board[r][c] = 0
            if count >= limit:
                return count
    return count


def generate_full_board():
    # 生成完整解（随机化回溯）
    board = [[0]*9 for _ in range(9)]
    numbers = list(range(1, 10))

    def fill():
        pos = find_empty(board)
        if not pos:
            return True
        r, c = pos
        random.shuffle(numbers)
        for val in numbers:
            if valid(board, r, c, val):
                board[r][c] = val
                if fill():
                    return True
                board[r][c] = 0
        return False

    fill()
    return board


def make_puzzle_with_uniqueness(full_board, empties, ensure_unique=True):
    board = [row[:] for row in full_board]
    coords = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(coords)
    removed = 0
    for r, c in coords:
        if removed >= empties:
            break
        backup = board[r][c]
        board[r][c] = 0
        if ensure_unique:
            # 检查唯一解
            copied = [row[:] for row in board]
            cnt = count_solutions(copied, limit=2)
            if cnt != 1:
                # 不唯一，回退
                board[r][c] = backup
                continue
        removed += 1
    return board

# ----------------- 应用：撤销/重做、存档、铅笔记号 -----------------

class ActionStack:
    def __init__(self):
        self.stack = []
        self.redo_stack = []

    def push(self, action):
        self.stack.append(action)
        self.redo_stack.clear()

    def undo(self):
        if not self.stack:
            return None
        a = self.stack.pop()
        self.redo_stack.append(a)
        return a

    def redo(self):
        if not self.redo_stack:
            return None
        a = self.redo_stack.pop()
        self.stack.append(a)
        return a

# ----------------- 主界面 -----------------

class SudokuApp:
    def __init__(self, master):
        self.master = master
        master.title('数独增强版')
        master.resizable(False, False)

        self.difficulty_map = {'简单': 30, '中等': 45, '困难': 55}
        self.difficulty = '中等'
        self.ensure_unique = True

        self.full_board = generate_full_board()
        self.puzzle = make_puzzle_with_uniqueness(self.full_board, self.difficulty_map[self.difficulty], self.ensure_unique)
        self.board = [row[:] for row in self.puzzle]
        self.fixed = [[(self.puzzle[r][c] != 0) for c in range(9)] for r in range(9)]
        # pencil marks: 每个格子为 set()
        self.pencils = [[set() for _ in range(9)] for _ in range(9)]

        self.selected = (0, 0)
        self.action_stack = ActionStack()

        self.start_time = None
        self.running = False
        self.elapsed = 0

        self.build_ui()
        self.draw_board()
        self.start_timer()

    def build_ui(self):
        # Canvas
        self.canvas = tk.Canvas(self.master, width=BOARD_SIZE+GRID_PADDING*2, height=BOARD_SIZE+GRID_PADDING*2, bg='white', highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=8, padx=12, pady=12)
        self.canvas.bind('<Button-1>', self.on_click)
        self.master.bind('<Key>', self.on_key)

        # controls
        cf = tk.Frame(self.master)
        cf.grid(row=0, column=1, sticky='n')

        tk.Label(cf, text='难度').grid(row=0, column=0)
        self.diff_var = tk.StringVar(value=self.difficulty)
        diff = ttk.Combobox(cf, textvariable=self.diff_var, values=list(self.difficulty_map.keys()), state='readonly', width=10)
        diff.grid(row=1, column=0)
        diff.bind('<<ComboboxSelected>>', self.change_difficulty)

        self.unique_var = tk.BooleanVar(value=self.ensure_unique)
        tk.Checkbutton(cf, text='生成唯一解', variable=self.unique_var, command=self.toggle_unique).grid(row=2, column=0, pady=(6,6))

        btns = [
            ('🔁 新游戏', self.new_game),
            ('🧭 检查', self.check_solution),
            ('✨ 求解', self.solve_and_show),
            ('💡 提示', self.hint_one),
            ('📝 存档', self.save_file),
            ('📂 读取', self.load_file),
            ('↶ 撤销', self.undo),
            ('↷ 重做', self.redo),
            ('♻ 重置答案', self.reset_user_entries),
        ]
        r = 3
        for text, cmd in btns:
            b = ttk.Button(cf, text=text, command=cmd, width=14)
            b.grid(row=r, column=0, pady=4)
            r += 1

        # pencil / normal toggle
        self.mode_var = tk.StringVar(value='normal')
        tk.Radiobutton(cf, text='输入', variable=self.mode_var, value='normal').grid(row=12, column=0, sticky='w')
        tk.Radiobutton(cf, text='铅笔', variable=self.mode_var, value='pencil').grid(row=13, column=0, sticky='w')

        # timer
        self.timer_label = tk.Label(cf, text='用时 00:00', font=('Helvetica', 12))
        self.timer_label.grid(row=14, column=0, pady=(10,0))

        note = tk.Label(cf, text='操作：点击格子选中，1-9 输入，Backspace 清除。铅笔模式用于候选数。')
        note.grid(row=15, column=0, pady=(6,0))

    def draw_gradient_bg(self):
        # 简单的竖直渐变（多条细矩形）
        self.canvas.delete('bg')
        steps = 40
        for i in range(steps):
            r = i / (steps - 1)
            color = self._interp_color(BG_START, BG_END, r)
            y0 = i * (BOARD_SIZE + GRID_PADDING*2) / steps
            y1 = (i+1) * (BOARD_SIZE + GRID_PADDING*2) / steps
            self.canvas.create_rectangle(0, y0, BOARD_SIZE + GRID_PADDING*2, y1, fill=color, outline=color, tags='bg')

    def _interp_color(self, a, b, t):
        # 颜色 '#rrggbb'
        ax = int(a[1:3], 16); ay = int(a[3:5], 16); az = int(a[5:7], 16)
        bx = int(b[1:3], 16); by = int(b[3:5], 16); bz = int(b[5:7], 16)
        cx = int(ax + (bx-ax)*t)
        cy = int(ay + (by-ay)*t)
        cz = int(az + (bz-az)*t)
        return f'#{cx:02x}{cy:02x}{cz:02x}'

    def draw_board(self):
        self.canvas.delete('all')
        self.draw_gradient_bg()
        off = GRID_PADDING

        # 高亮 (行/列/宫)
        r, c = self.selected
        self.canvas.create_rectangle(off, off + r*CELL_SIZE, off + 9*CELL_SIZE, off + (r+1)*CELL_SIZE, fill=HIGHLIGHT_COLOR, width=0)
        self.canvas.create_rectangle(off + c*CELL_SIZE, off, off + (c+1)*CELL_SIZE, off + 9*CELL_SIZE, fill=HIGHLIGHT_COLOR, width=0)
        br = (r//3)*3; bc = (c//3)*3
        self.canvas.create_rectangle(off + bc*CELL_SIZE, off + br*CELL_SIZE, off + (bc+3)*CELL_SIZE, off + (br+3)*CELL_SIZE, fill=HIGHLIGHT_COLOR, width=0)

        # 网格线
        for i in range(10):
            w = 3 if i % 3 == 0 else 1
            x0 = off + i*CELL_SIZE
            y0 = off
            x1 = x0
            y1 = off + 9*CELL_SIZE
            self.canvas.create_line(x0, y0, x1, y1, width=w, fill=LINE_COLOR)
            y0 = off + i*CELL_SIZE
            x0 = off
            y1 = y0
            x1 = off + 9*CELL_SIZE
            self.canvas.create_line(x0, y0, x1, y1, width=w, fill=LINE_COLOR)

        # 铅笔记号先画小字
        for rr in range(9):
            for cc in range(9):
                if self.board[rr][cc] == 0 and self.pencils[rr][cc]:
                    sx = off + cc*CELL_SIZE
                    sy = off + rr*CELL_SIZE
                    # 在 3x3 小格里排列 1..9
                    for n in range(1, 10):
                        if n in self.pencils[rr][cc]:
                            i = (n-1) // 3
                            j = (n-1) % 3
                            x = sx + 8 + j * 18
                            y = sy + 8 + i * 18
                            self.canvas.create_text(x, y, text=str(n), font=FONT_PENCIL, fill='#444')

        # 画数字
        for rr in range(9):
            for cc in range(9):
                val = self.board[rr][cc]
                if val != 0:
                    x = off + cc*CELL_SIZE + CELL_SIZE/2
                    y = off + rr*CELL_SIZE + CELL_SIZE/2
                    if self.fixed[rr][cc]:
                        self.canvas.create_text(x, y, text=str(val), font=FONT_FIXED, fill=FIXED_COLOR)
                    else:
                        self.canvas.create_text(x, y, text=str(val), font=FONT_MAIN, fill=USER_COLOR)

        # 选中框动画风格
        sx = off + c*CELL_SIZE
        sy = off + r*CELL_SIZE
        self.canvas.create_rectangle(sx, sy, sx+CELL_SIZE, sy+CELL_SIZE, outline=SELECT_COLOR, width=3)

    # ----------------- 事件 -----------------
    def on_click(self, event):
        x, y = event.x, event.y
        off = GRID_PADDING
        if not (off <= x <= off + 9*CELL_SIZE and off <= y <= off + 9*CELL_SIZE):
            return
        c = int((x - off) // CELL_SIZE)
        r = int((y - off) // CELL_SIZE)
        self.selected = (r, c)
        self.draw_board()

    def on_key(self, event):
        key = event.keysym
        r, c = self.selected
        if self.fixed[r][c]:
            return
        if key in ('BackSpace', 'Delete'):
            prev = self.board[r][c]
            if prev != 0:
                self.action_stack.push(('set', r, c, prev, 0))
            else:
                # 删除铅笔时不入撤销栈
                pass
            self.board[r][c] = 0
            self.pencils[r][c].clear()
            self.draw_board()
            return
        if key in [str(i) for i in range(1, 10)]:
            val = int(key)
            if self.mode_var.get() == 'normal':
                prev = self.board[r][c]
                if prev == val:
                    # 如果相同就清除
                    self.action_stack.push(('set', r, c, prev, 0))
                    self.board[r][c] = 0
                else:
                    self.action_stack.push(('set', r, c, prev, val))
                    self.board[r][c] = val
                    self.pencils[r][c].clear()
                    # 若插入导致冲突，闪烁
                    if not valid(self.board, r, c, val):
                        self.flash_cell_error(r, c)
                self.draw_board()
            else:
                # pencil 模式：切换候选
                if val in self.pencils[r][c]:
                    self.pencils[r][c].remove(val)
                else:
                    self.pencils[r][c].add(val)
                self.draw_board()
            # 自动完成检测
            if self.is_complete():
                self.stop_timer()
                if self.board == self.full_board:
                    messagebox.showinfo('完成', f'恭喜，你完成了数独！用时 {self.format_time(self.elapsed)}')
                else:
                    messagebox.showwarning('注意', '已填满，但可能不正确。')

    def flash_cell_error(self, r, c):
        off = GRID_PADDING
        x0 = off + c*CELL_SIZE
        y0 = off + r*CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=ERROR_COLOR)
        self.master.after(250, lambda: (self.canvas.delete(rect), self.draw_board()))

    # ----------------- 功能按钮 -----------------
    def new_game(self):
        # 生成新题（线程化避免界面卡死）
        def _gen():
            self.master.config(cursor='watch')
            self.full_board = generate_full_board()
            empties = self.difficulty_map[self.difficulty]
            self.puzzle = make_puzzle_with_uniqueness(self.full_board, empties, self.ensure_unique)
            self.board = [row[:] for row in self.puzzle]
            self.fixed = [[(self.puzzle[r][c] != 0) for c in range(9)] for r in range(9)]
            self.pencils = [[set() for _ in range(9)] for _ in range(9)]
            self.action_stack = ActionStack()
            self.selected = (0, 0)
            self.start_time = time.time()
            self.running = True
            self.elapsed = 0
            self.master.config(cursor='')
            self.draw_board()
        threading.Thread(target=_gen).start()

    def change_difficulty(self, event=None):
        v = self.diff_var.get()
        if v in self.difficulty_map:
            self.difficulty = v
            self.new_game()

    def toggle_unique(self):
        self.ensure_unique = self.unique_var.get()

    def check_solution(self):
        # 规则检查（行列宫）
        for r in range(9):
            row = self.board[r]
            if 0 in row:
                messagebox.showwarning('检查', '还有空格未填写')
                return
            if len(set(row)) != 9:
                messagebox.showwarning('检查', f'第 {r+1} 行有重复')
                return
        for c in range(9):
            col = [self.board[r][c] for r in range(9)]
            if len(set(col)) != 9:
                messagebox.showwarning('检查', f'第 {c+1} 列有重复')
                return
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                block = [self.board[r][c] for r in range(br, br+3) for c in range(bc, bc+3)]
                if len(set(block)) != 9:
                    messagebox.showwarning('检查', '有宫内重复')
                    return
        if self.board == self.full_board:
            self.stop_timer()
            messagebox.showinfo('检查', '答案正确！')
        else:
            messagebox.showinfo('检查', '规则通过，但与生成解不一致（可能有多解）')

    def solve_and_show(self):
        if not messagebox.askyesno('求解', '显示完整解将结束本题，是否继续？'):
            return
        self.board = [row[:] for row in self.full_board]
        self.pencils = [[set() for _ in range(9)] for _ in range(9)]
        self.draw_board()
        self.stop_timer()

    def hint_one(self):
        # 填一个空格或修正错误格
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    val = self.full_board[r][c]
                    self.action_stack.push(('set', r, c, 0, val))
                    self.board[r][c] = val
                    self.draw_board()
                    return
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != self.full_board[r][c]:
                    prev = self.board[r][c]
                    val = self.full_board[r][c]
                    self.action_stack.push(('set', r, c, prev, val))
                    self.board[r][c] = val
                    self.draw_board()
                    return
        messagebox.showinfo('提示', '没有可提示的格子')

    def reset_user_entries(self):
        self.action_stack.push(('reset', None))
        self.board = [row[:] for row in self.puzzle]
        self.pencils = [[set() for _ in range(9)] for _ in range(9)]
        self.draw_board()

    # ----------------- 撤销 / 重做 -----------------
    def undo(self):
        a = self.action_stack.undo()
        if a is None:
            return
        typ = a[0]
        if typ == 'set':
            _, r, c, prev, new = a
            # 反向操作：将值设回 prev
            self.board[r][c] = prev
        elif typ == 'reset':
            # 取消重置：无法完全恢复 -> 重新生成为 puzzle
            self.board = [row[:] for row in self.puzzle]
        self.draw_board()

    def redo(self):
        a = self.action_stack.redo()
        if a is None:
            return
        typ = a[0]
        if typ == 'set':
            _, r, c, prev, new = a
            self.board[r][c] = new
        elif typ == 'reset':
            self.board = [row[:] for row in self.puzzle]
        self.draw_board()

    # ----------------- 存档 / 读取 -----------------
    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension='.sudoku', filetypes=[('Sudoku save', '*.sudoku'), ('JSON', '*.json')])
        if not path:
            return
        payload = {
            'full_board': self.full_board,
            'puzzle': self.puzzle,
            'board': self.board,
            'pencils': [[sorted(list(s)) for s in row] for row in self.pencils],
            'fixed': self.fixed,
            'difficulty': self.difficulty,
            'ensure_unique': self.ensure_unique,
            'elapsed': self.elapsed,
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)
        messagebox.showinfo('存档', '保存成功')

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[('Sudoku save', '*.sudoku'), ('JSON', '*.json')])
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        try:
            self.full_board = payload['full_board']
            self.puzzle = payload['puzzle']
            self.board = payload['board']
            self.pencils = [[set(x) for x in row] for row in payload['pencils']]
            self.fixed = payload['fixed']
            self.difficulty = payload.get('difficulty', self.difficulty)
            self.ensure_unique = payload.get('ensure_unique', self.ensure_unique)
            self.elapsed = payload.get('elapsed', 0)
            self.start_time = time.time() - self.elapsed
            self.running = True
            self.draw_board()
            messagebox.showinfo('读取', '读取成功')
        except Exception as e:
            messagebox.showerror('读取失败', str(e))

    # ----------------- 计时器 -----------------
    def start_timer(self):
        if self.start_time is None:
            self.start_time = time.time()
        self.running = True
        self._tick()

    def _tick(self):
        if not self.running:
            return
        self.elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text='用时 ' + self.format_time(self.elapsed))
        self.master.after(1000, self._tick)

    def stop_timer(self):
        self.running = False

    def format_time(self, secs):
        m = secs // 60
        s = secs % 60
        return f"{m:02d}:{s:02d}"

    def is_complete(self):
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return False
        return True

# ----------------- 运行 -----------------

if __name__ == '__main__':
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()

# ----------------- 打包为 Mac 可执行文件（说明） -----------------
# 方法 A: PyInstaller（常用且跨平台）
# 1) 安装： pip install pyinstaller
# 2) 生成： pyinstaller --onefile --windowed sudoku_game.py
#    这会在 dist/ 下生成单个可执行文件（macOS 上为可运行的 app 二进制），
#    注意：如果使用 Tkinter，PyInstaller 通常能打包，但有时需要额外包含 tcl/tk 资源。
# 方法 B: py2app（专为 macOS）
# 1) 安装： pip install py2app
# 2) 创建 setup.py：
#    from setuptools import setup
#    APP = ['sudoku_game.py']
#    OPTIONS = {'argv_emulation': True, 'packages': []}
#    setup(app=APP, options={'py2app': OPTIONS}, setup_requires=['py2app'])
# 3) 运行： python setup.py py2app
#    生成的 app 会在 dist/ 中
# 额外提示：
# - 在 macOS 上分发时通常需要代码签名和 notarization（尤其在 macOS Catalina 之后）。
# - 如果你想把资源（图标、外部文件）打包进 app，参考 py2app 或 pyinstaller 的 --add-data 参数。
# - 本地测试时，请优先在目标 mac 上运行打包生成的 app，确认无缺失的 Tcl/Tk

