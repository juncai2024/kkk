@echo off

REM 批量文件重命名工具打包脚本
REM 使用 PyInstaller 打包为 Windows 可执行文件

echo 正在安装依赖...
python -m pip install pyinstaller

echo 正在打包程序...
python -m PyInstaller --onefile --windowed --name="BatchRenamer" batch_renamer.py

echo 打包完成！可执行文件位于 dist 目录下

pause