
import requests
import uuid
import time
import json
import re
import os
import base64

# 配置文件路径
CONFIG_FILE = "audio2srt_config.json"
DEFAULT_CONFIG = {
    "API_KEY": "",
    "RESOURCE_ID": "volc.bigasr.auc"
}


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置文件"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# 初始化配置
config = load_config()
API_KEY = config["API_KEY"]
RESOURCE_ID = config["RESOURCE_ID"]
AUDIO_URL_LIST = [
    "https://tts-file2.com/s5/file/2026-04-29-210554_136626.mp3"
]

MAX_LENGTH = 25
SPLIT_SYMBOL = "，"
DELETE_PERIOD = True

SUBMIT_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/submit"
QUERY_URL = "https://openspeech.bytedance.com/api/v3/auc/bigmodel/query"


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

def generate_srt(utterances):
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


def file_to_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


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

def optimize_srt_content(srt_content):
    # 修复可能的 HTML 转义字符
    srt_content = srt_content.replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&')
    
    blocks = re.split(r'\n\s*\n', srt_content.strip())
    new_blocks = []
    new_index = 1

    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if len(lines) < 3:
            continue
        
        # 查找包含 --> 的时间行
        time_line = None
        text_start = 0
        for i, line in enumerate(lines):
            if ' --> ' in line or '-->' in line:
                time_line = line
                text_start = i + 1
                break
        
        if time_line is None:
            continue
        
        # 提取时间
        if ' --> ' in time_line:
            start_str, end_str = time_line.split(' --> ')
        else:
            start_str, end_str = time_line.split('-->')
        start_str = start_str.strip()
        end_str = end_str.strip()
        
        start_ms = time_to_ms(start_str)
        end_ms = time_to_ms(end_str)
        total_ms = end_ms - start_ms

        text = ' '.join(lines[text_start:])

        parts = split_text_by_comma(text)
        if not parts:
            continue
        
        total_chars = sum(len(part.strip()) for part in parts)
        if total_chars == 0:
            continue
        
        current_start = start_ms
        for i, p in enumerate(parts):
            p_chars = len(p.strip())
            ratio = p_chars / total_chars
            part_ms = int(total_ms * ratio)
            
            if i == len(parts) - 1:
                current_end = end_ms
            else:
                current_end = current_start + part_ms
                if current_end > end_ms:
                    current_end = end_ms
            
            new_time = f"{ms_to_time(current_start)} --> {ms_to_time(current_end)}"
            new_blocks.append([str(new_index), new_time, p])
            
            current_start = current_end
            new_index += 1

    return "\n\n".join(["\n".join(b) for b in new_blocks]) + "\n"

def optimize_srt(input_path, output_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取SRT文件失败：{input_path} | 错误：{e}")
        return False

    optimized_content = optimize_srt_content(content)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(optimized_content)
        return True
    except Exception as e:
        print(f"写入优化后SRT失败：{output_path} | 错误：{e}")
        return False

def transcribe_audio(audio_input, log_cb=None, is_local_file=False):
    def log(msg):
        if log_cb:
            log_cb(msg)
        else:
            print(msg)
    
    task_id = str(uuid.uuid4())
    log("任务ID：" + task_id)
    
    if is_local_file:
        log("本地文件：" + audio_input)
    else:
        log("音频地址：" + audio_input)

    headers = {
        "X-Api-Key": API_KEY,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Request-Id": task_id,
        "X-Api-Sequence": "-1",
        "Content-Type": "application/json"
    }

    if is_local_file:
        audio_base64 = file_to_base64(audio_input)
        body = {
            "user": {"uid": "user123"},
            "audio": {"data": audio_base64, "format": "mp3"},
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "show_utterances": True
            }
        }
    else:
        body = {
            "user": {"uid": "user123"},
            "audio": {"url": audio_input, "format": "mp3"},
            "request": {
                "model_name": "bigmodel",
                "enable_itn": True,
                "enable_punc": True,
                "show_utterances": True
            }
        }

    log("提交转写任务...")
    resp = requests.post(SUBMIT_URL, headers=headers, json=body)
    code = resp.headers.get("X-Api-Status-Code")
    msg = resp.headers.get("X-Api-Message")
    log(f"提交结果：{code} | {msg}")
    
    if code == "45000010":
        log("")
        log("="*50)
        log("❌ API Key 无效！")
        log("请访问以下链接获取或更新 API Key：")
        log("https://console.volcengine.com/speech/new/setting/apikeys?projectName=default")
        log("然后在程序的\"设置\"页面更新 API Key")
        log("="*50)
        log("")

    if code != "20000000":
        log("提交失败！")
        return None

    log("任务提交成功，轮询识别结果...")
    result = None
    while True:
        time.sleep(2)
        q_resp = requests.post(QUERY_URL, headers=headers, json={})
        q_code = q_resp.headers.get("X-Api-Status-Code")
        q_msg = q_resp.headers.get("X-Api-Message")

        log(f"查询状态：{q_code} | {q_msg}")

        if q_code in ("20000001", "20000002"):
            continue
        if q_code != "20000000":
            log("识别失败")
            return None

        result = q_resp.json()
        break

    return result

def process_single_audio(audio_input, file_index, log_cb=None, is_local_file=False, filename_prefix=None):
    def log(msg):
        if log_cb:
            log_cb(msg)
        else:
            print(msg)
    
    log(f"\n===== 开始处理第 {file_index} 个音频 =====")
    
    result = transcribe_audio(audio_input, log_cb, is_local_file)
    if not result:
        log(f"第 {file_index} 个音频处理失败")
        return

    utters = result.get("result", {}).get("utterances", [])
    if not utters:
        log(f"第 {file_index} 个音频未获取到分句信息")
        return

    if filename_prefix:
        base_name = filename_prefix
    else:
        base_name = str(file_index)
    
    # 创建 SRT 文件夹
    srt_dir = os.path.join(os.getcwd(), "SRT")
    if not os.path.exists(srt_dir):
        os.makedirs(srt_dir)
    
    raw_srt_filename = os.path.join(srt_dir, f"{base_name}.srt")
    srt_content = generate_srt(utters)
    with open(raw_srt_filename, "w", encoding="utf-8") as f:
        f.write(srt_content)
    log(f"已生成原始SRT：{raw_srt_filename}")
    log("识别文本：\n" + result["result"]["text"])

    optimized_srt_filename = os.path.join(srt_dir, f"{base_name}已优化.srt")
    if optimize_srt(raw_srt_filename, optimized_srt_filename):
        log(f"已生成优化后SRT：{optimized_srt_filename}")
    else:
        log(f"第 {file_index} 个音频SRT优化失败")

def process_audio_list(url_list, log_cb=None):
    def log(msg):
        if log_cb:
            log_cb(msg)
        else:
            print(msg)
    
    total = len(url_list)
    for index, audio_url in enumerate(url_list, start=1):
        process_single_audio(audio_url, index, log_cb)
    
    log("\n所有音频处理完毕！")

def main():
    for index, audio_url in enumerate(AUDIO_URL_LIST, start=1):
        process_single_audio(audio_url, index)
    
    print("\n所有音频处理完毕！")

if __name__ == "__main__":
    main()
