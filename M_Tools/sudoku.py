"""
sudoku_game.py

带 UI 的数独游戏（Tkinter + Canvas）
功能：
- Canvas 绘制更美观的棋盘
- 高亮当前行/列/宫
- 回溯法求解器（用于生成、提示与验证）
- 计时器、难度选择、新游戏、检查、求解、提示

运行方式：python sudoku_game.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

# ---------- 数独算法（回溯求解 + 生成） ----------

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None


def valid(board, row, col, val):
    # 检查行
    for c in range(9):
        if board[row][c] == val:
            return False
    # 检查列
    for r in range(9):
        if board[r][col] == val:
            return False
    # 检查 3x3 宫
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


def generate_full_board():
    # 生成完整解：先用随机排列的数字填充第一行，然后回溯求解
    board = [[0]*9 for _ in range(9)]
    nums = list(range(1, 10))
    random.shuffle(nums)
    # 随机填充对角线 3x3，能加速生成
    for k in range(3):
        br = k*3
        bc = k*3
        block = nums[:]  # reuse shuffled list
        random.shuffle(block)
        idx = 0
        for r in range(br, br+3):
            for c in range(bc, bc+3):
                board[r][c] = block[idx]
                idx += 1
    # 使用回溯完成剩余
    solve_backtrack(board)
    return board


def make_puzzle(full_board, empties):
    # 从完整解复制并挖空 'empties' 个格子
    board = [row[:] for row in full_board]
    coords = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(coords)
    removed = 0
    for r, c in coords:
        if removed >= empties:
            break
        # 暂时移除并检测解的唯一性（这里为了效率不验证唯一解，常见做法是移除后检查是否仍有单一解）
        board[r][c] = 0
        removed += 1
    return board

# ---------- UI ----------

CELL_SIZE = 60
GRID_PADDING = 20
BOARD_SIZE = CELL_SIZE*9
HIGHLIGHT_COLOR = '#eaf2ff'
SELECT_COLOR = '#d0e8ff'
FIXED_COLOR = '#000000'
USER_COLOR = '#1b5e20'
ERROR_COLOR = '#ff6666'
LINE_COLOR = '#333333'


class SudokuApp:
    def __init__(self, master):
        self.master = master
        master.title('数独 — 带 UI 的练手项目')
        master.resizable(False, False)

        self.full_board = generate_full_board()
        # 默认中等难度：empties 45
        self.difficulty_map = {'简单': 30, '中等': 45, '困难': 55}
        self.difficulty = '中等'
        self.reset_puzzle()

        self.selected = (0, 0)
        self.start_time = None
        self.elapsed = 0
        self.running = False

        self.build_ui()
        self.draw_board()
        self.start_timer()

    def reset_puzzle(self):
        self.full_board = generate_full_board()
        empties = self.difficulty_map.get(self.difficulty, 45)
        self.puzzle = make_puzzle(self.full_board, empties)
        # 固定格子标记
        self.fixed = [[(self.puzzle[r][c] != 0) for c in range(9)] for r in range(9)]
        # 当前用户填写的状态（含0）
        self.board = [row[:] for row in self.puzzle]

    def build_ui(self):
        # 左侧 Canvas
        self.canvas = tk.Canvas(self.master, width=BOARD_SIZE+GRID_PADDING*2,
                                height=BOARD_SIZE+GRID_PADDING*2, bg='white')
        self.canvas.grid(row=0, column=0, rowspan=6, padx=10, pady=10)
        self.canvas.bind('<Button-1>', self.on_click)
        self.master.bind('<Key>', self.on_key)

        # 右侧控件
        control_frame = tk.Frame(self.master)
        control_frame.grid(row=0, column=1, sticky='n')

        # 难度
        tk.Label(control_frame, text='难度').grid(row=0, column=0, pady=(6,0))
        self.diff_var = tk.StringVar(value=self.difficulty)
        diff_menu = ttk.Combobox(control_frame, textvariable=self.diff_var, values=list(self.difficulty_map.keys()), state='readonly')
        diff_menu.grid(row=1, column=0)
        diff_menu.bind('<<ComboboxSelected>>', self.change_difficulty)

        # 按钮
        btn_frame = tk.Frame(control_frame)
        btn_frame.grid(row=2, column=0, pady=8)
        ttk.Button(btn_frame, text='新游戏', command=self.new_game).grid(row=0, column=0, sticky='we', pady=2)
        ttk.Button(btn_frame, text='检查答案', command=self.check_solution).grid(row=1, column=0, sticky='we', pady=2)
        ttk.Button(btn_frame, text='求解（填满）', command=self.solve_and_show).grid(row=2, column=0, sticky='we', pady=2)
        ttk.Button(btn_frame, text='提示（填一个格）', command=self.hint_one).grid(row=3, column=0, sticky='we', pady=2)
        ttk.Button(btn_frame, text='重置当前答案', command=self.reset_user_entries).grid(row=4, column=0, sticky='we', pady=2)

        # 计时器
        self.timer_label = tk.Label(control_frame, text='用时: 00:00', font=('Arial', 12))
        self.timer_label.grid(row=3, column=0, pady=(12, 0))

        # 说明
        note = tk.Label(control_frame, text='操作说明:\n点击格子选择，键盘数字1-9输入，Backspace清除。', justify='left')
        note.grid(row=4, column=0, pady=(12,0))

    def draw_board(self):
        self.canvas.delete('all')
        off = GRID_PADDING
        # 背景高亮（行/列/宫）
        self.draw_highlight()

        # 网格线
        for i in range(10):
            w = 3 if i % 3 == 0 else 1
            x0 = off + i*CELL_SIZE
            y0 = off
            x1 = off + i*CELL_SIZE
            y1 = off + 9*CELL_SIZE
            self.canvas.create_line(x0, y0, x1, y1, width=w, fill=LINE_COLOR)
            y0 = off + i*CELL_SIZE
            x0 = off
            y1 = off + i*CELL_SIZE
            x1 = off + 9*CELL_SIZE
            self.canvas.create_line(x0, y0, x1, y1, width=w, fill=LINE_COLOR)

        # 数字
        for r in range(9):
            for c in range(9):
                x = off + c*CELL_SIZE + CELL_SIZE/2
                y = off + r*CELL_SIZE + CELL_SIZE/2
                val = self.board[r][c]
                if val != 0:
                    if self.fixed[r][c]:
                        color = FIXED_COLOR
                        font = ('Helvetica', 18, 'bold')
                    else:
                        color = USER_COLOR
                        font = ('Helvetica', 18)
                    self.canvas.create_text(x, y, text=str(val), font=font, fill=color)

        # 选中格子边框
        sr, sc = self.selected
        x0 = off + sc*CELL_SIZE
        y0 = off + sr*CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        self.canvas.create_rectangle(x0, y0, x1, y1, outline=SELECT_COLOR, width=3)

    def draw_highlight(self):
        off = GRID_PADDING
        r, c = self.selected
        # 行高亮
        self.canvas.create_rectangle(off, off + r*CELL_SIZE, off + 9*CELL_SIZE, off + (r+1)*CELL_SIZE, fill=HIGHLIGHT_COLOR, width=0)
        # 列高亮
        self.canvas.create_rectangle(off + c*CELL_SIZE, off, off + (c+1)*CELL_SIZE, off + 9*CELL_SIZE, fill=HIGHLIGHT_COLOR, width=0)
        # 宫高亮
        br = (r//3)*3
        bc = (c//3)*3
        self.canvas.create_rectangle(off + bc*CELL_SIZE, off + br*CELL_SIZE, off + (bc+3)*CELL_SIZE, off + (br+3)*CELL_SIZE, fill=HIGHLIGHT_COLOR, width=0)

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
            self.board[r][c] = 0
            self.draw_board()
            return
        if key in [str(i) for i in range(1, 10)]:
            val = int(key)
            if valid(self.board, r, c, val):
                self.board[r][c] = val
            else:
                # 允许填入，但以红色提示短暂闪烁
                self.board[r][c] = val
                self.flash_cell_error(r, c)
            self.draw_board()
            # 如果完成了，停表并弹窗
            if self.is_complete():
                self.stop_timer()
                if self.board == self.full_board:
                    messagebox.showinfo('完成', f'恭喜！你完成了数独，用时 {self.format_time(self.elapsed)}')
                else:
                    messagebox.showinfo('提示', '看起来已填满，但答案可能不正确。')

    def flash_cell_error(self, r, c):
        off = GRID_PADDING
        x0 = off + c*CELL_SIZE
        y0 = off + r*CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=ERROR_COLOR)
        self.master.after(200, lambda: (self.canvas.delete(rect), self.draw_board()))

    def new_game(self):
        self.reset_puzzle()
        self.selected = (0, 0)
        self.elapsed = 0
        self.start_time = time.time()
        self.running = True
        self.draw_board()

    def change_difficulty(self, event=None):
        val = self.diff_var.get()
        if val in self.difficulty_map:
            self.difficulty = val
            self.new_game()

    def check_solution(self):
        # 判断填入是否与 full_board 一致
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    messagebox.showwarning('检查', '还有空格未填写。')
                    return
        # 检查规则
        for r in range(9):
            if len(set(self.board[r])) != 9:
                messagebox.showwarning('检查', '第 %d 行有重复。' % (r+1))
                return
        for c in range(9):
            col = [self.board[r][c] for r in range(9)]
            if len(set(col)) != 9:
                messagebox.showwarning('检查', '第 %d 列有重复。' % (c+1))
                return
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                block = [self.board[r][c] for r in range(br, br+3) for c in range(bc, bc+3)]
                if len(set(block)) != 9:
                    messagebox.showwarning('检查', '有宫内重复。')
                    return
        # 最后与完整解比对
        if self.board == self.full_board:
            self.stop_timer()
            messagebox.showinfo('检查', '恭喜！数独正确完成。')
        else:
            messagebox.showwarning('检查', '规则通过，但答案与生成解不一致（可能存在多个解）。')

    def solve_and_show(self):
        # 直接填入完整解
        if not messagebox.askyesno('求解', '确定要显示完整解吗？这会视为放弃本题。'):
            return
        self.board = [row[:] for row in self.full_board]
        self.draw_board()
        self.stop_timer()

    def hint_one(self):
        # 在一个空或错误位置填入一个正确数字
        # 优先填空格
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    self.board[r][c] = self.full_board[r][c]
                    self.draw_board()
                    return
        # 若无空格，寻找与解不符的位置
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != self.full_board[r][c]:
                    self.board[r][c] = self.full_board[r][c]
                    self.draw_board()
                    return
        messagebox.showinfo('提示', '没有可提示的格子。')

    def reset_user_entries(self):
        # 恢复为初始 puzzle
        self.board = [row[:] for row in self.puzzle]
        self.draw_board()

    def is_complete(self):
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    return False
        return True

    # 计时器方法
    def start_timer(self):
        if self.start_time is None:
            self.start_time = time.time()
        self.running = True
        self._tick()

    def _tick(self):
        if not self.running:
            return
        self.elapsed = int(time.time() - self.start_time)
        self.timer_label.config(text='用时: ' + self.format_time(self.elapsed))
        self.master.after(1000, self._tick)

    def stop_timer(self):
        self.running = False

    def format_time(self, secs):
        m = secs // 60
        s = secs % 60
        return f"{m:02d}:{s:02d}"


if __name__ == '__main__':
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()
