# config.py

# === 基础配置 ===
SITES = [
    "url,url,url"
]

# === 算力服务器配置 (Qwen2.5-VL) ===
LLM_API_URL = "https://coding.dashscope.aliyuncs.com/apps/anthropic/v1"
# 请确认你的模型名称，vLLM通常叫 "qwen2.5-vl-72b" 或类似的
MODEL_NAME = "qwen2.5_vl_72b" 
# 可选鉴权配置：
# 1. 如果算力服务器免密调用，保持 LLM_API_KEY = "" 不用改
# 2. 如果算力服务器需要密钥，就把密钥填到 LLM_API_KEY
# 3. 默认按 OpenAI 兼容格式发送：
#    Authorization: Bearer 你的密钥
# 4. 如果对方服务不是这个格式，再改下面两个参数
LLM_API_KEY = ""
# 请求头名称，常见值：
# "Authorization" 或 "X-API-Key"
LLM_API_KEY_HEADER = "Authorization"
# 请求头前缀，常见值：
# "Bearer " 或 ""（有些服务只要原始密钥，不要 Bearer）
LLM_API_KEY_PREFIX = "Bearer "

# === 企业微信配置 ===
WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"

# === 邮箱配置 (SMTP) ===
SMTP_CONFIG = {
    "host": "smtp.qiye.163.com",
    "port": 465,
    "user": "EMAS@163.com",
    "password": "密钥",
    "to_addrs": ["notice@163.com"]
}

# === 路径配置 ===
STATE_FILE = "site_state.json"
LOG_FILE = "monitor_system.log"
