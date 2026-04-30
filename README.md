# Audio2SRT - 音频转字幕工具箱

基于火山引擎豆包语音识别 API 的音频转 SRT 字幕工具，支持批量处理、SRT 优化，提供美观的图形界面。

## 功能特性

- 批量音频转 SRT 字幕
- 支持本地文件和在线链接两种模式
- SRT 字幕优化（按标点断句、控制字幕长度、自动分配时间轴）
- 拖拽文件添加
- 现代蓝色调 UI 界面
- 配置自动保存
- 可打包为独立 exe 文件

## 环境要求

- Python 3.9+
- Windows 10/11

## 安装依赖

```bash
pip install customtkinter Pillow requests tkinterdnd2
```

## 使用方法

### 启动程序

```bash
python tkmode.py
```

### 音频转 SRT

1. 点击左侧"音频转 SRT"
2. 选择"本地文件"或"外链模式"
3. 添加音频文件或输入 URL（每行一个）
4. 点击"开始处理"
5. 等待处理完成

支持的音频格式：MP3 / WAV / M4A / FLAC / AAC / OGG

### SRT 优化

1. 点击左侧"SRT 优化"
2. 选择 SRT 字幕文件
3. 点击"开始优化"
4. 生成 `filename_opt.srt`

优化内容：
- 自动按逗号断句
- 控制每行字幕长度（默认 25 字符）
- 自动分配时间轴
- 自动删除句号

### 设置

点击左侧"设置"配置：

| 配置项 | 说明 |
|--------|------|
| API Key | 火山引擎豆包语音 API 访问密钥 |
| Resource ID | 使用的资源 ID，默认 `volc.bigasr.auc` |

配置文件自动保存为 `audio2srt_config.json`。

## 获取免费识别时长

1. 登录 [火山引擎](https://console.volcengine.com/auth/login)
2. 进入 [豆包语音购买页](https://console.volcengine.com/speech/new/purchase?projectName=default)
3. 点击授权
4. [查看余量](https://console.volcengine.com/speech/new/setting/activate?projectName=default)

## 打包为 EXE

### 方式一：运行打包脚本

```powershell
.\build.ps1
```

### 方式二：手动打包

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "audio2srt" --icon=image/ico.png --add-data "image;image" --hidden-import=customtkinter --hidden-import=PIL --hidden-import=requests --hidden-import=tkinterdnd2 --collect-all customtkinter --exclude-module matplotlib --exclude-module numpy --exclude-module scipy --exclude-module pandas --exclude-module PIL.ImageGrab --exclude-module PIL.ImageQt --exclude-module tkinter.test --upx-dir=. --clean tkmode.py
```

生成的 exe 文件位于 `dist/audio2srt.exe`。

**减小体积**：项目目录放置 `upx.exe` 后，打包会自动压缩。

## 项目结构

```
audio2srt/
├── tkmode.py           # GUI 主程序入口
├── index.py            # 音频转写与 SRT 处理核心逻辑
├── build.ps1           # PowerShell 打包脚本
├── build.bat           # Batch 打包脚本（备用）
├── audio2srt_config.json  # 配置文件（自动生成）
├── image/              # 图片资源
│   ├── ico.png
│   ├── 授权.png
│   └── 余量.png
├── SRT/                # 输出的字幕文件（自动生成）
└── dist/               # 打包输出目录（自动生成）
```

## 技术栈

| 组件 | 说明 |
|------|------|
| CustomTkinter | 现代化 UI 框架 |
| tkinterdnd2 | 拖拽功能支持 |
| Pillow | 图片处理 |
| requests | HTTP 请求 |
| PyInstaller | 打包工具 |
| UPX | 可执行文件压缩 |
| 火山引擎 API | 语音识别服务 |

## 常见问题

**Q: 处理速度慢怎么办？**
A: 取决于网络状况和音频长度，请耐心等待。

**Q: 提示 API Key 无效？**
A: 请在火山引擎控制台获取有效 API Key，然后在程序的"设置"页面更新。

**Q: 配置文件在哪里？**
A: `audio2srt_config.json`，位于程序同目录下。

## 开源协议

MIT License

Copyright (c) 2026 Syie. All rights reserved.
