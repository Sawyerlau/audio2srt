#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import index as idx_module


def main():
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
    
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Invalid arguments"}))
        return

    command = sys.argv[1]
    options_json = sys.argv[2]

    try:
        options = json.loads(options_json)
    except:
        print(json.dumps({"error": "Invalid JSON"}))
        return

    if command == "process_audio":
        result = process_audio_command(options)
    elif command == "optimize_srt":
        result = optimize_srt_command(options)
    else:
        result = {"error": "Unknown command"}

    print(json.dumps(result))


def log(message):
    print(message, file=sys.stderr, flush=True)


def process_audio_command(options):
    try:
        input_type = options.get("type", "local")
        inputs = options.get("inputs", [])
        config_data = options.get("config", None)

        if config_data:
            # 正确更新 index 模块的全局变量
            idx_module.config.update(config_data)
            idx_module.API_KEY = config_data["API_KEY"]
            idx_module.RESOURCE_ID = config_data["RESOURCE_ID"]
            log(f"已加载配置 - API_KEY: {'已设置' if config_data.get('API_KEY') else '未设置'}")

        for idx, input_item in enumerate(inputs):
            log(f"\n===== 开始处理第 {idx + 1} 个文件 =====")
            
            if input_type == "local":
                filename_prefix = os.path.splitext(os.path.basename(input_item))[0]
                idx_module.process_single_audio(
                    input_item,
                    idx + 1,
                    log,
                    is_local_file=True,
                    filename_prefix=filename_prefix
                )
            else:
                idx_module.process_single_audio(
                    input_item,
                    idx + 1,
                    log,
                    is_local_file=False
                )

        return {"success": True, "message": "Processing completed"}
    except Exception as e:
        log(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}


def optimize_srt_command(options):
    try:
        input_path = options.get("input_path")
        config_data = options.get("config", None)

        if config_data:
            idx_module.config.update(config_data)
            idx_module.API_KEY = config_data["API_KEY"]
            idx_module.RESOURCE_ID = config_data["RESOURCE_ID"]

        srt_dir = os.path.join(os.getcwd(), "SRT")
        if not os.path.exists(srt_dir):
            os.makedirs(srt_dir)

        filename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(srt_dir, f"{filename}_opt.srt")

        log(f"正在优化SRT文件: {input_path}")
        success = idx_module.optimize_srt(input_path, output_path)

        if success:
            log(f"优化完成，输出文件: {output_path}")
            return {"success": True, "output_path": output_path}
        else:
            return {"success": False, "error": "Optimization failed"}
    except Exception as e:
        log(f"Error: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    main()
