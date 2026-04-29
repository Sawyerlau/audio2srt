import customtkinter as ctk
from tkinter import filedialog, messagebox, Listbox, Scrollbar
import threading
import os

from index import process_single_audio, optimize_srt

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    HAS_DND = True
except ImportError:
    HAS_DND = False


class App(TkinterDnD.Tk if HAS_DND else ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("音频工具箱")
        self.geometry("900x650")

        self.local_files = []

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()

    # =========================
    # UI 基础结构
    # =========================
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=160)
        sidebar.grid(row=0, column=0, sticky="ns")

        ctk.CTkLabel(
            sidebar,
            text="工具箱",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)

        ctk.CTkButton(sidebar, text="音频转SRT", command=self.show_tab1).pack(pady=10, padx=10)
        ctk.CTkButton(sidebar, text="SRT优化", command=self.show_tab2).pack(pady=10, padx=10)

    def create_main_area(self):
        self.main = ctk.CTkFrame(self)
        self.main.grid(row=0, column=1, sticky="nsew")

        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(3, weight=1)

        self.show_tab1()

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    # =========================
    # TAB 1
    # =========================
    def show_tab1(self):
        self.clear_main()

        ctk.CTkLabel(
            self.main,
            text="批量音频转SRT",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=10)

        self.tab_mode = ctk.CTkSegmentedButton(
            self.main,
            values=["外链模式", "本地文件"],
            command=self.switch_mode
        )
        self.tab_mode.set("本地文件")
        self.tab_mode.grid(row=1, column=0, sticky="w", pady=10)

        # =========================
        # URL 区
        # =========================
        self.frame_url = ctk.CTkFrame(self.main)
        self.frame_url.grid(row=2, column=0, sticky="nsew")
        self.frame_url.grid_remove()

        ctk.CTkLabel(self.frame_url, text="外链（每行一个）", text_color="gray").pack(anchor="w")

        self.url_text = ctk.CTkTextbox(self.frame_url, height=120)
        self.url_text.pack(fill="both", expand=True)

        # =========================
        # 本地文件区
        # =========================
        self.frame_local = ctk.CTkFrame(self.main)
        self.frame_local.grid(row=2, column=0, sticky="nsew")

        btn_row = ctk.CTkFrame(self.frame_local, fg_color="transparent")
        btn_row.pack(fill="x", pady=5)

        ctk.CTkButton(btn_row, text="选择文件", command=self.select_files, width=120).pack(side="left")
        ctk.CTkButton(btn_row, text="清空", command=self.clear_files, width=120).pack(side="left", padx=10)

        ctk.CTkLabel(btn_row, text="拖拽文件到这里", text_color="gray").pack(side="left", padx=20)

        # 👉 先创建 log1（关键修复点）
        self.log1 = ctk.CTkTextbox(self.main, height=120)
        self.log1.grid(row=3, column=0, sticky="nsew", pady=10)

        self._create_file_list(self.frame_local)

        ctk.CTkButton(self.main, text="开始处理", height=40, command=self.start_batch).grid(
            row=4, column=0, sticky="ew"
        )

        self.switch_mode("本地文件")

    # =========================
    # FILE LIST
    # =========================
    def _create_file_list(self, parent):
        wrap = ctk.CTkFrame(parent)
        wrap.pack(fill="both", expand=True)

        self.file_listbox = Listbox(
            wrap,
            bg="#2b2b2b",
            fg="white",
            selectbackground="#3a6ea5",
            font=("Microsoft YaHei", 10)
        )
        self.file_listbox.pack(side="left", fill="both", expand=True)

        scroll = Scrollbar(wrap, command=self.file_listbox.yview)
        scroll.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scroll.set)

        if HAS_DND:
            self.enable_dnd()

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
            self.file_listbox.insert("end", f" {os.path.basename(p)}")
            added += 1

        if added:
            self.log(f"已添加 {added} 个文件")

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="选择音频文件",
            filetypes=[("音频文件", "*.mp3 *.wav *.m4a *.flac *.aac *.ogg"), ("所有文件", "*.*")]
        )
        self.add_files(files)

    def clear_files(self):
        self.local_files.clear()
        self.file_listbox.delete(0, "end")

    # =========================
    # MODE SWITCH
    # =========================
    def switch_mode(self, mode):
        if mode == "外链模式":
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
        mode = self.tab_mode.get()

        if mode == "外链模式":
            text = self.url_text.get("0.0", "end")
            urls = [i.strip() for i in text.splitlines() if i.startswith("http")]

            if not urls:
                messagebox.showwarning("提示", "请输入URL")
                return

            def task():
                for i, url in enumerate(urls):
                    process_single_audio(url, i + 1, lambda m: self.log(m))
                self.log("全部完成")

            threading.Thread(target=task, daemon=True).start()

        else:
            if not self.local_files:
                messagebox.showwarning("提示", "请选择文件")
                return

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
                self.log("全部完成")

            threading.Thread(target=task, daemon=True).start()

    # =========================
    # TAB 2
    # =========================
    def show_tab2(self):
        self.clear_main()

        ctk.CTkLabel(
            self.main,
            text="SRT优化",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        self.srt_path = ctk.StringVar()

        row = ctk.CTkFrame(self.main)
        row.grid(row=1, column=0, sticky="ew", pady=10)
        row.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(row, textvariable=self.srt_path).grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(row, text="选择", command=self.browse).grid(row=0, column=1, padx=10)

        self.log2 = ctk.CTkTextbox(self.main)
        self.log2.grid(row=2, column=0, sticky="nsew")

        ctk.CTkButton(self.main, text="开始优化", command=self.optimize).grid(row=3, column=0, sticky="ew")

        self.main.grid_rowconfigure(2, weight=1)

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("SRT", "*.srt")])
        if path:
            self.srt_path.set(path)

    def optimize(self):
        path = self.srt_path.get()
        if not os.path.exists(path):
            messagebox.showwarning("错误", "文件不存在")
            return

        def task():
            out = os.path.splitext(path)[0] + "_opt.srt"
            optimize_srt(path, out)
            self.log(f"完成: {out}", self.log2)

        threading.Thread(target=task, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()