// 地图编辑器JavaScript代码
class MapEditor {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 20; // 初始格子大小
        this.totalRows = 20; // 初始行数
        this.totalCols = 20; // 初始列数
        this.rows = this.totalRows;
        this.cols = this.totalCols;
        
        // 游戏模式：draw, edge, arrow
        this.mode = 'draw';
        this.currentModeElement = document.getElementById('currentMode');
        
        // 初始化网格设置控件
        this.initGridSettings();
        
        // 初始化网格
        this.grid = this.initGrid();
        
        // 绑定事件
        this.bindEvents();
        
        // 绘制初始网格
        this.draw();
    }
    
    // 初始化网格设置控件
    initGridSettings() {
        // 初始化格子大小
        const gridSizeInput = document.getElementById('gridSize');
        gridSizeInput.value = this.gridSize;
        
        // 初始化行数和列数
        const gridRowsInput = document.getElementById('gridRows');
        gridRowsInput.value = this.totalRows;
        
        const gridColsInput = document.getElementById('gridCols');
        gridColsInput.value = this.totalCols;
        
        // 更新显示
        this.updateGridInfo();
    }
    
    // 更新网格信息显示
    updateGridInfo() {
        const gridInfo = document.getElementById('gridInfo');
        gridInfo.textContent = `(${this.totalCols}x${this.totalRows})`;
    }
    
    // 初始化网格
    initGrid() {
        let grid = [];
        for (let row = 0; row < this.rows; row++) {
            grid[row] = [];
            for (let col = 0; col < this.cols; col++) {
                grid[row][col] = {
                    isDrawn: false,     // 是否被绘制
                    isEdge: false,      // 是否是边缘
                    number: 0,          // 边缘数字
                    arrow: null,        // 箭头方向：up, right, down, left
                    rotation: 0         // 箭头旋转角度
                };
            }
        }
        return grid;
    }
    
    // 绑定事件
    bindEvents() {
        // 画布事件
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('contextmenu', (e) => this.handleCanvasRightClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleCanvasMouseMove(e));
        this.canvas.addEventListener('mousedown', (e) => this.handleCanvasMouseDown(e));
        this.canvas.addEventListener('mouseup', (e) => this.handleCanvasMouseUp(e));
        
        // 按钮事件
        document.getElementById('drawMode').addEventListener('click', () => this.switchMode('draw'));
        document.getElementById('edgeMode').addEventListener('click', () => this.switchMode('edge'));
        document.getElementById('arrowMode').addEventListener('click', () => this.switchMode('arrow'));
        document.getElementById('randomArrows').addEventListener('click', () => this.generateRandomArrows());
        document.getElementById('clear').addEventListener('click', () => this.clearGrid());
        document.getElementById('applyGridSettings').addEventListener('click', () => this.applyGridSettings());
        document.getElementById('save').addEventListener('click', () => this.saveMap());
        document.getElementById('load').addEventListener('click', () => this.loadMap());
        
        this.isDrawing = false;
    }
    
    // 应用网格设置
    applyGridSettings() {
        // 获取输入值
        const gridSizeInput = document.getElementById('gridSize');
        const gridRowsInput = document.getElementById('gridRows');
        const gridColsInput = document.getElementById('gridCols');
        
        const newGridSize = parseInt(gridSizeInput.value);
        const newRows = parseInt(gridRowsInput.value);
        const newCols = parseInt(gridColsInput.value);
        
        // 验证输入值
        if (newGridSize >= 5 && newGridSize <= 30 &&
            newRows >= 5 && newRows <= 20 &&
            newCols >= 5 && newCols <= 20) {
            
            // 更新设置
            this.gridSize = newGridSize;
            this.totalRows = newRows;
            this.totalCols = newCols;
            this.rows = newRows;
            this.cols = newCols;
            
            // 重新初始化网格
            this.grid = this.initGrid();
            
            // 更新显示
            this.updateGridInfo();
            this.draw();
            
            alert(`网格设置已更新：${newGridSize}px, ${newCols}x${newRows}`);
        } else {
            // 验证失败，恢复原值
            gridSizeInput.value = this.gridSize;
            gridRowsInput.value = this.totalRows;
            gridColsInput.value = this.totalCols;
            
            alert('请输入有效的网格设置：\n- 格子大小：5-30像素\n- 行数：5-20行\n- 列数：5-20列');
        }
    }
    
    // 处理右键点击（橡皮擦功能）
    handleCanvasRightClick(e) {
        e.preventDefault(); // 阻止默认右键菜单
        
        const pos = this.getGridPosition(e);
        if (this.isValidPosition(pos.row, pos.col)) {
            // 清除已绘制的格子
            this.grid[pos.row][pos.col].isDrawn = false;
            this.grid[pos.row][pos.col].isEdge = false;
            this.grid[pos.row][pos.col].number = 0;
            this.grid[pos.row][pos.col].arrow = null;
            this.grid[pos.row][pos.col].rotation = 0;
            this.draw();
        }
    }
    
    // 生成随机箭头
    generateRandomArrows() {
        // 重新生成随机箭头
        this.addArrows();
        // 重新计算边缘数字
        this.calculateEdgeNumbers();
        // 重新绘制
        this.draw();
        alert('已生成随机箭头！');
    }
    
    // 切换模式
    switchMode(mode) {
        this.mode = mode;
        this.currentModeElement.textContent = this.getModeName(mode);
        
        // 更新按钮状态
        document.querySelectorAll('.controls button').forEach(btn => btn.classList.remove('active'));
        document.getElementById(mode + 'Mode').classList.add('active');
        
        // 切换鼠标样式
        this.canvas.style.cursor = mode === 'draw' ? 'crosshair' : 'pointer';
    }
    
    // 获取模式名称
    getModeName(mode) {
        const names = {
            draw: '绘制模式',
            edge: '边缘检测',
            arrow: '箭头模式'
        };
        return names[mode] || mode;
    }
    
    // 获取鼠标在网格中的位置
    getGridPosition(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        return {
            col: Math.floor(x / this.gridSize),
            row: Math.floor(y / this.gridSize)
        };
    }
    
    // 处理画布点击
    handleCanvasClick(e) {
        const pos = this.getGridPosition(e);
        if (this.isValidPosition(pos.row, pos.col)) {
            switch (this.mode) {
                case 'draw':
                    this.toggleCell(pos.row, pos.col);
                    break;
                case 'arrow':
                    this.rotateArrow(pos.row, pos.col);
                    break;
            }
            this.draw();
        }
    }
    
    // 处理鼠标移动
    handleCanvasMouseMove(e) {
        if (this.isDrawing) {
            const pos = this.getGridPosition(e);
            if (this.isValidPosition(pos.row, pos.col)) {
                if (this.mode === 'draw' && e.buttons === 1) {
                    // 左键拖拽绘制
                    this.grid[pos.row][pos.col].isDrawn = true;
                    this.draw();
                } else if (e.buttons === 2) {
                    // 右键拖拽擦除
                    this.grid[pos.row][pos.col].isDrawn = false;
                    this.grid[pos.row][pos.col].isEdge = false;
                    this.grid[pos.row][pos.col].number = 0;
                    this.grid[pos.row][pos.col].arrow = null;
                    this.grid[pos.row][pos.col].rotation = 0;
                    this.draw();
                }
            }
        }
    }
    
    // 处理鼠标按下
    handleCanvasMouseDown(e) {
        this.isDrawing = true;
        if (e.button === 0 && this.mode === 'draw') {
            // 左键点击绘制
            const pos = this.getGridPosition(e);
            if (this.isValidPosition(pos.row, pos.col)) {
                this.toggleCell(pos.row, pos.col);
                this.draw();
            }
        }
    }
    
    // 处理鼠标释放
    handleCanvasMouseUp(e) {
        this.isDrawing = false;
    }
    
    // 检查位置是否有效
    isValidPosition(row, col) {
        return row >= 0 && row < this.rows && col >= 0 && col < this.cols;
    }
    
    // 切换格子绘制状态
    toggleCell(row, col) {
        this.grid[row][col].isDrawn = !this.grid[row][col].isDrawn;
    }
    
    // 旋转箭头
    rotateArrow(row, col) {
        const cell = this.grid[row][col];
        if (cell.arrow) {
            // 顺时针旋转90度
            cell.rotation = (cell.rotation + 90) % 360;
        } else if (cell.isDrawn && !cell.isEdge) {
            // 如果是内部格子且没有箭头，添加箭头
            cell.arrow = 'up';
            cell.rotation = 0;
        }
    }
    
    // 清空网格
    clearGrid() {
        this.grid = this.initGrid();
        this.draw();
    }
    
    // 绘制网格
    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 计算绘制区域大小
        const totalWidth = this.totalCols * this.gridSize;
        const totalHeight = this.totalRows * this.gridSize;
        
        // 绘制格子 - 只绘制指定的行数和列数
        for (let row = 0; row < this.totalRows; row++) {
            for (let col = 0; col < this.totalCols; col++) {
                this.drawCell(row, col);
            }
        }
        
        // 绘制网格线
        this.drawGridLines(totalWidth, totalHeight);
    }
    
    // 绘制格子
    drawCell(row, col) {
        const x = col * this.gridSize;
        const y = row * this.gridSize;
        const cell = this.grid[row][col];
        
        // 绘制格子背景
        if (cell.isDrawn) {
            this.ctx.fillStyle = cell.isEdge ? '#ffcccc' : '#ccffcc';
            this.ctx.fillRect(x, y, this.gridSize, this.gridSize);
        } else {
            this.ctx.fillStyle = '#fafafa';
            this.ctx.fillRect(x, y, this.gridSize, this.gridSize);
        }
        
        // 绘制边缘数字 - 显示所有边缘格子的数字，包括0
        if (cell.isEdge) {
            this.ctx.fillStyle = '#ff0000';
            this.ctx.font = 'bold 14px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(cell.number.toString(), x + this.gridSize / 2, y + this.gridSize / 2);
        }
        
        // 绘制箭头
        if (cell.arrow) {
            this.drawArrow(x, y, cell.rotation);
        }
    }
    
    // 绘制箭头
    drawArrow(x, y, rotation) {
        this.ctx.save();
        this.ctx.translate(x + this.gridSize / 2, y + this.gridSize / 2);
        this.ctx.rotate((rotation * Math.PI) / 180);
        
        // 箭头颜色
        this.ctx.fillStyle = '#0000ff';
        
        // 绘制箭头三角形
        this.ctx.beginPath();
        this.ctx.moveTo(0, -8);
        this.ctx.lineTo(8, 8);
        this.ctx.lineTo(0, 4);
        this.ctx.lineTo(-8, 8);
        this.ctx.closePath();
        this.ctx.fill();
        
        this.ctx.restore();
    }
    
    // 绘制网格线
    drawGridLines(totalWidth, totalHeight) {
        this.ctx.strokeStyle = '#ddd';
        this.ctx.lineWidth = 1;
        
        // 绘制垂直线 - 只绘制到指定列数
        for (let col = 0; col <= this.totalCols; col++) {
            this.ctx.beginPath();
            this.ctx.moveTo(col * this.gridSize, 0);
            this.ctx.lineTo(col * this.gridSize, totalHeight);
            this.ctx.stroke();
        }
        
        // 绘制水平线 - 只绘制到指定行数
        for (let row = 0; row <= this.totalRows; row++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, row * this.gridSize);
            this.ctx.lineTo(totalWidth, row * this.gridSize);
            this.ctx.stroke();
        }
    }
    
    // 边缘检测
    detectEdges() {
        // 重置边缘状态
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                this.grid[row][col].isEdge = false;
                this.grid[row][col].number = 0;
            }
        }
        
        // 检测边缘 - 只检查上下左右四个方向
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                if (this.grid[row][col].isDrawn) {
                    // 检查上下左右四个方向是否有未绘制的格子
                    const directions = [
                        {row: -1, col: 0}, // 上
                        {row: 1, col: 0},  // 下
                        {row: 0, col: -1}, // 左
                        {row: 0, col: 1}   // 右
                    ];
                    
                    const hasEmptyNeighbor = directions.some(dir => {
                        const newRow = row + dir.row;
                        const newCol = col + dir.col;
                        return !this.isValidPosition(newRow, newCol) || 
                               !this.grid[newRow][newCol].isDrawn;
                    });
                    
                    if (hasEmptyNeighbor) {
                        this.grid[row][col].isEdge = true;
                    }
                }
            }
        }
        
        // 为内部格子添加箭头
        this.addArrows();
        
        // 计算边缘数字
        this.calculateEdgeNumbers();
        
        this.draw();
    }
    
    // 获取周围邻居
    getNeighbors(row, col) {
        const directions = [
            {row: -1, col: -1}, {row: -1, col: 0}, {row: -1, col: 1},
            {row: 0, col: -1},                     {row: 0, col: 1},
            {row: 1, col: -1},  {row: 1, col: 0},  {row: 1, col: 1}
        ];
        return directions.map(dir => ({row: row + dir.row, col: col + dir.col}));
    }
    
    // 为内部格子添加箭头
    addArrows() {
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                const cell = this.grid[row][col];
                if (cell.isDrawn && !cell.isEdge) {
                    // 随机初始箭头方向 - 每次都随机生成
                    const directions = ['up', 'right', 'down', 'left'];
                    const randomDirection = directions[Math.floor(Math.random() * directions.length)];
                    cell.arrow = randomDirection;
                    // 根据随机方向设置初始旋转角度
                    switch (randomDirection) {
                        case 'up': cell.rotation = 0; break;
                        case 'right': cell.rotation = 90; break;
                        case 'down': cell.rotation = 180; break;
                        case 'left': cell.rotation = 270; break;
                    }
                } else if (!cell.isDrawn) {
                    // 清除外部格子的箭头
                    cell.arrow = null;
                    cell.rotation = 0;
                }
            }
        }
    }
    
    // 计算边缘数字
    calculateEdgeNumbers() {
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                if (this.grid[row][col].isEdge) {
                    // 统计指向该边缘格子的箭头数量
                    let count = 0;
                    
                    // 检查所有内部格子
                    for (let r = 0; r < this.rows; r++) {
                        for (let c = 0; c < this.cols; c++) {
                            const cell = this.grid[r][c];
                            if (cell.isDrawn && !cell.isEdge && cell.arrow) {
                                // 检查箭头是否指向边缘格子
                                if (this.isArrowPointingTo(cell, r, c, row, col)) {
                                    count++;
                                }
                            }
                        }
                    }
                    
                    this.grid[row][col].number = count;
                }
            }
        }
    }
    
    // 检查箭头是否指向目标格子
    isArrowPointingTo(cell, fromRow, fromCol, toRow, toCol) {
        const direction = this.getArrowDirection(cell.rotation);
        const delta = {
            up: {row: -1, col: 0},
            right: {row: 0, col: 1},
            down: {row: 1, col: 0},
            left: {row: 0, col: -1}
        };
        
        // 沿着箭头方向移动，看是否能到达目标格子
        let currentRow = fromRow;
        let currentCol = fromCol;
        
        while (this.isValidPosition(currentRow, currentCol)) {
            currentRow += delta[direction].row;
            currentCol += delta[direction].col;
            
            if (currentRow === toRow && currentCol === toCol) {
                return true;
            }
            
            // 如果遇到边缘或外部格子，停止
            if (!this.isValidPosition(currentRow, currentCol) || 
                (this.grid[currentRow][currentCol].isDrawn && this.grid[currentRow][currentCol].isEdge)) {
                break;
            }
        }
        
        return false;
    }
    
    // 获取箭头方向
    getArrowDirection(rotation) {
        const directions = {
            0: 'up',
            90: 'right',
            180: 'down',
            270: 'left'
        };
        return directions[rotation] || 'up';
    }
    
    // 保存地图
    saveMap() {
        // 只导出被占用的单元格
        const occupiedCells = [];
        
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                const cell = this.grid[row][col];
                if (cell.isDrawn) {
                    // 使用X,Y坐标表示单元格
                    occupiedCells.push({
                        x: col,
                        y: row,
                        isEdge: cell.isEdge,
                        number: cell.number,
                        arrow: cell.arrow,
                        rotation: cell.rotation
                    });
                }
            }
        }
        
        const mapData = {
            gridSize: this.gridSize,
            totalRows: Math.floor(this.rows),
            totalCols: Math.floor(this.cols),
            cells: occupiedCells
        };
        
        // 创建JSON数据
        const jsonString = JSON.stringify(mapData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        
        // 创建下载链接
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'map_' + new Date().getTime() + '.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        alert('地图已保存！');
    }
    
    // 加载地图
    loadMap() {
        const fileInput = document.getElementById('fileInput');
        fileInput.click();
        
        // 绑定文件选择事件
        fileInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    try {
                        const mapData = JSON.parse(event.target.result);
                        
                        // 设置网格大小
                        this.gridSize = mapData.gridSize;
                        this.rows = this.canvas.height / this.gridSize;
                        this.cols = this.canvas.width / this.gridSize;
                        
                        // 重新初始化网格
                        this.grid = this.initGrid();
                        
                        // 加载被占用的单元格
                        if (mapData.cells && Array.isArray(mapData.cells)) {
                            mapData.cells.forEach(cellData => {
                                const { x, y, isEdge, number, arrow, rotation } = cellData;
                                if (this.isValidPosition(y, x)) {
                                    const cell = this.grid[y][x];
                                    cell.isDrawn = true;
                                    cell.isEdge = isEdge;
                                    cell.number = number;
                                    cell.arrow = arrow;
                                    cell.rotation = rotation;
                                }
                            });
                        }
                        
                        // 更新网格信息并绘制
                        this.updateGridInfo();
                        this.draw();
                        alert('地图已加载！');
                    } catch (error) {
                        alert('地图文件格式错误！');
                    }
                };
                reader.readAsText(file);
            }
        };
    }
}

// 初始化地图编辑器
document.addEventListener('DOMContentLoaded', () => {
    const editor = new MapEditor();
    
    // 绑定边缘检测按钮
    document.getElementById('edgeMode').addEventListener('click', () => {
        editor.detectEdges();
    });
});