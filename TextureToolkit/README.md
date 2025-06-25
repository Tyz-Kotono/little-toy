# TextureToolkit

## 简介
TextureToolkit 是一个用于贴图处理和合成的多功能工具箱，支持多种贴图合成、颜色矩阵生成、序列帧拼接等功能，界面基于 PyQt6，操作直观。

## 主要功能

### 1. RGBA Atlas
- 支持将多张图片的 RGBA 通道合成为一张 2x2 序列帧贴图。
- 支持分辨率调整、预览和输出保存。

### 2. Merge Atlas
- 支持多张图片按指定行列拼接为序列帧贴图。
- 支持自定义填充色、输出分辨率、图片顺序调整、预览和保存。

### 3. Color Matrix / 颜色矩阵
- 支持自定义行列的颜色矩阵编辑，每个色块可单独拾色。
- 实时预览生成的颜色矩阵图片，可导出为PNG。
- 支持一键清除所有颜色。

### 4. Single Atlas
- 支持单张图片按指定行列合成序列帧贴图。
- 支持两种模式：全部重复单张、单张加颜色。
- 支持自定义填充色、输出分辨率、预览和保存。

## 使用方法
1. 启动主程序：
   ```bash
   python main.py
   ```
2. 通过左侧按钮切换不同功能区。
3. 按界面提示选择图片、设置参数，点击生成/保存按钮完成操作。

## 依赖
- Python 3.8+
- PyQt6
- Pillow

安装依赖：
```bash
pip install PyQt6 Pillow
```

## 目录结构
- main.py                主程序入口
- RGBAChannelMere.py     RGBA通道合成功能
- MergeAtalas.py         多图拼接合成功能
- ColorMatrixDock.py     颜色矩阵功能
- SingleAtlasDock.py     单图序列帧合成功能
- Library/               通用UI组件

---
如有问题或建议，欢迎反馈！ 