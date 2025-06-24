# XToolkit 视频下载器

一个支持 YouTube 和 Twitter 视频下载的桌面应用程序。

[![GitHub release](https://img.shields.io/github/v/release/Tyz-Kotono/little-toy)](https://github.com/Tyz-Kotono/little-toy/releases)
[![GitHub license](https://img.shields.io/github/license/Tyz-Kotono/little-toy)](https://github.com/Tyz-Kotono/little-toy/blob/main/LICENSE)

## 📥 快速下载

最新版本：[XToolkit v1.2](https://github.com/Tyz-Kotono/little-toy/releases/latest)

## 功能特性

- **多平台支持**：YouTube、Twitter
- **YouTube 功能**：
  - 自动检测可用画质和字幕
  - 选择特定格式下载
  - 下载字幕文件
- **Twitter 功能**：
  - 视频下载
  - 可选的 GIF 转换
- **GIF 预览**：动态 GIF 播放，支持播放控制
- **Dock 布局**：预览窗口以 Dock 形式显示
- **进度显示**：实时下载进度

## 系统要求

- Python 3.8+
- Windows 10/11
- FFmpeg（用于 GIF 转换，yt-dlp 会自动调用）

## 安装方法

### 方法一：使用预编译版本（推荐）

1. 前往 [Releases](https://github.com/Tyz-Kotono/little-toy/releases) 页面
2. 下载最新版本的 `XToolkit_v*.exe`
3. 直接运行即可（无需安装 Python 环境）

### 方法二：从源码运行

1. 克隆项目：
   ```bash
   git clone https://github.com/Tyz-Kotono/little-toy.git
   cd little-toy/XToolkit
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python main.py
   ```

## 使用方法

1. 启动程序（默认选择 Twitter 平台）
2. 输入视频链接
3. 选择平台（YouTube/Twitter）
4. 根据需要配置选项：
   - YouTube：点击"检测视频信息"获取画质和字幕选项
   - Twitter：可选择"转换为 GIF 动图"
5. 选择下载位置
6. 点击"下载"开始下载
7. 下载完成后可预览 GIF（如果适用）

## 项目结构

```
little-toy/
├── XToolkit/
│   ├── main.py                 # 主程序
│   ├── youtube_downloader.py   # YouTube 下载器模块
│   ├── twitter_downloader.py   # Twitter 下载器模块
│   ├── Icon/                   # 图标文件夹
│   ├── requirements.txt        # 依赖列表
│   ├── README.md              # 说明文档
│   └── RELEASE.md             # 发布说明
├── .gitignore                 # Git 忽略文件
└── README.md                  # 项目总览
```

## 版本信息

- **当前版本**：1.2
- **作者**：tyz_kotono
- **GitHub**：[https://github.com/Tyz-Kotono/little-toy](https://github.com/Tyz-Kotono/little-toy)

## 更新日志

### v1.2
- ✨ 添加 Dock 布局预览窗口
- ✨ 支持动态 GIF 播放控制
- ✨ 优化用户界面体验
- 🐛 修复菜单栏兼容性问题

### v1.1
- ✨ 添加下载进度条
- ✨ 支持 Twitter GIF 转换
- ✨ 添加 GIF 预览功能

### v1.0
- 🎉 初始版本发布
- ✨ 支持 YouTube 和 Twitter 下载
- ✨ 基础界面和功能

## 注意事项

- 确保网络连接正常
- YouTube 下载需要遵守相关服务条款
- Twitter 下载需要遵守相关服务条款
- GIF 转换需要系统安装 FFmpeg

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目仅供学习和个人使用。

---

⭐ 如果这个项目对你有帮助，请给个 Star！ 