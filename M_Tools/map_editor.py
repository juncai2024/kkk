import pygame
import json
import sys
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


class MapEditor:
    def __init__(self):
        pygame.init()

        # 初始化变量
        self.grid_width = 10
        self.grid_height = 10
        self.cell_size = 40
        self.line_color = BLUE
        self.start_color = RED
        self.default_color = GREEN

        # 计算窗口大小
        self.sidebar_width = 250
        self.window_width = self.grid_width * self.cell_size + self.sidebar_width
        self.window_height = max(self.grid_height * self.cell_size, 450)

        # 创建窗口
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))

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
        self.eraser_button = Button(sidebar_x + 10, 190, 230, 30, self.get_localized_text("橡皮擦模式", "Eraser Mode"))

        # 标签 - 位置在右侧面板
        self.width_label = self.font.render(self.get_localized_text("宽度:", "Width:"), True, WHITE)
        self.height_label = self.font.render(self.get_localized_text("高度:", "Height:"), True, WHITE)
        self.info_label = self.font.render(self.get_localized_text("操作说明:", "Instructions:"), True, WHITE)
        self.info1_label = self.font.render(self.get_localized_text("- 拖动鼠标绘制线条", "- Drag to draw lines"), True,
                                            LIGHT_GRAY)
        self.info2_label = self.font.render(
            self.get_localized_text("- 点击线条端点设置起点", "- Click endpoints to set start"), True, LIGHT_GRAY)
        self.info3_label = self.font.render(
            self.get_localized_text("- 起点(1)：红色，默认(2)：绿色", "- Start(1): Red, Default(2): Green"), True,
            LIGHT_GRAY)
        self.info4_label = self.font.render(
            self.get_localized_text("- 橡皮擦模式下点击删除线条", "- Click to erase lines in Eraser Mode"), True,
            LIGHT_GRAY)
        self.info5_label = self.font.render(
            self.get_localized_text("- 格子显示坐标和编号", "- Cells show coordinates & numbers"), True, LIGHT_GRAY)

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
                    pygame.draw.rect(self.screen, self.default_color, rect)

                # 绘制网格坐标 (x,y)
                coord_text = f"({x},{y})"
                coord_surface = self.small_font.render(coord_text, True, BLACK)
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
        self.screen.blit(self.info_label, (sidebar_x + 10, 230))
        self.screen.blit(self.info1_label, (sidebar_x + 10, 260))
        self.screen.blit(self.info2_label, (sidebar_x + 10, 290))
        self.screen.blit(self.info3_label, (sidebar_x + 10, 320))
        self.screen.blit(self.info4_label, (sidebar_x + 10, 350))
        self.screen.blit(self.info5_label, (sidebar_x + 10, 380))

        # 绘制输入框
        self.width_input.draw(self.screen)
        self.height_input.draw(self.screen)

        # 绘制按钮
        self.apply_button.draw(self.screen)
        self.clear_button.draw(self.screen)
        self.export_button.draw(self.screen)

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
        """结束当前线条绘制，分配编号"""
        if len(self.current_line) >= 2:
            # 为新线条创建编号（从0开始）
            line_numbers = list(range(len(self.current_line)))
            # 存储线条数据，包含点坐标和编号
            self.lines[self.next_line_id] = {
                "points": self.current_line.copy(),
                "numbers": line_numbers
            }
            # 更新下一条线的编号
            self.next_line_id += 1
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
        """导出为JSON文件，按照指定格式"""
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
            with open("map_data.json", "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            # 显示导出成功提示
            success_msg = self.get_localized_text("地图数据已导出到 map_data.json",
                                                  "Map data exported to map_data.json")
            print(success_msg)
            self.show_temp_message(success_msg, 2000)

        except Exception as e:
            error_msg = self.get_localized_text(f"导出失败: {e}", f"Export failed: {e}")
            print(error_msg)
            self.show_temp_message(error_msg, 3000)

    def resize_grid(self, width: int, height: int):
        """调整网格大小"""
        if width <= 0 or height <= 0:
            error_msg = self.get_localized_text("请输入有效的数字", "Please enter valid numbers")
            self.show_temp_message(error_msg, 2000)
            return

        self.grid_width = width
        self.grid_height = height

        # 重新计算窗口大小
        self.window_width = self.grid_width * self.cell_size + self.sidebar_width
        self.window_height = max(self.grid_height * self.cell_size, 450)

        # 重新创建窗口
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))

        # 重置网格数据
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.lines = {}
        self.current_line = []
        self.selected_start = None
        self.next_line_id = 0  # 重置线条编号

        # 重新创建UI元素
        self.create_ui_elements()

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

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
                    cell = self.get_cell_at_pos(event.pos)
                    if cell and cell != self.current_line[-1]:
                        self.add_point_to_line(cell)

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
