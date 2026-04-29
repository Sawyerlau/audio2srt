import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import uuid
import time
import json
import re
import os
import threading

# ===================== 配置区 =====================
API_KEY = "6804f065-c9b1-4bb3-b250-6a05e489b3b4"
RESOURCE_ID = "volc.bigasr.auc"
SUBMIT_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"
QUERY_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"

MAX_LENGTH = 25
SPLIT_SYMBOL = "，"
DELETE_PERIOD = True
# ==================================================

# ===================== 工具函数 =====================
def ms_to_srt(ms):
    ms = int(ms)
    s = ms // 1000
    ms = ms % 1000
    m = s // 60
    s = s % 60
    h = m // 60
    m = m % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def time_to_ms(time_str):
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    h = int(parts[0])
    m = int(parts[1])
    s = float(parts[2])
    return int((h * 3600 + m * 60 + s) * 1000)

def ms_to_time(ms):
    ms = int(ms)
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

def split_text_by_comma(text):
    text = text.strip()
    if DELETE_PERIOD:
        text = text.replace("。", "")
    raw_parts = text.split(SPLIT_SYMBOL)
    parts = []
    current = ""
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if len(current) + len(part) + 1 <= MAX_LENGTH:
            current += (SPLIT_SYMBOL if current else "") + part
        else:
            if current:
                parts.append(current)
            current = part
    if current:
        parts.append(current)
    return [p for p in parts if p]

# ===================== SRT 优化（按字数比例） =====================
def optimize_srt_content(srt_content):
    content = srt_content
    blocks = re.split(r'\n\s*\n', content.strip())
    new_blocks = []
    new_index = 1

    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 3:
            continue
        time_line = lines[1]
        text = ' '.join(lines[2:])
        if ' --> ' not in time_line:
            continue

        start_str, end_str = time_line.split(' --> ')
        start_ms = time_to_ms(start_str)
        end_ms = time_to_ms(end_str)
        total_ms = end_ms - start_ms

        parts = split_text_by_comma(text)
        if not parts:
            continue

        total_chars = sum(len(p.strip()) for p in parts)
        if total_chars == 0:
            continue

        current_start = start_ms
        for i, p in enumerate(parts):
            char_len = len(p.strip())
            ratio = char_len / total_chars
            part_ms = int(total_ms * ratio)

            if i == len(parts) - 1:
                current_end = end_ms
            else:
                current_end = current_start + part_ms

            new_time = f"{ms_to_time(current_start)} --> {ms_to_time(current_end)}"
            new_blocks.append([str(new_index), new_time, p])
            current_start = current_end
            new_index += 1

    return "\n\n".join(["\n".join(b) for b in new_blocks]) + "\n"

# ===================== 音频转写（支持批量） =====================
def process_audio_list(url_list, log_cb):
    def task():
        total = len(url_list)
        for idx, url in enumerate(url_list, 1):
            log_cb(f"\n==================================")
            log_cb(f"正在处理第 {idx}/{total} 个音频")
            log_cb(f"链接：{url}")

            task_id = str(uuid.uuid4())
            headers = {
                "X-Api-Key": API_KEY,
                "X-Api-Resource-Id": RESOURCE_ID,
                "X-Api-Request-Id": task_id,
                "X-Api-Sequence": "-1",
                "Content-Type": "application/json"
            }

            body = {
                "user": {"uid": "user123"},
                "audio": {"url": url, "format": "mp3"},
                "request": {
                    "model_name": "bigmodel",
                    "enable_itn": True,
                    "enable_punc": True,
                    "show_utterances": True
                }
            }

            log_cb("提交转写任务...")
            try:
                resp = requests.post(SUBMIT_URL, headers=headers, json=body, timeout=20)
            except:
                log_cb("❌ 网络请求失败")
                continue

            code = resp.headers.get("X-Api-Status-Code")
            msg = resp.headers.get("X-Api-Message")

            if code != "20000000":
                log_cb(f"❌ 提交失败：{code} {msg}")
                continue

            log_cb("任务提交成功，等待识别结果...")
            result = None
            while True:
                time.sleep(2)
                try:
                    q_resp = requests.post(QUERY_URL, headers=headers, json={}, timeout=10)
                except:
                    log_cb("⚠️ 查询超时，重试中...")
                    continue

                q_code = q_resp.headers.get("X-Api-Status-Code")
                if q_code in ("20000001", "20000002"):
                    continue
                if q_code != "20000000":
                    log_cb("❌ 识别失败")
                    break
                result = q_resp.json()
                break

            if not result:
                continue

            utters = result.get("result", {}).get("utterances", [])
            if not utters:
                log_cb("❌ 未获取到分句信息")
                continue

            # 生成原始SRT
            srt_content = ""
            num = 1
            for utt in utters:
                srt_content += f"{num}\n{ms_to_srt(utt['start_time'])} --> {ms_to_srt(utt['end_time'])}\n{utt['text']}\n\n"
                num += 1

            # 优化
            log_cb("正在优化 SRT（按字数比例分配时间）...")
            optimized = optimize_srt_content(srt_content)

            # 保存
            raw_name = f"{idx}.srt"
            opt_name = f"{idx}_已优化.srt"
            with open(raw_name, "w", encoding="utf-8") as f:
                f.write(srt_content)
            with open(opt_name, "w", encoding="utf-8") as f:
                f.write(optimized)

            log_cb(f"✅ 第 {idx} 个处理完成！")
            log_cb(f"📄 原始文件：{raw_name}")
            log_cb(f"✅ 优化文件：{opt_name}")

        log_cb("\n🎉 所有音频批量处理完成！")

    threading.Thread(target=task, daemon=True).start()

# ===================== 界面 =====================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("音频批量转SRT + SRT智能优化工具（按字数比例）")
        self.root.geometry("720x520")

        tab_control = ttk.Notebook(root)
        self.tab1 = ttk.Frame(tab_control)
        self.tab2 = ttk.Frame(tab_control)
        tab_control.add(self.tab1, text="🎵 批量音频外链转SRT")
        tab_control.add(self.tab2, text="📝 本地SRT优化")
        tab_control.pack(expand=1, fill="both", padx=5, pady=5)

        # === 标签1：批量转写 ===
        ttk.Label(self.tab1, text="请粘贴音频外链（一行一个，支持批量）：").pack(pady=3)
        self.url_text = tk.Text(self.tab1, height=6, width=85)
        self.url_text.pack(pady=3, padx=5)
        self.url_text.insert("end", "https://\n")

        self.log1 = tk.Text(self.tab1, height=14, width=85)
        self.log1.pack(pady=3, padx=5)

        ttk.Button(self.tab1, text="开始批量转写 + 优化", command=self.start_batch).pack(pady=5)

        # === 标签2：SRT优化 ===
        ttk.Label(self.tab2, text="选择要优化的SRT文件：").pack(pady=8)
        self.srt_path_var = tk.StringVar()
        ttk.Entry(self.tab2, textvariable=self.srt_path_var, width=80).pack(pady=3)
        ttk.Button(self.tab2, text="浏览文件", command=self.browse_srt).pack(pady=2)

        self.log2 = tk.Text(self.tab2, height=16, width=85)
        self.log2.pack(pady=5, padx=5)

        ttk.Button(self.tab2, text="开始优化（按字数比例）", command=self.optimize_srt_file).pack(pady=5)

    def log(self, msg, tab=1):
        if tab == 1:
            self.log1.insert(tk.END, msg + "\n")
            self.log1.see(tk.END)
        else:
            self.log2.insert(tk.END, msg + "\n")
            self.log2.see(tk.END)

    def start_batch(self):
        text = self.url_text.get("1.0", tk.END).strip()
        lines = [l.strip() for l in text.splitlines() if l.strip() and l.strip().startswith("http")]
        if not lines:
            messagebox.showerror("错误", "请输入至少一个有效音频链接！")
            return
        self.log1.delete("1.0", tk.END)
        process_audio_list(lines, lambda m: self.log(m, 1))

    def browse_srt(self):
        path = filedialog.askopenfilename(filetypes=[("SRT文件", "*.srt")])
        if path:
            self.srt_path_var.set(path)

    def optimize_srt_file(self):
        path = self.srt_path_var.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("错误", "请选择有效的SRT文件")
            return
        self.log2.delete("1.0", tk.END)
        def task():
            try:
                self.log("读取文件中...", 2)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.log("正在优化（按字数比例分配时间）...", 2)
                new_content = optimize_srt_content(content)
                name = os.path.splitext(path)[0]
                out_path = name + "_已优化.srt"
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                self.log(f"✅ 完成！文件已保存：\n{out_path}", 2)
            except Exception as e:
                self.log(f"错误：{e}", 2)
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()