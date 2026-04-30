import customtkinter as ctk
from tkinter import filedialog, messagebox, Listbox, Scrollbar
import threading
import os
import json
import webbrowser
import sys

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# 引入 index 模块，用于同步配置
import index
from index import process_single_audio, optimize_srt
import tkinter as tk 
# =========================
# 配置管理
# =========================
CONFIG_FILE = "audio2srt_config.json"
DEFAULT_CONFIG = {
    "API_KEY": "",
    "RESOURCE_ID": "volc.bigasr.auc"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
        except:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# 加载初始配置
config = load_config()
API_KEY = config["API_KEY"]
RESOURCE_ID = config["RESOURCE_ID"]

# =========================
# 自定义主题系统 - 现代蓝色调主题
# =========================
THEME = {
    "bg_primary": "#f0f2f5",
    "bg_secondary": "#ffffff",
    "bg_tertiary": "#e8ebee",
    "accent": "#0066ff",
    "accent_hover": "#3385ff",
    "accent_disabled": "#99c2ff",
    "text_primary": "#1a1a1a",
    "text_secondary": "#4d4d4d",
    "text_muted": "#999999",
    "border": "#d0d3d9",
    "success": "#00c853",
    "warning": "#ffab00",
    "error": "#ff5252",
    "file_list_bg": "#f7f8fa",
    "file_list_select": "#0066ff",
    "drop_zone": "#e8ebee",
    "drop_zone_active": "#0066ff",
}

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False


class App(TkinterDnD.Tk if HAS_DND else ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("音频转SRT By：Syie")
        self.state('zoomed')  # 默认全屏
        self.resizable(True, True)
        self.minsize(900, 600)  # 设置最小窗口尺寸
        self.icon = tk.PhotoImage(file=resource_path("./image/ico.png"))  # 保存图标引用
        self.iconphoto(True, self.icon)   # True 表示同时影响任务栏图标（尽量）
        self.local_files = []
        self.active_tab = None
        self.file_cards = []  # 存储文件卡片

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.configure(bg=THEME["bg_primary"])

        self.create_sidebar()
        self.create_main_area()

    # =========================
    # UI 基础结构
    # =========================
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=180,
            fg_color=THEME["bg_secondary"],
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent", corner_radius=0)
        title_frame.pack(pady=(25, 10), padx=15, fill="x")

        try:
            from PIL import Image as PILImage
            img = PILImage.open(resource_path("./image/ico.png"))
            max_height = 25
            if img.height > max_height:
                ratio = max_height / img.height
                new_size = (int(img.width * ratio), max_height)
                img = img.resize(new_size, PILImage.Resampling.LANCZOS)
            self.sidebar_icon_image = ctk.CTkImage(light_image=img, size=(img.width, img.height))
            ctk.CTkLabel(
                title_frame,
                image=self.sidebar_icon_image,
                text=""
            ).pack(side="left", padx=(0, 8))
        except Exception:
            pass

        ctk.CTkLabel(
            title_frame,
            text="字幕生成工具箱",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        separator = ctk.CTkFrame(sidebar, height=1, fg_color=THEME["border"], corner_radius=0)
        separator.pack(pady=(5, 15), padx=15, fill="x")

        self.btn_tab1 = self._create_sidebar_button(
            sidebar,
            text="🔄 音频转SRT",
            command=lambda: self.show_tab1()
        )

        self.btn_tab2 = self._create_sidebar_button(
            sidebar,
            text="✨ SRT优化",
            command=lambda: self.show_tab2()
        )

        # 底部的按钮区域
        sidebar_bottom = ctk.CTkFrame(sidebar, fg_color="transparent", corner_radius=0)
        sidebar_bottom.pack(side="bottom", fill="x", pady=20, padx=15)

        self.btn_settings = self._create_sidebar_button(
            sidebar_bottom,
            text="⚙️ 设置",
            command=lambda: self.show_settings()
        )

        self.btn_help = self._create_sidebar_button(
            sidebar_bottom,
            text="❓ 帮助中心",
            command=lambda: self.show_help()
        )

    def _create_sidebar_button(self, parent, text, command):
        btn = ctk.CTkButton(
            parent,
            text=text,
            font=ctk.CTkFont(size=14, family="Microsoft YaHei UI"),
            fg_color="transparent",
            hover_color=THEME["bg_tertiary"],
            text_color=THEME["text_secondary"],
            text_color_disabled=THEME["text_muted"],
            anchor="w",
            height=40,
            corner_radius=8,
            command=command
        )
        btn.pack(pady=4, padx=15, fill="x")
        return btn

    def _update_sidebar_active(self, active_btn):
        for btn in [self.btn_tab1, self.btn_tab2, self.btn_settings, self.btn_help]:
            if btn == active_btn:
                btn.configure(
                    fg_color=THEME["accent"],
                    text_color="#ffffff",
                    hover_color=THEME["accent_hover"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=THEME["text_secondary"],
                    hover_color=THEME["bg_tertiary"]
                )

    def create_main_area(self):
        self.main = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_primary"],
            corner_radius=0
        )
        self.main.grid(row=0, column=1, sticky="nsew")

        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(3, weight=1)

        self.show_tab1()

    def clear_main(self):
        # 如果当前在设置页面，先自动保存配置
        if self.active_tab == "settings":
            self.save_settings(silent=True)
        for w in self.main.winfo_children():
            w.destroy()
        
        # 重置网格配置到默认状态
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(0, weight=0)
        self.main.grid_rowconfigure(1, weight=0)
        self.main.grid_rowconfigure(2, weight=0)
        self.main.grid_rowconfigure(3, weight=1)

    # =========================
    # TAB 1 - 音频转SRT
    # =========================
    def show_tab1(self):
        self.clear_main()
        self.active_tab = "tab1"
        self._update_sidebar_active(self.btn_tab1)

        # Header area
        header_frame = ctk.CTkFrame(self.main, fg_color="transparent", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(15, 5))

        ctk.CTkLabel(
            header_frame,
            text="批量音频转SRT（自带SRT优化）",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(side="left", padx=(20, 0))

        # 模式选择区 - 使用自定义按钮
        mode_frame = ctk.CTkFrame(self.main, fg_color="transparent", corner_radius=0)
        mode_frame.grid(row=1, column=0, sticky="w", pady=(5, 10))

        ctk.CTkLabel(
            mode_frame,
            text="模式：",
            font=ctk.CTkFont(size=14),
            text_color=THEME["text_secondary"]
        ).pack(side="left", padx=(20, 0))

        self.current_mode = "local"  # 默认本地文件模式

        self.btn_url_mode = ctk.CTkButton(
            mode_frame,
            text="🔗 外链模式",
            width=110,
            height=32,
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            corner_radius=8,
            command=lambda: self.switch_mode("url")
        )
        self.btn_url_mode.pack(side="left", padx=(0, 5))

        self.btn_local_mode = ctk.CTkButton(
            mode_frame,
            text="📁 本地文件",
            width=110,
            height=32,
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            corner_radius=8,
            command=lambda: self.switch_mode("local")
        )
        self.btn_local_mode.pack(side="left")

        # 初始化模式按钮状态
        self._update_mode_buttons()

        # =========================
        # URL 区
        # =========================
        self.frame_url = ctk.CTkFrame(
            self.main,
            fg_color=THEME["bg_secondary"],
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"]
        )
        self.frame_url.grid(row=2, column=0, sticky="nsew", pady=10, padx=15)
        self.frame_url.grid_remove()

        ctk.CTkLabel(
            self.frame_url,
            text="🔗 外链输入（每行一个URL）",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.url_text = ctk.CTkTextbox(
            self.frame_url,
            height=120,
            font=("Consolas", 11),
            fg_color=THEME["bg_tertiary"],
            border_width=1,
            border_color=THEME["border"],
            text_color=THEME["text_primary"],
            corner_radius=8
        )
        self.url_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # =========================
        # 本地文件区
        # =========================
        self.frame_local = ctk.CTkFrame(
            self.main,
            fg_color=THEME["bg_secondary"],
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"]
        )
        self.frame_local.grid(row=2, column=0, sticky="nsew", pady=10, padx=15)

        btn_row = ctk.CTkFrame(self.frame_local, fg_color="transparent", corner_radius=0)
        btn_row.pack(fill="x", pady=(15, 10), padx=15)

        ctk.CTkButton(
            btn_row,
            text="📁 选择文件",
            command=self.select_files,
            width=120,
            height=36,
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            text_color="#ffffff",
            corner_radius=8
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="🗑️ 清空",
            command=self.clear_files,
            width=120,
            height=36,
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            fg_color=THEME["bg_tertiary"],
            hover_color=THEME["border"],
            text_color=THEME["text_primary"],
            corner_radius=8
        ).pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            btn_row,
            text="💡 拖拽文件到下方区域",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_muted"]
        ).pack(side="left", padx=(20, 0))

        # 👉 先创建 log1（关键修复点）
        self.log1 = ctk.CTkTextbox(
            self.main,
            height=140,
            font=("Consolas", 15),
            fg_color=THEME["bg_secondary"],
            border_width=1,
            border_color=THEME["border"],
            text_color=THEME["text_primary"],
            corner_radius=8
        )
        self.log1.grid(row=3, column=0, sticky="nsew", pady=(0, 10), padx=15)

        self._create_file_list(self.frame_local)

        # 进度条
        self.progress_frame = ctk.CTkFrame(self.main, fg_color="transparent", corner_radius=0)
        self.progress_frame.grid(row=4, column=0, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            height=8,
            fg_color=THEME["bg_tertiary"],
            progress_color=THEME["accent"],
            corner_radius=4
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=10)

        ctk.CTkButton(
            self.main,
            text="🚀 开始处理",
            height=44,
            font=ctk.CTkFont(size=15, weight="bold", family="Microsoft YaHei UI"),
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            text_color="#ffffff",
            corner_radius=10,
            command=self.start_batch
        ).grid(row=5, column=0, sticky="ew", pady=(0, 15))

        self.switch_mode("local")

    def _update_mode_buttons(self):
        """更新模式按钮的视觉状态"""
        if self.current_mode == "url":
            self.btn_url_mode.configure(
                fg_color=THEME["accent"],
                text_color="#ffffff",
                hover_color=THEME["accent_hover"]
            )
            self.btn_local_mode.configure(
                fg_color=THEME["bg_tertiary"],
                text_color=THEME["text_primary"],
                hover_color=THEME["border"]
            )
        else:
            self.btn_local_mode.configure(
                fg_color=THEME["accent"],
                text_color="#ffffff",
                hover_color=THEME["accent_hover"]
            )
            self.btn_url_mode.configure(
                fg_color=THEME["bg_tertiary"],
                text_color=THEME["text_primary"],
                hover_color=THEME["border"]
            )

    # =========================
    # FILE LIST
    # =========================
    def _create_file_list(self, parent):
        """创建文件列表容器"""
        self.file_list_container = ctk.CTkScrollableFrame(
            parent,
            fg_color=THEME["bg_tertiary"],
            corner_radius=8
        )
        self.file_list_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # 拖拽提示
        drop_label = ctk.CTkLabel(
            parent,
            text="⬆️ 支持拖拽音频文件拖放到上方任务栏",
            font=ctk.CTkFont(size=12),
            text_color=THEME["text_muted"],
            anchor="center"
        )
        drop_label.pack(pady=(0, 5))

        if HAS_DND:
            self.enable_dnd()

    def _add_file_card(self, file_path):
        """添加单个文件卡片"""
        file_name = os.path.basename(file_path)
        
        # 创建文件卡片
        card = ctk.CTkFrame(
            self.file_list_container,
            fg_color=THEME["file_list_bg"],
            corner_radius=6,
            border_width=1,
            border_color=THEME["border"]
        )
        card.pack(fill="x", pady=5, padx=5)

        # 文件图标和名称
        name_frame = ctk.CTkFrame(card, fg_color="transparent")
        name_frame.pack(side="left", fill="x", expand=True, padx=12, pady=10)

        ctk.CTkLabel(
            name_frame,
            text=f"🎵 {file_name}",
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        # 删除按钮
        delete_btn = ctk.CTkButton(
            card,
            text="🗑️ 删除",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=THEME["error"],
            hover_color="#ff7070",
            text_color="#ffffff",
            corner_radius=6,
            command=lambda: self._remove_file_card(card, file_path)
        )
        delete_btn.pack(side="right", padx=10, pady=8)

        # 保存卡片引用
        self.file_cards.append({"card": card, "path": file_path})

    def _remove_file_card(self, card, file_path):
        """移除文件卡片"""
        # 从列表中删除
        try:
            index = self.local_files.index(file_path)
            del self.local_files[index]
        except ValueError:
            pass
        
        # 移除卡片引用
        self.file_cards = [fc for fc in self.file_cards if fc["card"] != card]
        
        # 销毁卡片
        card.pack_forget()
        card.destroy()
        
        self.log(f"已删除：{os.path.basename(file_path)}")

    # =========================
    # DRAG & DROP
    # =========================
    def enable_dnd(self):
        def on_drop(event):
            try:
                files = self.tk.splitlist(event.data)
                self.add_files(files)
            except Exception as e:
                self.log(f"拖拽失败: {e}")

        # 拖拽整个区域更自然
        self.frame_local.drop_target_register(DND_FILES)
        self.frame_local.dnd_bind("<<Drop>>", on_drop)

        self.log("拖拽功能已启用")

    # =========================
    # FILE LOGIC
    # =========================
    def add_files(self, paths):
        added = 0

        for p in paths:
            p = p.strip().strip("{}").strip('"')

            if not os.path.isfile(p):
                continue

            if p in self.local_files:
                continue

            self.local_files.append(p)
            self._add_file_card(p)
            self.log(f"已添加：{os.path.basename(p)}")
            added += 1

        if added:
            self.log(f"共添加 {added} 个文件")

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="选择音频文件",
            filetypes=[("音频文件", "*.mp3 *.wav *.m4a *.flac *.aac *.ogg"), ("所有文件", "*.*")]
        )
        self.add_files(files)

    def clear_files(self):
        self.local_files.clear()
        
        # 清空所有文件卡片
        for fc in self.file_cards:
            fc["card"].pack_forget()
            fc["card"].destroy()
        self.file_cards.clear()

    # =========================
    # MODE SWITCH
    # =========================
    def switch_mode(self, mode):
        """切换模式"""
        self.current_mode = mode
        self._update_mode_buttons()
        
        if mode == "url":
            self.frame_url.grid()
            self.frame_local.grid_remove()
        else:
            self.frame_url.grid_remove()
            self.frame_local.grid()

    # =========================
    # LOG（安全版，防炸）
    # =========================
    def log(self, msg, box=None):
        try:
            target = self.log1 if box is None else box
            target.insert("end", msg + "\n")
            target.see("end")
        except Exception:
            print(msg)

    # =========================
    # RUN
    # =========================
    def start_batch(self):
        global API_KEY, RESOURCE_ID
        # 确保使用最新配置
        API_KEY = config["API_KEY"]
        RESOURCE_ID = config["RESOURCE_ID"]
        
        mode = self.current_mode

        if mode == "url":
            text = self.url_text.get("0.0", "end")
            urls = [i.strip() for i in text.splitlines() if i.startswith("http")]

            if not urls:
                messagebox.showwarning("提示", "请输入URL")
                return

            self.progress_bar.set(0)
            total = len(urls)

            def task():
                for i, url in enumerate(urls):
                    process_single_audio(url, i + 1, lambda m: self.log(m))
                    self.after(0, lambda v=(i + 1) / total: self.progress_bar.set(v))
                self.after(0, lambda: self.progress_bar.set(1.0))
                self.log("全部完成")

            threading.Thread(target=task, daemon=True).start()

        else:
            if not self.local_files:
                messagebox.showwarning("提示", "请选择文件")
                return

            self.progress_bar.set(0)
            total = len(self.local_files)

            def task():
                for i, path in enumerate(self.local_files):
                    filename = os.path.splitext(os.path.basename(path))[0]
                    process_single_audio(
                        path,
                        i + 1,
                        lambda m: self.log(m),
                        is_local_file=True,
                        filename_prefix=filename
                    )
                    self.after(0, lambda v=(i + 1) / total: self.progress_bar.set(v))
                self.after(0, lambda: self.progress_bar.set(1.0))
                self.log("全部完成")

            threading.Thread(target=task, daemon=True).start()

    # =========================
    # 设置页面
    # =========================
    def show_settings(self):
        self.clear_main()
        self.active_tab = "settings"
        self._update_sidebar_active(self.btn_settings)

        header_frame = ctk.CTkFrame(self.main, fg_color="transparent", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(15, 15))

        ctk.CTkLabel(
            header_frame,
            text="系统设置",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(side="left", padx=(20, 0))

        # 设置卡片
        settings_card = ctk.CTkFrame(
            self.main,
            fg_color=THEME["bg_secondary"],
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"]
        )
        settings_card.grid(row=1, column=0, sticky="ew", pady=10, padx=15)

        # API Key
        ctk.CTkLabel(
            settings_card,
            text="🔑 API Key",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.api_key_entry = ctk.CTkEntry(
            settings_card,
            placeholder_text="请输入火山引擎 API Key",
            font=("Consolas", 12),
            fg_color=THEME["bg_tertiary"],
            border_width=1,
            border_color=THEME["border"],
            text_color=THEME["text_primary"],
            corner_radius=8,
            height=40
        )
        self.api_key_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.api_key_entry.insert(0, config.get("API_KEY", ""))

        # Resource ID
        ctk.CTkLabel(
            settings_card,
            text="📦 Resource ID",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(5, 5))

        self.resource_id_entry = ctk.CTkEntry(
            settings_card,
            placeholder_text="请输入火山引擎 Resource ID",
            font=("Consolas", 12),
            fg_color=THEME["bg_tertiary"],
            border_width=1,
            border_color=THEME["border"],
            text_color=THEME["text_primary"],
            corner_radius=8,
            height=40
        )
        self.resource_id_entry.pack(fill="x", padx=15, pady=(0, 15))
        self.resource_id_entry.insert(0, config.get("RESOURCE_ID", ""))

        # 说明文字容器 - 使用帮助中心样式
        help_container = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        help_container.grid(row=2, column=0, sticky="nsew", padx=15, pady=10)

        self.main.grid_rowconfigure(2, weight=1)

        # API Key 获取指南
        api_key_content = """- API_KEY 是火山引擎豆包语音识别API的凭证
- API_KEY 需要在 [点击获取](https://console.volcengine.com/speech/new/setting/apikeys?projectName=default) 获取
- RESOURCE_ID 默认为volc.bigasr.auc（录音文件识别1.0）
- 配置自动保存到 audio2srt_config.json
- 切换页面或点击保存按钮都会自动保存配置"""

        self._create_help_section(help_container, "💡 设置说明", api_key_content, expanded=True)

        # 如何白嫖录音文件识别时长
        free_content = """1. 登录火山引擎后 [点击进入登录页面](https://console.volcengine.com/auth/login)
2. [点击进入豆包语音购买界面](https://console.volcengine.com/speech/new/purchase?projectName=default)
3. 点击授权
![](./image/授权.png)
4. [点击查看余量](https://console.volcengine.com/speech/new/setting/activate?projectName=default)
![](./image/余量.png)"""

        self._create_help_section(help_container, "🎁 免费获取识别时长", free_content, expanded=False)

        # 保存按钮
        ctk.CTkButton(
            self.main,
            text="💾 保存配置",
            height=44,
            font=ctk.CTkFont(size=15, weight="bold", family="Microsoft YaHei UI"),
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            text_color="#ffffff",
            corner_radius=10,
            command=self.save_settings
        ).grid(row=3, column=0, sticky="ew", padx=15, pady=(15, 15))

    # =========================
    # TAB 2
    # =========================
    def show_tab2(self):
        self.clear_main()
        self.active_tab = "tab2"
        self._update_sidebar_active(self.btn_tab2)

        header_frame = ctk.CTkFrame(self.main, fg_color="transparent", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text="SRT优化",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(side="left", padx=(20, 0))

        self.srt_path = ctk.StringVar()

        # File selection area
        file_frame = ctk.CTkFrame(
            self.main,
            fg_color=THEME["bg_secondary"],
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"]
        )
        file_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=15)

        ctk.CTkLabel(
            file_frame,
            text="选择SRT文件:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(15, 10))

        row = ctk.CTkFrame(file_frame, fg_color="transparent", corner_radius=0)
        row.pack(fill="x", padx=15, pady=(0, 15))
        row.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(
            row,
            textvariable=self.srt_path,
            font=("Consolas", 15),
            fg_color=THEME["bg_tertiary"],
            border_width=1,
            border_color=THEME["border"],
            text_color=THEME["text_primary"],
            corner_radius=8,
            height=36
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ctk.CTkButton(
            row,
            text="📂 浏览",
            command=self.browse,
            width=100,
            height=36,
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            text_color="#ffffff",
            corner_radius=8
        ).grid(row=0, column=1)

        # Log area
        self.log2 = ctk.CTkTextbox(
            self.main,
            font=("Consolas", 15),
            fg_color=THEME["bg_secondary"],
            border_width=1,
            border_color=THEME["border"],
            text_color=THEME["text_primary"],
            corner_radius=8
        )
        self.log2.grid(row=2, column=0, sticky="nsew", pady=(0, 10), padx=15)

        # Progress bar for tab2
        self.progress_frame2 = ctk.CTkFrame(self.main, fg_color="transparent", corner_radius=0)
        self.progress_frame2.grid(row=3, column=0, sticky="ew")

        self.progress_bar2 = ctk.CTkProgressBar(
            self.progress_frame2,
            height=8,
            fg_color=THEME["bg_tertiary"],
            progress_color=THEME["accent"],
            corner_radius=4
        )
        self.progress_bar2.set(0)
        self.progress_bar2.pack(fill="x", pady=10)

        ctk.CTkButton(
            self.main,
            text="🔧 开始优化",
            height=44,
            font=ctk.CTkFont(size=15, weight="bold", family="Microsoft YaHei UI"),
            fg_color=THEME["accent"],
            hover_color=THEME["accent_hover"],
            text_color="#ffffff",
            corner_radius=10,
            command=self.optimize
        ).grid(row=4, column=0, sticky="ew", pady=(0, 15))

        self.main.grid_rowconfigure(2, weight=1)

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("SRT", "*.srt")])
        if path:
            self.srt_path.set(path)

    def optimize(self):
        global API_KEY, RESOURCE_ID
        # 确保使用最新配置
        API_KEY = config["API_KEY"]
        RESOURCE_ID = config["RESOURCE_ID"]
        
        path = self.srt_path.get()
        if not os.path.exists(path):
            messagebox.showwarning("错误", "文件不存在")
            return

        self.progress_bar2.set(0)

        def task():
            # 创建 SRT 文件夹
            srt_dir = os.path.join(os.getcwd(), "SRT")
            if not os.path.exists(srt_dir):
                os.makedirs(srt_dir)
            
            filename = os.path.splitext(os.path.basename(path))[0]
            out = os.path.join(srt_dir, f"{filename}_opt.srt")
            optimize_srt(path, out)
            self.after(0, lambda: self.progress_bar2.set(1.0))
            self.log(f"完成：{out}", self.log2)

        threading.Thread(target=task, daemon=True).start()

    # =========================
    # 保存设置
    # =========================
    def save_settings(self, silent=False):
        """保存用户配置"""
        global config, API_KEY, RESOURCE_ID
        
        # 确保设置页面的输入框存在
        if not hasattr(self, 'api_key_entry') or not hasattr(self, 'resource_id_entry'):
            return
        
        config["API_KEY"] = self.api_key_entry.get().strip()
        config["RESOURCE_ID"] = self.resource_id_entry.get().strip()
        
        # 保存到配置文件
        save_config(config)
        
        # 更新当前文件的配置
        API_KEY = config["API_KEY"]
        RESOURCE_ID = config["RESOURCE_ID"]
        
        # 同步更新 index 模块的配置
        index.API_KEY = config["API_KEY"]
        index.RESOURCE_ID = config["RESOURCE_ID"]
        index.config = config
        
        if not silent:
            messagebox.showinfo("成功", "配置已保存！\n配置文件：audio2srt_config.json")

    # =========================
    # 帮助中心
    # =========================
    def show_help(self):
        self.clear_main()
        self.active_tab = "help"
        self._update_sidebar_active(self.btn_help)

        # 设置网格配置，让第一行是标题，第二行占据所有剩余空间
        self.main.grid_rowconfigure(0, weight=0)  # 标题行固定高度
        self.main.grid_rowconfigure(1, weight=1)  # 内容行占据所有剩余空间
        self.main.grid_rowconfigure(2, weight=0)  # 空行，权重为0
        self.main.grid_rowconfigure(3, weight=0)  # 空行，权重为0
        self.main.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.main, fg_color="transparent", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(15, 15))

        ctk.CTkLabel(
            header_frame,
            text="帮助中心",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        ).pack(side="left", padx=(20, 0))

        # 帮助卡片容器
        help_container = ctk.CTkScrollableFrame(self.main, fg_color="transparent")
        help_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)

        # 读取并渲染 Markdown 文档
        self._render_markdown_help(help_container)
    
    def _render_markdown_help(self, parent):
        """渲染硬编码的帮助文档"""
        
        # 帮助内容硬编码
        help_sections = [
            ("🚀 快速入门", """1. 点击左侧"音频转SRT"
2. 选择"本地文件"或"外链模式"
3. 添加音频文件或输入URL
4. 点击"开始处理"
5. 等待处理完成"""),
            
            ("如何白嫖录音文件识别时长", """1.登录火山引擎后[点击进入登录页面](https://console.volcengine.com/auth/login)
2. [点击进入豆包语音购买界面](https://console.volcengine.com/speech/new/purchase?projectName=default)
3.点击授权
![](./image/授权.png)
4.[点击查看余量](https://console.volcengine.com/speech/new/setting/activate?projectName=default)
![](./image/余量.png)
"""),
            
            (" 音频转SRT", """支持两种模式：
• 本地文件模式：支持 MP3/WAV/M4A/FLAC/AAC/OGG
• 外链模式：每行一个 HTTP/HTTPS 音频链接

支持批量处理，处理后会生成：
• 1.srt（原始字幕）
• 1已优化.srt（优化后字幕）
按照解析的先后顺序进行命名，例如 1.srt, 2.srt, 3.srt 等
"""),
            
            ("✨ SRT优化", """优化功能：
• 自动按标点符号断句
• 控制每行字幕长度（默认25字符）
• 自动分配时间轴
• 自动删除句号

使用方法：
1. 点击左侧"SRT优化"
2. 选择已有的 SRT 字幕文件
3. 点击"开始优化"
4. 生成 filename_opt.srt"""),
            
            ("⚙️ 设置说明", """配置项说明：
• API Key：火山引擎豆包语音 API 访问密钥
• Resource ID：使用的资源 ID（默认是录音文件识别1.0）

获取方式：
1. 登录火山引擎控制台 [点击跳转到API Key管理页面](https://console.volcengine.com/speech/new/setting/apikeys?projectName=default)
2. 在管理页面获取 API Key 即可粘贴到设置内

更多信息请访问 [火山引擎文档](https://www.volcengine.com/docs)"""),
            
            ("❓ 常见问题", """**Q: 处理速度慢怎么办？**
A: 取决于网络状况和音频长度，请耐心等待

**Q: 支持什么音频格式？**
A: 本地支持 MP3/WAV/M4A/FLAC/AAC/OGG，外链支持主流格式

**Q: 配置文件在哪里？**
A: audio2srt_config.json，位于程序同目录下"""),
            
            ("ℹ️ 关于", """音频工具箱
版本：1.0

基于火山引擎大语音识别API
使用 CustomTkinter 构建

鸣谢：Trae Doubao-Seed-2.0-Code ChatGPT Qwen-3.6-Plus
开源协议：MIT 协议
Copyright © 2026 Syie. All rights reserved.
"""),
        ]
        
        # 渲染每个区块，默认全部展开
        for title, content in help_sections:
            self._create_help_section(parent, title, content, expanded=True)

    def _create_help_section(self, parent, title, content, expanded=False):
        """创建可折叠的帮助信息区块，支持超链接和图片"""
        card = ctk.CTkFrame(
            parent,
            fg_color=THEME["bg_secondary"],
            corner_radius=12,
            border_width=1,
            border_color=THEME["border"]
        )
        card.pack(fill="x", pady=10)

        # 标题行（可点击）
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=15)
        header_frame.bind("<Button-1>", lambda e: self._toggle_help_section(card))
        
        # 箭头标签
        arrow_label = ctk.CTkLabel(
            header_frame,
            text="▶" if not expanded else "▼",
            font=ctk.CTkFont(size=16),
            text_color=THEME["text_secondary"],
            anchor="w"
        )
        arrow_label.pack(side="left", padx=(0, 10))
        arrow_label.bind("<Button-1>", lambda e: self._toggle_help_section(card))
        
        # 标题标签
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=THEME["text_primary"],
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        title_label.bind("<Button-1>", lambda e: self._toggle_help_section(card))
        
        # 内容容器
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        if expanded:
            content_frame.pack(fill="x", padx=15, pady=(0, 15))
        else:
            content_frame.pack_forget()
        
        # 保存引用
        card._content_frame = content_frame
        card._arrow_label = arrow_label
        card._expanded = expanded
        
        # 解析并渲染内容，支持超链接和图片
        self._render_content_with_links(content_frame, content)
    
    def _toggle_help_section(self, card):
        """切换帮助区块的展开/收起状态"""
        card._expanded = not card._expanded
        
        if card._expanded:
            card._arrow_label.configure(text="▼")
            card._content_frame.pack(fill="x", padx=15, pady=(0, 15))
        else:
            card._arrow_label.configure(text="▶")
            card._content_frame.pack_forget()
    
    def _render_content_with_links(self, parent, content):
        """渲染内容，支持超链接和图片"""
        import re
        
        lines = content.split('\n')
        
        for line in lines:
            # 检查图片语法 ![alt](url)
            image_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if image_match:
                alt_text = image_match.group(1)
                url = image_match.group(2)
                self._render_image(parent, url, alt_text)
                continue
            
            # 检查普通链接语法 [text](url)
            # 分割文本，将链接和普通文本分开渲染
            parts = re.split(r'(\[.*?\]\(.*?\))', line)
            
            if len(parts) > 1:
                line_frame = ctk.CTkFrame(parent, fg_color="transparent")
                line_frame.pack(fill="x", anchor="w")
                
                for part in parts:
                    if part:
                        link_match = re.match(r'\[(.*?)\]\((.*?)\)', part)
                        if link_match:
                            text = link_match.group(1)
                            url = link_match.group(2)
                            self._render_link(line_frame, text, url)
                        else:
                            ctk.CTkLabel(
                                line_frame,
                                text=part,
                                font=("Microsoft YaHei UI", 13),
                                text_color=THEME["text_primary"],
                                anchor="w"
                            ).pack(side="left")
            else:
                # 普通文本行
                ctk.CTkLabel(
                    parent,
                    text=line,
                    font=("Microsoft YaHei UI", 13),
                    text_color=THEME["text_primary"],
                    anchor="w"
                ).pack(fill="x", anchor="w")
    
    def _render_link(self, parent, text, url):
        """渲染超链接"""
        link_label = ctk.CTkLabel(
            parent,
            text=text,
            font=("Microsoft YaHei UI", 13, "underline"),
            text_color=THEME["accent"],
            anchor="w",
            cursor="hand2"
        )
        link_label.pack(side="left")
        link_label.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
    
    def _render_image(self, parent, url, alt_text=""):
        """渲染图片"""
        try:
            # 检查是否有必要的库
            PIL_available = False
            requests_available = False
            
            try:
                from PIL import Image as PILImage
                PIL_available = True
            except ImportError:
                pass
            
            try:
                import requests
                from io import BytesIO
                requests_available = True
            except ImportError:
                pass
            
            # 如果没有必要的库，显示替代文本
            if not PIL_available:
                alt_display = f"[图片: {alt_text}] (需要安装 Pillow 库)"
                ctk.CTkLabel(
                    parent,
                    text=alt_display,
                    font=("Microsoft YaHei UI", 13),
                    text_color=THEME["text_muted"],
                    anchor="w"
                ).pack(fill="x", anchor="w")
                return
            
            # 尝试加载图片
            if url.startswith('http'):
                if not requests_available:
                    alt_display = f"[图片: {alt_text}] (需要安装 requests 库)"
                    ctk.CTkLabel(
                        parent,
                        text=alt_display,
                        font=("Microsoft YaHei UI", 13),
                        text_color=THEME["text_muted"],
                        anchor="w"
                    ).pack(fill="x", anchor="w")
                    return
                
                # 下载网络图片
                response = requests.get(url, timeout=10)
                img_data = BytesIO(response.content)
                img = PILImage.open(img_data)
            else:
                # 本地图片
                img_path = os.path.join(os.path.dirname(__file__), url)
                if not os.path.exists(img_path):
                    alt_display = f"[图片不存在: {alt_text}]"
                    ctk.CTkLabel(
                        parent,
                        text=alt_display,
                        font=("Microsoft YaHei UI", 13),
                        text_color=THEME["text_muted"],
                        anchor="w"
                    ).pack(fill="x", anchor="w")
                    return
                img = PILImage.open(img_path)
            
            # 调整图片大小（最大宽度可以根据需要调整）
            max_width = 1500
            display_img = img
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                display_img = img.resize((max_width, new_height), PILImage.Resampling.LANCZOS)
            
            # 转换为 CTkImage
            ctk_image = ctk.CTkImage(light_image=display_img, size=(display_img.width, display_img.height))
            
            # 显示图片，左对齐
            img_container = ctk.CTkFrame(parent, fg_color="transparent")
            img_container.pack(fill="x", anchor="w", pady=5)
            
            img_label = ctk.CTkLabel(img_container, image=ctk_image, text="")
            img_label.image = ctk_image  # 保持引用
            img_label.pack(anchor="w")
            
        except Exception as e:
            # 图片加载失败，显示替代文本
            error_text = f"[图片加载失败: {alt_text}]"
            ctk.CTkLabel(
                parent,
                text=error_text,
                font=("Microsoft YaHei UI", 13),
                text_color=THEME["text_muted"],
                anchor="w"
            ).pack(fill="x", anchor="w")
    



if __name__ == "__main__":
    App().mainloop()