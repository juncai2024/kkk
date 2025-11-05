import pygame
import json
import sys
import tkinter as tk
from tkinter import filedialog
from typing import List, Tuple, Dict, Optional

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 100, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
LIME = (0, 255, 128)
TEAL = (0, 128, 128)
PINK = (255, 192, 203)
MAROON = (128, 0, 0)
NAVY = (0, 0, 128)
OLIVE = (128, 128, 0)

# 线条颜色列表
LINE_COLORS = [BLUE, GREEN, PURPLE, ORANGE, CYAN, MAGENTA, LIME, TEAL, PINK, MAROON, NAVY, OLIVE]


class MapEditor:
    def __init__(self):
        pygame.init()

        # 初始化变量
        self.grid_width = 10
        self.grid_height = 10
        self.cell_size = 40
        self.start_color = RED
        self.default_color = GREEN

        # 计算窗口大小
        self.sidebar_width = 250
        self.window_width = self.grid_width * self.cell_size + self.sidebar_width
        self.window_height = max(self.grid_height * self.cell_size, 450)
        self.min_window_width = 600
        self.min_window_height = 450

        # 创建可调整大小的窗口
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)

        # 初始化字体
        self.font = self.get_system_font()
        self.small_font = self.get_system_font(size=16)

        # 初始化网格数据
        self.grid: List[List[int]] = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        # 线条数据格式: {线编号: {"points": [(x,y), ...], "numbers": [0,1,2,...]}}
        self.lines: Dict[int, Dict] = {}
        self.current_line: List[Tuple[int, int]] = []
        self.dragging = False
        self.selected_start: Optional[Tuple[int, int]] = None
        self.next_line_id = 0  # 下一条线的编号

        # 临时消息变量
        self.temp_message = None
        self.message_time = 0

        # 橡皮擦模式
        self.eraser_mode = False

        # 创建UI元素
        self.create_ui_elements()

        # 设置窗口标题
        self.set_window_caption()

    def get_system_font(self, size=24):
        """获取系统字体，优先支持中文"""
        try:
            # 尝试使用常见的中文字体
            font = pygame.font.SysFont(["SimHei", "Microsoft YaHei", "WenQuanYi Zen Hei", "Arial", "sans-serif"], size)
            # 测试字体渲染
            test_surface = font.render("测试", True, WHITE)
            if test_surface.get_width() > 0:
                return font
        except:
            pass

        #  fallback到默认字体
        return pygame.font.Font(None, size)

    def create_ui_elements(self):
        """创建UI元素"""
        # 网格大小输入框 - 位置在右侧面板
        sidebar_x = self.grid_width * self.cell_size
        self.width_input = InputBox(sidebar_x + 10, 30, 80, 30, str(self.grid_width))
        self.height_input = InputBox(sidebar_x + 100, 30, 80, 30, str(self.grid_height))

        # 按钮 - 位置在右侧面板
        self.apply_button = Button(sidebar_x + 10, 70, 230, 30,
                                   self.get_localized_text("应用网格大小", "Apply Grid Size"))
        self.clear_button = Button(sidebar_x + 10, 110, 230, 30,
                                   self.get_localized_text("清除所有线条", "Clear All Lines"))
        self.export_button = Button(sidebar_x + 10, 150, 230, 30,
                                    self.get_localized_text("导出为JSON", "Export to JSON"))
        self.import_button = Button(sidebar_x + 10, 190, 230, 30,
                                    self.get_localized_text("导入JSON", "Import JSON"))
        self.eraser_button = Button(sidebar_x + 10, 230, 230, 30, self.get_localized_text("橡皮擦模式", "Eraser Mode"))

        # 标签 - 位置在右侧面板
        self.width_label = self.font.render(self.get_localized_text("宽度:", "Width:"), True, WHITE)
        self.height_label = self.font.render(self.get_localized_text("高度:", "Height:"), True, WHITE)
        self.info_label = self.font.render(self.get_localized_text("操作说明:", "Instructions:"), True, WHITE)
        self.info1_label = self.font.render(self.get_localized_text("- 拖动鼠标绘制线条", "- Drag to draw lines"), True,
                                            LIGHT_GRAY)
        self.info2_label = self.font.render(
            self.get_localized_text("- 点击线条端点设置起点", "- Click endpoints to set start"), True, LIGHT_GRAY)
        self.info3_label = self.font.render(
            self.get_localized_text("- 起点(1)：红色，不同线条不同颜色", "- Start(1): Red, Different colors for lines"), True,
            LIGHT_GRAY)
        self.info4_label = self.font.render(
            self.get_localized_text("- 橡皮擦模式下点击删除线条", "- Click to erase lines in Eraser Mode"), True,
            LIGHT_GRAY)
        self.info5_label = self.font.render(
            self.get_localized_text("- 格子显示坐标和编号", "- Cells show coordinates & numbers"), True, LIGHT_GRAY)
        self.info6_label = self.font.render(
            self.get_localized_text("- 可导入之前导出的JSON文件", "- Can import previously exported JSON files"), True,
            LIGHT_GRAY)

    def get_localized_text(self, chinese_text, english_text):
        """获取本地化文本，如果中文显示有问题则使用英文"""
        # 测试中文字体是否能正常渲染
        test_surface = self.font.render(chinese_text, True, WHITE)
        if test_surface.get_width() > 0 and not self.is_text_gibberish(chinese_text, test_surface):
            return chinese_text
        else:
            return english_text

    def is_text_gibberish(self, text, surface):
        """检测文本是否显示为乱码（方块）"""
        avg_char_width = surface.get_width() / max(1, len(text))
        return avg_char_width < 5  # 假设正常字符宽度至少为5像素

    def draw_grid(self):
        """绘制网格，包含坐标和编号"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, GRAY, rect, 1)

                # 绘制网格内容
                value = self.grid[y][x]
                if value == 1:
                    pygame.draw.rect(self.screen, self.start_color, rect)
                elif value == 2:
                    # 查找该单元格所属的线条ID，使用对应的线条颜色
                    line_id, _ = self.get_line_info((x, y))
                    if line_id is not None:
                        # 使用线条ID从颜色列表中选择颜色，如果颜色列表不够则循环使用
                        color_index = line_id % len(LINE_COLORS)
                        pygame.draw.rect(self.screen, LINE_COLORS[color_index], rect)
                    else:
                        pygame.draw.rect(self.screen, self.default_color, rect)

                # 绘制网格坐标 x,y
                coord_text = f"{x},{y}"
                # 创建比small_font小1个字号的字体
                smaller_font = self.get_system_font(size=15)
                coord_surface = smaller_font.render(coord_text, True, BLACK)
                self.screen.blit(coord_surface, (x * self.cell_size + 2, y * self.cell_size + 2))

                # 绘制线条编号（如果有）
                line_id, point_num = self.get_line_info((x, y))
                if line_id is not None and point_num is not None:
                    # 线条ID从1开始显示，点编号从1开始显示
                    num_text = f"#{line_id + 1}-{point_num + 1}"
                    num_surface = self.small_font.render(num_text, True, BLACK)
                    # 显示在格子右下角
                    self.screen.blit(num_surface, (x * self.cell_size + 5, y * self.cell_size + self.cell_size - 20))

    def get_line_info(self, cell: Tuple[int, int]) -> Tuple[Optional[int], Optional[int]]:
        """获取单元格所属的线条ID和点编号"""
        x, y = cell
        for line_id, line_data in self.lines.items():
            if cell in line_data["points"]:
                idx = line_data["points"].index(cell)
                return line_id, line_data["numbers"][idx]
        return None, None

    def draw_sidebar(self):
        """绘制侧边栏"""
        sidebar_x = self.grid_width * self.cell_size

        # 绘制侧边栏背景
        sidebar_rect = pygame.Rect(sidebar_x, 0, self.sidebar_width, self.window_height)
        pygame.draw.rect(self.screen, BLACK, sidebar_rect)

        # 绘制标签
        self.screen.blit(self.width_label, (sidebar_x + 10, 10))
        self.screen.blit(self.height_label, (sidebar_x + 90, 10))
        self.screen.blit(self.info_label, (sidebar_x + 10, 270))
        self.screen.blit(self.info1_label, (sidebar_x + 10, 300))
        self.screen.blit(self.info2_label, (sidebar_x + 10, 330))
        self.screen.blit(self.info3_label, (sidebar_x + 10, 360))
        self.screen.blit(self.info4_label, (sidebar_x + 10, 390))
        self.screen.blit(self.info5_label, (sidebar_x + 10, 420))
        self.screen.blit(self.info6_label, (sidebar_x + 10, 450))

        # 绘制输入框
        self.width_input.draw(self.screen)
        self.height_input.draw(self.screen)

        # 绘制按钮
        self.apply_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        self.export_button.draw(self.screen)
        self.import_button.draw(self.screen)

        # 绘制橡皮擦按钮，根据模式显示不同颜色
        if self.eraser_mode:
            self.eraser_button.color = RED
            self.eraser_button.hover_color = (255, 100, 100)
        else:
            self.eraser_button.color = GRAY
            self.eraser_button.hover_color = LIGHT_GRAY
        self.eraser_button.draw(self.screen)

        # 绘制当前线条信息
        if self.current_line:
            line_info = self.get_localized_text(f"当前线条: {len(self.current_line)}个格子",
                                                f"Current Line: {len(self.current_line)} cells")
            line_surface = self.font.render(line_info, True, WHITE)
            self.screen.blit(line_surface, (sidebar_x + 10, 410))

        # 绘制总线条信息
        total_lines = len(self.lines)
        lines_info = self.get_localized_text(f"总线条数: {total_lines}",
                                             f"Total Lines: {total_lines}")
        lines_surface = self.font.render(lines_info, True, WHITE)
        self.screen.blit(lines_surface, (sidebar_x + 10, 440))

    def get_cell_at_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """根据鼠标位置获取网格坐标"""
        x, y = pos
        if x < 0 or x >= self.grid_width * self.cell_size or y < 0 or y >= self.grid_height * self.cell_size:
            return None
        return (x // self.cell_size, y // self.cell_size)

    def start_new_line(self, cell: Tuple[int, int]):
        """开始绘制新线条"""
        self.current_line = [cell]
        self.grid[cell[1]][cell[0]] = 2
        self.dragging = True

    def add_point_to_line(self, cell: Tuple[int, int]):
        """向当前线条添加点"""
        if cell not in self.current_line:
            # 检查是否与已有线条重叠（除了端点）
            if len(self.current_line) > 1 and self.grid[cell[1]][cell[0]] == 2:
                # 找到最近的端点并连接
                for line_id, line_data in list(self.lines.items()):
                    if cell in line_data["points"]:
                        # 合并线条
                        line_points = line_data["points"]
                        if line_points[0] == cell:
                            self.current_line = line_points + self.current_line[1:]
                        else:
                            self.current_line += line_points[1:]
                        del self.lines[line_id]
                        break

            self.current_line.append(cell)
            self.grid[cell[1]][cell[0]] = 2

    def end_line(self):
        """结束当前线条绘制，分配编号（复用已删除线条的编号）"""
        if len(self.current_line) >= 2:
            # 找到最小的未使用编号
            used_ids = set(self.lines.keys())
            new_line_id = 0
            while new_line_id in used_ids:
                new_line_id += 1
            
            # 为新线条创建编号（从0开始）
            line_numbers = list(range(len(self.current_line)))
            # 存储线条数据，包含点坐标和编号
            self.lines[new_line_id] = {
                "points": self.current_line.copy(),
                "numbers": line_numbers
            }
            # 更新next_line_id，但不影响编号复用逻辑
            if new_line_id >= self.next_line_id:
                self.next_line_id = new_line_id + 1
        else:
            # 如果线条只有一个点，清除它
            if self.current_line:
                x, y = self.current_line[0]
                self.grid[y][x] = 0
        self.current_line = []
        self.dragging = False

    def set_window_caption(self):
        """设置窗口标题"""
        caption = self.get_localized_text("简单地图编辑器", "Map Editor")
        pygame.display.set_caption(caption)

    def set_start_point(self, cell: Tuple[int, int]):
        """设置起点（属性1）"""
        # 找到包含该单元格的线条
        line_id = None
        point_index = -1

        for lid, line_data in self.lines.items():
            if cell in line_data["points"]:
                line_id = lid
                point_index = line_data["points"].index(cell)
                break

        if line_id is None:
            return

        line_points = self.lines[line_id]["points"]

        # 检查是否是端点
        if point_index != 0 and point_index != len(line_points) - 1:
            return

        # 清除当前线条的起点
        for x, y in line_points:
            if self.grid[y][x] == 1:
                self.grid[y][x] = 2

        # 设置新起点
        x, y = cell
        self.grid[y][x] = 1
        self.selected_start = cell

    def clear_all(self):
        """清除所有线条"""
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.lines = {}
        self.current_line = []
        self.selected_start = None
        self.next_line_id = 0  # 重置线条编号
        # 如果在橡皮擦模式，退出橡皮擦模式
        if self.eraser_mode:
            self.eraser_mode = False

    def erase_cell(self, cell: Tuple[int, int]):
        """擦除包含该单元格的线条"""
        x, y = cell

        # 如果单元格没有线条，直接返回
        if self.grid[y][x] == 0:
            return

        # 找到包含该单元格的线条
        line_to_remove = None
        for line_id, line_data in self.lines.items():
            if cell in line_data["points"]:
                line_to_remove = line_id
                break

        if line_to_remove is not None:
            # 清除该线条的所有格子
            for px, py in self.lines[line_to_remove]["points"]:
                self.grid[py][px] = 0

            # 移除线条
            del self.lines[line_to_remove]

            # 如果删除的是起点，清除选中的起点
            if self.selected_start == cell:
                self.selected_start = None

            # 显示提示信息
            erase_msg = self.get_localized_text("已擦除线条", "Line erased")
            self.show_temp_message(erase_msg, 500)

    def export_to_json(self):
        """导出为JSON文件，让用户选择保存路径和文件名"""
        # 准备导出数据 - 包含所有网格单元格
        export_data = []

        for y in range(self.grid_height):
            for x in range(self.grid_width):
                cell_data = {
                    "x": x,
                    "y": y,
                    "id": 0,  # 0表示未被线条占用
                    "nodeIndex": -1  # -1表示未被线条占用
                }

                # 检查该单元格是否被线条占用
                line_id, point_num = self.get_line_info((x, y))
                if line_id is not None and point_num is not None:
                    # id从1开始计算（原线条ID+1）
                    cell_data["id"] = line_id + 1
                    # nodeIndex从1开始计算（原点编号+1）
                    cell_data["nodeIndex"] = point_num + 1

                export_data.append(cell_data)

        try:
            # 创建一个临时的Tkinter根窗口并隐藏它
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 设置窗口为前台窗口
            root.attributes('-topmost', True)
            
            # 打开文件保存对话框
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*")],
                title=self.get_localized_text("保存地图数据", "Save Map Data"),
                initialfile="map_data.json"
            )
            
            # 关闭Tkinter窗口
            root.destroy()
            
            # 如果用户选择了文件路径
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)

                # 显示导出成功提示
                success_msg = self.get_localized_text(f"地图数据已导出到 {file_path}",
                                                    f"Map data exported to {file_path}")
                print(success_msg)
                self.show_temp_message(success_msg, 2000)
            else:
                # 用户取消了保存操作
                cancel_msg = self.get_localized_text("导出操作已取消", "Export operation cancelled")
                print(cancel_msg)

        except Exception as e:
            error_msg = self.get_localized_text(f"导出失败: {e}", f"Export failed: {e}")
            print(error_msg)
            self.show_temp_message(error_msg, 3000)
            
    def import_from_json(self):
        """从JSON文件导入地图数据"""
        try:
            # 使用pygame的文件对话框选择文件
            import tkinter as tk
            from tkinter import filedialog
            
            # 创建一个隐藏的Tk窗口
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            # 打开文件选择对话框
            file_path = filedialog.askopenfilename(
                title=self.get_localized_text("选择地图JSON文件", "Select Map JSON File"),
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
            )
            
            # 如果用户取消选择，则返回
            if not file_path:
                return
            
            # 读取JSON文件
            with open(file_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)
            
            # 分析导入数据，确定网格大小
            max_x = 0
            max_y = 0
            for cell in import_data:
                max_x = max(max_x, cell["x"])
                max_y = max(max_y, cell["y"])
            
            # 调整网格大小
            new_width = max_x + 1
            new_height = max_y + 1
            
            # 重新设置网格
            self.grid_width = new_width
            self.grid_height = new_height
            
            # 重新计算窗口大小
            self.window_width = self.grid_width * self.cell_size + self.sidebar_width
            self.window_height = max(self.grid_height * self.cell_size, 450)
            
            # 重新创建窗口
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            
            # 重置数据
            self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
            self.lines = {}
            self.current_line = []
            self.selected_start = None
            self.next_line_id = 0
            
            # 重建UI元素
            self.create_ui_elements()
            
            # 按线条ID分组单元格数据
            line_cells = {}
            for cell in import_data:
                x, y = cell["x"], cell["y"]
                line_id = cell["id"] - 1  # 转回0开始的索引
                node_index = cell["nodeIndex"] - 1  # 转回0开始的索引
                
                if line_id >= 0:
                    if line_id not in line_cells:
                        line_cells[line_id] = []
                    line_cells[line_id].append((x, y, node_index))
            
            # 重建线条数据
            for line_id, cells in line_cells.items():
                # 按nodeIndex排序，确保点的顺序正确
                cells.sort(key=lambda c: c[2])
                
                # 提取点坐标和编号
                points = [(x, y) for x, y, _ in cells]
                numbers = [i for _, _, i in cells]
                
                # 存储线条数据
                self.lines[line_id] = {
                    "points": points,
                    "numbers": numbers
                }
                
                # 更新网格数据
                for x, y, _ in cells:
                    self.grid[y][x] = 2
                
                # 如果线条不为空，将第一个点设为起点
                if points:
                    start_x, start_y = points[0]
                    self.grid[start_y][start_x] = 1
                    self.selected_start = (start_x, start_y)
                
                # 更新下一个线条ID
                self.next_line_id = max(self.next_line_id, line_id + 1)
            
            # 显示导入成功提示
            success_msg = self.get_localized_text(f"成功导入地图数据，网格大小: {new_width}x{new_height}",
                                                  f"Successfully imported map data, grid size: {new_width}x{new_height}")
            print(success_msg)
            self.show_temp_message(success_msg, 2000)
            
        except json.JSONDecodeError:
            error_msg = self.get_localized_text("JSON文件格式错误", "Invalid JSON file format")
            print(error_msg)
            self.show_temp_message(error_msg, 3000)
        except Exception as e:
            error_msg = self.get_localized_text(f"导入失败: {e}", f"Import failed: {e}")
            print(error_msg)
            self.show_temp_message(error_msg, 3000)

    def resize_grid(self, width: int, height: int):
        """调整网格大小"""
        # 验证输入
        if width <= 0 or height <= 0:
            error_msg = self.get_localized_text("网格大小必须为正数", "Grid size must be positive")
            self.show_temp_message(error_msg, 2000)
            return

        # 更新网格大小
        self.grid_width = width
        self.grid_height = height

        # 重新创建网格数据
        # 保留已有的线条信息
        old_grid = self.grid
        old_lines = self.lines
        
        # 创建新的网格
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # 尝试将旧的线条信息复制到新的网格中（如果空间足够）
        for line_id, line_data in old_lines.items():
            points = line_data["points"]
            numbers = line_data["numbers"]
            
            # 检查所有点是否都在新的网格范围内
            all_points_valid = True
            for x, y in points:
                if x >= self.grid_width or y >= self.grid_height:
                    all_points_valid = False
                    break
            
            if all_points_valid:
                # 如果所有点都有效，保留这条线
                self.lines[line_id] = line_data
                # 更新网格
                for i, (x, y) in enumerate(points):
                    # 起点标记为1，其他点标记为2
                    self.grid[y][x] = 1 if i == 0 else 2
        
        # 重新计算窗口大小
        new_width = self.grid_width * self.cell_size + self.sidebar_width
        new_height = max(self.grid_height * self.cell_size, 450)
        
        # 确保窗口不小于最小尺寸
        self.window_width = max(new_width, self.min_window_width)
        self.window_height = max(new_height, self.min_window_height)

        # 重新创建可调整大小的窗口
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)

        # 重置当前线条和选择的起点
        self.current_line = []
        self.selected_start = None
        
        # 重新计算下一个可用的线条ID
        if self.lines:
            # 查找最小的未使用ID
            used_ids = set(self.lines.keys())
            self.next_line_id = 0
            while self.next_line_id in used_ids:
                self.next_line_id += 1
        else:
            self.next_line_id = 0

        # 重新创建UI元素
        self.create_ui_elements()

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # 处理窗口调整大小事件
            elif event.type == pygame.VIDEORESIZE:
                # 确保窗口不小于最小尺寸
                new_width = max(event.w, self.min_window_width)
                new_height = max(event.h, self.min_window_height)
                
                # 重新计算单元格大小以适应新窗口
                available_width = new_width - self.sidebar_width
                self.cell_size = min(available_width // self.grid_width, new_height // self.grid_height)
                # 确保单元格大小至少为10
                self.cell_size = max(self.cell_size, 10)
                
                # 更新窗口大小
                self.window_width = new_width
                self.window_height = new_height
                
                # 重新创建窗口
                self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                
                # 重新创建UI元素以适应新的窗口大小
                self.create_ui_elements()

            # 处理输入框事件
            self.width_input.handle_event(event)
            self.height_input.handle_event(event)

            # 处理按钮点击
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    pos = pygame.mouse.get_pos()

                    # 检查是否点击了侧边栏按钮
                    if self.apply_button.is_clicked(pos):
                        try:
                            width = int(self.width_input.text)
                            height = int(self.height_input.text)
                            self.resize_grid(width, height)
                        except ValueError:
                            error_msg = self.get_localized_text("请输入有效的数字", "Please enter valid numbers")
                            self.show_temp_message(error_msg, 2000)

                    elif self.clear_button.is_clicked(pos):
                        self.clear_all()

                    elif self.export_button.is_clicked(pos):
                        self.export_to_json()
                        
                    elif self.import_button.is_clicked(pos):
                        self.import_from_json()

                    elif self.eraser_button.is_clicked(pos):
                        self.eraser_mode = not self.eraser_mode
                        mode_msg = self.get_localized_text("橡皮擦模式已开启",
                                                           "Eraser mode enabled") if self.eraser_mode else \
                            self.get_localized_text("橡皮擦模式已关闭", "Eraser mode disabled")
                        self.show_temp_message(mode_msg, 1000)

                    else:
                        # 检查是否点击了网格
                        cell = self.get_cell_at_pos(pos)
                        if cell:
                            x, y = cell

                            # 如果在橡皮擦模式下
                            if self.eraser_mode:
                                self.erase_cell(cell)
                            else:
                                # 如果点击了已有线条的端点，设置为起点
                                if self.grid[y][x] == 2:
                                    self.set_start_point(cell)
                                elif self.grid[y][x] == 1:
                                    # 如果点击了已有的起点，清除它
                                    self.grid[y][x] = 2
                                    self.selected_start = None
                                else:
                                    # 开始绘制新线条
                                    self.start_new_line(cell)

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    current_cell = self.get_cell_at_pos(event.pos)
                    if current_cell:
                        last_cell = self.current_line[-1]
                        # 如果鼠标移动到了新单元格
                        if current_cell != last_cell:
                            # 计算当前单元格和上一个单元格之间的所有单元格
                            last_x, last_y = last_cell
                            curr_x, curr_y = current_cell
                            
                            # 处理水平或垂直移动的情况
                            if last_x == curr_x:  # 垂直移动
                                step = 1 if curr_y > last_y else -1
                                for y in range(last_y + step, curr_y + step, step):
                                    self.add_point_to_line((last_x, y))
                            elif last_y == curr_y:  # 水平移动
                                step = 1 if curr_x > last_x else -1
                                for x in range(last_x + step, curr_x + step, step):
                                    self.add_point_to_line((x, last_y))
                            else:
                                # 对于对角线移动，仍然只添加目标单元格
                                # 这样可以避免意外添加不必要的单元格
                                self.add_point_to_line(current_cell)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    self.end_line()

        return True

    def show_temp_message(self, message, duration=2000):
        """显示临时消息"""
        self.temp_message = message
        self.message_time = pygame.time.get_ticks() + duration

    def draw_temp_message(self):
        """绘制临时消息"""
        if self.temp_message and pygame.time.get_ticks() < self.message_time:
            text_surface = self.font.render(self.temp_message, True, WHITE)
            text_rect = text_surface.get_rect(center=(self.window_width // 2, self.window_height // 2))

            # 绘制半透明背景
            bg_rect = pygame.Rect(text_rect.x - 10, text_rect.y - 5, text_rect.width + 20, text_rect.height + 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=5)

            # 绘制文本
            self.screen.blit(text_surface, text_rect)
        else:
            self.temp_message = None

    def run(self):
        """运行编辑器"""
        running = True
        while running:
            self.screen.fill(WHITE)

            # 绘制网格
            self.draw_grid()

            # 绘制侧边栏
            self.draw_sidebar()

            # 绘制临时消息
            self.draw_temp_message()

            # 处理事件
            running = self.handle_events()

            # 更新显示
            pygame.display.flip()

        pygame.quit()


class InputBox:
    def __init__(self, x, y, width, height, initial_text=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = LIGHT_GRAY
        self.text = initial_text
        # 使用系统字体支持中文
        self.font = self.get_system_font()
        self.txt_surface = self.font.render(self.text, True, BLACK)
        self.active = False

    def get_system_font(self):
        """获取系统字体，优先支持中文"""
        try:
            return pygame.font.SysFont(["SimHei", "Microsoft YaHei", "WenQuanYi Zen Hei", "Arial"], 24)
        except:
            return pygame.font.Font(None, 24)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 如果点击了输入框，激活它
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # 更改颜色以指示活动状态
            self.color = RED if self.active else LIGHT_GRAY

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False
                    self.color = LIGHT_GRAY
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # 更新文本表面
                self.txt_surface = self.font.render(self.text, True, BLACK)

    def draw(self, screen):
        # 绘制输入框背景
        pygame.draw.rect(screen, self.color, self.rect)
        # 绘制文本
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # 绘制边框
        pygame.draw.rect(screen, BLACK, self.rect, 2)


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = GRAY
        self.hover_color = LIGHT_GRAY
        self.text = text
        # 使用系统字体支持中文
        self.font = self.get_system_font()
        self.txt_surface = self.font.render(text, True, WHITE)

    def get_system_font(self):
        """获取系统字体，优先支持中文"""
        try:
            return pygame.font.SysFont(["SimHei", "Microsoft YaHei", "WenQuanYi Zen Hei", "Arial"], 24)
        except:
            return pygame.font.Font(None, 24)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, screen):
        # 检查鼠标是否悬停在按钮上
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        # 绘制文本
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)

        # 绘制边框
        pygame.draw.rect(screen, BLACK, self.rect, 2)


if __name__ == "__main__":
    editor = MapEditor()
    editor.run()
