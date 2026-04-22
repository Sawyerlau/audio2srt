# ====================== SRT字幕批量优化工具 ======================
# 功能：自动处理当前目录所有srt | 按逗号拆分 | 时间均分不重叠 | 删句号
# 输出：原文件名+已优化.srt
# ==================================================================

import re
import os

# ====================== 可自定义参数 ======================
MAX_LENGTH = 25       # 每行字幕最大字数
SPLIT_SYMBOL = "，"   # 按中文逗号拆分
DELETE_PERIOD = True  # 删除句号
# ==========================================================

def time_to_ms(time_str):
    """时间字符串转毫秒"""
    time_str = time_str.replace(',', '.')
    parts = time_str.split(':')
    h = int(parts[0])
    m = int(parts[1])
    s = float(parts[2])
    return int((h * 3600 + m * 60 + s) * 1000)

def ms_to_time(ms):
    """毫秒转回SRT时间格式"""
    ms = int(ms)
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    millis = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

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

def process_single_srt(input_path, output_path):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print(f"⚠️  读取失败：{input_path}")
        return

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

    with open(output_path, 'w', encoding='utf-8') as f:
        for b in new_blocks:
            f.write('\n'.join(b) + '\n\n')

    print(f"✅ 已完成：{os.path.basename(output_path)}")

def batch_process_srt():
    current_dir = os.getcwd()
    files = [f for f in os.listdir(current_dir) if f.lower().endswith(".srt")]
    
    if not files:
        print("❌ 当前目录没有找到 SRT 文件！")
        return

    print(f"📂 找到 {len(files)} 个 SRT 文件，开始处理...\n")
    
    for file in files:
        if "已优化" in file:
            continue  # 跳过已经处理过的文件
        
        input_path = os.path.join(current_dir, file)
        name, ext = os.path.splitext(file)
        output_file = f"{name}已优化{ext}"
        output_path = os.path.join(current_dir, output_file)
        
        process_single_srt(input_path, output_path)

    print("\n🎉 所有文件处理完成！")

if __name__ == "__main__":
    batch_process_srt()