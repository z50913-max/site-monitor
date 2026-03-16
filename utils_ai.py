# utils_ai.py
print(">>> [系统] 正在加载 AI 模块...") # 强制打印，证明脚本运行了
import requests
import base64
import config
import os
import time

def build_request_headers():
    headers = {}
    api_key = getattr(config, "LLM_API_KEY", "")
    header_name = getattr(config, "LLM_API_KEY_HEADER", "Authorization")
    prefix = getattr(config, "LLM_API_KEY_PREFIX", "Bearer ")

    if api_key:
        headers[header_name] = f"{prefix}{api_key}" if prefix else api_key

    return headers

def analyze_content(text, image_path=None):
    messages = []
    user_content = [{"type": "text", "text": text}]
    
    # 图片处理逻辑
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            b64_str = base64.b64encode(img_file.read()).decode('utf-8')
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_str}"}
            })
            
    messages.append({"role": "user", "content": user_content})

    payload = {
        "model": config.MODEL_NAME,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 100
    }

    try:
        # 发送请求
        resp = requests.post(
            config.LLM_API_URL,
            json=payload,
            headers=build_request_headers(),
            timeout=60
        )
        
        if resp.status_code != 200:
            return False, f"HTTP错误 (状态码: {resp.status_code}) - 内容: {resp.text}"
            
        try:
            res_json = resp.json()
            content = res_json['choices'][0]['message']['content']
            return True, content
        except:
            return False, f"JSON解析失败: {resp.text[:200]}"
            
    except Exception as e:
        return False, f"请求异常: {str(e)}"

# === 独立测试入口 (这一段必须有！) ===
if __name__ == "__main__":
    print("--------------------------------------------------")
    print(">>> [3/3] 开始测试：Qwen 算力接口 (AI)")
    print(f"目标接口: {config.LLM_API_URL}")
    print(f"目标模型: {config.MODEL_NAME}")
    print("正在发送测试请求 (预计耗时 5-20 秒)...")
    
    start_time = time.time()
    # 发送一个简单的测试请求
    success, result = analyze_content("请回复：系统正常")
    end_time = time.time()
    
    duration = end_time - start_time

    if success:
        print(f"\n【测试正常】 (耗时: {duration:.2f}秒)")
        print(f"AI 回复内容: {result}")
    else:
        print(f"\n【测试失败】 (耗时: {duration:.2f}秒)")
        print(f"原因: {result}")
    print("--------------------------------------------------")
