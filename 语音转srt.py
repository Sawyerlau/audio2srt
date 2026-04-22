import requests
import uuid
import time
import json

# ===================== 配置区 =====================
API_KEY = "6804f065-c9b1-4bb3-b250-6a05e489b3b4"
RESOURCE_ID = "volc.bigasr.auc"  # 录音1.0标准版

# 在这里添加你所有的音频链接，会按顺序生成 1.srt、2.srt、3.srt...
AUDIO_URL_LIST = [
    "https://tts-file2.com/s14/file/2026-04-22-092700_148811.mp3"
]
# ====================================================

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

def process_single_audio(audio_url, file_index):
    """处理单个音频并生成对应序号的srt文件"""
    task_id = str(uuid.uuid4())
    print(f"\n===== 开始处理第 {file_index} 个音频 =====")
    print("任务ID：", task_id)
    print("音频地址：", audio_url)

    headers = {
        "X-Api-Key": API_KEY,
        "X-Api-Resource-Id": RESOURCE_ID,
        "X-Api-Request-Id": task_id,
        "X-Api-Sequence": "-1",
        "Content-Type": "application/json"
    }

    body = {
        "user": {
            "uid": "user123"
        },
        "audio": {
            "url": audio_url,
            "format": "mp3"
        },
        "request": {
            "model_name": "bigmodel",
            "enable_itn": True,
            "enable_punc": True,
            "show_utterances": True
        }
    }

    # 提交任务
    print("提交任务...")
    resp = requests.post(SUBMIT_URL, headers=headers, json=body)
    code = resp.headers.get("X-Api-Status-Code")
    msg = resp.headers.get("X-Api-Message")
    print(f"提交结果：{code} | {msg}")

    if code != "20000000":
        print(f"第 {file_index} 个音频提交失败！")
        return

    # 轮询结果
    print("任务提交成功，轮询识别结果...")
    while True:
        time.sleep(2)
        q_resp = requests.post(QUERY_URL, headers=headers, json={})
        q_code = q_resp.headers.get("X-Api-Status-Code")
        q_msg = q_resp.headers.get("X-Api-Message")

        print(f"查询状态：{q_code} | {q_msg}")

        if q_code in ("20000001", "20000002"):
            continue
        if q_code != "20000000":
            print(f"第 {file_index} 个音频识别失败")
            return

        result = q_resp.json()
        break

    # 生成srt
    utters = result.get("result", {}).get("utterances", [])
    if not utters:
        print(f"第 {file_index} 个音频未获取到分句信息")
        return

    # 按序号命名：1.srt、2.srt、3.srt...
    srt_filename = f"{file_index}.srt"
    srt_content = generate_srt(utters)
    with open(srt_filename, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"\n✅ 第 {file_index} 个音频处理完成！已生成 {srt_filename}")
    print("识别文本：\n" + result["result"]["text"])

def main():
    # 遍历所有音频链接，按顺序处理
    for index, audio_url in enumerate(AUDIO_URL_LIST, start=1):
        process_single_audio(audio_url, index)
    
    print("\n🎉 所有音频处理完毕！")

if __name__ == "__main__":
    main()