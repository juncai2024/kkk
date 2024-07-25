import os
import pandas as pd
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.simpledialog as simpledialog

# 配置日志记录
logging.basicConfig(filename='file_operations.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# 全局变量，用于撤销操作
undo_stack = []


def add_prefix(folder_path, file_types, prefix):
    if file_types == ['1']:
        to_rename = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    else:
        to_rename = [f for f in os.listdir(folder_path) if
                     os.path.isfile(os.path.join(folder_path, f)) and f.split('.')[-1] in file_types]

    preview_changes(to_rename, prefix=prefix)
    if not confirm_action("确认要添加前缀吗？"):
        return

    for filename in to_rename:
        old_filepath = os.path.join(folder_path, filename)
        new_filename = prefix + filename
        new_filepath = os.path.join(folder_path, new_filename)
        rename_file(old_filepath, new_filepath)


def add_suffix(folder_path, file_types, suffix):
    if file_types == ['1']:
        to_rename = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    else:
        to_rename = [f for f in os.listdir(folder_path) if
                     os.path.isfile(os.path.join(folder_path, f)) and f.split('.')[-1] in file_types]

    preview_changes(to_rename, suffix=suffix)
    if not confirm_action("确认要添加后缀吗？"):
        return

    for filename in to_rename:
        old_filepath = os.path.join(folder_path, filename)
        filename_parts = os.path.splitext(filename)
        new_filename = filename_parts[0] + suffix + filename_parts[1]
        new_filepath = os.path.join(folder_path, new_filename)
        rename_file(old_filepath, new_filepath)


def rename_from_excel(folder_path, excel_path, file_types):
    df = pd.read_excel(excel_path)
    to_rename = df[['原文件名', '修改后文件名']].values.tolist()

    if file_types != ['1']:
        to_rename = [row for row in to_rename if row[0].split('.')[-1] in file_types]

    preview_changes([row[0] for row in to_rename], new_names=[row[1] for row in to_rename])
    if not confirm_action("确认要根据Excel文件重命名吗？"):
        return

    for old_filename, new_filename in to_rename:
        old_filepath = os.path.join(folder_path, old_filename)
        new_filepath = os.path.join(folder_path, new_filename)
        if os.path.exists(new_filepath):
            counter = 1
            while os.path.exists(new_filepath):
                name, extension = os.path.splitext(new_filename)
                new_filename = f"{name}_{counter}{extension}"
                new_filepath = os.path.join(folder_path, new_filename)
                counter += 1
        rename_file(old_filepath, new_filepath)


def remove_chars(folder_path, file_types, chars):
    if file_types == ['1']:
        to_rename = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    else:
        to_rename = [f for f in os.listdir(folder_path) if
                     os.path.isfile(os.path.join(folder_path, f)) and f.split('.')[-1] in file_types]

    preview_changes(to_rename, rm_chars=chars)
    if not confirm_action("确认要删除指定字符吗？"):
        return

    for filename in to_rename:
        old_filepath = os.path.join(folder_path, filename)
        new_filename = filename.replace(chars, '')
        new_filepath = os.path.join(folder_path, new_filename)
        rename_file(old_filepath, new_filepath)


def rename_file(old_filepath, new_filepath):
    try:
        os.rename(old_filepath, new_filepath)
        undo_stack.append((new_filepath, old_filepath))
        logging.info(f"Renamed: {old_filepath} to {new_filepath}")
    except Exception as e:
        logging.error(f"Error renaming {old_filepath} to {new_filepath}: {e}")


def preview_changes(file_list, prefix="", suffix="", rm_chars="", new_names=None):
    preview_text = "预览文件名更改：\n"
    for i, filename in enumerate(file_list):
        if new_names:
            new_filename = new_names[i]
        else:
            new_filename = prefix + filename.replace(rm_chars, '') + suffix
        preview_text += f"{filename} -> {new_filename}\n"
    messagebox.showinfo("预览", preview_text)


def confirm_action(prompt):
    return messagebox.askyesno("确认", prompt)


def undo_last_action():
    if not undo_stack:
        messagebox.showinfo("信息", "没有操作可以撤销。")
        return

    last_action = undo_stack.pop()
    try:
        os.rename(last_action[0], last_action[1])
        logging.info(f"Undo rename: {last_action[0]} to {last_action[1]}")
    except Exception as e:
        logging.error(f"Error undoing rename {last_action[0]} to {last_action[1]}: {e}")


def batch_modify_file_attributes(folder_path, file_types):
    if file_types == ['1']:
        to_modify = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    else:
        to_modify = [f for f in os.listdir(folder_path) if
                     os.path.isfile(os.path.join(folder_path, f)) and f.split('.')[-1] in file_types]

    for filename in to_modify:
        old_filepath = os.path.join(folder_path, filename)
        try:
            # 示例：修改文件权限为只读
            os.chmod(old_filepath, 0o444)
            logging.info(f"Changed attributes for: {old_filepath}")
        except Exception as e:
            logging.error(f"Error changing attributes for {old_filepath}: {e}")


def run_task():
    folder_path = filedialog.askdirectory(title="选择要处理的文件夹")
    if not folder_path:
        return

    file_types_input = simpledialog.askstring("输入",
                                              "请输入要处理的文件类型（用逗号分隔，例如：jpg,png,txt），或输入1处理所有文件：")
    if not file_types_input:
        return
    file_types = file_types_input.split(',')

    task = tk.StringVar()

    def on_task_select():
        if task.get() == '1':
            prefix = simpledialog.askstring("输入", "请输入要添加的前缀字符：")
            add_prefix(folder_path, file_types, prefix)
        elif task.get() == '2':
            suffix = simpledialog.askstring("输入", "请输入要添加的后缀字符：")
            add_suffix(folder_path, file_types, suffix)
        elif task.get() == '3':
            excel_path = filedialog.askopenfilename(title="选择Excel文件", filetypes=[("Excel files", "*.xlsx")])
            if excel_path:
                rename_from_excel(folder_path, excel_path, file_types)
        elif task.get() == '4':
            chars = simpledialog.askstring("输入", "请输入要删除的字符：")
            remove_chars(folder_path, file_types, chars)
        elif task.get() == '5':
            undo_last_action()
        elif task.get() == '6':
            batch_modify_file_attributes(folder_path, file_types)
        else:
            messagebox.showerror("错误", "无效的选项，请重新运行程序并输入正确的选项。")
        if messagebox.askyesno("继续", "操作已完成，是否继续执行其他任务？"):
            run_task()
        else:
            root.destroy()

    task_window = tk.Toplevel(root)
    task_window.title("选择任务")

    tk.Radiobutton(task_window, text="批量在文件名前加指定的前缀", variable=task, value='1').pack(anchor='w')
    tk.Radiobutton(task_window, text="批量在文件名后加后缀", variable=task, value='2').pack(anchor='w')
    tk.Radiobutton(task_window, text="读取excel列表，按excel列表里的文件名给文件夹里的文件重命名", variable=task,
                   value='3').pack(anchor='w')
    tk.Radiobutton(task_window, text="删除文件名里的指定字符", variable=task, value='4').pack(anchor='w')
    tk.Radiobutton(task_window, text="撤销上一步操作", variable=task, value='5').pack(anchor='w')
    tk.Radiobutton(task_window, text="批量修改文件属性", variable=task, value='6').pack(anchor='w')

    tk.Button(task_window, text="确定", command=on_task_select).pack()

    # 设置任务窗口在屏幕中央
    task_window.update_idletasks()
    x = (task_window.winfo_screenwidth() // 2) - (task_window.winfo_reqwidth() // 2)
    y = (task_window.winfo_screenheight() // 2) - (task_window.winfo_reqheight() // 2)
    task_window.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("批量文件处理工具")
    tk.Button(root, text="开始", command=run_task).pack(pady=20)
    tk.Button(root, text="退出", command=root.quit).pack(pady=20)

    # 设置主窗口在屏幕中央
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_reqwidth() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_reqheight() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()
