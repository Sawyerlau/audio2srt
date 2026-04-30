<p align="center">
  <img src="image/ico.png" alt="Audio2SRT Logo" width="120">
</p>

<h1 align="center">Audio2SRT - 音频转字幕工具箱</h1>

<p align="center">
  <strong>基于火山引擎豆包语音识别 API 的音频转 SRT 字幕工具</strong>
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python&logoColor=white" alt="Python Version"></a>
  <a href="https://github.com/naaive/origin/releases"><img src="https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=flat-square&logo=windows&logoColor=white" alt="Platform"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"></a>
</p>

<p align="center">
  批量音频转写 · SRT 字幕优化 · 现代 GUI 界面 · 支持本地文件与在线链接
</p>

---

## ✨ 功能特性

- **批量处理** - 一次添加多个音频文件，自动转写生成 SRT 字幕
- **双模式支持** - 本地文件模式与在线链接模式，满足不同场景需求
- **SRT 优化** - 智能断句、字幕长度控制、自动时间轴分配
- **拖拽操作** - 支持拖拽文件添加，操作更便捷
- **现代 UI** - 基于 CustomTkinter 的蓝色调美观界面
- **配置持久化** - 设置自动保存，无需重复配置
- **独立打包** - 可打包为独立 exe 文件，无需 Python 环境

## 🚀 快速开始

### 环境要求

- Python 3.9 或更高版本
- Windows 10/11 操作系统

### 安装依赖

```bash
pip install customtkinter Pillow requests tkinterdnd2
```

### 启动程序

```bash
python tkmode.py
```

## 📖 使用指南

### 音频转 SRT

1. 点击左侧"音频转 SRT"
2. 选择"本地文件"或"外链模式"
3. 添加音频文件或输入 URL（每行一个）
4. 点击"开始处理"
5. 等待处理完成

**支持的音频格式**：MP3 / WAV / M4A / FLAC / AAC / OGG

### SRT 优化

1. 点击左侧"SRT 优化"
2. 选择需要优化的 SRT 字幕文件
3. 点击"开始优化"
4. 生成优化后的 `filename_opt.srt` 文件

**优化内容**：
- 自动按逗号断句
- 控制每行字幕长度（默认 25 字符）
- 自动分配时间轴
- 自动删除句号

### 设置

点击左侧"设置"页面配置以下参数：

| 配置项 | 说明 |
|--------|------|
| API Key | 火山引擎豆包语音 API 访问密钥 |
| Resource ID | 使用的资源 ID，默认 `volc.bigasr.auc` |

> 配置文件会自动保存为 `audio2srt_config.json`，位于程序同目录下。

## 🔑 获取免费识别时长

1. 登录 [火山引擎控制台](https://console.volcengine.com/auth/login)
2. 进入 [豆包语音购买页](https://console.volcengine.com/speech/new/purchase?projectName=default)
3. 点击授权开通服务
4. [查看余量](https://console.volcengine.com/speech/new/setting/activate?projectName=default)

## 📁 项目结构

```
audio2srt/
├── tkmode.py                    # GUI 主程序入口
├── index.py                     # 音频转写与 SRT 处理核心逻辑
├── audio2srt_config.json        # 配置文件（自动生成）
├── image/                       # 图片资源
│   ├── ico.png                  # 应用图标
│   ├── 授权.png                 # 授权指引截图
│   └── 余量.png                 # 余量查看截图
└── SRT/                         # 输出的字幕文件目录（自动生成）
```

## 🛠️ 技术栈

| 组件 | 说明 |
|------|------|
| [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) | 现代化 UI 框架 |
| [tkinterdnd2](https://github.com/TomSchimansky/tkinterdnd2) | 拖拽功能支持 |
| [Pillow](https://python-pillow.org/) | 图片处理 |
| [requests](https://requests.readthedocs.io/) | HTTP 请求库 |
| [PyInstaller](https://pyinstaller.org/) | 打包为可执行文件 |
| [UPX](https://upx.github.io/) | 可执行文件压缩 |
| 火山引擎 API | 语音识别服务 |

## ❓ 常见问题

**Q: 处理速度慢怎么办？**  
A: 处理速度取决于网络状况和音频长度，请耐心等待。

**Q: 提示 API Key 无效？**  
A: 请在火山引擎控制台检查 API Key 是否有效，然后在程序的"设置"页面更新。

**Q: 配置文件在哪里？**  
A: `audio2srt_config.json` 位于程序同目录下。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进项目！

## 📄 开源协议

本项目采用 MIT License 开源协议。

Copyright (c) 2026 Syie. All rights reserved.
