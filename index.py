import requests
import uuid
import time
import json
import re
import os

# ===================== 基础配置区 =====================
# 语音转写API配置
API_KEY = "6804f065-c9b1-4bb3-b250-6a05e489b3b4"
RESOURCE_ID = "volc.bigasr.auc"  # 录音1.0标准版
AUDIO_URL_LIST = [
    "https://tts-file2.com/s3/file/2026-04-22-103656_121183.mp3"
]

# SRT优化配置
MAX_LENGTH = 25       # 每行字幕最大字数
SPLIT_SYMBOL = "，"   # 按中文逗号拆分
DELETE_PERIOD = True  # 删除句号
# ====================================================

# 语音转写接口地址
SUBMIT_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"
QUERY_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"

# ===================== 时间格式转换工具 =====================
def ms_to_srt(ms):
    """毫秒转SRT时间格式（用于转写）"""
    ms = int(ms)
    s = ms // 1000
    ms = ms % 1000
    m = s // 60
    s = s % 60
    h = m // 60
    m = m % 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def time_to_ms(time_str):
    """SRT时间字符串转毫秒（用于拆分）"""
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    h = int(parts[0])
    m = int(parts[1])
    s = float(parts[2])
    return int((h * 3600 + m * 60 + s) * 1000)

def ms_to_time(ms):
    """毫秒转回SRT时间格式（用于拆分）"""
    ms = int(ms)
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

# ===================== SRT生成与优化 =====================
def generate_srt(utterances):
    """生成原始SRT内容"""
    srt = []
    idx = 1
    for utt in utterances:
        start = utt["start_time"]
        end = utt["end_time"]
        text = utt["text"].strip()
        srt.append(str(idx))
        srt.append(f"{ms_to_srt(start)} --> {ms_to_srt(end)}")
        srt.append(text)
        srt.append("")
        idx += 1
    return "\n".join(srt)

def split_text_by_comma(text):
    """按逗号拆分句子，控制长度"""
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

def optimize_srt(input_path, output_path):
    """优化SRT文件（拆分长句、均分时间）"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  读取SRT文件失败：{input_path} | 错误：{e}")
        return False

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
        
        count = len(parts)
        per_ms = total_ms // count
        current_start = start_ms

        for p in parts:
            current_end = current_start + per_ms
            if current_end > end_ms:
                current_end = end_ms
            new_time = f"{ms_to_time(current_start)} --> {ms_to_time(current_end)}"
            new_blocks.append([str(new_index), new_time, p])
            current_start = current_end
            new_index += 1

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for b in new_blocks:
                f.write('\n'.join(b) + '\n\n')
        return True
    except Exception as e:
        print(f"⚠️  写入优化后SRT失败：{output_path} | 错误：{e}")
        return False

# ===================== 音频处理主逻辑 =====================
def process_single_audio(audio_url, file_index):
    """处理单个音频：转写生成SRT → 自动优化SRT"""
    task_id = str(uuid.uuid4())
    print(f"\n===== 开始处理第 {file_index} 个音频 =====")
    print("任务ID：", task_id)
    print("音频地址：", audio_url)

    # 1. 配置请求头
    headers = {
        "X-Api-Key": API_KEY,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Request-Id": task_id,
        "X-Api-Sequence": "-1",
        "Content-Type": "application/json"
    }

    # 2. 提交转写任务
    body = {
        "user": {"uid": "user123"},
        "audio": {"url": audio_url, "format": "mp3"},
        "request": {
            "model_name": "bigmodel",
            "enable_itn": True,
            "enable_punc": True,
            "show_utterances": True
        }
    }

    print("提交转写任务...")
    resp = requests.post(SUBMIT_URL, headers=headers, json=body)
    code = resp.headers.get("X-Api-Status-Code")
    msg = resp.headers.get("X-Api-Message")
    print(f"提交结果：{code} | {msg}")

    if code != "20000000":
        print(f"❌ 第 {file_index} 个音频提交失败！")
        return

    # 3. 轮询转写结果
    print("任务提交成功，轮询识别结果...")
    result = None
    while True:
        time.sleep(2)
        q_resp = requests.post(QUERY_URL, headers=headers, json={})
        q_code = q_resp.headers.get("X-Api-Status-Code")
        q_msg = q_resp.headers.get("X-Api-Message")

        print(f"查询状态：{q_code} | {q_msg}")

        if q_code in ("20000001", "20000002"):  # 处理中/等待中
            continue
        if q_code != "20000000":
            print(f"❌ 第 {file_index} 个音频识别失败")
            return

        result = q_resp.json()
        break

    # 4. 生成原始SRT文件
    utters = result.get("result", {}).get("utterances", [])
    if not utters:
        print(f"❌ 第 {file_index} 个音频未获取到分句信息")
        return

    raw_srt_filename = f"{file_index}.srt"
    srt_content = generate_srt(utters)
    with open(raw_srt_filename, "w", encoding="utf-8") as f:
        f.write(srt_content)
    print(f"✅ 已生成原始SRT：{raw_srt_filename}")
    print("识别文本：\n" + result["result"]["text"])

    # 5. 自动优化SRT文件
    optimized_srt_filename = f"{file_index}已优化.srt"
    if optimize_srt(raw_srt_filename, optimized_srt_filename):
        print(f"✅ 已生成优化后SRT：{optimized_srt_filename}")
    else:
        print(f"❌ 第 {file_index} 个音频SRT优化失败")

def main():
    """主函数：批量处理所有音频"""
    for index, audio_url in enumerate(AUDIO_URL_LIST, start=1):
        process_single_audio(audio_url, index)
    
    print("\n🎉 所有音频处理完毕！")

if __name__ == "__main__":
    main()